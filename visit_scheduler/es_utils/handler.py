from visit_scheduler.es_utils.models import VendorModel, ES_INDEX_VENDORS, ES_INDEX_TIME_SLOTS, TimeSlotModel, TIME_SLOT_DURATION, RatingModel
from visit_scheduler.es_utils.client import get_es_client
from visit_scheduler.app.models.models import SearchVendorModel

def add_vendor(data: VendorModel):
    es_client = get_es_client()
    es_client.index(index=ES_INDEX_VENDORS, body=data.model_dump())

def add_time_slot(data: TimeSlotModel):
    # times slots should be chanked into N min slots with rounded to the nearest N min
    no_chunks = (data.end_time - data.start_time) / TIME_SLOT_DURATION
    for i in range(no_chunks):
        start_time = data.start_time + i * TIME_SLOT_DURATION
        end_time = start_time + TIME_SLOT_DURATION
        _add_time_slot_chunk(TimeSlotModel(vendor_id=data.vendor_id, start_time=start_time, end_time=end_time, status=data.status))
    

def _add_time_slot_chunk(data: TimeSlotModel):
    es_client = get_es_client()
    es_client.index(index=ES_INDEX_TIME_SLOTS, body=data.model_dump())

def add_rating(data: RatingModel):
    # update the vendor rating
    es_client = get_es_client()
    es_client.update(index=ES_INDEX_VENDORS, id=data.vendor_id, body={"rating": data.rating, "rating_amount": data.rating_amount})

def _get_time_slots(data, vendor_ids):
    es_client = get_es_client()
    query_time_slots = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "start_time": {
                                "gte": data.start_time
                            }
                        }
                    },
                    {
                        "range": {
                            "end_time": {
                                "lte": data.end_time
                            }
                        }
                    },
                    {
                        "terms": {
                            "vendor_id": vendor_ids
                        }
                    },
                    {
                        "term": {
                            "status": "available"
                        }
                    }
                ]
            }
        },
        "aggs": {
            "by_vendor": {
                "terms": {
                    "field": "vendor_id",
                    "size": len(vendor_ids)
                },
            }
        },
        "size": 0  # We don't need hits, just aggregations
    }
    
    return es_client.search(index=ES_INDEX_TIME_SLOTS, body=query_time_slots)

def _get_vendor_ids(data):
    es_client = get_es_client()
    query_vendors = {
        "query": {
            "function_score": {
                "query": {
                    "match": {
                        "service_types": data.service_type
                    }
                },
                "functions": [ # final score function: rating * 3 + distance * (0.5 if distance < 5km else 1)
                    {
                        # Rating score - higher weight (3x) since it's more important
                        "field_value_factor": {
                            "field": "rating",
                            "factor": 3,
                            "missing": 0
                        }
                    },
                    {
                        # Distance score - decay function based on distance from user
                        "gauss": {
                            "location": {
                                "origin": {"lat": data.location[0], "lon": data.location[1]},
                                "scale": "5km",  # Distance at which the score is reduced by half
                                "decay": 0.5
                            }
                        },
                        "weight": 1
                    }
                ],
                "score_mode": "sum",
                "boost_mode": "multiply"
            }
        },
        "size": 1000  # Limit results to top 1000 matches
    }
    vendors = es_client.search(index=ES_INDEX_VENDORS, body=query_vendors)
    
    # Extract vendor IDs from the search results
    vendor_ids = [hit["_id"] for hit in vendors["hits"]["hits"]]
    return vendor_ids


def search_vendors(data: SearchVendorModel):
    # search is two stage process:
    # 1. search for vendors in the area with the service type sort by rating and location
    # 2. filter the vendors by the time slot
    
    # 1. search for vendors in the area with the service type sort by rating and location
    vendor_ids = _get_vendor_ids(data)
    
    # 2. filter the vendors by the time slot and group by vendor_id
    return _get_time_slots(data, vendor_ids)

def get_all_time_slots():
    es_client = get_es_client()
    return es_client.search(index=ES_INDEX_TIME_SLOTS, body={})