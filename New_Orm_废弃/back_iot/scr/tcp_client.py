import socket

host = '127.0.0.1'
port = 12580
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 声明socket类型面向连接，套接字家族为AF_INET
try:
    s.connect((host, port))
except Exception as e:
    print('服务端不存在！')
    # sys.exit()
    s.connect((host, port))
while True:
    conn = input('you say：')
    print(f'确认{conn}')
    s.send(conn.encode('utf-8'))  # 发送信息你叫什么名字？
    data = s.recv(2048)  # 接受数据并指定大小为2048字节
    data = data.decode()  # 解码接受的数据
    print('接受到的数据：', data, '\n')
    if conn.lower == "再见":  # 如果最后输入再见，表示会话结束！
        break
s.close()  # 会话关闭
