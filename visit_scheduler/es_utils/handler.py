import datetime

from fastapi import HTTPException

from visit_scheduler.app.models.models import SearchVendorModel
from visit_scheduler.es_utils.client import get_es_client
from visit_scheduler.es_utils.models import (
    ES_INDEX_TIME_SLOTS,
    ES_INDEX_VENDORS,
    TIME_SLOT_DURATION,
    RatingModel,
    TimeSlotModelRated,
    TimeSlotReturnModel,
    BaseTimeSlotModel,
    VendorModel,
    TimeSlotStatus,
)
from visit_scheduler.package_utils.logger_conf import logger


def add_vendor(data: VendorModel):
    es_client = get_es_client()
    es_client.index(index=ES_INDEX_VENDORS, body=data.model_dump())
    logger.info(f"Added vendor: {data.vendor_email}")


def add_time_slot(data: BaseTimeSlotModel):
    # times slots should be chunked into N min slots with rounded to the nearest N min
    slot_duration = datetime.timedelta(minutes=TIME_SLOT_DURATION)
    total_duration = data.end_time - data.start_time
    no_chunks = int(total_duration.total_seconds() / slot_duration.total_seconds())
    for i in range(no_chunks):
        start_time = data.start_time + i * slot_duration
        end_time = start_time + slot_duration
        _add_time_slot_chunk(
            BaseTimeSlotModel(vendor_email=data.vendor_email, start_time=start_time, end_time=end_time, 
                              status=data.status, vendor_name=data.vendor_name)
        )


def _add_time_slot_chunk(data: BaseTimeSlotModel):
    es_client = get_es_client()
    es_client.index(index=ES_INDEX_TIME_SLOTS, body=data.model_dump())


def add_rating(data: RatingModel):
    # update the vendor rating
    es_client = get_es_client()
    es_client.update(
        index=ES_INDEX_VENDORS, id=data.vendor_email, body={"rating": data.rating, "rating_amount": data.rating_amount}
    )


def _get_time_slots(data: SearchVendorModel, vendor_data: list[tuple[str, float, str, float, int]]):
    # If no vendors found, return empty list
    if not vendor_data:
        return []

    # Extract just the emails for the Elasticsearch query
    vendor_emails = [email for email, _, _, _, _ in vendor_data]

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

    # Create vendor score mapping for sorting
    vendor_scores = {email: {"score": score, "vendor_name": vendor_name, "vendor_rating": vendor_rating, "vendor_rating_amount": vendor_rating_amount} 
                     for email, score, vendor_name, vendor_rating, vendor_rating_amount in vendor_data}

    # Convert to TimeSlotReturnModel objects with vendor data
    time_slot_objects = []
    for hit in time_slots["hits"]["hits"]:
        source = hit["_source"]
        vendor_email = source["vendor_email"]
        vendor_info = vendor_scores.get(vendor_email, {"vendor_name": "", "vendor_rating": 0.0, "vendor_rating_amount": 0})
        
        time_slot = TimeSlotReturnModel(
            **source,
            vendor_rating=vendor_info["vendor_rating"],
            vendor_rating_amount=vendor_info["vendor_rating_amount"],
            id=hit["_id"]
        )
        time_slot_objects.append(time_slot)

    # Sort time slots by vendor score (descending), then by start_time
    sorted_time_slots = sorted(
        time_slot_objects,
        key=lambda slot: (
            -vendor_scores.get(slot.vendor_email, {"score": 0})["score"],  # Negative for descending order (higher scores first)
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

    # Return both vendor emails and their scores
    vendor_data = [(hit["_source"]["vendor_email"], hit["_score"], hit["_source"]["name"], hit["_source"]["rating"], hit["_source"]["rating_amount"]) 
                   for hit in vendors["hits"]["hits"]]
    return vendor_data


def search_vendors(data: SearchVendorModel):
    # search is two stage process:
    # 1. search for vendors in the area with the service type sort by rating and location
    # 2. filter the vendors by the time slot

    # 1. search for vendors in the area with the service type sort by rating and location
    vendor_data = _get_vendor_emails(data)

    # 2. filter the vendors by the time slot and group by vendor_id
    return _get_time_slots(data, vendor_data)


def get_all_time_slots():
    # shit doesnt work. but doesnt matter
    es_client = get_es_client()
    return [
        TimeSlotReturnModel(**hit["_source"], id=hit["_id"], vendor_rating=get_vendor_rating(hit["_source"]["vendor_email"]), vendor_rating_amount=get_vendor_rating_amount(hit["_source"]["vendor_email"]))
        for hit in es_client.search(index=ES_INDEX_TIME_SLOTS, body={"query": {"match_all": {}}})["hits"]["hits"]
    ]

def change_es_time_slot_status(time_slot_ids: list[str], status: TimeSlotStatus):
    es_client = get_es_client()
    for time_slot_id in time_slot_ids:
        es_client.update(index=ES_INDEX_TIME_SLOTS, id=time_slot_id, body={"status": status})


def get_time_slot(time_slot_ids: list[str]):
    es_client = get_es_client()
    # join time slots into one time slot if they are consecutive
    time_slots = [es_client.get(index=ES_INDEX_TIME_SLOTS, id=x) for x in time_slot_ids]
    vendor_rating, vendor_rating_amount = get_vendor_rating_and_amount(time_slots[0]["_source"]["vendor_email"])
    time_slots = [BaseTimeSlotModel(**hit["_source"]) for hit in time_slots]
    time_slots = sorted(time_slots, key=lambda x: x.start_time)
    for i in range(len(time_slots) - 1):
        if time_slots[i].end_time != time_slots[i + 1].start_time:
            raise HTTPException(status_code=400, detail="Time slots are not consecutive") # nit: we probably dont want to raise http execepton in not fastapi part of the code
    return BaseTimeSlotModel(vendor_email=time_slots[0].vendor_email, start_time=time_slots[0].start_time, end_time=time_slots[-1].end_time, status=TimeSlotStatus.BOOKED, vendor_name=time_slots[0].vendor_name)


def get_vendor_rating(vendor_email: str) -> tuple[float, int]:
    es_client = get_es_client()
    vendor = es_client.search(index=ES_INDEX_VENDORS, body={"query": {"match": {"vendor_email": vendor_email}}})
    return vendor["hits"]["hits"][0]["_source"]["rating"]

def get_vendor_rating_and_amount(vendor_email: str) -> tuple[float, int]:
    es_client = get_es_client()
    vendor = es_client.search(index=ES_INDEX_VENDORS, body={"query": {"match": {"vendor_email": vendor_email}}})
    return vendor["hits"]["hits"][0]["_source"]["rating"], vendor["hits"]["hits"][0]["_source"]["rating_amount"]

def get_vendor_rating_amount(vendor_email: str) -> int:
    es_client = get_es_client()
    vendor = es_client.search(index=ES_INDEX_VENDORS, body={"query": {"match": {"vendor_email": vendor_email}}})
    return vendor["hits"]["hits"][0]["_source"]["rating_amount"]