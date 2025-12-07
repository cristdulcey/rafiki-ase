import os
from typing import Optional

from fastapi.security import HTTPBearer
# from fastapi_jwt_auth import AuthJWT
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
    database_uri: Optional[str] = os.getenv('database_uri', 'sqlite:///./test.db')
    sentry_token: Optional[str] = None
    authjwt_secret_key: Optional[str] = os.getenv('authjwt_secret_key', None)
    tenant_id: Optional[str] = os.getenv('tenant_id', '438fa74a-fa7d-4317-9ced-dde32ece1787')
    url_rafiki: Optional[str] = os.getenv('url_rafiki', 'http://127.0.0.1:3001')
    url_auth: Optional[str] = os.getenv('url_auth', 'http://127.0.0.1:3009')
    url_auth_server_domain: Optional[str] = os.getenv('url_auth_server_domain', 'http://127.0.0.1:3006')
    url_self_service: Optional[str] = os.getenv('url_self_service', 'http://localhost:8000')
    secret_graphql: Optional[str] = os.getenv('secret_graphql', 'iyIgCprjb9uL8wFckR+pLEkJWMB7FJhgkvqhTQR/964=')
    version_graphql: Optional[int] = os.getenv('version_graphql', 1)
    idp_secret: Optional[str] = os.getenv('idp_secret', '2pEcn2kkCclbOHQiGNEwhJ0rucATZhrA807HTm2rNXE=')
    is_tenant: Optional[bool] = os.getenv('is_tenant', False)
    domain_wallet: Optional[str] = os.getenv('domain_wallet', 'https://open-payments.cristdulcey.com/accounts')
    # tiger_beetle_address: Optional[str] = os.getenv('tiger_beetle_address', '4242')
    tiger_beetle_api_url: Optional[str] = os.getenv('tiger_beetle_api_url', 'http://tigerbeetle_api:50051')
    add_peer: Optional[str] = os.getenv('add_peer', '')
    asset_id: Optional[str] = os.getenv('asset_id', '06cdd91e-caee-4182-93c9-b0b405bf7f20')


# # callback to get your configuration
# @AuthJWT.load_config
# def get_config():
#     return Settings()


settings = Settings()
