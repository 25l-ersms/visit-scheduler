es_mapping_vendor = {
    "properties": {
        "user_id": {"type": "keyword"},  # Use keyword for exact matches
        "vendor_email": {"type": "keyword"},  # Use keyword for exact matches
        "name": {"type": "text"},  # Use text for full-text search
        "rating": {"type": "float"},
        "rating_amount": {"type": "integer"},
        "location": {"type": "geo_point"},
        "service_types": {"type": "text"},  # Use text for searchable service types
    }
}

es_mapping_time_slot = {
    "properties": {
        "start_time": {"type": "date", "format": "strict_date_optional_time||epoch_millis"},
        "end_time": {"type": "date", "format": "strict_date_optional_time||epoch_millis"},
        "vendor_email": {"type": "keyword"},  # Use keyword for exact matches
        "status": {"type": "keyword"},  # Use keyword for exact status matching
    }
}


# implementation note:
# make two queries: one for vendors -> then based on vendors pre chosen, choose only those with matching timeslots
