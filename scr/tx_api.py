import time

# import requests
import pytz
import datetime


class TX_API:
    def __init__(self):
        self._url = 'http://apis.tianapi.com/'
        self._key = '0dac85a4dcd43b3d0f312badab9f1e3a'
        self.city = "桂林"

    def get_weather(self):
        api = 'tianqi/index'
        params = {
            "key": self._key,
            "city": "桂林",
            "type": "1"
        }
        response = requests.get(url=self._url + api, params=params).json()
        weather = {
            'weather': response['result']['weather'],
            'wind': response['result']['wind'],
            'windsc': response['result']['windsc']}
        return weather


def t_st(t: int, f="%Y-%m-%d %H:%M:%S"):
    tz = pytz.timezone('Asia/Shanghai')
    dt = datetime.datetime.fromtimestamp(t)
    l_dt = tz.localize(dt)
    return l_dt.strftime(f)


if __name__ == '__main__':
    # weather = TX_API().get_weather()
    # print(weather)
    # msg = f"D:weather_{weather['weather']};D:wind_{weather['wind']};D:windsc_{weather['windsc']};"
    # print(msg)
    t = int(time.time())
    print(time.time())
    print(t_st(t))
