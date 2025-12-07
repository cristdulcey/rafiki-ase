from models.transfer import Transfer
from schemas.transfer_schema import TransferCreateBase


def get_transfer(db, transfer_id):
    return db.query(Transfer).filter(Transfer.id == transfer_id).first()


def get_transfers(db, skip: int = 0, limit: int = 100, sender_wallet_address: str = None,
                  receiver_wallet_address: str = None):
    query = db.query(Transfer)
    if sender_wallet_address:
        query = query.filter(Transfer.sender_wallet_address == sender_wallet_address)
    if receiver_wallet_address:
        query = query.filter(Transfer.receiver_wallet_address == receiver_wallet_address)
    return query.offset(skip).limit(limit).all()


def create_transfer_db(db, transfer: TransferCreateBase):
    new_transfer = Transfer(**transfer.model_dump())
    db.add(new_transfer)
    db.commit()
    db.refresh(new_transfer)
    return new_transfer
