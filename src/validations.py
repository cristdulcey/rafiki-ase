# # Select your transport with a defined url endpoint
# from gql import Client
# from gql.transport.aiohttp import AIOHTTPTransport
#
# from helpers.create_wallet import get_wallet
#
# transport = AIOHTTPTransport(url="http://localhost:3001/graphql")
#
# # Create a GraphQL client using the defined transport
# client = Client(transport=transport, fetch_schema_from_transport=True)
#
# result = get_wallet(client, "4e33de7b-4e27-4079-8556-3331cf6a8134")
# print(result)
from datetime import datetime

from helpers.tigger_bettle import get_accounts_by_id, to_tiger_beetle_id, get_transactions_by_account, \
    get_balances_by_account, get_transfers_by_id, from_tiger_beetle_id, create_tiger_beetle_account_wallet, \
    create_transfer_tiger_bettle, get_transfers

tb_peer_id = to_tiger_beetle_id('b7dd6753-c17f-4022-8d6d-26c391e13f10')  # Replace with the actual Tiger Beetle ID`)
tb_asset_id = to_tiger_beetle_id('d5a43edb-3b47-495c-b7fc-9278a8bf7817')  # Replace with the actual Tiger Beetle ID`)
tb_wallet_id = to_tiger_beetle_id('092c2003-2b40-4856-8119-1850f255142e')  # Replace with the actual Tiger Beetle ID`)
tb_wallet2_id = to_tiger_beetle_id('37ac23f6-abb1-4a0d-be63-fe26be1419e6')  # Replace with the actual Tiger Beetle ID`)
tb_incoming_id = to_tiger_beetle_id('9683034c-2d32-4ef1-98ac-bf8bb4f74d98')  # Replace with the actual Tiger Beetle ID`)
tb_outgoing_id = to_tiger_beetle_id('2d4d805c-5302-47f8-b971-17b27cf35099')  # Replace with the actual Tiger Beetle ID`)

############# CREATE ACCOUNT

# uuid = tb_wallet2_id # Wallet ID
# uuid_asset = tb_asset_id # Asset ID
# ledger = 1 # Asset Ledger usd = 1
# code = 1 # LIQUIDITY_WEB_MONETIZATION
# created = create_tiger_beetle_account_wallet(uuid, uuid_asset, ledger, code)
# if created:
#     print("Tiger Beetle account created successfully.")


############# CREATE DEPOSIT

# id_transaction = '00000000-0000-0000-0000-000000000005' # Transaction ID Incoming payment or Outgoing payment or Deposit
# debit_account = '678673a7-8319-40cb-93a5-f38fc85f4dbb'  # Asset ID
# credit_account = '0c8e5e4d-42cb-4db1-865f-1041964b0010' # Wallet ID
# amount = 500  # Amount in smallest unit (e.g., cents for USD)
# ledger = 1  # Asset Ledger usd = 1
# created = create_transfer(id_transaction, debit_account, credit_account, amount, ledger,1) # code=1 for TRANSFER code=2 for DEPOSIT code=3 for WITHDRAWAL
# if created:
#     print("Deposit created successfully.")

############ GET ACCOUNTS BY ID

print('GET ACCOUNTS BY ID')
accounts = get_accounts_by_id(
    [
        1,
        tb_peer_id,
        tb_asset_id,
        tb_wallet_id,
        # tb_wallet2_id,
        tb_incoming_id,
        tb_outgoing_id
    ]
)
for account in accounts:
    dict_account = account.__dict__
    if dict_account.get('user_data_128') != 0:
        dict_account['user_data_128_uuid'] = from_tiger_beetle_id(dict_account['user_data_128'])
    if dict_account.get('id') != 0:
        dict_account['id_uuid'] = from_tiger_beetle_id(dict_account['id'])
    if dict_account.get('timestamp') != 0:
        dict_account['timestamp_date'] = f'{datetime.fromtimestamp(dict_account.get("timestamp") / 1_000_000_000)}'
    print(f"\n{account.__dict__}\n")

############# LIST TRANSACTIONS BY ACCOUNT

