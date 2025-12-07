from fastapi import HTTPException
from sqlalchemy.orm import Session
from tigerbeetle import TransferFlags

from helpers.signature import GraphQLClient
from helpers.tigger_bettle_api import create_transfer_tiger_bettle
from models.account import Account
from rafiki_api.transfer import cancel_outgoing_payment, deposit_outgoing_payment_liquidity
from rafiki_api.wallet import get_wallet
from schemas.webhook_schema import WebHook

client = GraphQLClient()


def handle_event_outgoing_created(event: WebHook, db: Session):
    """

    """
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
    amount = int(payment.debitAmount.value)
    if amount is None:
        print("No amount found in the received payment data.")
        return
    if amount == 0:
        print("Received amount is zero, no update needed.")
        return
    wallet_object = get_wallet(client, f'{wallet_address_id}')
    if not wallet_object:
        raise HTTPException(status_code=404, detail="Wallet not found")
    liquidity = int(wallet_object.get('liquidity', 0))
    if amount > liquidity:
        print(f"Insufficient liquidity in the wallet: {liquidity} for amount: {amount}")
        cancel_outgoing_payment(client, f'{payment.id}')
        return
    # send the pending transfer to the asset from the wallet
    ledger = int(db_account.asset_ledger)
    id_transaction = f'{payment.id}'  # Transaction ID Outgoing payment
    debit_account = f'{wallet_address_id}'
    credit_account = f'{db_account.asset_id}'
    # ledger = 1
    created = create_transfer_tiger_bettle(
        id_transaction, debit_account, credit_account, amount, ledger, 1, {'pending': True}
    )  # code=1 for TRANSFER code=2 for DEPOSIT code=3 for WITHDRAWAL
    if not created:
        raise HTTPException(status_code=500, detail="Transfer creation failed")
    deposit = deposit_outgoing_payment_liquidity(client, f'{payment.id}')
    if not deposit:
        raise HTTPException(status_code=500, detail="Deposit creation failed")
    print(f"Deposit {deposit} for payment {payment.id}")

    return
