import os

from fastapi import Request, Form, HTTPException, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional

from starlette import status
from starlette.templating import Jinja2Templates

from helpers.grants import process_grant_amounts
from models.idp import ConsentScreenContext, InstanceConfig, Access, GrantAmount, AmountType
from urllib.parse import urlencode, parse_qs, urlparse

from rafiki_api.api_auth import ApiClient
from settings import settings

router = APIRouter(prefix="/idp", tags=["idp"])

templates = Jinja2Templates(directory="templates")


async def process_grant_amounts(ctx: ConsentScreenContext, outgoing_payment_access: Access) -> ConsentScreenContext:
    if outgoing_payment_access.limits:
        debit_amount = outgoing_payment_access.limits.get("debitAmount")
        receive_amount = outgoing_payment_access.limits.get("receiveAmount")

        if debit_amount and receive_amount:
            ctx.errors.append("only one of receiveAmount or debitAmount allowed")
        else:
            if receive_amount:
                ctx.price = GrantAmount(
                    amount=float(receive_amount["value"]) / (10 ** receive_amount["assetScale"]),
                    currencyDisplayCode=receive_amount["assetCode"]
                )

            if debit_amount:
                ctx.costToUser = GrantAmount(
                    amount=float(debit_amount["value"]) / (10 ** debit_amount["assetScale"]),
                    currencyDisplayCode=debit_amount["assetCode"]
                )

            # Update return URL with additional parameters
            try:
                from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

                parsed = urlparse(ctx.returnUrl)
                query_params = parse_qs(parsed.query)

                # Add grant information to return URL
                query_params.update({
                    "grantId": [outgoing_payment_access.grantId] if hasattr(outgoing_payment_access, 'grantId') else [],
                    "thirdPartyName": [ctx.thirdPartyName],
                    "thirdPartyUri": [ctx.thirdPartyUri],
                    "currencyDisplayCode": [
                        debit_amount.get("assetCode") if debit_amount
                        else receive_amount.get("assetCode") if receive_amount
                        else ""
                    ],
                    "amountValue": [
                        str(debit_amount.get("value")) if debit_amount
                        else str(receive_amount.get("value")) if receive_amount
                        else ""
                    ],
                    "amountScale": [
                        str(debit_amount.get("assetScale")) if debit_amount
                        else str(receive_amount.get("assetScale")) if receive_amount
                        else ""
                    ],
                    "amountType": [
                        AmountType.RECEIVE.value if receive_amount
                        else AmountType.DEBIT.value if debit_amount
                        else AmountType.UNLIMITED.value
                    ]
                })

                new_query = urlencode(query_params, doseq=True)
                ctx.returnUrl = urlunparse((
                    parsed.scheme, parsed.netloc, parsed.path,
                    parsed.params, new_query, parsed.fragment
                ))

            except Exception as e:
                ctx.errors.append(f"Error processing return URL: {str(e)}")

    return ctx


def get_instance_config() -> InstanceConfig:
    """Get instance configuration"""
    return InstanceConfig(
        name="Mock Identity Provider",
        logo="logo.svg"
    )


@router.get("/", response_class=HTMLResponse)
async def consent_screen(
        request: Request,
        interactId: Optional[str] = None,
        nonce: Optional[str] = None,
        returnUrl: Optional[str] = None,
        clientName: Optional[str] = None,
        clientUri: Optional[str] = None,
):
    """Main consent screen route"""
    auth_server_domain = settings.url_auth_server_domain
    # validate if exist session_id
    print(f"Auth server domain: {auth_server_domain} interactId: {interactId} nonce: {nonce} returnUrl: {returnUrl} clientName: {clientName} clientUri: {clientUri}")
    if not request.cookies.get("sessionId"):
        response = RedirectResponse(
            url=f"{auth_server_domain}/interact/{interactId}/{nonce}?clientName={clientName}&clientUri={clientUri}",
            status_code=status.HTTP_302_FOUND)
        return response
    else:
        if request.cookies.get("uuid"):
            # delete cookie uuid
            response = RedirectResponse(
                url=f"{auth_server_domain}/interact/{interactId}/{nonce}?clientName={clientName}&clientUri={clientUri}",
                status_code=status.HTTP_302_FOUND)
            response.delete_cookie("uuid")
            response.delete_cookie("sessionId")
            return response
        else:
            uuid = os.urandom(16).hex()

    # Initialize context
    ctx = ConsentScreenContext(
        ready=False,
        thirdPartyName="",
        thirdPartyUri="",
        interactId=interactId or "demo-interact-id",
        nonce=nonce or "demo-interact-nonce",
        returnUrl=returnUrl or f"{settings.url_self_service}/idp/consent?",
        accesses=None,
        outgoingPaymentAccess=None,
        price=None,
        costToUser=None,
        errors=[]
    )

    instance_config = get_instance_config()

    # If we have both interactId and nonce from URL params, process the grant
    if interactId and nonce:
        ctx.ready = True
        ctx.interactId = interactId
        ctx.nonce = nonce
        ctx.thirdPartyName = clientName or ""
        ctx.thirdPartyUri = clientUri or ""
        if returnUrl:
            ctx.returnUrl = returnUrl
        try:
            # Get grant information
            api_client = ApiClient()
            response = await api_client.get_grant(
                interact_id=interactId,
                nonce=nonce,
            )
            if response["isFailure"]:
                ctx.errors = [error for error in response["errors"]]
            elif not response["payload"]:
                ctx.errors = ["no accesses in grant"]
            else:
                ctx.accesses = [Access(**access) for access in response["payload"]]

                # Find outgoing payment access
                outgoing_payment_access = None
                for access in ctx.accesses:
                    if access.type == "outgoing-payment":
                        outgoing_payment_access = access
                        break

                ctx.outgoingPaymentAccess = outgoing_payment_access

                if outgoing_payment_access:
                    # Process amounts and build return URL
                    ctx = await process_grant_amounts(ctx, outgoing_payment_access)

        except Exception as e:
            ctx.errors = [str(e)]
    response = templates.TemplateResponse(
        "consent_screen.html",
        {
            "request": request,
            "ctx": ctx,
            "instance_config": instance_config,
            "default_idp_secret": settings.idp_secret,
            "is_tenant": settings.is_tenant
        }
    )
    if uuid:
        response.set_cookie("uuid", uuid)
    return response


