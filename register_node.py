# register_node.py

import os
import json
import boto3
import requests
from requests.exceptions import RequestException
import pyshark
import queue
import threading
import time
from prometheus_client import start_http_server, Counter

METADATA_BASE_URL = "http://169.254.169.254/latest/"
METADATA_TIMEOUT = 1.0

def get_imdsv2_token():
    try:
        response = requests.put(METADATA_BASE_URL + "api/token",
                                headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
                                timeout=METADATA_TIMEOUT)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        print(f"Error fetching IMDSv2 token: {e}")
        return None

def get_metadata(path, token):
    try:
        response = requests.get(METADATA_BASE_URL + "meta-data/" + path, headers={"X-aws-ec2-metadata-token": token}, timeout=METADATA_TIMEOUT)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        print(f"Error fetching metadata: {e}")
        return None

def register_node():
    token = get_imdsv2_token()
    if not token:
        print("Failed to fetch IMDSv2 token. Exiting.")
        return

    node_name = get_metadata("hostname", token)
    node_ip = get_metadata("local-ipv4", token)
    availability_zone = get_metadata("placement/availability-zone", token)
    availability_zone_id = get_metadata("placement/availability-zone-id", token)

    if node_name and node_ip and availability_zone:
        return {
            "node_name": node_name,
            "node_ip": node_ip, 
            "availability_zone": availability_zone,
            "availability_zone_id": availability_zone_id
        }

    else:
        print("Failed to fetch metadata. Exiting.")

node_metadata = register_node()
if not node_metadata:
    print("Failed to fetch node_metadata. Exiting.")
    pass

# Keep the main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass