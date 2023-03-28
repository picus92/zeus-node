import os
import requests
from requests.exceptions import RequestException
import time

METADATA_BASE_URL = "http://169.254.169.254/latest/"
METADATA_TIMEOUT = 1.0

class MetadataError(Exception):
    pass

def get_imdsv2_token():
    try:
        response = requests.put(METADATA_BASE_URL + "api/token",
                                headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
                                timeout=METADATA_TIMEOUT)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        raise MetadataError(f"Error fetching IMDSv2 token: {e}")

def get_metadata(path, token):
    try:
        response = requests.get(METADATA_BASE_URL + "meta-data/" + path, headers={"X-aws-ec2-metadata-token": token}, timeout=METADATA_TIMEOUT)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        raise MetadataError(f"Error fetching metadata: {e}")

def register_node():
    token = get_imdsv2_token()
    if not token:
        raise MetadataError("Failed to fetch IMDSv2 token. Exiting.")

    node_name = get_metadata("hostname", token)
    node_ip = get_metadata("local-ipv4", token)
    availability_zone = get_metadata("placement/availability-zone", token)
    availability_zone_id = get_metadata("placement/availability-zone-id", token)

    if not (node_name and node_ip and availability_zone):
        raise MetadataError("Failed to fetch metadata. Exiting.")

    return {
        "node_name": node_name,
        "node_ip": node_ip, 
        "availability_zone": availability_zone,
        "availability_zone_id": availability_zone_id
    }

try:
    node_metadata = register_node()
except MetadataError as e:
    print(str(e))
    exit(1)

# Keep the main thread alive
def shutdown_hook():
    print("Shutting down...")
    # do cleanup here

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    shutdown_hook()
