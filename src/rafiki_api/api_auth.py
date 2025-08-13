import httpx
from typing import Dict, Any, Optional, List

from pydantic import BaseModel

from settings import settings


class ApiResponse(BaseModel):
    isFailure: bool
    payload: Optional[Any] = None
    errors: List[str] = []


class ApiClient:
    def __init__(self):
        self.base_url = settings.url_auth

    async def get_grant(self, interact_id: str, nonce: str) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/grant/{interact_id}/{nonce}",
                    headers={
                        "Content-Type": "application/json",
                        'x-idp-secret': f'{settings.idp_secret}'
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "isFailure": False,
                        "payload": data.get("access", []),
                        "errors": [],
                        'contextUpdates': data
                    }
                else:
                    return {
                        "isFailure": True,
                        "payload": None,
                        "errors": [f"API request failed with status {response.status_code}"]
                    }

        except Exception as e:
            return {
                "isFailure": True,
                "payload": None,
                "errors": [str(e)]
            }

    async def choose_consent(self, interact_id: str, nonce: str, accept: bool) -> ApiResponse:
        try:
            acceptance_sub_path = "accept" if accept else "reject"
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/grant/{interact_id}/{nonce}/{acceptance_sub_path}",
                    headers={
                        "x-idp-secret": settings.idp_secret,
                        "Content-Type": "application/json"
                    }
                )
                if response.status_code == 202:
                    return ApiResponse(
                        isFailure=False,
                        payload=response.text if response.content else None,
                        errors=[]
                    )
                else:
                    return ApiResponse(
                        isFailure=True,
                        payload=None,
                        errors=[f"Request failed with status {response.status_code}"]
                    )
        except Exception as e:
            return ApiResponse(
                isFailure=True,
                payload=None,
                errors=[f"Error submitting consent: {str(e)}"]
            )

    @staticmethod
    def create_redirect_response(interact_id: str, nonce: str, auth_server_domain: str) -> str:
        redirect_url = f"{auth_server_domain}/interact/{interact_id}/{nonce}/finish"
        return redirect_url
