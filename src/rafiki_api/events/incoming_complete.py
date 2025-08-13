import time
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from helpers.create_key import generate_uuid
from helpers.signature import GraphQLClient
from helpers.tigger_bettle import create_transfer_tiger_bettle, get_accounts_by_id
from models.account import Account
from rafiki_api.transfer import create_incoming_payment_withdrawal
from schemas.webhook_schema import WebHook

client = GraphQLClient()


def handle_event_incoming_complete(event: WebHook, db: Session):
    """
    Handle the 'event_incoming_complete' event.

    This function processes the incoming event and performs necessary actions
    based on the event type and data provided.

    Args:
        event (dict): The incoming event data.
        db (Session): The database session to interact with the database.
    """
    # Example processing logic
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
    # Update the account's liquidity based on the incoming payment
    amount = int(payment.receivedAmount.value)
    if amount is None:
        print("No amount found in the received payment data.")
        return
    if amount == 0:
        print("Received amount is zero, no update needed.")
        return
    withdrawal = create_incoming_payment_withdrawal(client, payment.id)
    if not withdrawal:
        print("No withdrawal data found in the received payment data.")
    # send the transfer to the asset from the ledger
    ledger = int(db_account.asset_ledger)
    id_transaction = generate_uuid()
    debit_account = ledger
    credit_account = f'{db_account.asset_id}'  # Asset ID
    # ledger = 1
    created = create_transfer_tiger_bettle(
        id_transaction, debit_account, credit_account, amount, ledger, 3
    )  # code=1 for TRANSFER code=2 for DEPOSIT code=3 for WITHDRAWAL
    if not created:
        raise HTTPException(status_code=500, detail="Transfer creation failed send the transfer to the asset from the wallet address")
    # send the transfer to the ledger from the asset
    id_transaction_ledger = generate_uuid()  # Transaction ID Incoming payment or Outgoing payment or Deposit
    debit_account_ledger = f'{db_account.asset_id}'  # Asset Address ID
    credit_account_ledger = f'{db_account.wallet_address_id}' # Wallet ID
    # ledger = 1
    created_ledger = create_transfer_tiger_bettle(
        id_transaction_ledger, debit_account_ledger, credit_account_ledger, amount, ledger, 1
    )  # code=1 for TRANSFER code=2 for DEPOSIT code=3 for WITHDRAWAL
    if not created_ledger:
        raise HTTPException(status_code=500, detail="Transfer creation ledger failed")
    return
