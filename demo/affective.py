from copy import deepcopy
import logging

import settings
from demo.protocol.request import AffectiveRequest

logger = logging.getLogger('__name__')


class AffectiveService(object):
    """情感计算服务方法类
    """

    def __init__(self, sender):
        """初始化

        Args:
            sender ([func]): [数据包发送回调函数]
        """
        self.sender = sender

    def start(self, biodata_type):
        """启动某情感计算服务

        Args:
            biodata_type ([str]): [相关的基础服务类型]
        """
        req = deepcopy(AffectiveRequest.Start)
        req["kwargs"]["cloud_services"] = settings.ACTIVE_SERVICES[biodata_type]
        self.sender(req)

    def subscribe(self, affective_type):
        """订阅某情感服务数据

        Args:
            affective_type ([str]): [情感服务类型]
        """
        req = deepcopy(AffectiveRequest.Subscribe)
        req["args"] = [affective_type]
        self.sender(req)

    def subscribed(self, response):
        """订阅状态返回

        Args:
            response ([dict]): [返回数据]
        """
        pass

    def realtime_data(self, response):
        """订阅实时数据返回

        Args:
            response ([dict]): [返回数据]
        """

    def report(self, affective_type):
        """请求报表

        Args:
            affective_type ([str]): [情感服务类型]
        """
        report = deepcopy(AffectiveRequest.Report)
        report["kwargs"]["cloud_services"] = [affective_type]
        self.sender(report)

    def reported(self, response):
        """报表返回

        Args:
            response ([dict]): [返回数据]
        """
        pass

    def finish(self, affective_type):
        """请求结束

        Args:
            affective_type ([str]): [情感服务类型]
        """
        report = deepcopy(AffectiveRequest.Finish)
        report["kwargs"]["cloud_services"] = [affective_type]
        self.sender(report)

    def finished(self, response):
        """服务完成返回

        Args:
            response ([dict]): [返回数据]
        """
        pass
