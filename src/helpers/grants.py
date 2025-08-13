from models.idp import ConsentScreenContext, Access, GrantAmount, AmountType


async def process_grant_amounts(ctx: ConsentScreenContext, outgoing_payment_access: Access) -> ConsentScreenContext:
    """Process grant amounts and update context"""

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
