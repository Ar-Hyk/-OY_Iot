# 日志
import logging
# 基础
import threading
import time
import os
# 定时
from apscheduler.schedulers.background import BackgroundScheduler
# Flask
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import and_
# 自编模块
from scr.iot_server import IotServer, DataMsg, CommandMsg
from scr.mysql_operation import DB as Sava_DB
from scr.tx_api import TX_API, t_st

# IOT
iot_server = IotServer()
# 天行api接口
tx_api = TX_API()
# 日志
logger = logging.getLogger('logger')
# 定时任务
plan = BackgroundScheduler(timezone='Asia/Shanghai')
# 数据入库
s_db = Sava_DB()

# API(flask初始化与设置)
api_server = Flask(__name__)
api_server.config[
    'SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://iot_admin:admin_iot@20.187.248.206:3306/iot?charset=utf8'
api_server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api_server.config['SQLALCHEMY_ECHO'] = True
CORS(api_server, supports_credentials=True)
# 数据库ORM模型与API绑定
db = SQLAlchemy(api_server)


# API密钥
# api_server.secret_key = "IOT-Test"


# 初始化 ORM模型
class IOT_ORM(db.Model):
    __tablename__ = 'data'
    t = db.Column(db.BigInteger, primary_key=True)
    key = db.Column(db.VARCHAR(20), primary_key=True)
    value = db.Column(db.DECIMAL(10, 2), primary_key=True)
    unit = db.Column(db.VARCHAR(20), primary_key=True)

    def __repr__(self):
        return f'<IOT_ORM {self.__dict__}>'


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
    if data.strip() == s:
        # 发送时间，表示认证成功
        sq.put(DataMsg(f'{t_st(time.time(), "%y-%m-%d %H-%M-%S")}', level=85))
        time.sleep(0.05)
        # 将连接iot属性设置为True,表示认证成功
        iot_server.conns[conn]['iot'] = True
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
        # 从value里分离出v与u
        for i in value.split(' '):
            vu = i.split('(')
            try:
                float(vu[0])
            except ValueError:
                logger.error('数据异常！' + '_'.join(vu))
                continue
            if len(vu) == 1:
                yield i, 'False'
            else:
                v, u = vu
                yield v, u[:-1]

    for i in data.split(';'):
        # 分离出单数据
        if i == '':
            continue
        k, v = i.split(':')
        for v, u in v2unit(v):
            logger.info(f'数据入库: {k}: {v} ({u})')
            s_db.save_data(k, v, u)


@api_server.route('/iot/list', methods=['post', 'get'])
def api_iot_list():
    """
    查看数据库里保存的数据都有什么数据类型（key）
    """
    datas = IOT_ORM.query.group_by(IOT_ORM.key).all()
    data = [i.key for i in datas]
    return jsonify({'code': 200, 'msg': '成功', 'data': data})


@api_server.route('/iot/<key>', methods=['post', 'get'])
def api_iot_key(key):
    """
    必须参数：
    key(路径)：数据类型（key）
    返回：
    200：成功，数据类型（key）的全部数据（value）
    100：失败，数据类型（key）不存在
    """
    datas = IOT_ORM.query.filter(IOT_ORM.key == key).limit(100).all()
    if datas:
        data = []
        for i in datas:
            cell = i.__dict__
            cell.pop('_sa_instance_state')
            data.append(cell)
        return jsonify({'code': 200, 'msg': '成功', 'data': data})
    datas = IOT_ORM.query.group_by(IOT_ORM.key).all()
    data = [i.key for i in datas]
    return jsonify({'code': 100, 'msg': f'key “{key}” 不存在', 'data': data})


@api_server.route('/iot/<key>/unit', methods=['post', 'get'])
def api_iot_key_unit(key):
    """
    必须参数：
    key(路径)：数据类型（key）
    可选参数：
    unit(参数体)：返回指定单位（unit）的数据类型（key）的全部数据（value）
    返回：
    200：成功，unit存在，返回指定单位（unit）的数据类型（key）的全部数据（value）
    201：成功，unit不存在，返回数据类型（key）的全部单位（unit）
    100：失败，数据类型（key）不存在
    101：失败，unit存在但错误
    """
    unit = request.args.get("unit")
    # 判断key存在
    datas = IOT_ORM.query.group_by(IOT_ORM.key).all()
    data = [i.key for i in datas]
    if key not in data: return jsonify({'code': 100, 'msg': f'key “{key}” 不存在', 'data': data})
    # 判断unit存在
    datas = IOT_ORM.query.filter(IOT_ORM.key == key).group_by(IOT_ORM.unit).all()
    data = [i.unit for i in datas]
    if unit is None: return jsonify({'code': 201, 'msg': f'成功，unit不存在', 'data': data})
    if unit not in data: return jsonify({'code': 101, 'msg': f'unit “{unit}” 不存在', 'data': data})
    # 返回数据
    datas = IOT_ORM.query.filter(and_(IOT_ORM.key == key, IOT_ORM.unit == unit)).limit(
        100).all()
    data = []
    for i in datas:
        cell = i.__dict__
        cell.pop('_sa_instance_state')
        data.append(cell)
    return jsonify({'code': 200, 'msg': '成功', 'info': f'{key}({unit})', 'data': data})


@api_server.route('/command', methods=['post', 'get'])
def send_command():
    command = request.args.get('command')
    for i in [v['sq'] for v in iot_server.conns.values() if v['iot']]:
        i.put(CommandMsg(command))
    return {'code': 200, 'msg': '成功', 'data': []}


@api_server.route('/query', methods=['post', 'get'])
def iot_query():
    """"""
    # 判断token
    token = request.args.get("token")
    if token is None: return {'code': 100, 'msg': 'token不存在', 'data': []}
    if token != 'iot_test': return {'code': 110, 'msg': 'token错误', 'data': []}
    # 判断num
    num = request.args.get("num")
    if num is None: num = 100
    try:
        num = int(num)
    except ValueError:
        return {'code': 104, 'msg': f'num 【{num}】无法转化为数字', 'data': []}
    # 初始化et
    et = request.args.get("et")
    if et is None: et = int(time.time())
    # 初始化st
    st = request.args.get("st")
    if st is None: st = int(et) - 3600
    # 判断st与et
    try:
        et = int(et)
    except ValueError:
        return {'code': 1031, 'msg': f'et 【{et}】无法转化为数字', 'data': []}
    try:
        st = int(st)
    except ValueError:
        return {'code': 1032, 'msg': f'st 【{st}】无法转化为数字', 'data': []}
    if st > et: return {'code': 1033, 'msg': f'st【{st}】不能大于et【{et}】', 'data': []}
    # 判断key
    key = request.args.get("key")
    if key is None: return {'code': 101, 'msg': 'key不存在', 'data': []}
    datas = IOT_ORM.query.group_by(IOT_ORM.key).all()
    data = [i.key for i in datas]
    if key not in data: return jsonify({'code': 1011, 'msg': f'key “{key}” 不存在', 'data': data})
    # 判断unit
    unit = request.args.get("unit")
    if unit is None: return {'code': 102, 'msg': 'unit不存在', 'data': []}
    datas = IOT_ORM.query.filter(IOT_ORM.key == key).group_by(IOT_ORM.unit).all()
    data = [i.unit for i in datas]
    if unit not in data: return jsonify({'code': 1021, 'msg': f'unit “{unit}” 不存在', 'data': data})

    datas = IOT_ORM.query.filter(
        and_(IOT_ORM.key == key, IOT_ORM.unit == unit, IOT_ORM.t < et * 10,
             IOT_ORM.t > st * 10)).order_by(-IOT_ORM.t).limit(num).all()
    if datas:
        t = [t_st(i.t // 10, "%H:%M:%S") for i in datas]
        value = [i.value for i in datas]
        t.reverse()
        value.reverse()
        return {
            'code': 200,
            'msg': '成功',
            'name': key,
            'unit': unit,
            'st': st,
            'st_str': t_st(st),
            'et': et,
            'et_str': t_st(et),
            'time': t,
            'value': value,
            'data': [{i.t: i.value} for i in datas]
        }
    return {
        'code': 201,
        'msg': '当前查询条件下无数据',
        'name': key,
        'unit': unit,
        'st': st,
        'st_str': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st)),
        'et': et,
        'et_str': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(et)),
        'time': [],
        'value': [],
        'data': datas
    }


@api_server.get('/')
def html_home():
    return render_template("index.html")


@api_server.get('/test')
def html_test():
    return render_template("test.html")


@api_server.get('/th')
def th():
    th = threading.enumerate()
    logger.debug(f'线程列表: 数量 {len(th)}')
    for k, v in enumerate(th):
        logger.debug(f'线程{k + 1} {v}')
    logger.debug('线程列表结束')
    return jsonify([i.name for i in th])


if __name__ == '__main__':
    # 单线程运行iot_server
    # iot_server.main()
    # 定时任务
    plan.add_job(send_weather, 'interval', seconds=1800)
    plan.start()
    # 多线程运行iot_server
    threading.Thread(target=iot_server.run, name='IotServer_Main', daemon=True).start()
    # 运行api_server
    # uvicorn.run(api_server, host='0.0.0.0', port=12588)
    # threading.Thread(target=api_server.run, name='ApiServer_Main', daemon=True).start()
    api_server.run(host='0.0.0.0', port=12588)
