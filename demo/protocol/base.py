import json


class ProtocolBase(object):
    """
    协议基础类
    """
    def dumps(self):
        return json.dumps(self.dict())

    def dict(self):
        return self.__dict__

    def __str__(self):
        return self.dumps()


class ProtocolDictBody(ProtocolBase):
    """
    协议体类
    """
    def __init__(self, **kwargs):
        super(ProtocolDictBody, self).__init__()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def dumps(self):
        return json.dumps(self.dict())

    def dict(self):
        return self.__dict__

    def __str__(self):
        return self.dumps()