# print('LIST TRANSACTIONS BY ACCOUNT')
# tb_credit_id = to_tiger_beetle_id(tb_peer_id)
# transactions = get_transactions_by_account(tb_credit_id)
# for transaction in transactions:
#     dict_transaction = transaction.__dict__
#     if dict_transaction.get('id') != 0:
#         dict_transaction['id_uuid'] = from_tiger_beetle_id(dict_transaction['id'])
#     if dict_transaction.get('user_data_128') != 0:
#         dict_transaction['user_data_128_uuid'] = from_tiger_beetle_id(dict_transaction['user_data_128'])
#     if dict_transaction.get('debit_account_id') != 0:
#         dict_transaction['debit_account_uuid'] = from_tiger_beetle_id(dict_transaction['debit_account_id'])
#     if dict_transaction.get('credit_account_id') != 0:
#         dict_transaction['credit_account_uuid'] = from_tiger_beetle_id(dict_transaction['credit_account_id'])
#     if dict_transaction.get('timestamp') != 0:
#         dict_transaction[
#             'timestamp_date'] = f'{datetime.fromtimestamp(dict_transaction.get("timestamp") / 1_000_000_000)}'
#     print(f"\n{dict_transaction}\n")
#

############## LIST TRaNSFERS

print('LIST TRANSFERS')
transfers = get_transfers()
for transfer in transfers:
    dict_transaction = transfer.__dict__
    if dict_transaction.get('id') != 0:
        dict_transaction['id_uuid'] = from_tiger_beetle_id(dict_transaction['id'])
    if dict_transaction.get('user_data_128') != 0:
        dict_transaction['user_data_128_uuid'] = from_tiger_beetle_id(dict_transaction['user_data_128'])
    if dict_transaction.get('debit_account_id') != 0:
        dict_transaction['debit_account_uuid'] = from_tiger_beetle_id(dict_transaction['debit_account_id'])
    if dict_transaction.get('credit_account_id') != 0:
        dict_transaction['credit_account_uuid'] = from_tiger_beetle_id(dict_transaction['credit_account_id'])
    if dict_transaction.get('timestamp') != 0:
        dict_transaction[
            'timestamp_date'] = f'{datetime.fromtimestamp(dict_transaction.get("timestamp") / 1_000_000_000)}'
    print(f"\n{dict_transaction}\n")



############ BALANCES BY ACCOUNT

# print('BALANCES BY ACCOUNT')
# tb_credit_id = to_tiger_beetle_id('0c8e5e4d-42cb-4db1-865f-1041964b0010')
# balances = get_balances_by_account(tb_credit_id)
# for balance in balances:
#     dict_balance = balance.__dict__
#     if dict_balance.get('timestamp') != 0:
#         dict_balance['timestamp_date'] = f'{datetime.fromtimestamp(dict_balance.get("timestamp") / 1_000_000_000)}'
#     print(f"\n{dict_balance}\n")

########### GET TRANSFER BY ID
#
# print('GET TRANSFER BY ID')
# tb_credit_id = to_tiger_beetle_id('1f211994-7a9f-49da-a4c8-843b1aa18984')
# transactions = get_transfers_by_id([tb_credit_id])
# for transaction in transactions:
#     dict_transaction = transaction.__dict__
#     if dict_transaction.get('id') != 0:
#         dict_transaction['id_uuid'] = from_tiger_beetle_id(dict_transaction['id'])
#     if dict_transaction.get('user_data_128') != 0:
#         dict_transaction['user_data_128_uuid'] = from_tiger_beetle_id(dict_transaction['user_data_128'])
#     if dict_transaction.get('debit_account_id') != 0:
#         dict_transaction['debit_account_uuid'] = from_tiger_beetle_id(dict_transaction['debit_account_id'])
#     if dict_transaction.get('credit_account_id') != 0:
#         dict_transaction['credit_account_uuid'] = from_tiger_beetle_id(dict_transaction['credit_account_id'])
#     if dict_transaction.get('timestamp') != 0:
#         dict_transaction['timestamp_date'] = f'{datetime.fromtimestamp(dict_transaction.get("timestamp") / 1_000_000_000)}'
#     print(f"\n{dict_transaction}\n")


# print(from_tiger_beetle_id(307136249398997544367078564061939085952))
