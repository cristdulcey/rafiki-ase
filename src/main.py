import os
import sentry_sdk

from database import config_elastic
from elasticsearch_middleware import ElasticsearchLoggerMiddleware
from middlewares.error_handler import error_middleware

# Ensure TigerBeetle client avoids io_uring on hosts that block it
os.environ.setdefault("TB_CLIENT_IO", "sync")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from helpers.signature import GraphQLClient
from rafiki_api.peer import create_auto_peer
from routers import webhooks_router
from routers import accounts_router
from routers import transfers_router
from routers import rates_router
from routers import idp
from settings import settings

app = FastAPI(
    title="Rafiki ASE",
    description="simple rest-full api with fastapi",
    version="1.0",
)

origins = [
    "*",
]
app.middleware("http")(error_middleware)



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhooks_router.router)
app.include_router(accounts_router.router)
app.include_router(transfers_router.router)
app.include_router(rates_router.router)
app.include_router(idp.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")

app.add_middleware(SessionMiddleware, secret_key=secret_key)

if settings.ELASTIC_URL != '':
    app.add_middleware(ElasticsearchLoggerMiddleware, config=config_elastic)


if settings.add_peer != "":
    client = GraphQLClient()
    peer = create_auto_peer(client, settings.add_peer, settings.asset_id, 0)
    print(f"Peer created: {peer}")


# @app.middleware("http")
# async def db_session_middleware(request: Request, call_next):
#     response = Response("Internal server error", status_code=500)
#     try:
#         request.state.db = SessionLocal()
#         response = await call_next(request)
#     finally:
#         request.state.db.close()
#     return response


# @app.exception_handler(AuthJWTException)
# def authjwt_exception_handler(request: Request, exc: AuthJWTException):
#     if exc.message == "Signature has expired":
#         return JSONResponse(status_code=401, content={"detail": exc.message})
#     elif exc.message == "Signature verification failed":
#         return JSONResponse(status_code=401, content={"detail": exc.message})
#     return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/")
async def root():
    return {"message": "ASE API"}

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
    )
