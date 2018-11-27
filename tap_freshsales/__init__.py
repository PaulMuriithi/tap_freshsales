#!/usr/bin/env python3
import os
import json
import sys
import time
import backoff
import requests
from requests.exceptions import HTTPError
import singer
from singer import utils, metadata

from tap_freshsales import utils as tap_utils


REQUIRED_CONFIG_KEYS = ["api_key", "domain", "start_date"]
PER_PAGE = 100
BASE_URL = "https://{}.freshsales.io"
CONFIG = {}
STATE = {}
LOGGER = singer.get_logger()
SESSION = requests.Session()

endpoints = {
    "leads": "/api/leads/view/",
    "contacts": "/api/contacts/view/",
    "accounts": "/api/sales_accounts/view/",
    "deals": "/api/deals/view/",
    "tasks": "/api/tasks?filter=",
    "appointments": "/api/appointments?filter=",
    "sales": "/api/sales_activities"
}

def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

def get_url(endpoint, **kwargs):
    return BASE_URL.format(CONFIG['domain']) + endpoints[endpoint].format(**kwargs)

# Load schemas from schemas folder
def load_schemas():
    schemas = {}

    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = json.load(file)

    return schemas

def discover():
    raw_schemas = load_schemas()
    streams = []

    for schema_name, schema in raw_schemas.items():

        # TODO: populate any metadata and stream's key properties here..
        stream_metadata = []
        stream_key_properties = []

        # create and add catalog entry
        catalog_entry = {
            'stream': schema_name,
            'tap_stream_id': schema_name,
            'schema': schema,
            'metadata' : [],
            'key_properties': []
        }
        streams.append(catalog_entry)

    return {'streams': streams}

def get_selected_streams(catalog):
    '''
    Gets selected streams.  Checks schema's 'selected' first (legacy)
    and then checks metadata (current), looking for an empty breadcrumb
    and mdata with a 'selected' entry
    '''
    selected_streams = []
    for stream in catalog.streams:
        stream_metadata = metadata.to_map(stream.metadata)
        # stream metadata will have an empty breadcrumb
        if metadata.get(stream_metadata, (), "selected"):
            selected_streams.append(stream.tap_stream_id)

    return selected_streams

def sync_accounts():
    '''
    Sync Sales Accounts Data, Standard schema is kept as columns,
    Custom fields are saved as JSON content
    '''

def sync(config, state, catalog):

    selected_stream_ids = get_selected_streams(catalog)

    # Loop over streams in catalog
    for stream in catalog.streams:
        stream_id = stream.tap_stream_id
        stream_schema = stream.schema
        if stream_id in selected_stream_ids:
            
            LOGGER.info('Syncing stream:' + stream_id)
    return

@utils.handle_top_exception(LOGGER)
def main():

    # Parse command line arguments
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)

    # If discover flag was passed, run discovery mode and dump output to stdout
    if args.discover:
        catalog = discover()
        print(json.dumps(catalog, indent=2))
    # Otherwise run in sync mode
    else:
        if args.catalog:
            catalog = args.catalog
        else:
            catalog =  discover()

        sync(args.config, args.state, catalog)

if __name__ == "__main__":
    main()
