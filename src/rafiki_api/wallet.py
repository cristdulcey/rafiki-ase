import base64
import json
import os
import uuid

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from helpers.create_key import generate_jwk
from settings import settings


def get_wallet(client, wallet_id: str, tenant_id: str):
    graphql_query = {
        "query": """
            query GetWalletAddress($id: String!) {
                walletAddress(id: $id) {
                    id
                    asset {
                        id
                        code
                        scale
                        withdrawalThreshold
                        createdAt
                    }
                    liquidity
                    createdAt
                    incomingPayments {
                        edges {
                            node {
                                id
                                state
                                incomingAmount {
                                    value
                                }
                                receivedAmount {
                                    value
                                }
                            }
                            cursor
                        }
                        pageInfo {
                            endCursor
                            hasNextPage
                            hasPreviousPage
                            startCursor
                        }
                    }
                    walletAddressKeys {
                      edges {
                        node {
                          id
                          jwk {
                            kid
                            x
                            alg
                            kty
                            crv
                          }
                          revoked
                          createdAt
                        }
                      }
                      pageInfo {
                        endCursor
                        hasNextPage
                        hasPreviousPage
                        startCursor
                      }
                    }
                    status
                    additionalProperties {
                      key
                      value
                      visibleInOpenPayments
                    }
                    tenantId
                }
            }
        """,
        "variables": {
            "id": f"{wallet_id}",
            "tenantId": tenant_id
        }
    }
    headers = client.get_signature_headers(graphql_query)
    wallet = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        wallet_complete = response.json()
        if wallet_complete.get('errors'):
            return None
        wallet = {
            'liquidity': wallet_complete.get('data', {}).get('walletAddress', {}).get('liquidity', 0) or 0,
            'status': wallet_complete.get('data', {}).get('walletAddress', {}).get('status', False)
        }
        # accounts = get_accounts_by_id(
        #     [
        #         to_tiger_beetle_id(wallet_id)
        #     ]
        # )
        # for account in accounts:
        #     dict_account = account.__dict__
        #     if dict_account.get('user_data_128') != 0:
        #         dict_account['user_data_128_uuid'] = from_tiger_beetle_id(dict_account['user_data_128'])
        #     if dict_account.get('id') != 0:
        #         dict_account['id_uuid'] = from_tiger_beetle_id(dict_account['id'])
        #     if dict_account.get('timestamp') != 0:
        #         dict_account['timestamp_date'] = f'{datetime.fromtimestamp(dict_account.get("timestamp") / 1_000_000_000)}'
        #     print(f"\n{account.__dict__}\n")

    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return wallet


def create_wallet(client, wallet_path: str, asset_id: str, name: str,tenant_id: str,additional_properties: list = None):
    graphql_query = {
        "query": """
                mutation CreateWalletAddres($input: CreateWalletAddressInput!) {
                  createWalletAddress(input: $input) {
                    walletAddress {
                      id
                      createdAt
                      publicName
                      address
                      status
                      asset {
                        code
                        createdAt
                        id
                        scale
                        withdrawalThreshold
                      }
                      additionalProperties {
                        key
                        value
                        visibleInOpenPayments
                      }
                      tenantId
                    }
                  }
                }
            """,
        "variables": {
            "input": {
                "assetId": asset_id,
                "address": f'{settings.domain_wallet}/{wallet_path}',
                "publicName": name,
                "additionalProperties": additional_properties,
                "tenantId": tenant_id
            }
        }
    }
    headers = client.get_signature_headers(graphql_query)
    wallet = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        print(response.text)
        response.raise_for_status()
        wallet = response.json()
        if wallet.get('errors'):
            return None
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    except Exception as err:
        print("OOps: Something", err)
    return wallet


