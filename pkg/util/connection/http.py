# pkg/util/router.py

from fastapi import FastAPI, Request

class Router:
    def __init__(self):
        self.app = FastAPI()

    def register(self, path: str, handler, methods=None):
        if methods is None:
            methods = ["GET"]  # default

        async def endpoint(request: Request):
            try:
                # Handle different request types
                if request.method in ["POST", "PUT", "PATCH"]:
                    body = await request.json()
                else:
                    body = dict(request.query_params)

                return await handler(body, request)

            except Exception as e:
                return {"error": str(e)}

        self.app.add_api_route(path, endpoint, methods=methods)