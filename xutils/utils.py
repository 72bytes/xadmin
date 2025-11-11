import re
from dataclasses import dataclass
from typing import Any
from django.conf import settings
from django.utils import timezone
from django.utils.dateformat import format


@dataclass
class RespSuccessTempl:
    success: bool = True
    code: int = 200
    msg: str = "操作成功"
    data: Any  = None

    def as_dict(self) -> dict:
        return dict(
            success = self.success,
            code = self.code,
            msg = self.msg,
            data = self.data,
            timestamp = int(timezone.localtime().timestamp()*1000)
        )
    
@dataclass
class RespFailedTempl:
    success: bool = False
    code: int = 400
    msg: str = "操作失败"
    data: Any  = None

    def as_dict(self) -> dict:
        return dict(
            success = self.success,
            code = self.code,
            msg = self.msg,
            data = self.data,
            timestamp = int(timezone.localtime().timestamp()*1000)
        )
    
def camel_to_snake(name):
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def dateformat(ds):
    return format(timezone.localtime(ds), settings.TITW_DATE_FORMAT)
