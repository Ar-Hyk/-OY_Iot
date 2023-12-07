import time
import logging
import pymysql
from pymysql import InterfaceError

LOGGER = logging.getLogger('logger')


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

    def __del__(self):
        LOGGER.info('已断开数据库链接')
        self.conn.close()
        self.cur.close()

    def execute_sql(self, sql):
        try:
            LOGGER.debug(f'sql: {sql}')
            self.cur.execute(sql)
        except InterfaceError:
            LOGGER.warning(f'连接过期，尝试重连……')
            try:
                self.cur.close()
                self.conn.ping(reconnect=True)
                self.cur = self.conn.cursor()
                LOGGER.info('重连成功')
                self.execute_sql(sql)
            except Exception as e:
                LOGGER.error(f'重连失败 {e}')
            else:
                try:
                    self.cur.execute(sql)
                except Exception as e:
                    LOGGER.error(f'sql错误 {sql} -- {e}')
                    self.up_cur(sql)
        except Exception as e:
            LOGGER.error(f'sql错误 {sql} -- {e}')
            self.up_cur(sql)

    def up_cur(self, sql):
        self.cur.close()
        LOGGER.warning('尝试获取新游标……')
        try:
            self.cur = self.conn.cursor()
        except Exception as e:
            self.conn.close()
            LOGGER.error(e)
            LOGGER.warning('获取新游标失败，尝试建立新连接……')
            try:
                self.conn = pymysql.connect(
                    host=self.host,
                    user=self.user,
                    passwd=self.passwd,
                    port=self.port,
                    db=self.db,
                    charset=self.charset
                )
            except Exception as e:
                LOGGER.error(e)
                raise e
            self.up_cur(sql)
        else:
            self.execute_sql(sql)

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
                self.cur.ping(reconnect=True)
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

    def iot_list(self) -> list:
        data = []
        sql = 'SELECT `key` FROM data GROUP BY `key`'
        self.execute_sql(sql)
        for i in self.cur.fetchall():
            data.append(*i)
        return data

    def iot_name(self, name):
        data = []
        sql = f"SELECT from_unixtime((`t` / 10 )) AS `stime`,`key`,`value`,`unit`,`t` FROM data WHERE `key` = '{name}' ORDER BY `t` DESC"
        self.execute_sql(sql)
        for i in self.cur.fetchall():
            data.append(zip(['st', 'key', 'value', 'unit', 't'], i))
        return data

    def iot_name_unit(self, name, unit=None):
        data = []
        if unit is None:
            # TODO：查询数据类型（key）的全部单位（unit）
            sql = f"SELECT data.unit FROM `data` WHERE `data`.`key` = '{name}' GROUP BY `data`.unit "
            self.execute_sql(sql)
            for i in self.cur.fetchall():
                data.append(*i)
        else:
            # TODO：查询指定单位（unit）的数据类型（key）的全部数据（value）
            sql = f"SELECT from_unixtime( t / 10 ) AS stime,  `data`.`key`,  `data`.`value`,  `data`.unit,  `data`.t FROM `data` WHERE `data`.`key` = '{name}' AND `data`.`unit`= '{unit}'"
            self.execute_sql(sql)
            for i in self.cur.fetchall():
                data.append(zip(['st', 'key', 'value', 'unit', 't'], i))
        return data


if __name__ == '__main__':
    db = DB()
