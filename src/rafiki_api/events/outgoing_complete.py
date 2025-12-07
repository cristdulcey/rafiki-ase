import time

from fastapi import HTTPException
from sqlalchemy.orm import Session

from helpers.create_key import generate_uuid
from helpers.signature import GraphQLClient
from helpers.tigger_bettle_api import create_transfer_tiger_bettle
from models.account import Account
from rafiki_api.transfer import create_outgoing_payment_withdrawal, post_liquidity_withdrawal
from rafiki_api.wallet import get_wallet
from schemas.webhook_schema import WebHook

client = GraphQLClient()


def handle_event_outgoing_complete(event: WebHook, db: Session):
    """

    """
    time.sleep(1)  # Sleep to ensure the event is processed after the payment is created
    payment = event.data
    if not payment:
        print("No payment data found in the event.")
        return
    wallet_address_id = payment.walletAddressId
    if not wallet_address_id:
        print("No wallet address found in the payment data.")
        return
    db_account = db.query(Account).filter(Account.wallet_address_id == f'{wallet_address_id}').first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    wallet_object = get_wallet(client, f'{wallet_address_id}')
    if not wallet_object:
        raise HTTPException(status_code=404, detail="Wallet not found")
    debit = int(payment.debitAmount.value)
    send = int(payment.sentAmount.value)
    balance = int(payment.balance or 0)
    to_void = debit - send
    ledger = int(db_account.asset_ledger)

    print('Debit:', debit, 'Send:', send, 'To Void:', to_void)
    if to_void > 0:
        if balance == to_void:
            send_fee_to_asset = create_transfer_tiger_bettle(
                generate_uuid(), debit, f'{db_account.asset_id}', send, ledger, 3
            )  # code=1 for TRANSFER code=2 for DEPOSIT code=3 for WITHDRAWAL

    outgoing_withdraw = create_outgoing_payment_withdrawal(client, payment.id)
    if not outgoing_withdraw:
        print("No outgoing withdrawal data found in the event.")
    print(outgoing_withdraw)
    post_liquidity = post_liquidity_withdrawal(client, payment.id)
    if not post_liquidity:
        print("No post liquidity data found in the event.")
    print(post_liquidity)
    # send the transfer to the ledger from the asset
    id_transaction_ledger = generate_uuid()
    debit_account_ledger = f'{db_account.asset_id}'  # Asset ID
    credit_account_ledger = ledger
    # ledger = 1
    created_ledger = create_transfer_tiger_bettle(
        id_transaction_ledger, debit_account_ledger, credit_account_ledger, send, ledger, 3
    )  # code=1 for TRANSFER code=2 for DEPOSIT code=3 for WITHDRAWAL
    if not created_ledger:
        raise HTTPException(status_code=500, detail="Transfer creation ledger failed")
    return
