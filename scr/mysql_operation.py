import time
import logging
import pymysql
from pymysql import InterfaceError

LOGGER = logging.getLogger('logger')


class DB:
    def __init__(self):
        # self.host = '127.0.0.1'  # 本地127.0.0.1
        # self.host = '20.255.58.209'  # 旧
        # self.host = '159.75.73.107'  # test
        self.host = '20.187.248.206'  # 新
        self.user = 'iot_admin'  # 用户名
        self.passwd = 'admin_iot'  # 密码
        self.port = 3306  # 默认为3306
        self.db = 'iot'  # 数据库名称
        self.charset = 'utf8'  # 字符编码
        self.conn, self.cur = self.get_cur()

    def get_cur(self, conn=None, cur=None):
        if conn is not None:
            cur.close()
        if cur is not None:
            conn.close()
        conn = pymysql.connect(
            host=self.host,
            user=self.user,
            passwd=self.passwd,
            port=self.port,
            db=self.db,
            charset=self.charset
        )
        cur = conn.cursor()
        return conn, cur

    def save_data(self, k, v, u):
        t = int(time.time() * 10)
        sql = f"INSERT INTO `iot`.`data` (`t`, `key`, `value`, `unit`) VALUES ({t}, '{k}', {v}, '{u}')"
        try:
            self.cur.execute(sql)
            self.conn.commit()
            LOGGER.info('保存成功！')
        except InterfaceError:
            LOGGER.warning('连接过期，尝试重连……')
            try:
                self.conn, self.cur = self.get_cur()
                LOGGER.info('重连成功')
            except Exception as e:
                LOGGER.error(f'重连失败 {e}')
            else:
                try:
                    self.cur.execute(sql)
                    self.conn.commit()
                    LOGGER.info('保存成功！')
                except Exception as e:
                    LOGGER.error(f'保存失败 {sql} -- {e}')
        except Exception as e:
            LOGGER.error(f'保存失败 {sql} -- {e}')


if __name__ == '__main__':
    db = DB()
