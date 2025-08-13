import uuid

import requests

from settings import settings


def create_incoming_payment(client, wallet_url: str, amount: int, scale: int, asset_code: str, description: str):
    graphql_query = {
        "query": """
            mutation CreateReceiver($input: CreateReceiverInput!) {
              createReceiver(input: $input) {
                receiver {
                  completed
                  createdAt
                  expiresAt
                  metadata
                  id
                  incomingAmount {
                    assetCode
                    assetScale
                    value
                  }
                  walletAddressUrl
                  receivedAmount {
                    assetCode
                    assetScale
                    value
                  }
                }
              }
            }
        """,
        "variables": {
            "input": {
                "metadata": {
                    "description": description
                },
                "incomingAmount": {
                    "assetCode": asset_code,
                    "assetScale": scale,
                    "value": amount
                },
                "walletAddressUrl": wallet_url
            }
        }
    }
    headers = client.get_signature_headers(graphql_query)
    incoming_payment = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        incoming_payment = response.json()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return incoming_payment


def create_quote(client, wallet_address_id: str, receiver_id: str):
    graphql_query = {
        "query": """
                mutation CreateQuote($input: CreateQuoteInput!) {
                  createQuote(input: $input) {
                    quote {
                      createdAt
                      expiresAt
                      id
                      walletAddressId
                      receiveAmount {
                        assetCode
                        assetScale
                        value
                      }
                      receiver
                      debitAmount {
                        assetCode
                        assetScale
                        value
                      }
                    }
                  }
                }
            """,
        "variables": {
            "input": {
                "walletAddressId": wallet_address_id,
                "receiver": receiver_id
            }
        }
    }
    headers = client.get_signature_headers(graphql_query)
    quote_payment = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        quote_payment = response.json()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return quote_payment


def create_outgoing_payment(client, wallet_address_id: str, quote_id: str):
    graphql_query = {
        "query": """
            mutation CreateOutgoingPayment($input: CreateOutgoingPaymentInput!) {
              createOutgoingPayment(input: $input) {
                payment {
                  createdAt
                  error
                  metadata
                  id
                  walletAddressId
                  receiveAmount {
                    assetCode
                    assetScale
                    value
                  }
                  receiver
                  debitAmount {
                    assetCode
                    assetScale
                    value
                  }
                  sentAmount {
                    assetCode
                    assetScale
                    value
                  }
                  state
                  stateAttempts
                }
              }
            }
        """,
        "variables": {
            "input": {
                "walletAddressId": wallet_address_id,
                "quoteId": quote_id
            }
        }
    }
    headers = client.get_signature_headers(graphql_query)
    outgoing_payment = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        outgoing_payment = response.json()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return outgoing_payment


def create_incoming_payment_withdrawal(client, incoming_payment_id: str):
    graphql_query = {
        "query": """
            mutation CreateIncomingPaymentWithdrawal($input: CreateIncomingPaymentWithdrawalInput!) {  
                createIncomingPaymentWithdrawal(input: $input) {    
                    success
                }
            }
        """,
        "variables": {
            "input": {
                "incomingPaymentId": incoming_payment_id,
                "idempotencyKey": f'{uuid.uuid4()}',
                "timeoutSeconds": 0
            }
        }
    }
    headers = client.get_signature_headers(graphql_query)
    withdrawal = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        withdrawal = response.json()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return withdrawal


def deposit_outgoing_payment_liquidity(client, outgoing_payment_id: str):
    graphql_query = {
        "query": """
            mutation DepositOutgoingPaymentLiquidity($input: DepositOutgoingPaymentLiquidityInput!) {
              depositOutgoingPaymentLiquidity(input: $input) {
                success
              }
            }
        """,
        "variables": {
            "input": {
                "outgoingPaymentId": outgoing_payment_id,
                "idempotencyKey": f'{uuid.uuid4()}'
            }
        }
    }
    headers = client.get_signature_headers(graphql_query)
    deposit_outgoing = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        deposit_outgoing = response.json()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return deposit_outgoing


def create_outgoing_payment_withdrawal(client, outgoing_payment_id: str):
    graphql_query = {
        "query": """
            mutation CreateOutgoingPaymentWithdrawal($input: CreateOutgoingPaymentWithdrawalInput!) {  
                createOutgoingPaymentWithdrawal(input: $input) {
                    success
                }
            }
        """,
        "variables": {
            "input": {
                "outgoingPaymentId": outgoing_payment_id,
                "idempotencyKey": f'{uuid.uuid4()}',
                "timeoutSeconds": 0
            }
        }
    }
    headers = client.get_signature_headers(graphql_query)
    withdrawal_outgoing = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        withdrawal_outgoing = response.json()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return withdrawal_outgoing


