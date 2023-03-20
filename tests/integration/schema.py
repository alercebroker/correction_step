# previous detections schema


EXTRA_FIELDS = {
    "type": "map",
    "values": ["null", "int", "float", "string"],
    "default": {},
}

DETECTION = {
    "type": "record",
    "name": "alert",
    "fields": [
        {"name": "oid", "type": "string"},
        {"name": "tid", "type": "string"},
        {"name": "pid", "type": "long"},
        {"name": "candid", "type": ["long", "string"]},
        {"name": "mjd", "type": "double"},
        {"name": "fid", "type": "int"},
        {"name": "ra", "type": "double"},
        {"name": "dec", "type": "double"},
        {"name": "mag", "type": "float"},
        {"name": "e_mag", "type": "float"},
        {"name": "isdiffpos", "type": "int"},
        {"name": "e_ra", "type": "float"},
        {"name": "e_dec", "type": "float"},
        {
            "name": "extra_fields",
            "type": EXTRA_FIELDS,
        },
        {"name": "aid", "type": "string"},
    ]
}

NON_DETECTION = {
    "type": "record",
    "name": "non_detection",
    "fields": [
        {"name": "aid", "type": "string"},
        {"name": "tid", "type": "string"},
        {"name": "oid", "type": "string"},
        {"name": "mjd", "type": "double"},
        {"name": "fid", "type": "int"},
        {"name": "diffmaglim", "type": "double"},
    ]
}

SCHEMA = {
    "type": "record",
    "doc": "Multi stream alert of any telescope/survey",
    "name": "alerce.alert",
    "fields": [
        {"name": "aid", "type": "string"},
        {"name": "new_alert", "type": DETECTION},
        {"name": "prv_detections", "type": {"type": "array", "items": "alert"}},
        {"name": "non_detections", "type": {"type": "array", "items": NON_DETECTION}}
    ],
}