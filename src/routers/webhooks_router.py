import json

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from models.webhook import TypeEnumWebhook
from rafiki_api.events.incoming_complete import handle_event_incoming_complete
from rafiki_api.events.outgoing_complete import handle_event_outgoing_complete
from rafiki_api.events.outgoing_created import handle_event_outgoing_created
from rafiki_api.events.wallet_address_not_found import handle_event_wallet_address_not_found
from rafiki_api.events.web_monetization import handle_event_web_monetization
from schemas.webhook_schema import WebHook

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("", status_code=status.HTTP_200_OK)
async def webhooks(webhook: WebHook, db: Session = Depends(get_db)):
    # print(json.dumps(webhook.dict(), indent=4, sort_keys=True))
    if webhook.type == TypeEnumWebhook.INCOMING_CREATED:
        print("Received incoming created webhook")
    elif webhook.type == TypeEnumWebhook.INCOMING_COMPLETED:
        print("Received incoming completed webhook")
        handle_event_incoming_complete(webhook, db)
    elif webhook.type == TypeEnumWebhook.INCOMING_EXPIRED:
        print("Received incoming expired webhook")
        handle_event_incoming_complete(webhook, db)
    elif webhook.type == TypeEnumWebhook.OUTGOING_CREATED:
        print("Received outgoing created webhook")
        handle_event_outgoing_created(webhook, db)
    elif webhook.type == TypeEnumWebhook.OUTGOING_COMPLETED:
        print("Received outgoing completed webhook")
        handle_event_outgoing_complete(webhook, db)
    elif webhook.type == TypeEnumWebhook.OUTGOING_FAILED:
        print("Received outgoing failed webhook")
        handle_event_outgoing_complete(webhook, db)
    elif webhook.type == TypeEnumWebhook.WALLET_NOT_FOUND:
        handle_event_wallet_address_not_found(webhook, db)
    elif webhook.type == TypeEnumWebhook.ASSET_LIQUIDITY_LOW:
        print("Received asset liquidity low webhook")
    elif webhook.type == TypeEnumWebhook.PEER_LIQUIDITY_LOW:
        print("Received peer liquidity low webhook")
    elif webhook.type == TypeEnumWebhook.WALLET_ADDRESS_WEB_MONETIZATION:
        print("Received wallet address web monetization webhook")
        handle_event_web_monetization(webhook, db)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid webhook event {webhook.type}")
    return None
