import requests

from helpers.signature import GraphQLClient
from settings import settings


def get_asset_by_code_and_scale(client: GraphQLClient, code: str, scale: int, tenant_id: str ):
    graphql_query = {
        "query": """
            query GetAssetByCodeAndScale($code: String!, $scale: UInt8!) {
              assetByCodeAndScale(code: $code, scale: $scale) {
                id
                code
                scale
                liquidityThreshold
                tenantId
              }
            }
        """,
        "variables": {
            "code": code,
            "scale": scale,
            "tenantId": tenant_id
        }
    }
    headers = client.get_signature_headers(graphql_query)
    asset = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        asset = response.json()
        if asset.get('errors'):
            return None
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return asset

def get_asset_by_id(client: GraphQLClient, asset_id: str, tenant_id: str):
    graphql_query = {
        "query": """
            query GetAsset($id: String!) {
                asset(id: $id) {
                code
                createdAt
                id
                scale
                withdrawalThreshold
                liquidityThreshold
                liquidity
                sendingFee {
                    id
                    type
                    basisPoints
                    fixed
                }
                receivingFee {
                    id
                    type
                    basisPoints
                    fixed
                }
                tenantId
              }
            }
        """,
        "variables": {
            "id": asset_id,
            "tenantId": tenant_id
        }
    }
    headers = client.get_signature_headers(graphql_query)
    asset = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        asset = response.json()
        if asset.get('errors'):
            return None
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return asset


def create_asset(client: GraphQLClient, code: str, scale: int, tenant_id: str):
    validate_if_exists = get_asset_by_code_and_scale(client, code, scale, settings.tenant_id)
    if validate_if_exists:
        return validate_if_exists
    graphql_query = {
        "query": """
            mutation CreateAsset($input: CreateAssetInput!) {
              createAsset(input: $input) {
                asset {
                  id
                  code
                  scale
                  liquidityThreshold
                  tenantId
                }
              }
            }
        """,
        "variables": {
            "input": {
                "code": code,
                "scale": scale,
                "tenantId": tenant_id
            }
        }
    }
    headers = client.get_signature_headers(graphql_query)
    asset = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        asset = response.json()
        if asset.get('errors'):
            return None
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return asset
