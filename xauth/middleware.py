import json
from ninja.responses import Response
from xutils import utils


class UnifiedResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if isinstance(response, Response):
            resp = utils.RespSuccessTempl()
            if 200 <= response.status_code < 299:
                pass
            elif response.status_code >= 400:
                resp = utils.RespFailedTempl()
            resp.code = response.status_code
            resp.data = response.content
            response.content = json.dumps(resp.as_dict())

        return response

