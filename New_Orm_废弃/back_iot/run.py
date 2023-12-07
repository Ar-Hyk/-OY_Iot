# 基础
import time
import threading
# fastapi
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 定时
from apscheduler.schedulers.background import BackgroundScheduler
# 日志
import logging
# 自编模块
from scr.iot_server import IotServer, DataMsg, CommandMsg
from scr.mysql_operation import DB
from scr.tx_api import TX_API

api_server = FastAPI()
iot_server = IotServer()
db = DB()
tx_api = TX_API()
logger = logging.getLogger('logger')

# 定时任务
plan = BackgroundScheduler(timezone='Asia/Shanghai')

# 解决FastAPI跨域问题
api_server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许访问的源
    allow_credentials=True,  # 支持 cookie
    allow_methods=["*"],  # 允许使用的请求方法
    allow_headers=["*"]  # 允许携带的 Headers
)


# 定时任务-给设备发送天气数据
def send_weather():
    logger.info(f'获取天气……')
    weather = tx_api.get_weather()
    logger.info(f'天气情况{weather}')
    for k, v in weather.items():
        for sq in [i['sq'] for i in iot_server.conns.values() if i['iot']]:
            sq.put(DataMsg(f'{k}_{v}'))


@iot_server.after_receive
def iot_registration(conn, data, s='Message from ESP32 and STM32', ):
    """
    设备认证，当收到的数据为’s‘时，认证设备，iot=True
    """
    sq = iot_server.conns[conn]['sq']
    try:
        data = data.decode('utf-8')
    except UnicodeDecodeError:
        logger.error('编码错误！')
        return
    if data.strip() == s:
        # 将连接放入已经认证的设备列表
        iot_server.conns[conn]['iot'] = True
        # 发送时间，表示认证成功
        sq.put(DataMsg(f'{time.strftime("%y-%m-%d %H-%M-%S", time.localtime())}', level=90))
        return True


@iot_server.after_receive
def save_data(conn, data):
    """
    数据入库
    """
    try:
        data = data.decode('utf-8')
    except UnicodeDecodeError:
        logger.error('编码错误！')
        return
    if ':' not in data:
        return

    def v2unit(value):
        for i in value.split(' '):
            if len(i.split('(')) == 1:
                yield i, False
            else:
                v, u = i.split('(')
                yield v, u[:-1]

    for i in data.split(';'):
        if i == '':
            continue
        k, v = i.split(':')
        for v, u in v2unit(v):
            logger.info(f'数据入库: {k}: {v} ({u})')
            db.save_data(k, v, u)


@api_server.api_route('/iot/list', methods=['post', 'get'])
def api_iot_list():
    """
    查看数据库里保存的数据都有什么数据类型（key）
    """
    return {'code': 200, 'msg': '成功', 'data': db.iot_list()}


@api_server.api_route('/iot/{name}', methods=['post', 'get'])
def api_iot_name(name):
    """
    必须参数：
    name(路径)：数据类型（key）
    返回：
    200：成功，数据类型（key）的全部数据（value）
    100：失败，数据类型（key）不存在
    """
    iot_list = db.iot_list()
    if name in iot_list:
        return {'code': 200, 'msg': '成功', 'data': {name: db.iot_name(name)}}
    else:
        return {'code': 100, 'msg': f'key “{name}” 不存在', 'data': {'name': iot_list}}


@api_server.api_route('/iot/{name}/unit', methods=['post', 'get'])
def api_iot_name_unit(name, unit=None):
    """
    必须参数：
    name(路径)：数据类型（key）
    可选参数：
    unit(参数体)：返回指定单位（unit）的数据类型（key）的全部数据（value）
    返回：
    200：成功，unit存在，返回指定单位（unit）的数据类型（key）的全部数据（value）
    201：成功，unit不存在，数据类型（key）的全部单位（unit）
    100：失败，数据类型（key）不存在
    101：失败，unit存在但错误
    """
    iot_list = db.iot_list()
    if name not in iot_list:
        return {'code': 100, 'msg': f'key “{name}” 不存在', 'data': {'name': iot_list}}
    iot_name_unit = db.iot_name_unit(name)
    if unit is None:
        return {'code': 201, 'msg': f'成功', 'data': {name: iot_name_unit}}
    elif unit in iot_name_unit:
        return {'code': 101, 'msg': f'unit “{unit}” 不存在', 'data': {name: iot_name_unit}}
    return {'code': 200, 'msg': '成功', 'data': {f'{name}({unit})': db.iot_name_unit(name, unit)}}


@api_server.api_route('/iot/command', methods=['post'])
def send_command(command):
    for i in [v['sq'] for v in iot_server.conns.values() if v['iot']]:
        i.put(CommandMsg(command))
    return {'code': 200, 'msg': '成功', 'data': []}


if __name__ == '__main__':
    # 单线程运行iot_server
    # iot_server.main()
    # 定时任务
    plan.add_job(send_weather, 'interval', seconds=1800)
    plan.start()
    # 多线程运行iot_server
    thread = threading.Thread(target=iot_server.run, name='IotServer_Main', daemon=True).start()

    # 运行api_server
    uvicorn.run(api_server, host='0.0.0.0', port=12588)
