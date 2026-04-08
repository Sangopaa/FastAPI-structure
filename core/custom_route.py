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
            
            # Interceptar solo respuestas que sean de tipo JSON
            is_json = isinstance(response, JSONResponse) or getattr(response, "media_type", None) == "application/json" or response.headers.get("content-type") == "application/json"
            
            if is_json:
                try:
                    body = response.body.decode()
                    data = json.loads(body) if body else None
                except Exception:
                    data = None
                
                # Prevenir doble envoltura si ya tiene el formato esperado
                if isinstance(data, dict) and "ok" in data and "data" in data and "message" in data:
                    return response

                ok = 200 <= response.status_code < 300
                wrapper = {
                    "ok": ok,
                    "data": data,
                    "message": "Success" if ok else "Error"
                }

                # Si ya es un dict y tiene 'message', preservarlo
                if isinstance(data, dict):
                     if "message" in data:
                         wrapper["message"] = data.pop("message")
                     if "ok" in data:
                         data.pop("ok")
                     
                headers = dict(response.headers)
                # Remueve content-length ya que vamos a cambiar el tamaño del body
                if "content-length" in headers:
                    del headers["content-length"]
                
                return JSONResponse(
                    status_code=response.status_code,
                    content=wrapper,
                    headers=headers,
                    media_type=getattr(response, "media_type", "application/json") or "application/json"
                )
            
            return response

        return custom_route_handler
