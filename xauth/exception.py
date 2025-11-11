from http import HTTPStatus
from django.http import Http404


class HttpNotFound(Http404):
    def __init__(self, msg='the requested resource is not found.'):
        self.status = HTTPStatus.NOT_FOUND
        self.msg = msg
        super().__init__(self.msg)
