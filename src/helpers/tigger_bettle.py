import re
import tigerbeetle as tb
from tigerbeetle import AccountFlags, TransferFlags

from settings import settings


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


def from_tiger_beetle_id(bi: int) -> str:
    str_val = hex(bi)[2:]  # Remove '0x' prefix
    str_val = str_val.rjust(32, '0')  # Pad to 32 chars
    if len(str_val) == 32:
        return f"{str_val[0:8]}-{str_val[8:12]}-{str_val[12:16]}-{str_val[16:20]}-{str_val[20:]}"
    return str_val


def create_tiger_beetle_account_wallet(id, asset_id, ledger, code) -> bool:
    tb_id = to_tiger_beetle_id(id)
    asset_id = to_tiger_beetle_id(asset_id)
    flags = AccountFlags(
        AccountFlags.DEBITS_MUST_NOT_EXCEED_CREDITS | AccountFlags.HISTORY
    )
    with tb.ClientAsync(cluster_id=0, replica_addresses=settings.tiger_beetle_address) as client:
        account = tb.Account(
            id=tb_id,
            debits_pending=0,
            debits_posted=0,
            credits_pending=0,
            credits_posted=0,
            user_data_128=asset_id,
            user_data_64=0,
            user_data_32=0,
            ledger=ledger,
            code=code,
            flags=flags,
            timestamp=0,
        )
        try:
            account_errors = client.create_accounts([account])
            if account_errors:
                print(f"Error creating account: {account_errors}")
                return False
        except Exception as error:
            print(f"Error creating account: {error}")
            return False
        return True


def create_transfer_tiger_bettle(id_transaction, debit_account, credit_account, amount, ledger, code: int = 2,
                                 flag: TransferFlags = TransferFlags.NONE, pending_id: str = '') -> bool:
    with tb.ClientAsync(cluster_id=0, replica_addresses=settings.tiger_beetle_address) as client:
        tb_transaction_id = to_tiger_beetle_id(id_transaction)
        tb_debit_id = to_tiger_beetle_id(debit_account)
        tb_credit_id = to_tiger_beetle_id(credit_account)
        if pending_id != '':
            pending_id = to_tiger_beetle_id(pending_id)
        else:
            pending_id = 0
        transfers = [tb.Transfer(
            id=tb_transaction_id,  # TigerBeetle time-based ID.
            debit_account_id=tb_debit_id,
            credit_account_id=tb_credit_id,
            amount=amount,
            pending_id=pending_id,
            user_data_128=0,
            user_data_64=0,
            user_data_32=0,
            timeout=0,
            ledger=ledger,
            code=code,
            flags=flag,
            timestamp=0,
        )]

        try:
            transfer_errors = client.create_transfers(transfers)
            if transfer_errors:
                print(f"Error creating transfer: {transfer_errors}")
                return False
            return True
        except Exception as error:
            print(f"Exception creating transfer: {error}")
        return False


def get_accounts_by_id(id_list) -> list:
    tb_ids = [to_tiger_beetle_id(id) for id in id_list]
    print('TB IDS:', tb_ids,settings.tiger_beetle_address)
    with tb.ClientAsync(cluster_id=0, replica_addresses=settings.tiger_beetle_address) as client:
        accounts = client.lookup_accounts(tb_ids)
        print('Accounts:', accounts)
        return accounts


def get_transactions_by_account(id_account) -> list:
    with tb.ClientAsync(cluster_id=0, replica_addresses=settings.tiger_beetle_address) as client:
        filter = tb.AccountFilter(
            account_id=id_account,
            user_data_128=0,  # No filter by UserData.
            user_data_64=0,
            user_data_32=0,
            code=0,  # No filter by Code.
            timestamp_min=0,  # No filter by Timestamp.
            timestamp_max=0,  # No filter by Timestamp.
            limit=10,  # Limit to ten balances at most.
            flags=tb.AccountFilterFlags.DEBITS |  # Include transfer from the debit side.
                  tb.AccountFilterFlags.CREDITS |  # Include transfer from the credit side.
                  tb.AccountFilterFlags.REVERSED |  # Sort by timestamp in reverse-chronological order.
                  tb.AccountFilterFlags.NONE  # Sort by timestamp in reverse-chronological order.
        )
        account_transfers = client.get_account_transfers(filter)
        return account_transfers


def get_balances_by_account(id_account) -> list:
    with tb.ClientAsync(cluster_id=0, replica_addresses=settings.tiger_beetle_address) as client:
        filter = tb.AccountFilter(
            account_id=id_account,
            user_data_128=0,  # No filter by UserData.
            user_data_64=0,
            user_data_32=0,
            code=0,  # No filter by Code.
            timestamp_min=0,  # No filter by Timestamp.
            timestamp_max=0,  # No filter by Timestamp.
            limit=10,  # Limit to ten balances at most.
            flags=tb.AccountFilterFlags.DEBITS |  # Include balances.
                  tb.AccountFilterFlags.NONE |  # Sort by timestamp in reverse-chronological order.
                  tb.AccountFilterFlags.CREDITS |  # Sort by timestamp in reverse-chronological order.
                  tb.AccountFilterFlags.REVERSED  # Sort by timestamp in reverse-chronological order.
        )
        account_balances = client.get_account_balances(filter)
        return account_balances


def get_transfers_by_id(id_list) -> list:
    tb_ids = [to_tiger_beetle_id(id) for id in id_list]
    with tb.ClientAsync(cluster_id=0, replica_addresses=settings.tiger_beetle_address) as client:
        transfers = client.lookup_transfers(tb_ids)
        return transfers


def get_transfers() -> list:
    with tb.ClientAsync(cluster_id=0, replica_addresses=settings.tiger_beetle_address) as client:
        query_filter = tb.QueryFilter(
            user_data_128=0,  # No Filter by user_data_128.
            user_data_64=0,  # No Filter by user_data_64.
            user_data_32=0,  # No Filter by user_data_32.
            code=0,  # No Filter by Code.
            ledger=0,  # No filter by Ledger.
            timestamp_min=0,  # No filter by Timestamp.
            timestamp_max=0,  # No filter by Timestamp.
            limit=20,  # Limit to ten balances at most.
            flags=tb.QueryFilterFlags.REVERSED,  # Sort by timestamp in reverse-chronological order.
        )

        query_transfers = client.query_transfers(query_filter)
        return query_transfers
