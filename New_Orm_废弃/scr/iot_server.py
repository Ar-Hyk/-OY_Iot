import logging
import socket
import threading
import time
from queue import PriorityQueue
from typing import Union
import os


class BasicMsg:
    """
    基础消息体
    """

    def __init__(self, msg: Union[bytes, str], level: int = 100, t=time.time()):
        """
        conn:socket连接套接字
        msg:需要发送的消息
        """
        self.level = level
        self.t = t
        if type(msg) is str:
            self.msg = msg.encode('utf-8') + b';'
        else:
            self.msg = msg + b';'

    def __lt__(self, other):
        if self.level < other.level:
            return True
        if self.level > other.level:
            return False
        else:
            return self.t < other.t


class DataMsg(BasicMsg):
    """
    数据消息体
    """

    def __init__(self, msg: Union[bytes, str], level=90):
        super().__init__(msg, level)
        self.msg = b'D:' + self.msg


class CommandMsg(BasicMsg):
    """
    命令消息体
    """

    def __init__(self, msg: Union[bytes, str], level=80):
        super().__init__(msg, level)
        self.msg = b'C:' + self.msg


class IotServer:
    def __init__(self):
        # 日志设置
        self.logger = logging.getLogger()
        # 服务端设置
        self.host = os.getenv('IOT_HOST')
        self.port = int(os.getenv('IOT_PORT'))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 声明socket类型面向连接,套接字家族为AF_INET
        self.heartbeat_t = int(os.getenv('IOT_HEARTBEAT'))  # 心跳检查时间
        # 连接列表
        self.conns = {}
        # 收到消息后的处理函数列表
        self.after_receive_funcs = []
        self.logger.info('IotServer初始化完成')

    def after_receive(self, func):
        """
        装饰器：将函数注册为消息处理函数
        """
        self.after_receive_funcs.append(func)

    def process_receive(self, conn, data):
        """
        按顺序执行每个注册的消息处理函数,如果消息处理函数存在返回值则终止后续处理函数
        """
        for f in self.after_receive_funcs:
            r = f(conn, data)
            if r is True:
                return r

    def receive(self, conn):
        while True:
            try:
                data = conn.recv(2048)  # 接收数据
            except Exception as e:
                self.logger.error('接收错误 {}:{} -- {}'.format(*self.conns[conn]['addr'], e))
                del self.conns[conn]
                conn.close()
                break
            if data != b'':  # 数据非空,客户端在线
                self.logger.debug('接收成功 {}:{} -- {}'.format(*conn.getpeername(), data))
                self.conns[conn]['t'] = time.time()
                # 消息处理
                self.process_receive(conn=conn, data=data)
                self.send(conn)
            else:  # 数据空,客户端离线
                self.logger.warning('连接断开 {}:{}'.format(*self.conns[conn]['addr']))
                del self.conns[conn]
                conn.close()
                break

    def send(self, conn):
        q = self.conns[conn]['sq']
        if not q.empty():
            sendmsg = q.get()
        else:
            sendmsg = DataMsg('OK')
        try:
            conn.send(sendmsg.msg)
            self.logger.info('发送成功 {}:{} -- {}'.format(*self.conns[conn]['addr'], sendmsg.msg))
        except Exception as e:
            self.logger.error('发送失败 {}:{} -- {}'.format(*self.conns[conn]['addr'], sendmsg.msg))
            self.logger.warning('连接断开 {}:{} -- {}'.format(*self.conns[conn]['addr'], e))
            del self.conns[conn]
            conn.close()

    def listen(self):
        while True:
            conn, addr = self.s.accept()
            self.logger.info('与 {}:{} 连接成功！'.format(*addr))  # conn是客户端链接过来,在服务器端生成一个链接实例
            self.conns[conn] = {
                'addr': addr,
                'sq': PriorityQueue(),
                't': time.time(),
                'iot': False
            }
            threading.Thread(
                target=self.receive,
                kwargs={'conn': conn},
                name='IotServer_Receive_{}:{}'.format(*addr),
                daemon=True
            ).start()

    def main(self):
        self.s.bind((self.host, self.port))  # 绑定地址和端口
        self.s.listen(5)  # 可以使5个链接排队
        self.logger.info(f'IotServer运行于: {self.host}:{self.port}')
        # 开启监听线程
        threading.Thread(
            target=self.listen,
            name='IotServer_Listen',
            daemon=True
        ).start()

    def run(self):
        self.main()
        while True:
            t = threading.enumerate()
            self.logger.debug(f'线程列表: 数量 {len(t)}')
            for k, v in enumerate(t):
                self.logger.debug(f'线程{k + 1} {v}')
            self.logger.debug('线程列表结束')

            self.logger.info(f'连接检查: 数量 {len(self.conns)}')
            for conn, v in self.conns.items():
                addr = v['addr']
                t = v['t']
                sq = v['sq']
                # iot = v['iot']
                if t + self.heartbeat_t <= time.time():
                    self.logger.warning(f'连接[{"{}:{}".format(*addr)}]: 存活超时！')
                    self.logger.info(f'连接[{"{}:{}".format(*addr)}]: 存活检查……')
                    self.send(conn)
                elif sq.qsize() > 10:
                    self.logger.warning(f'连接[{"{}:{}".format(*addr)}]: 消息队列异常！当前队列大小{sq.qsize()}')
                    if sq.qsize() > 20:
                        self.logger.error(f'连接[{"{}:{}".format(*addr)}]: 消息队列异常过大！清空队列！')
                        sq.clear()
                self.logger.info(f'连接[{"{}:{}".format(*addr)}]: 状态正常！')
            self.logger.info(f'连接检查完成: 存活连接数量 {len(self.conns)}')
            time.sleep(self.heartbeat_t)


if __name__ == '__main__':
    from dotenv import load_dotenv

    load_dotenv(override=True)
    from scr.log import logger

    server = IotServer()

    server.run()
