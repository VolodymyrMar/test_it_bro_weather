import requests
from bs4 import BeautifulSoup
import json
from google_api import make_weather_record
from datetime import datetime
import socket, time
from threading import Thread


socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_.bind(('localhost', 8080))
socket_.listen(5)

url_wikipedia = 'https://uk.wikipedia.org/wiki/%D0%9C%D1%96%D1%81%D1%82%D0%B0_%D0%A3%D0%BA%D1%80%D0%B0%D1%97%D0%BD%D0%B8_(%D0%B7%D0%B0_%D0%BD%D0%B0%D1%81%D0%B5%D0%BB%D0%B5%D0%BD%D0%BD%D1%8F%D0%BC)'
headers_wikipedia = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
                     }
token_gismeteo = {'X-Gismeteo-Token' : '605091efde0a99.85836198'}
url_gismeteo = 'https://api.gismeteo.net/v2/weather/current/'
city_id = 'https://api.gismeteo.net/v2/search/cities/?lang=ua&query='

type_precipitation = ('Нет осадков', 'Дождь', 'Снег', 'Смешанные осадки', 'За Вашим запитом нічого не знайдено ')

previous_result = {}


def listen_port():
    while True:
        time.sleep(5)
        (client_, address) = socket_.accept()
        data = client_.recv(2**9)
        if data.lower() == 'q':
            socket_.close()
            break

        print("RECEIVED: %s" % data)
        socket_.sendall(b'OK')
        if data.lower() == 'q':
            socket_.close()
            break

def get_html():
    response = requests.get(url_wikipedia, headers=headers_wikipedia)
    return response


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('center').find_all('table')[-2].find_all('tr')
    column = 0
    for tr in trs[1:]:
        link = tr.find('a')
        if link:
            city = link.get_text()
            current_weather = get_weather(city, headers=token_gismeteo)
            if current_weather != 4:
                column += 1
            if previous_result.get(city) != current_weather:
                make_weather_record(
                    column,
                    city=city,
                    precipitation=type_precipitation[current_weather],
                )
                previous_result[city] = current_weather


def parse():
    html = get_html()
    if html.status_code == 200:
        get_content(html.text)
    else:
        print(f'Status code {html.status_code}')
    delay_weather_update()


def get_id(city):
    response = requests.get(city_id + city, headers=token_gismeteo)
    if len(str(json.loads(response.text)['response']['items'])) > 2:
        return str(json.loads(response.text)['response']['items'][0]['id'])


def get_weather(city, url=url_gismeteo, headers=None):
    if get_id(city) is not None:
        request = requests.get(url+get_id(city), headers=headers)
        return json.loads(request.text)['response']['precipitation']['type']
    return 4


def delay_weather_update():
    current_time = datetime.now()
    while True:
        if (datetime.now() - current_time).seconds > 3 * 60 *60:
            parse()


if __name__ == '__main__':
    thread = Thread(target=listen_port)
    thread.daemon = True
    thread.start()
    parse()
