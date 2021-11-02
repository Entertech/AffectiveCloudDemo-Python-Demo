from copy import deepcopy
import logging

import settings
from demo.protocol.request import BioDataRequest

logger = logging.getLogger('__name__')


class BiodataService(object):
    """基础服务方法类
    """

    def __init__(self, sender):
        """初始化

        Args:
            sender ([func]): [数据包发送回调函数]
        """
        self.sender = sender

    def init(self):
        """初始化基础服务
        """
        init_req = deepcopy(BioDataRequest.Init)
        init_req["kwargs"]["bio_data_type"] = list(settings.ACTIVE_SERVICES.keys())
        self.sender(init_req)

    def subscribe(self, biodata_type):
        """订阅服务数据

        Args:
            biodata_type ([str]): [服务类型]
        """
        sub_req = deepcopy(BioDataRequest.Subscribe)
        sub_req["args"] = [biodata_type]
        self.sender(sub_req)

    def subscribed(self, response):
        """订阅返回

        Args:
            response ([dict]): [返回数据]
        """
        pass

    def upload(self, biodata_type, data_slice):
        """上传原始数据

        Args:
            biodata_type ([str]): [数据对应的服务类型]
            data_slice ([list]): [数据片段]
        """
        request = deepcopy(BioDataRequest.Upload)
        request['kwargs'][biodata_type] = data_slice
        self.sender(request)

    def realtime_data(self, response):
        """实时数据返回

        Args:
            response ([dict]): [返回数据]
        """
        pass

    def report(self, biodata_type):
        """请求报表

        Args:
            biodata_type ([str]): [服务类型]
        """
        report = deepcopy(BioDataRequest.Report)
        report["kwargs"]["bio_data_type"] = [biodata_type]
        self.sender(report)

    def reported(self, response):
        """报表返回

        Args:
            response ([dict]): [返回数据]
        """
        pass
