from fastapi import HTTPException
from sqlalchemy.orm import Session

from helpers.create_key import generate_uuid
from helpers.signature import GraphQLClient
from models.account import Account
from rafiki_api.transfer import cancel_outgoing_payment, deposit_outgoing_payment_liquidity, \
    create_wallet_address_withdrawal, post_liquidity_withdrawal
from rafiki_api.wallet import get_wallet
from schemas.webhook_schema import WebHook

client = GraphQLClient()


def handle_event_web_monetization(event: WebHook, db: Session):
    """

    """
    payment = event.data
    if not payment:
        print("No payment data found in the event.")
        return
    wallet_address = payment.walletAddress
    if not wallet_address:
        print("No wallet address found in the payment data.")
        return
    db_account = db.query(Account).filter(Account.wallet_address_id == f'{wallet_address.id}').first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    withdrawal_id = generate_uuid()
    wallet_address_withdrawal = create_wallet_address_withdrawal(client, withdrawal_id, wallet_address.id)
    if not wallet_address_withdrawal:
        print("Failed to create wallet address withdrawal.")
    amount = int(wallet_address.receivedAmount.value)
    if amount <= 0:
        print("Received amount is zero or negative, no transfer will be created.")
    post_liquidity = post_liquidity_withdrawal(client, withdrawal_id)
    if not post_liquidity:
        print("No post liquidity data found in the event.")
    return post_liquidity