@router.post("/begin-consent")
async def begin_consent(
        request: Request,
        interactId: str = Form(...),
        nonce: str = Form(...),
        returnUrl: str = Form(...)
):
    """Handle begin consent form submission"""

    # Redirect to main consent screen with parameters
    params = {
        "interactId": interactId,
        "nonce": nonce,
        "returnUrl": returnUrl
    }

    return RedirectResponse(
        url=f"/?{urlencode(params)}",
        status_code=302
    )


@router.get("/consent-decision")
async def consent_decision(
        interactId: str,
        nonce: str,
        decision: str,
        returnUrl: str
):
    """Handle consent decision and redirect"""

    # Parse the return URL and add parameters
    parsed_url = urlparse(returnUrl)
    query_params = parse_qs(parsed_url.query)

    # Add our parameters
    query_params["interactId"] = [interactId]
    query_params["nonce"] = [nonce]
    query_params["decision"] = [decision]

    # Rebuild the URL
    new_query = urlencode(query_params, doseq=True)
    redirect_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{new_query}"

    return RedirectResponse(url=redirect_url, status_code=302)


@router.get("/consent", response_class=HTMLResponse)
async def consent_result(
        request: Request,
        interactId: Optional[str] = None,
        nonce: Optional[str] = None,
        decision: Optional[str] = None,
        grantId: Optional[str] = None,
        thirdPartyName: Optional[str] = None,
        thirdPartyUri: Optional[str] = None,
        currencyDisplayCode: Optional[str] = None,
        amountValue: Optional[str] = None,
        amountScale: Optional[str] = None,
        amountType: Optional[str] = None
):
    """Handle consent result page with updated ApiResponse handling"""

    # Calculate amount from value and scale
    amount = 0
    if amountValue and amountScale:
        try:
            amount = float(amountValue) / (10 ** int(amountScale))
        except (ValueError, TypeError):
            amount = 0

    # Initialize context
    ctx = {
        "done": False,
        "authorized": False,
        "interactId": "",
        "nonce": "",
        "grantId": grantId,
        "thirdPartyName": thirdPartyName or "",
        "thirdPartyUri": thirdPartyUri,
        "currencyDisplayCode": currencyDisplayCode or "",
        "amount": amount,
        "amountType": amountType or "",
        "error": None
    }

    instance_config = get_instance_config()
    auth_server_domain = settings.url_auth_server_domain

    # Process consent if we have the required parameters
    if interactId and nonce and decision:
        acceptance_decision = decision.lower() == 'accept'
        try:
            api_client = ApiClient()
            api_response = await api_client.choose_consent(
                interact_id=interactId,
                nonce=nonce,
                accept=acceptance_decision,
            )
            if api_response.isFailure:
                ctx.update({
                    "done": True,
                    "interactId": interactId,
                    "nonce": nonce,
                    "error": "; ".join(api_response.errors)
                })
            else:
                ctx.update({
                    "done": True,
                    "authorized": acceptance_decision,
                    "interactId": interactId,
                    "nonce": nonce
                })

        except Exception as e:
            ctx.update({
                "done": True,
                "interactId": interactId,
                "nonce": nonce,
                "error": str(e)
            })

    return templates.TemplateResponse(
        "consent_result.html",
        {
            "request": request,
            "ctx": ctx,
            "instance_config": instance_config,
            "auth_server_domain": auth_server_domain
        }
    )


@router.post("/end-interaction")
async def end_interaction(
        request: Request,
        interactId: str = Form(...),
        nonce: str = Form(...),
        authServerDomain: str = Form(...)
):
    """Handle end interaction request with redirect"""
    try:
        api_client = ApiClient()
        # Get the redirect response
        redirect_response = api_client.create_redirect_response(interactId, nonce, authServerDomain)
        return {'url': redirect_response}

    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/send-money", response_class=HTMLResponse)
async def send_money(request: Request, ):
    instance_config = get_instance_config()

    return templates.TemplateResponse(
        "send_money.html",
        {
            "request": request,
            "instance_config": instance_config,

        }
    )
