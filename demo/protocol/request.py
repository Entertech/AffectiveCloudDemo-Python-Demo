import hashlib
import time

import settings


def sign(client_id=None):
    """签名算法

    Args:
        client_id (str, optional): 用户 ID (通常使用不同用户唯一标识的 MD5 值). Defaults to None.

    Returns:
        [str, str]: 签名有效时间；签名字符串
    """
    _timestamp = str(int(time.time()))
    params = 'app_key={}&app_secret={}&timestamp={}&user_id={}'.format(
        settings.APP_KEY,
        settings.SECRET,
        _timestamp,
        client_id or settings.CLIENT_ID
    )
    _md5 = hashlib.md5()
    _md5.update(params.encode())
    return _timestamp, _md5.hexdigest().upper()


class SessionRequest(object):
    """会话协议
    """
    services = "session"

    Create = {
        "services": services,
        "op": "create",
        "kwargs": {
            "app_key": settings.APP_KEY,
            "sign": '_sign()',
            "user_id": settings.CLIENT_ID,
            "timestamp": '_timestamp',
            "upload_cycle": settings.UPLOAD_CYCLE,
        },
    }

    Restore = {
        "services": services,
        "op": "restore",
        "kwargs": {
            "app_key": settings.APP_KEY,
            "sign": '_sign()',
            "user_id": settings.CLIENT_ID,
            "timestamp": '_timestamp',
            "session_id": settings.SESSION_ID,
            "upload_cycle": settings.UPLOAD_CYCLE,
        },
    }

    Close = {"services": "session", "op": "close"}


class BioDataRequest(object):
    """基础服务协议
    """
    services = "biodata"

    Init = {
        "services": services,
        "op": "init",
        "kwargs": {
            "bio_data_type": [],
            "algorithm_params": {
                "eeg": {
                    "channel_power_verbose": False,
                    "filter_mode": "smart",
                    "power_mode": "rate",
                },
                "mceeg": {
                    "channel_power_verbose": False,
                    "filter_mode": "smart",
                    "power_mode": "rate",
                    "channel_num": 8
                },
            },
        },
    }

    Subscribe = {
        "services": 'biodata',
        "op": "subscribe",
        "args": list(settings.ACTIVE_SERVICES.keys())
    }

    Upload = {"services": services, "op": "upload", "kwargs": {}}

    Report = {
        "services": services,
        "op": "report",
        "kwargs": {"bio_data_type": []},
    }


class AffectiveRequest(object):
    """情感计算服务协议
    """
    services = "affective"

    Start = {
        "services": "affective",
        "op": "start",
        "kwargs": {"cloud_services": []},
    }

    Subscribe = {
        "services": "affective",
        "op": "subscribe",
        "args": [],
    }

    Report = {
        "services": services,
        "op": "report",
        "kwargs": {"cloud_services": []},
    }

    Finish = {
        "services": 'affective',
        "op": "finish",
        "kwargs": {"cloud_services": []},
    }
