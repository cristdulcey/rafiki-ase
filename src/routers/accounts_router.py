import uuid

from fastapi import Depends, HTTPException, APIRouter
from starlette import status

from database import get_db
from helpers.signature import GraphQLClient
from helpers.tigger_bettle_api import get_accounts_by_id, create_tiger_beetle_account_wallet
from rafiki_api.asset import get_asset_by_id
from schemas.account_schema import AccountDetailResponse, LinkKeyBase

from models.account import Account
from rafiki_api.wallet import get_wallet, create_wallet, create_wallet_address_key, withdraw_wallet, \
    create_wallet_address_key_from_client
from schemas.account_schema import AccountResponse, AccountCreate, AccountListResponse
from sqlalchemy.orm import Session

client = GraphQLClient()
router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    db_account = db.query(Account).filter(Account.path == account.path).first()
    if db_account:
        raise HTTPException(status_code=400, detail="Account name already exists")
    asset = get_asset_by_id(client, f'{account.asset_id}')
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    wallet = create_wallet(client, account.path, f'{account.asset_id}', account.name)
    if not wallet:
        raise HTTPException(status_code=500, detail="Failed to create wallet address")
    asset_code = f'{asset.get("data", {}).get("asset", {}).get("code", "USD")}'
    asset_scale = asset.get("data", {}).get("asset", {}).get("scale", 2)
    account_asset = get_accounts_by_id([f'{account.asset_id}'])
    if len(account_asset) == 0:
        raise HTTPException(status_code=400, detail="Tiger Beetle account ledger not exists")
    ledger = int(account_asset[0].get('ledger', 0))
    wallet_id = wallet.get('data', {}).get('createWalletAddress', {}).get('walletAddress', {}).get('id', '')
    wallet_address = wallet.get('data', {}).get('createWalletAddress', {}).get('walletAddress', {}).get('address', '')
    wallet_key = create_wallet_address_key(client, wallet_id)
    if not wallet_key:
        raise HTTPException(status_code=500, detail="Failed to create wallet address key")
    account_data = Account(
        name=account.name,
        path=account.path,
        asset_code=asset_code,
        asset_scale=asset_scale,
        asset_id=f'{account.asset_id}',
        asset_ledger=ledger,
        wallet_address_id=wallet_id,
        wallet_address=wallet_address,
        public_key=wallet_key.get('public_key', ''),
        private_key=wallet_key.get('private_key', ''),
    )
    db.add(account_data)
    db.commit()
    db.refresh(account_data)
    account_data.liquidity = 0
    account_data.status = "ACTIVE"  # Default status, can be updated later
    if not account_data:
        raise HTTPException(status_code=500, detail="Failed to create account")
    code = 1  # LIQUIDITY_WEB_MONETIZATION
    account_tigerbeetle_created = create_tiger_beetle_account_wallet(wallet_id, f'{account.asset_id}', ledger, code)
    if account_tigerbeetle_created.get('results', None):
        raise HTTPException(status_code=500, detail="Failed to create Tiger Beetle account")
    return account_data


@router.get("", response_model=AccountListResponse)
async def get_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()
    if not accounts:
        raise HTTPException(status_code=404, detail="No accounts found")
    return AccountListResponse(
        accounts=accounts,
        count=len(accounts)
    )


@router.get("/{wallet_id}", response_model=AccountDetailResponse)
async def get_account(wallet_id: uuid.UUID, db: Session = Depends(get_db)):
    db_account = db.query(Account).filter(Account.wallet_address_id == f'{wallet_id}').first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    wallet_object = get_wallet(client, f'{wallet_id}')
    if not wallet_object:
        raise HTTPException(status_code=404, detail="Wallet not found")
    db_account.liquidity = wallet_object.get('liquidity', 0)
    db_account.status = wallet_object.get('status')
    return db_account

@router.get("/{wallet_address}", response_model=AccountDetailResponse)
async def get_account(wallet_address: str, db: Session = Depends(get_db)):
    db_account = db.query(Account).filter(Account.path == f'{wallet_address}').first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    wallet_object = get_wallet(client, f'{db_account.wallet_address_id}')
    if not wallet_object:
        raise HTTPException(status_code=404, detail="Wallet not found")
    db_account.liquidity = wallet_object.get('liquidity', 0)
    db_account.status = wallet_object.get('status')
    return db_account


@router.post("/key", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def link_key_to_wallet(withdraw: LinkKeyBase, db: Session = Depends(get_db)):
    db_account = db.query(Account).filter(Account.wallet_address_id == f'{withdraw.wallet_address_id}').first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    created = create_wallet_address_key_from_client(client, f'{db_account.wallet_address_id}', withdraw.key)
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create key")
    return db_account
