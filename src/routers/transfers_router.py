
from fastapi import Depends, HTTPException, APIRouter
from starlette import status

from database import get_db
from helpers.create_key import generate_uuid
from helpers.signature import GraphQLClient
from helpers.tigger_bettle import create_transfer_tiger_bettle
from models.account import Account
from rafiki_api.transfer import create_transfer

from sqlalchemy.orm import Session

from rafiki_api.wallet import withdraw_wallet
from schemas.account_schema import DepositBase, AccountResponse, WithdrawBase
from schemas.transfer_schema import TransferBase, TransferResponse

client = GraphQLClient()
router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TransferResponse)
async def transfer(transfer: TransferBase, db: Session = Depends(get_db)):
    aux = transfer.dict()
    aux['wallet_sender_id'] = f'{aux.get("wallet_sender_id")}'
    transfer_response = create_transfer(client, **aux)
    if not transfer_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transfer creation failed"
        )
    return {'id': transfer_response}


@router.post("/top-up", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def top_up_account(deposit: DepositBase, db: Session = Depends(get_db)):
    db_account = db.query(Account).filter(Account.wallet_address_id == f'{deposit.wallet_address_id}').first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    id_transaction = generate_uuid()  # Transaction ID Incoming payment or Outgoing payment or Deposit
    debit_account = f'{db_account.asset_id}'  # Asset ID
    credit_account = f'{deposit.wallet_address_id}'  # Wallet ID
    amount = int(deposit.credit * (10 ** db_account.asset_scale))
    ledger = int(db_account.asset_ledger)
    print('top-up',id_transaction, debit_account, credit_account, amount, ledger, 1)
    created = create_transfer_tiger_bettle(
        id_transaction, debit_account, credit_account, amount, ledger, 1
    )  # code=1 for TRANSFER code=2 for DEPOSIT code=3 for WITHDRAWAL
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create deposit transfer")
    return db_account

@router.post("/deposit", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def deposit_account(deposit: DepositBase, db: Session = Depends(get_db)):
    db_account = db.query(Account).filter(Account.wallet_address_id == f'{deposit.wallet_address_id}').first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    id_transaction = generate_uuid()  # Transaction ID Incoming payment or Outgoing payment or Deposit
    debit_account = f'{db_account.asset_id}'  # Asset ID
    credit_account = f'{deposit.wallet_address_id}'  # Wallet ID
    amount = int(deposit.credit * (10 ** db_account.asset_scale))
    ledger = int(db_account.asset_ledger)
    print('send_to_asset',id_transaction, debit_account, credit_account, amount, ledger, 2)
    send_to_asset = create_transfer_tiger_bettle(
        id_transaction, ledger, f'{db_account.asset_id}', amount, ledger, 2
    )  # code=1 for TRANSFER code=2 for DEPOSIT code=3 for WITHDRAWAL
    if not send_to_asset:
        raise HTTPException(status_code=500, detail="Failed to create deposit to asset")
    id_transaction = generate_uuid()  # Transaction ID Incoming payment or Outgoing payment or Deposit
    print('created',id_transaction, debit_account, credit_account, amount, ledger, 1)
    created = create_transfer_tiger_bettle(
        id_transaction, debit_account, credit_account, amount, ledger, 1
    )  # code=1 for TRANSFER code=2 for DEPOSIT code=3 for WITHDRAWAL
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create deposit transfer")
    return db_account


@router.post("/withdraw", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def withdraw_account(withdraw: WithdrawBase, db: Session = Depends(get_db)):
    db_account = db.query(Account).filter(Account.wallet_address_id == f'{withdraw.wallet_address_id}').first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    created = withdraw_wallet(client, f'{db_account.wallet_address_id}')
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create withdraw")
    return db_account
