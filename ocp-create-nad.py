import json
from kubernetes import client

# 1. OpenShift Cluster Connection Configuration
OPENSHIFT_API_URL = "https://api.your-openshift-cluster.com:6443"
API_TOKEN = "sha256~your_openshift_api_token_here"

# Set up client configuration
config = client.Configuration()
config.host = OPENSHIFT_API_URL
config.api_key["authorization"] = f"Bearer {API_TOKEN}"

# Optional: Disable SSL verification for development clusters with self-signed certs
# config.verify_ssl = False

# Create API Client instance
api_client = client.ApiClient(config)
custom_api = client.CustomObjectsApi(api_client)

# 2. Define NetworkAttachmentDefinition (NAD) Manifest
namespace = "default"
nad_name = "macvlan-vlan100"

nad_manifest = {
    "apiVersion": "k8s.cni.cncf.io/v1",
    "kind": "NetworkAttachmentDefinition",
    "metadata": {
        "name": nad_name,
        "namespace": namespace,
        "annotations": {
            "description": "Macvlan network for VLAN 100 traffic"
        }
    },
    "spec": {
        # The CNI configuration must be passed as a JSON-encoded string
        "config": json.dumps({
            "cniVersion": "0.3.1",
            "name": nad_name,
            "type": "macvlan",
            "master": "eth1",
            "mode": "bridge",
            "ipam": {
                "type": "whereabouts",
                "range": "192.168.100.0/24",
                "range_start": "192.168.100.50",
                "range_end": "192.168.100.100",
                "gateway": "192.168.100.1"
            }
        })
    }
}

# 3. Apply NAD to the Cluster
def create_network_attachment_definition():
    try:
        response = custom_api.create_namespaced_custom_object(
            group="k8s.cni.cncf.io",
            version="v1",
            namespace=namespace,
            plural="network-attachment-definitions",
            body=nad_manifest
        )
        print(f"Successfully created NAD '{nad_name}' in namespace '{namespace}'.")
        print(f"Resource UID: {response['metadata']['uid']}")

    except client.exceptions.ApiException as e:
        if e.status == 409:
            print(f"NAD '{nad_name}' already exists in namespace '{namespace}'.")
        else:
            print(f"Failed to create NAD: {e}")

if __name__ == "__main__":
    create_network_attachment_definition()