def create_wallet_address_key(client, wallet_id: str):
    private = ed25519.Ed25519PrivateKey.generate()
    public_key_pem = private.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    # Export private key in PEM (PKCS8)
    private_key_pem = private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    # SAVE KEYS TO FILES
    # # create directory for keys if not exists
    # if not os.path.exists(f"keys/{wallet_id}"):
    #     os.makedirs(f"keys/{wallet_id}")
    # # write private and public keys to files
    # with open(f"keys/{wallet_id}/private_key.pem", "w") as f:
    #     f.write(private_key_pem)
    #     f.close()
    # with open(f"keys/{wallet_id}/public_key.pem", "w") as f:
    #     f.write(public_key_pem)
    #     f.close()
    kid = uuid.uuid4()
    result_jwk = generate_jwk(private, f'keyid-{kid}')
    graphql_query = {
        "query": """
            mutation CreateWalletAddressKey ($input: CreateWalletAddressKeyInput!) {
                createWalletAddressKey(input: $input) {
                    walletAddressKey {
                        id
                        revoked
                        walletAddressId
                        createdAt
                        jwk {
                            alg
                            crv
                            kid
                            kty
                            x
                        }
                    }
                }
            }
        """,
        "variables": {
            "input": {
                "walletAddressId": wallet_id,
                "jwk": result_jwk
            }
        }
    }
    headers = client.get_signature_headers(graphql_query)
    wallet_key = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        wallet_key = response.json()
        if wallet_key.get('errors'):
            return None
        # convert content private_key_pem to base64
        wallet_key_public_base64 = base64.b64encode(public_key_pem.encode('utf-8')).decode('utf-8')
        wallet_key_private_base64 = base64.b64encode(private_key_pem.encode('utf-8')).decode('utf-8')
        wallet_key['public_key'] = wallet_key_public_base64
        wallet_key['private_key'] = wallet_key_private_base64
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return wallet_key


def withdraw_wallet(client, wallet_id: str):
    graphql_query = {
        "query": """
            mutation CreateWalletAddressWithdrawal($input: CreateWalletAddressWithdrawalInput!) {
              createWalletAddressWithdrawal(input: $input) {
                withdrawal {
                  amount
                  id
                  walletAddress {
                    id
                    address
                    asset {
                      id
                      code
                      scale
                      withdrawalThreshold
                    }
                  }
                }
              }
            }
        """,
        "variables": {
            "input": {
                "id": f"{uuid.uuid4()}",
                "walletAddressId": f"{wallet_id}",
                "idempotencyKey": f"{uuid.uuid4()}",
                "timeoutSeconds": 0
            }
        }
    }
    headers = client.get_signature_headers(graphql_query)
    response = requests.post(
        f"{settings.url_rafiki}/graphql",
        json=graphql_query,
        headers=headers,
        timeout=5
    )
    response.raise_for_status()
    withdraw = response.json()
    print('withdraw', withdraw)
    if withdraw.get('errors', None):
        return None
    return withdraw


def create_wallet_address_key_from_client(client, wallet_id: str, key: str):
    if not key.strip():
        raise ValueError('Key cannot be empty')
    decoded_key = base64.b64decode(key)
    jwk = json.loads(decoded_key.decode('utf-8'))
    if not jwk.get('kty') or jwk['kty'] != 'OKP':
        raise ValueError('Key type must be OKP')
    if not jwk.get('crv') or jwk['crv'] != 'Ed25519':
        raise ValueError('Key curve must be Ed25519')
    if not jwk.get('x'):
        raise ValueError('Key x must be present')
    if not jwk.get('kid'):
        raise ValueError('Key id must be present')
    jwk['alg'] = 'EdDSA'
    graphql_query = {
        "query": """
            mutation CreateWalletAddressKey ($input: CreateWalletAddressKeyInput!) {
                createWalletAddressKey(input: $input) {
                    walletAddressKey {
                        id
                        revoked
                        walletAddressId
                        createdAt
                        jwk {
                            alg
                            crv
                            kid
                            kty
                            x
                        }
                    }
                }
            }
        """,
        "variables": {
            "input": {
                "walletAddressId": wallet_id,
                "jwk": jwk
            }
        }
    }
    headers = client.get_signature_headers(graphql_query)
    wallet_key = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        wallet_key = response.json()
        if wallet_key.get('errors'):
            return None
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return wallet_key
