import socket
import threading
import time
from queue import PriorityQueue
from typing import Union

from scr.log import Logger


class SendMsg:
    """
    消息体
    """

    def __init__(self, conn: socket.socket, msg: Union[bytes, str]):
        """
        conn:socket连接套接字
        msg:需要发送的消息
        """
        self.conn = conn
        if type(msg) is str:
            self.msg = msg.encode('utf-8')
        else:
            self.msg = msg


class IotServer:
    def __init__(self, host: str = '0.0.0.0', port: int = 12580, log_dir: str = 'log/IotServer.log',
                 heartbeat_t: int = 10):
        # 日志设置
        self.logger = Logger(log_dir).logger
        # 服务端设置
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 声明socket类型面向连接,套接字家族为AF_INET
        self.s.bind((self.host, self.port))  # 绑定地址和端口
        self.s.listen(5)  # 可以使5个链接排队
        self.heartbeat_t = heartbeat_t  # 心跳检查时间

        # 连接列表iot_server.py
        self.conns = []
        # 设备列表
        self.equipment = []
        # 发送消息队列
        self.send_queues = PriorityQueue(10)

        # 收到消息后的处理函数列表
        self.after_receive_funcs = []

        self.logger.debug('Receive初始化完成')
        self.logger.info(f'运行于：{self.host}:{self.port}')

    def after_receive(self, func):
        """
        装饰器：将函数注册为消息处理函数
        """
        self.after_receive_funcs.append(func)
        return func

    def process_receive(self, **kwargs):
        """
        按顺序执行每个注册的消息处理函数,如果消息处理函数存在返回值则终止后续处理函数
        """
        for f in self.after_receive_funcs:
            r = f(**kwargs)
            if r is True:
                return r

    def receive(self, conn):
        while True:
            try:
                data = conn.recv(2048)  # 接收数据
            except Exception as e:
                self.logger.error(e)
                self.conns.remove(conn)
                self.equipment.remove(conn)
                conn.close()
                break
            if data != b'':  # 数据非空,客户端在线
                self.logger.debug('接收{}:{} - {}'.format(*conn.getpeername(), data))
                # 消息处理
                self.process_receive(conn=conn, data=data)
            else:  # 数据空,客户端离线
                self.logger.warning('与 {}:{} 连接断开！'.format(*conn.getpeername()))
                self.conns.remove(conn)
                self.equipment.remove(conn)
                conn.close()
                break

    def send(self, conn=None):
        if not self.send_queues.empty():
            sendmsg = self.send_queues.get()[2]
        else:
            sendmsg = SendMsg(conn, 'D:OK')
        try:
            sendmsg.conn.send(sendmsg.msg)
            self.logger.debug('发送{}:{} - {}'.format(*sendmsg.conn.getpeername(), sendmsg.msg))
        except Exception as e:
            print(type(e))
            self.logger.error(e)
            self.conns.remove(sendmsg.conn)
            self.equipment.remove(sendmsg.conn)
            sendmsg.conn.close()

    def listen(self):
        while True:
            conn, addr = self.s.accept()
            self.logger.info('与 {}:{} 连接成功！'.format(*addr))  # conn是客户端链接过来,在服务器端生成一个链接实例
            self.conns.append(conn)
            thread = threading.Thread(target=self.receive, args=(conn,), name='IotServer_Conn_{}:{}'.format(*addr))
            thread.setDaemon(True)
            thread.start()

    def main(self):
        # 开启监听线程
        thread = threading.Thread(target=self.listen, name='IotServer_Listen')
        thread.setDaemon(True)
        thread.start()
        # 开启发送线程
        # thread = threading.Thread(target=self.send, name='IotServer_Send')
        # thread.setDaemon(True)
        # thread.start()

    def heartbeat(self):
        for i in self.conns:
            self.send_queues.put(SendMsg(i, b'D:heartbeat'))

    def run(self):
        self.main()
        while True:
            t = threading.enumerate()
            print(f'当前线程数量：{len(t)}')
            for i in t:
                print(i)
            print('检查连接存存活……')
            self.heartbeat()
            print('========================')
            time.sleep(self.heartbeat_t)


if __name__ == '__main__':
    server = IotServer(log_dir='../log/ReceiveServer.log')
    server.run()