def post_liquidity_withdrawal(client, outgoing_payment_id: str):
    graphql_query = {
        "query": """
            mutation PostLiquidityWithdrawal($input: PostLiquidityWithdrawalInput!) {
              postLiquidityWithdrawal(input: $input) {
                success
              }
            }
        """,
        "variables": {
            "input": {
                "withdrawalId": outgoing_payment_id,
                "idempotencyKey": f'{uuid.uuid4()}',
            }
        }
    }
    headers = client.get_signature_headers(graphql_query)
    post_liquidity = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        post_liquidity = response.json()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return post_liquidity


def create_wallet_address_withdrawal(client, id_withdraw: str, wallet_address_id: str):
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
            {
                "input": {
                    "id": id_withdraw,
                    "walletAddressId": wallet_address_id,
                    "idempotencyKey": f'{uuid.uuid4()}',
                }
            }
        }
    }
    headers = client.get_signature_headers(graphql_query)
    withdraw = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        withdraw = response.json()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return withdraw


def cancel_outgoing_payment(client, outgoing_payment_id: str, reason: str = 'Not enough balance'):
    graphql_query = {
        "query": """
            mutation CancelOutgoingPayment($input: CancelOutgoingPaymentInput!) {
              cancelOutgoingPayment(input: $input) {
                payment {
                  createdAt
                  error
                  metadata
                  id
                  walletAddressId
                  quote {
                    createdAt
                    expiresAt
                    id
                    estimatedExchangeRate
                    walletAddressId
                    receiveAmount {
                      assetCode
                      assetScale
                      value
                    }
                    receiver
                    debitAmount {
                      assetCode
                      assetScale
                      value
                    }
                  }
                  receiveAmount {
                    assetCode
                    assetScale
                    value
                  }
                  receiver
                  debitAmount {
                    assetCode
                    assetScale
                    value
                  }
                  sentAmount {
                    assetCode
                    assetScale
                    value
                  }
                  state
                  stateAttempts
                }
              }
            }
        """,
        "variables": {
            "input": {
                "id": f"{outgoing_payment_id}",
                "reason": reason
            }
        }
    }
    headers = client.get_signature_headers(graphql_query)
    cancel_outgoing = None
    try:
        response = requests.post(
            f"{settings.url_rafiki}/graphql",
            json=graphql_query,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        cancel_outgoing = response.json()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return cancel_outgoing


def create_transfer(client, wallet_receive_url: str, amount: int, wallet_sender_id: str, description: str):
    wallet = None
    try:
        # Fetch the wallet details to get the asset code
        response = requests.get(wallet_receive_url)
        response.raise_for_status()
        wallet = response.json()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    asset_code = wallet.get('assetCode', None)
    asset_scale = wallet.get('assetScale', None)
    if not asset_code or not asset_scale:
        raise ValueError("Asset code or scale not found in wallet details")
    amount_in_asset = int(amount * (10 ** asset_scale))
    incoming_payment = create_incoming_payment(
        client, wallet_receive_url, amount_in_asset, asset_scale, asset_code, description
    )
    if not incoming_payment:
        raise ValueError("Failed to create incoming payment")
    receiver_id = incoming_payment.get('data', {}).get('createReceiver', {}).get('receiver', {}).get('id', None)
    if not receiver_id:
        raise ValueError("Receiver ID not found in incoming payment response")
    quote = create_quote(client, wallet_sender_id, receiver_id)
    if not quote:
        raise ValueError("Failed to create quote")
    quote_id = quote.get('data', {}).get('createQuote', {}).get('quote', {}).get('id', None)
    if not quote_id:
        raise ValueError("Quote ID not found in quote response")
    outgoing_payment = create_outgoing_payment(client, wallet_sender_id, quote_id)
    if not outgoing_payment:
        raise ValueError("Failed to create outgoing payment")
    payment_id = outgoing_payment.get('data', {}).get('createOutgoingPayment', {}).get('payment', {}).get('id', None)
    if not payment_id:
        raise ValueError("Payment ID not found in outgoing payment response")
    return payment_id
