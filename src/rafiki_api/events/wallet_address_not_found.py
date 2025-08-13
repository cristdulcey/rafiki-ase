from fastapi import HTTPException
from sqlalchemy.orm import Session

from helpers.signature import GraphQLClient
from models.account import Account
from schemas.webhook_schema import WebHook

client = GraphQLClient()


def handle_event_wallet_address_not_found(event: WebHook, db: Session):
    """

    """
    payment = event.data
    if not payment:
        print("No payment data found in the event.")
        return
    wallet_address_url = payment.walletAddressUrl
    if not wallet_address_url:
        print("No wallet address url found")
        return
    db_account = db.query(Account).filter(Account.wallet_address == f'{wallet_address_url}').first()
    if not db_account:
        print('Account not found')
        # raise HTTPException(status_code=404, detail="Account not found")
    return
