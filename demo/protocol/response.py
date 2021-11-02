import json
from copy import deepcopy

from demo.protocol.base import ProtocolDictBody, ProtocolBase


class ResponseRequestBody(ProtocolBase):
    """协议返回包
    """

    services: str = None

    op: str = None

    def __init__(self, **kwargs):
        super(ResponseRequestBody, self).__init__()
        for k, v in kwargs.items():
            if k not in ('services', 'op'):
                raise Exception('Protocol Error: invalid parameters({}).'.format(k))
            setattr(self, k, v)

    def dumps(self):
        return json.dumps(self.dict(), indent=4)

    def dict(self):
        return self.__dict__

    def __str__(self):
        return self.dumps()


class ResponseProtocol(ProtocolBase):
    """通用协议
    """
    code: int = None

    request: ResponseRequestBody = None

    data = None

    msg: str = None

    def __init__(self, **kwargs):
        super(ResponseProtocol, self).__init__()
        for k, v in kwargs.items():
            if k == 'request':
                setattr(self, k, ResponseRequestBody(**v))
                continue
            if k not in ('code', 'request', 'data', 'msg'):
                raise Exception('Protocol Error: invalid parameters({}).'.format(k))
            setattr(self, k, v)

    def dumps(self):
        return json.dumps(self.dict())

    def dict(self):
        d = deepcopy(self.__dict__)
        d['request'] = self.request.dict()
        if isinstance(self.data, ProtocolDictBody):
            d['data'] = self.data.dict()
        return d

    def __str__(self):
        return self.dumps()
