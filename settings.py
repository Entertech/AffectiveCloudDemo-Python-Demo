import logging
import os

# 情感云服务 WebSocket 地址
URL = 'wss://server.affectivecloud.cn/ws/algorithm/v2/'

# 上传周期
UPLOAD_CYCLE = 3

# 需要使用的服务（不同的基础服务可能对应不同的情感算法服务）
ACTIVE_SERVICES = {
    'eeg': [
        'attention',
        'relaxation',
        'pleasure',
    ],
    'hr-v2': [
        'pressure',
        'arousal',
        'coherence',
    ]
}

# 设置 Demo 触发结束发包的时机（如: 10 代表在触发 10 次算法调度后结束发包）
CLOSE_AFTER_TRIGGER = 10

# 客户端 ID（用于标记具体使用的用户；可根据实际情况修改）
CLIENT_ID = '728276BB353D74A85E7B17F9330E88BD'

# 会话 ID（设置为 None，则 Demo 运行时，创建新会话；设置具体会话 ID，则为恢复会话操作）
SESSION_ID = None

# AppKey & Secret
APP_KEY = os.environ.get('APP_KEY')
SECRET = os.environ.get('SECRET')

assert(APP_KEY and SECRET)

# ------------------------------------------------------------------
# 日志配置
log_fmt = (
    '[%(asctime)s] '
    '[%(levelname)s] '
    '[%(name)s:%(lineno)d:%(funcName)s] '
    ')=> %(message)s'
)
formatter = logging.Formatter(log_fmt)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logging.getLogger().addHandler(stream_handler)
logging.getLogger().setLevel(logging.DEBUG)
