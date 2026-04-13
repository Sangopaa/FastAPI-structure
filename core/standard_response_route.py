import json
from typing import Callable
from fastapi import Request, Response
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse


class StandardResponseRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            response: Response = await original_route_handler(request)

            # Intercept only JSON responses
            is_json = (
                isinstance(response, JSONResponse)
                or getattr(response, "media_type", None) == "application/json"
                or response.headers.get("content-type") == "application/json"
            )

            if is_json:
                try:
                    body = response.body.decode()
                    data = json.loads(body) if body else None
                except Exception:
                    data = None

                # Prevent double-wrapping if the response already has the expected format
                if (
                    isinstance(data, dict)
                    and "ok" in data
                    and "data" in data
                    and "message" in data
                ):
                    return response

                ok = 200 <= response.status_code < 300
                wrapper = {
                    "ok": ok,
                    "data": data,
                    "message": "Success" if ok else "Error",
                }

                # If it's already a dict and has 'message', preserve it
                if isinstance(data, dict):
                    if "message" in data:
                        wrapper["message"] = data.pop("message")
                    if "ok" in data:
                        data.pop("ok")

                headers = dict(response.headers)
                # Remove content-length since the body size will change
                if "content-length" in headers:
                    del headers["content-length"]

                return JSONResponse(
                    status_code=response.status_code,
                    content=wrapper,
                    headers=headers,
                    media_type=getattr(response, "media_type", "application/json")
                    or "application/json",
                )

            return response

        return custom_route_handler
