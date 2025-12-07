from fastapi import Depends, HTTPException, APIRouter
from starlette import status

from database import get_db
from enums.auth import TransferEnum
from helpers.account import get_db_account
from helpers.create_key import generate_uuid
from helpers.dependencies import validate_auth
from helpers.signature import GraphQLClient
from helpers.tigger_bettle_api import create_transfer_tiger_bettle
from helpers.transfers import create_transfer_db

from rafiki_api.transfer import create_transfer

from sqlalchemy.orm import Session

from rafiki_api.wallet import withdraw_wallet
from schemas.account_schema import DepositBase, AccountResponse, WithdrawBase
from schemas.transfer_schema import TransferBase, TransferResponse, TransferCreateBase

client = GraphQLClient()
router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TransferResponse)
async def transfer(transfer_obj: TransferBase, db: Session = Depends(get_db), payload=Depends(validate_auth)):
    '''
    Create a transfer between two accounts of the node
    '''
    aux = transfer_obj.dict()
    aux['wallet_sender_id'] = f'{aux.get("wallet_sender_id")}'
    transfer_response = create_transfer(client, **aux)
    if not transfer_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transfer creation failed"
        )
    try:
        wallet_object = get_db_account(db, f'{transfer_obj.wallet_sender_id}')
        db_transfer = TransferCreateBase(
            type_transfer=TransferEnum.TRANSFER,
            sender_wallet_address=wallet_object.wallet_address,
            receiver_wallet_address=transfer_obj.wallet_receive_url,
            asset_code=wallet_object.asset_code,
            amount=transfer_obj.amount * (10 ** wallet_object.asset_scale),
            description=transfer_obj.description,
            # transaction_hash = transfer_response
        )
        create_transfer_db(db, db_transfer)
    except Exception as error:
        print('Error saving transfer to database:', error)
    return {'id': transfer_response}


@router.post("/top-up", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def top_up_account(deposit: DepositBase, db: Session = Depends(get_db), payload=Depends(validate_auth)):
    '''
    Top-up an account by creating a transfer in Tiger Beetle.
    :param deposit:
    :param db:
    :return:
    '''
    db_account = get_db_account(db, f'{deposit.wallet_address_id}')
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    id_transaction = generate_uuid()  # Transaction ID Incoming payment or Outgoing payment or Deposit
    debit_account = f'{db_account.asset_id}'  # Asset ID
    credit_account = f'{deposit.wallet_address_id}'  # Wallet ID
    amount = int(deposit.credit * (10 ** db_account.asset_scale))
    ledger = int(db_account.asset_ledger)
    print('top-up', id_transaction, debit_account, credit_account, amount, ledger, 1)
    created = create_transfer_tiger_bettle(
        id_transaction, debit_account, credit_account, amount, ledger, 1
    )  # code=1 for TRANSFER code=2 for DEPOSIT code=3 for WITHDRAWAL
    if created.get('results', None):
        raise HTTPException(status_code=500, detail="Failed to create deposit transfer")
    try:
        db_transfer = TransferCreateBase(
            type_transfer=TransferEnum.TOP_UP,
            sender_wallet_address=f'{db_account.asset_id}',
            receiver_wallet_address=db_account.wallet_address,
            asset_code=db_account.asset_code,
            amount=amount,
            description='',
            # transaction_hash = transfer_response
        )
        create_transfer_db(db, db_transfer)
    except Exception as error:
        print('Error saving transfer top up to db:', error)
    return db_account


@router.post("/deposit", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def deposit_account(deposit: DepositBase, db: Session = Depends(get_db), payload=Depends(validate_auth)):
    '''
    Deposit an account by creating a transfer in Tiger Beetle. From Ledger to Asset and then Asset to Wallet of client.
    :param deposit:
    :param db:
    :return:
    '''
    db_account = get_db_account(db, f'{deposit.wallet_address_id}')
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    id_transaction_ledger = generate_uuid()  # Transaction ID Incoming payment or Outgoing payment or Deposit
    debit_account = f'{db_account.asset_id}'  # Asset ID
    credit_account = f'{deposit.wallet_address_id}'  # Wallet ID
    amount = int(deposit.credit * (10 ** db_account.asset_scale))
    ledger = int(db_account.asset_ledger)
    print('send_to_asset', id_transaction_ledger, debit_account, credit_account, amount, ledger, 2)
    send_to_asset = create_transfer_tiger_bettle(
        id_transaction_ledger, ledger, f'{db_account.asset_id}', amount, ledger, 2
    )  # code=1 for TRANSFER code=2 for DEPOSIT code=3 for WITHDRAWAL
    if send_to_asset.get('results', None):
        raise HTTPException(status_code=500, detail="Failed to create deposit to asset")
    id_transaction_asset = generate_uuid()  # Transaction ID Incoming payment or Outgoing payment or Deposit
    print('create deposit', id_transaction_asset, debit_account, credit_account, amount, ledger, 1)
    created = create_transfer_tiger_bettle(
        id_transaction_asset, debit_account, credit_account, amount, ledger, 1
    )  # code=1 for TRANSFER code=2 for DEPOSIT code=3 for WITHDRAWAL
    if created.get('results', None):
        raise HTTPException(status_code=500, detail="Failed to create deposit transfer")
    print('created', created)
    try:
        db_transfer = TransferCreateBase(
            type_transfer=TransferEnum.DEPOSIT,
            sender_wallet_address=f'{db_account.asset_id}',
            receiver_wallet_address=db_account.wallet_address,
            asset_code=db_account.asset_code,
            amount=amount,
            description='',
            transaction_hash=f'{id_transaction_asset}|{id_transaction_ledger}'
        )
        create_transfer_db(db, db_transfer)
    except Exception as error:
        print('Error saving transfer deposit to db:', error)
    return db_account


@router.post("/withdraw", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def withdraw_account(withdraw: WithdrawBase, db: Session = Depends(get_db), payload=Depends(validate_auth)):
    db_account = get_db_account(db, f'{withdraw.wallet_address_id}')
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    created = withdraw_wallet(client, f'{db_account.wallet_address_id}')
    print('created', created)
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create withdraw")
    try:
        pass
        db_transfer = TransferCreateBase(
            type_transfer=TransferEnum.WITHDRAW,
            sender_wallet_address=f'{db_account.wallet_address}',
            receiver_wallet_address=f'{db_account.asset_ledger}',
            asset_code=db_account.asset_code,
            amount=created.get('data', {}).get('createWalletAddressWithdrawal', {}).get('withdrawal', {}).get('amount',
                                                                                                              0),
            description='',
            transaction_hash=f''
        )
        create_transfer_db(db, db_transfer)
    except Exception as error:
        print('Error saving transfer withdraw to db:', error)
    return db_account
