es_mapping_vendor = {
      "_all":           { "enabled": False },
      "properties": {
        "user_id":              { "type": "string"  },
        "name":                 { "type": "string"  },
        "rating":               { "type": "float" },
        "rating_amount":        { "type": "integer" },
        "location":             { "type": "geo_point"},
        "service_types":        { "type": "string" },
      }
}

es_mapping_time_slot = {
      "_all":           { "enabled": False },
      "properties": {
        "start_time": { "type": "date", "format": "strict_date_optional_time||epoch_millis" },
        "end_time":   { "type": "date", "format": "strict_date_optional_time||epoch_millis" },
        "vendor_id":  { "type": "string"  },
        "status":     { "type": "string"  },
      }
}


# implementation note:
# make two queries: one for vendors -> then based on vendors pre chosen, choose only those with matching timeslots