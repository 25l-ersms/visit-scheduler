import datetime

from visit_scheduler.app.models.models import SearchVendorModel
from visit_scheduler.es_utils.client import get_es_client
from visit_scheduler.es_utils.models import (
    ES_INDEX_TIME_SLOTS,
    ES_INDEX_VENDORS,
    TIME_SLOT_DURATION,
    RatingModel,
    TimeSlotModel,
    VendorModel,
)
from visit_scheduler.package_utils.logger_conf import logger


def add_vendor(data: VendorModel):
    es_client = get_es_client()
    es_client.index(index=ES_INDEX_VENDORS, body=data.model_dump())


def add_time_slot(data: TimeSlotModel):
    # times slots should be chunked into N min slots with rounded to the nearest N min
    slot_duration = datetime.timedelta(minutes=TIME_SLOT_DURATION)
    total_duration = data.end_time - data.start_time
    no_chunks = int(total_duration.total_seconds() / slot_duration.total_seconds())
    for i in range(no_chunks):
        start_time = data.start_time + i * slot_duration
        end_time = start_time + slot_duration
        _add_time_slot_chunk(
            TimeSlotModel(vendor_email=data.vendor_email, start_time=start_time, end_time=end_time, status=data.status)
        )


def _add_time_slot_chunk(data: TimeSlotModel):
    es_client = get_es_client()
    es_client.index(index=ES_INDEX_TIME_SLOTS, body=data.model_dump())


def add_rating(data: RatingModel):
    # update the vendor rating
    es_client = get_es_client()
    es_client.update(
        index=ES_INDEX_VENDORS, id=data.vendor_email, body={"rating": data.rating, "rating_amount": data.rating_amount}
    )


def _get_time_slots(data: SearchVendorModel, vendor_data: list[tuple[str, float]]):
    # If no vendors found, return empty list
    if not vendor_data:
        return []

    # Extract just the emails for the Elasticsearch query
    vendor_emails = [email for email, score in vendor_data]

    es_client = get_es_client()
    query_time_slots = {
        "query": {
            "bool": {
                "must": [
                    {"range": {"start_time": {"gte": data.start_time}}},
                    {"range": {"end_time": {"lte": data.end_time}}},
                    {"terms": {"vendor_email": vendor_emails}},
                    {"term": {"status": "available"}},
                ]
            }
        },
        "aggs": {"by_vendor": {"terms": {"field": "vendor_email", "size": len(vendor_emails)}}},
        "size": 1000,
    }

    time_slots = es_client.search(index=ES_INDEX_TIME_SLOTS, body=query_time_slots)
    print(f"Time slots: {time_slots}")

    # Convert to TimeSlotModel objects
    time_slot_objects = [TimeSlotModel(**hit["_source"]) for hit in time_slots["hits"]["hits"]]

    # Create vendor score mapping for sorting
    vendor_scores = {email: score for email, score in vendor_data}

    # Sort time slots by vendor score (descending), then by start_time
    sorted_time_slots = sorted(
        time_slot_objects,
        key=lambda slot: (
            -vendor_scores.get(slot.vendor_email, 0),  # Negative for descending order (higher scores first)
            slot.start_time,  # Secondary sort by start time
        ),
    )

    return sorted_time_slots


def _get_vendor_emails(data: SearchVendorModel):
    es_client = get_es_client()
    query_vendors = {
        "query": {
            "function_score": {
                "query": {"match": {"service_types": data.service_type}},
                "functions": [
                    {
                        # Rating score - higher weight (10x) since it's more important
                        "field_value_factor": {"field": "rating", "factor": 1, "missing": 0},
                        "weight": 10,  # Rating is most important
                    },
                    {
                        # Distance score - decay function based on distance from user
                        "gauss": {
                            "location": {
                                "origin": {"lat": data.location_lat, "lon": data.location_lon},
                                "scale": "5km",  # Distance at which the score is reduced by half
                                "decay": 0.5,
                            }
                        },
                        "weight": 2,
                    },
                ],
                "score_mode": "sum",
                "boost_mode": "replace",  # Use only the function scores, ignore text relevance
            }
        },
        "sort": [
            {"_score": {"order": "desc"}},
        ],
        "size": 1000,
    }
    vendors = es_client.search(index=ES_INDEX_VENDORS, body=query_vendors)

    # Debug: Log vendor scores TODO delete
    logger.info("Vendor search results with scores:")
    for hit in vendors["hits"]["hits"]:
        logger.info(
            f"Vendor: {hit['_source']['vendor_email']}, Score: {hit['_score']}, Location: {hit['_source'].get('location', 'N/A')}"
        )

    # Return both vendor emails and their scores
    vendor_data = [(hit["_source"]["vendor_email"], hit["_score"]) for hit in vendors["hits"]["hits"]]
    return vendor_data


def search_vendors(data: SearchVendorModel):
    # search is two stage process:
    # 1. search for vendors in the area with the service type sort by rating and location
    # 2. filter the vendors by the time slot

    # 1. search for vendors in the area with the service type sort by rating and location
    vendor_data = _get_vendor_emails(data)
    print(f"Vendor data: {vendor_data}")

    # 2. filter the vendors by the time slot and group by vendor_id
    return _get_time_slots(data, vendor_data)


def get_all_time_slots():
    es_client = get_es_client()
    return [
        TimeSlotModel(**hit["_source"])
        for hit in es_client.search(index=ES_INDEX_TIME_SLOTS, body={"query": {"match_all": {}}})["hits"]["hits"]
    ]
