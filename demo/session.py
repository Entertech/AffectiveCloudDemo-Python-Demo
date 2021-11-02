from copy import deepcopy
import logging

from demo.protocol.request import (
    SessionRequest,
    sign,
)

logger = logging.getLogger('__name__')


class Session(object):
    """会话方法类
    """

    def __init__(self, sender):
        """初始化

        Args:
            sender ([func]): [数据包发送回调函数]
        """
        self.sender = sender

    def create(self):
        """创建会话
        """
        logger.debug('session create')
        request = deepcopy(SessionRequest.Create)
        ts, sign_str = sign(request['kwargs']['user_id'])
        request['kwargs']['sign'] = sign_str
        request['kwargs']['timestamp'] = ts
        self.sender(request)
        logger.debug('ClientID: {}'.format(request['kwargs']['user_id']))

    def created(self, response):
        """会话创建返回

        Args:
            response ([dict]): [返回数据]
        """
        pass

    def restore(self):
        """恢复会话
        """
        logger.debug('session restore')
        request = deepcopy(SessionRequest.Restore)
        ts, sign_str = sign(request['kwargs']['user_id'])
        request['kwargs']['sign'] = sign_str
        request['kwargs']['timestamp'] = ts
        self.sender(request)
        logger.debug('ClientID: {}'.format(request['kwargs']['user_id']))
        logger.debug('SessionID: {}'.format(request['kwargs']['session_id']))

    def restored(self, response):
        """会话恢复返回

        Args:
            response ([dict]): [返回数据]
        """
        pass

    def close(self):
        """关闭会话
        """
        logger.debug('session close')
        self.sender(SessionRequest.Close)

    def closed(self, response):
        """会话关闭返回

        Args:
            response ([dict]): [返回数据]
        """
        pass
