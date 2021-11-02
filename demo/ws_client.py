import gzip
import json
import logging
import threading
import time
import os

import websocket

import settings

from demo.protocol.request import (
    SessionRequest,
    BioDataRequest,
    AffectiveRequest
)
from demo.protocol.response import ResponseProtocol
from demo.session import Session
from demo.biodata import BiodataService
from demo.affective import AffectiveService


logger = logging.getLogger(__name__)


class WSClient(object):
    """WebSocket 客户端
    """
    def __init__(self):
        # 发包总数
        self.package_num_total = {}
        # 情感服务完成计数
        self.finished = 0
        # 算法触发次数计数
        self.trigger = {}
        # 发包计数
        self.package_num = {}
        websocket.enableTrace(False)
        # 连接服务器
        self.ws = websocket.WebSocketApp(
            url=settings.URL,
            on_open=self.on_open,
            on_message=self.on_message,
            on_close=self.on_close,
        )
        self.ws.run_forever(ping_interval=15)

    def send(self, data):
        """发送数据包

        Args:
            data ([dict]): [数据包]
        """
        data = json.dumps(data)
        # 压缩待发送数据
        data = gzip.compress(data.encode())
        self.ws.send(data, websocket.ABNF.OPCODE_BINARY)

    def on_open(self):
        logger.debug('on open')
        self.session = Session(self.send)
        self.biodata_service = BiodataService(self.send)
        self.affective_service = AffectiveService(self.send)
        # 根据 settings.SESSION_ID 来确认 Demo 是创建新会话还是恢复会话
        if settings.SESSION_ID:
            self.session.restore()
        else:
            self.session.create()

    def on_error(self, err):
        logger.debug('on error: {}'.format(err))

    def on_close(self):
        logger.debug('on close')

    def on_message(self, message):
        # 收到服务端发送的包需要先解压
        message = gzip.decompress(message)
        resp = ResponseProtocol(**json.loads(message))
        logger.debug('--->>> {}'.format(resp))
        # code 不为 0 则代表发生异常，详情看 resp
        if resp.code != 0:
            logger.warning('>>> {}'.format(resp))
            return
        # 根据协议调度不同模块的处理方法
        if resp.request.services == SessionRequest.services:
            self.session_response(resp)
        elif resp.request.services == BioDataRequest.services:
            self.biodata_response(resp)
        elif resp.request.services == AffectiveRequest.services:
            self.affective_response(resp)

    def session_response(self, resp):
        if resp.request.op == SessionRequest.Create.get('op'):
            self.session.created(resp)
            self.biodata_service.init()
        elif resp.request.op == SessionRequest.Restore.get('op'):
            self.session.restored(resp)
            self.biodata_service.init()
        elif resp.request.op == SessionRequest.Close.get('op'):
            self.session.closed(resp)
            self.ws.close()

    def biodata_response(self, resp):
        if resp.request.op == BioDataRequest.Init.get('op'):
            for biodata_type in resp.data.get('bio_data_type'):
                self.trigger[biodata_type] = 0
                self.package_num[biodata_type] = 0
                self.biodata_service.subscribe(biodata_type)
                self.affective_service.start(biodata_type)
        elif resp.request.op == BioDataRequest.Subscribe.get('op'):
            for key, _ in resp.data.items():
                if 'sub_' in key:
                    if key.split('_')[1] == 'eeg':
                        threading.Thread(target=self.send_eeg_data).start()
                    elif key.split('_')[1] == 'hr-v2':
                        threading.Thread(target=self.send_hr_data).start()
                else:
                    self.trigger[key] += 1
                    self.biodata_service.realtime_data(resp)
                    if self.trigger[key] == settings.CLOSE_AFTER_TRIGGER \
                        or self.package_num_total[key] == self.trigger[key]:
                        self.biodata_service.report(key)
        elif resp.request.op == BioDataRequest.Report.get('op'):
            self.biodata_service.reported(resp)

    def affective_response(self, resp):
        if resp.request.op == AffectiveRequest.Start.get('op'):
            for affective_type in resp.data.get('cloud_service'):
                self.trigger[affective_type] = 0
                self.package_num[affective_type] = 0
                self.affective_service.subscribe(affective_type)
        elif resp.request.op == AffectiveRequest.Subscribe.get('op'):
            for key, _ in resp.data.items():
                if 'sub_' in key:
                    self.affective_service.subscribed(key.split('_')[1])
                    break
                else:
                    self.trigger[key] += 1
                    self.affective_service.realtime_data(resp)
                    if self.trigger[key] == settings.CLOSE_AFTER_TRIGGER \
                        or self.package_num_total['eeg'] == self.trigger[key]:  # 暴力触发
                        self.affective_service.report(key)
        elif resp.request.op == AffectiveRequest.Report.get('op'):
            for d_type, _ in resp.data.items():
                self.affective_service.finish(d_type)
        elif resp.request.op == AffectiveRequest.Finish.get('op'):
            self.affective_service.finished(resp)
            self.finished += 1
            if self.finished == sum([len(v) for v in settings.ACTIVE_SERVICES.values()]):
                self.session.close()

    def load_data_file(self, file_path):
        """读取仿真文件

        Args:
            file_path ([str]): [文件路径]

        Returns:
            [list]: [原始数据]
        """
        if os.path.getsize(file_path) == 0:
            return []
        with open(file_path, 'r') as f:
            raw_data_str = f.read()
            raw_data_str = raw_data_str.replace('——————————', ',')
            if raw_data_str[-1] == ',':
                raw_data_str = raw_data_str[:-1]
            raw_data_list = raw_data_str.replace('\n', '').replace('[', '').replace(']', '').replace(' ', '').split(',')
        raw_data = []
        for byte_data in raw_data_list:
            raw_data.append(int(byte_data))

        return raw_data

    # 数据驱动仿真
    def send_eeg_data(self):
        eeg_raw_data = self.load_data_file('./simulation_data/eeg.txt')
        step_len = 1000 * settings.UPLOAD_CYCLE
        num = int(len(eeg_raw_data) / step_len)
        self.package_num_total['eeg'] = num
        for count, index in enumerate(range(0, len(eeg_raw_data), step_len)):
            data_slice = eeg_raw_data[index: index + step_len]
            if len(data_slice) < step_len or count == settings.CLOSE_AFTER_TRIGGER:
                break
            logger.debug('<<< EEG -> {}/{}'.format(count + 1, num))
            self.package_num['eeg'] += 1
            self.biodata_service.upload('eeg', data_slice)
            time.sleep(0.6 * settings.UPLOAD_CYCLE)

    def send_hr_data(self):
        hr_raw_data = self.load_data_file('./simulation_data/hr.txt')
        step_len = 3 * settings.UPLOAD_CYCLE
        num = int(len(hr_raw_data) / step_len)
        self.package_num_total['hr-v2'] = num
        for count, index in enumerate(range(0, len(hr_raw_data), step_len)):
            data_slice = hr_raw_data[index: index + step_len]
            if len(data_slice) < step_len or count == settings.CLOSE_AFTER_TRIGGER:
                break
            logger.debug('<<< HR -> {}/{}'.format(count + 1, num))
            self.package_num['hr-v2'] += 1
            self.biodata_service.upload('hr-v2', data_slice)
            time.sleep(0.6 * settings.UPLOAD_CYCLE)
