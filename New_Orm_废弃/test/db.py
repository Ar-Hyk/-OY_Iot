import time

import pymysql


class DB:
    def __init__(self):
        # self.host = '127.0.0.1'  # 本地127.0.0.1
        self.host = '20.255.58.209'
        self.user = 'iot_admin'  # 用户名
        self.passwd = 'admin_iot'  # 密码
        self.port = 3306  # 默认为3306
        self.db = 'iot'  # 数据库名称
        self.charset = 'utf8'  # 字符编码
        self.conn = pymysql.connect(
            host=self.host,
            user=self.user,
            passwd=self.passwd,
            port=self.port,
            db=self.db,
            charset=self.charset
        )
        self.cur = self.conn.cursor()

    def save_data(self, t, k, v, unit=False):
        if not unit:
            sql = f"INSERT INTO `iot`.`iot_test` (`t`, `type`, `value`) VALUES ({t}, '{k}', '{v}')"
        else:
            sql = f"INSERT INTO `iot`.`iot_test` (`t`, `type`, `value`, `unit`) VALUES ({t}, '{k}', '{v}', {unit})"
        try:
            print(sql)
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f'保存错误！sql:{sql} E:{e}')

    def select(self):
        self.cur.execute('SELECT COUNT(iot_copy1.t) FROM iot_copy1')
        n = self.cur.fetchone()[0]
        self.cur.execute('SELECT * FROM `iot`.`iot_copy1`')
        for i in range(n):
            yield self.cur.fetchone()


def v2unit(value):
    for i in value.split(' '):
        if len(i.split('(')) == 1:
            yield i, False
        else:
            k, u = i.split('(')
            yield k, u[:-1]


if __name__ == '__main__':
    db1 = DB()
    # db2 = DB()
    for t, ty, v in db1.select():
        for k, u in v2unit(v):
            print(f't:{t}   type:{ty}   v:{k}   u:{u}')
            with open('data.txt', 'a', encoding='utf-8') as f:
                f.write(f'{t},{ty},{k},{u}\n')

            # db2.save_data(t, ty, k, u)
