import re
import requests
from tigerbeetle import TransferFlags

from settings import settings


### VALIDATE STATUS CODES
# https://github.com/lil5/tigerbeetle_api/blob/a742ce86a037e05c874c8ceea8a1d1ed2b699364/proto/tigerbeetle.proto

def validate_id(id_str: str) -> bool:
    # UUID v4 string hyphenated pattern: 8-4-4-4-12 hex chars
    return bool(re.fullmatch(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', id_str))


def uuid_to_bigint(id_str: str) -> int:
    return int('0x' + id_str.replace('-', ''), 16)


def to_tiger_beetle_id(id_value) -> int:
    if isinstance(id_value, int):
        return id_value
    elif isinstance(id_value, str):
        if not validate_id(id_value):
            raise ValueError('wrong format of id')
        return uuid_to_bigint(id_value)
    else:
        raise TypeError('Unsupported type for id')


def from_tiger_beetle_id(str_val: str) -> str:
    # str_val = hex(bi) # Remove '0x' prefix
    # str_val = str_val.rjust(32, '0')  # Pad to 32 chars
    if len(str_val) == 32:
        return f"{str_val[0:8]}-{str_val[8:12]}-{str_val[12:16]}-{str_val[16:20]}-{str_val[20:]}"
    return str_val


def create_tiger_beetle_account_wallet(id, asset_id, ledger, code):
    tb_id = hex(to_tiger_beetle_id(id)).replace('0x', '')
    tb_asset_id = hex(to_tiger_beetle_id(asset_id)).replace('0x', '')
    payload = {
        "accounts": [
            {
                "id": tb_id,
                "debits_pending": 0,
                "debits_posted": 0,
                "credits_pending": 0,
                "credits_posted": 0,
                "ledger": ledger,
                "user_data_128": tb_asset_id,
                "user_data_64": "0",
                "user_data_32": 0,
                "code": code,
                "flags": {
                    "linked": False,
                    "debits_must_not_exceed_credits": True,
                    "credits_must_not_exceed_debits": False,
                    "history": True
                }
            }
        ]
    }
    try:
        url = f"{settings.tiger_beetle_api_url}/accounts/create"
        response = requests.post(
            url,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        response = getattr(error, 'response', None)
        if response is not None:
            print(f"Error creating account via API: {response.status_code} {response.text}")
        else:
            print(f"Error creating account via API: {error}")
        return None


def create_transfer_tiger_bettle(id_transaction, debit_account, credit_account, amount, ledger, code: int = 2,
                                 flags: dict = None, pending_id: str = '') -> bool:
    tb_transaction_id = hex(to_tiger_beetle_id(id_transaction)).replace('0x', '')
    tb_debit_id = hex(to_tiger_beetle_id(debit_account)).replace('0x', '')
    tb_credit_id = hex(to_tiger_beetle_id(credit_account)).replace('0x', '')
    tb_pending_id = hex(to_tiger_beetle_id(pending_id)).replace('0x', '') if pending_id else None
    payload = {
        "transfers": [
            {
                "id": tb_transaction_id,
                "debit_account_id": tb_debit_id,
                "credit_account_id": tb_credit_id,
                "amount": amount,
                "pending_id": tb_pending_id,
                "user_data_128": "0",
                "user_data_64": "0",
                "user_data_32": 0,
                "timeout": 0,
                "ledger": ledger,
                "code": code,
                "flags": flags,
            }
        ]
    }
    try:
        url = f"{settings.tiger_beetle_api_url}/transfers/create"
        response = requests.post(
            url,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        response = getattr(error, 'response', None)
        if response is not None:
            print(f"Error creating transfer via API: {response.status_code} {response.text}")
        else:
            print(f"Error creating transfer via API: {error}")
        return None


def get_accounts_by_id(id_list) -> list:
    tb_ids = [hex(to_tiger_beetle_id(id)).replace('0x', '') for id in id_list]
    payload = {"account_ids": tb_ids}
    url = f"{settings.tiger_beetle_api_url}/accounts/lookup"
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        response_obj = response.json()
        return response_obj.get('accounts', [])
    except requests.RequestException as error:
        response = getattr(error, 'response', None)
        if response is not None:
            print(f"Error fetching accounts via API: {response.status_code} {response.text}")
        else:
            print(f"Error fetching accounts via API: {error}")
        return None


def get_transfers() -> list:
    payload = {
        "filter": {
            # "code": 1,
            "ledger": 1,
            "limit": 50,
            "flags": {
                # "reversed": False
            }
        }
    }
    url = f"{settings.tiger_beetle_api_url}/transfers/query"
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        response_obj = response.json()
        return response_obj.get('transfers', [])
    except requests.RequestException as error:
        response = getattr(error, 'response', None)
        if response is not None:
            print(f"Error fetching transfers via API: {response.status_code} {response.text}")
        else:
            print(f"Error fetching transfers via API: {error}")
        return None
