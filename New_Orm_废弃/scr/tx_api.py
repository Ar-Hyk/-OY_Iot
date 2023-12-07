import requests
import os


class TX_API:
    def __init__(self):
        self._url = 'http://apis.tianapi.com/'
        self._key = os.getenv('TX_KEY')
        self.city = os.getenv('CITY')

    def get_weather(self):
        api = 'tianqi/index'
        params = {
            "key": self._key,
            "city": self.city,
            "type": 1
        }
        print(params)
        response = requests.get(url=self._url + api, params=params).json()
        print(response)
        weather = {
            'weather': response['result']['weather'],
            'wind': response['result']['wind'],
            'windsc': response['result']['windsc']}
        return weather


if __name__ == '__main__':
    from dotenv import load_dotenv

    load_dotenv(override=True)
    weather = TX_API().get_weather()
    print(weather)
    msg = f"D:weather_{weather['weather']};D:wind_{weather['wind']};D:windsc_{weather['windsc']};"
    print(msg)
