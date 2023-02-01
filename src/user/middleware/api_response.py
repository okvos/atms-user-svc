from aiohttp.web import Request, Response, middleware


@middleware
async def api_response(request: Request, handler) -> Response:
    if request.method == "OPTIONS":
        return Response()
    resp: Response = await handler(request)
    return resp
