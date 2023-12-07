from fastapi import FastAPI
from scr.app import view
from fastapi.middleware.cors import CORSMiddleware

# api_server
api_server = FastAPI()
api_server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许访问的源
    allow_credentials=True,  # 支持 cookie
    allow_methods=["*"],  # 允许使用的请求方法
    allow_headers=["*"]  # 允许携带的 Headers
)
api_server.include_router(view)


# API接口
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
        return {'code': 200, 'msg': '成功', 'data': {f'{name}({unit})': db.iot_name_unit(name, unit)}}
    return {'code': 101, 'msg': f'unit “{unit}” 不存在', 'data': {name: iot_name_unit}}


@api_server.api_route('/iot/command', methods=['post'])
def send_command(command):
    for i in [v['sq'] for v in iot_server.conns.values() if v['iot']]:
        i.put(CommandMsg(command))
    return {'code': 200, 'msg': '成功', 'data': []}
