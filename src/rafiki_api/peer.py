import requests

from helpers.signature import GraphQLClient
from settings import settings


def get_peer_by_url(client: GraphQLClient, peer_url: str, asset_id: str, tenant_id: str):
    graphql_query = {
        "query": """
            query GetPeerByAddressAndAsset($address: String!, $assetId: String!) {
              peerByAddressAndAsset(staticIlpAddress: $address, assetId: $assetId) {
                id
                name
                http {
                  outgoing {
                    authToken
                    endpoint
                  }
                }
                liquidity
                liquidityThreshold
                tenantId
              }
            }
        """,
        "variables": {
            "address": peer_url,
            "assetId": asset_id,
            "tenantId": tenant_id
        }
    }
    headers = client.get_signature_headers(graphql_query)
    peer = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        peer = response.json()
        if peer.get('errors'):
            return None
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return peer


def create_auto_peer(client: GraphQLClient, peer_url: str, asset_id: str, liquidity_to_deposit: int):
    get_peer = get_peer_by_url(client, peer_url, asset_id, settings.tenant_id)
    print(get_peer)
    if get_peer and get_peer.get('data', {}).get('id'):
        print(f"Peer already exists: {get_peer}")
        return get_peer
    graphql_query = {
        "query": """
             mutation CreateOrUpdatePeerByUrl($input: CreateOrUpdatePeerByUrlInput!) {
              createOrUpdatePeerByUrl(input: $input) {
                peer {
                  id
                  name
                  asset {
                    id
                    scale
                    code
                    withdrawalThreshold
                  }
                }
              }
            }
        """,
        "variables": {
            "input": {
                "peerUrl": peer_url,
                "assetId": asset_id,
                "liquidityToDeposit": liquidity_to_deposit
            }
        }
    }
    headers = client.get_signature_headers(graphql_query)
    peer = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        peer = response.json()
        if peer.get('errors'):
            return None
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return peer
