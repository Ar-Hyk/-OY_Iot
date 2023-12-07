import socket
import threading
import time
from queue import PriorityQueue
from typing import Union

from scr.log import Logger


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
    def __init__(self, host: str = '0.0.0.0', port: int = 12580, log_dir: str = 'log/IotServer.log',
                 heartbeat_t: int = 5):
        # 日志设置
        self.logger = Logger(log_dir).logger
        # 服务端设置
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 声明socket类型面向连接,套接字家族为AF_INET
        self.heartbeat_t = heartbeat_t  # 心跳检查时间
        # 连接列表
        self.conns = {}
        # 收到消息后的处理函数列表
        self.after_receive_funcs = []
        self.logger.info('Receive初始化完成')

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
            r = False
            try:
                r = f(conn, data)
            except Exception as e:
                self.logger.warning('注册函数【{}】错误 {}:{} -- {}'.format(f.__name__, *self.conns[conn]['addr'], e))
            if r is True:
                return

    def receive(self, conn):
        addr = self.conns[conn]['addr']
        while True:
            try:
                data = conn.recv(2048)  # 接收数据
            except Exception as e:
                self.logger.error('接收错误 {}:{} -- {}'.format(*addr, e))
                self.logger.debug('服务器断开与 {}:{} 的连接'.format(*addr))
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
                self.conns.pop(conn)
                break
            if data != b'':  # 数据非空,客户端在线
                self.logger.debug('接收成功 {}:{} -- {}'.format(*addr, data))
                self.conns[conn]['t'] = time.time()
                # 消息处理
                self.process_receive(conn=conn, data=data)
                self.send(conn)
            else:  # 数据空,客户端离线
                self.logger.warning('连接断开 {}:{}'.format(*addr))
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
                self.conns.pop(conn)
                break

    def send(self, conn):
        sq = self.conns[conn]['sq']
        if not sq.empty():
            sendmsg = sq.get()
        else:
            sendmsg = DataMsg('OK')
        try:
            conn.send(sendmsg.msg)
            self.logger.info('发送成功 {}:{} -- {}'.format(*self.conns[conn]['addr'], sendmsg.msg))
        except Exception as e:
            self.logger.error('发送失败 {}:{} -- {}'.format(*self.conns[conn]['addr'], sendmsg.msg))
            self.logger.warning('连接断开 {}:{} -- {}'.format(*self.conns[conn]['addr'], e))
            self.conns.pop(conn)
            conn.shutdown(socket.SHUT_RDWR)
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
        self.logger.info(f'IotServer运行于: {self.host}:{self.port}')
        self.s.listen(10)  # 可以使5个链接排队
        # 开启监听线程
        threading.Thread(
            target=self.listen,
            name='IotServer_Listen',
            daemon=True
        ).start()

    def run(self):
        self.main()
        while True:
            try:
                t = threading.enumerate()
                self.logger.debug(f'线程列表: 数量 {len(t)}')
                for k, v in enumerate(t):
                    self.logger.debug(f'线程{k + 1} {v}')
                self.logger.debug('线程列表结束')

                conns = self.conns
                self.logger.info(f'连接检查: 数量 {len(conns)}')
                out_t = []
                for conn, v in conns.items():
                    addr = v['addr']
                    t = v['t']
                    sq = v['sq']
                    # # iot = v['iot']
                    if t + self.heartbeat_t * 2 <= time.time():
                        self.logger.warning(f'连接[{"{}:{}".format(*addr)}]: 存活超时！')
                        out_t.append(conn)
                    elif sq.qsize() > 10:
                        self.logger.warning(f'连接[{"{}:{}".format(*addr)}]: 消息队列异常！当前队列大小{sq.qsize()}')
                        if sq.qsize() > 20:
                            self.logger.error(f'连接[{"{}:{}".format(*addr)}]: 消息队列异常过大！清空队列！')
                            sq.clear()
                self.logger.info(f'连接检查完成: 死连接数量 {len(out_t)}')
                for conn in out_t:
                    addr = self.conns[conn]['addr']
                    self.logger.warning('开始清理 {}:{}'.format(*addr))
                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()
                    self.conns.pop(conn)
                    self.logger.warning('成功清理 {}:{}'.format(*addr))
                self.logger.info(f'连接检查完成: 存活连接数量 {len(self.conns)}')
            except Exception as e:
                self.logger.error(f'Main错误！{e}')
            time.sleep(self.heartbeat_t)


if __name__ == '__main__':
    server = IotServer(log_dir='../log/TestIotServer.log')
    server.run()
