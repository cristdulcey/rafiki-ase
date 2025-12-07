from models.account import Account


def get_db_account(db,wallet_address_id):
    return db.query(Account).filter(Account.wallet_address_id == f'{wallet_address_id}').first()
