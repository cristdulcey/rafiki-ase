from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class AmountType(Enum):
    DEBIT = "debit"
    RECEIVE = "receive"
    UNLIMITED = "unlimited"

class GrantAmount(BaseModel):
    amount: float
    currencyDisplayCode: str

class Access(BaseModel):
    type: str
    grantId: Optional[str] = None
    limits: Optional[Dict[str, Any]] = None

class InstanceConfig(BaseModel):
    name: str
    logo: str

class ConsentScreenContext(BaseModel):
    ready: bool
    thirdPartyName: str
    thirdPartyUri: str
    interactId: str
    nonce: str
    returnUrl: str
    accesses: Optional[List[Access]]
    outgoingPaymentAccess: Optional[Access]
    price: Optional[GrantAmount]
    costToUser: Optional[GrantAmount]
    errors: List[str]

class ConsentScreenProps(BaseModel):
    idpSecretParam: str

class LoaderData(BaseModel):
    defaultIdpSecret: str
    isTenant: bool