from json import JSONDecodeError
import requests
from http.server import BaseHTTPRequestHandler
import json
import time


# 获取时间戳
def get_timestamp():
    return time.time()


def get_v1_movie(name):
    movie_page = requests.get("http://aliyun.k8aa.com/mogai_api.php/v1.comment?rid={0}&mid=1&page=1&limit=1".format(name))
    data = movie_page.text
    try:
        data = json.loads(data)
    except JSONDecodeError:
        data = None
    return data


def get_v2_movie(name):
    movie_page = requests.get("http://aliyun.k8aa.com:80/mogai_api.php/v1.vod/detail?vod_id={0}&rel_limit=1".format(name))
    data = movie_page.text
    try:
        data = json.loads(data)
    except JSONDecodeError:
        data = None
    return data


def getmovie(name):
    data = get_v1_movie(name)
    while not data:
        data = get_v1_movie(name)
    # 获取视频地址
    try:
        play_list = list(data['data']['list'][0]['data']['vod_play_list'].values())
    except IndexError as e:
        data = get_v2_movie(name)
        while not data:
            data = get_v2_movie(name)
        play_list = list(data['data']['vod_play_list'])
    return play_list


def read_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        _html = f.read()
    return _html


def index_html(url_list, begin_time):
    name_list = []
    url_final = []
    address_list = []
    for i in url_list:
        name = i['player_info']['show']
        address = i['player_info']['parse2']
        if address:
            address = address.replace('..', '.')
            address_list_temp = address.split(',')
            address_list_temp.insert(0, '请将下面的地址拼接起来使用\n')
            address_str = '\n'.join(address_list_temp)
        else:
            address_str = '本资源无特殊说明'
        name_list.append(name)
        address_list.append(address_str)
        url = i['urls']
        url_temp = []
        for i in url:
            try:
                name = url.get(i).get('name')
                _url = url.get(i).get('url')
            except:
                name = i.get('name')
                _url = i.get('url')
            url_temp.append(name+'<br>'+_url)
        url_temp = '\n'.join(url_temp)
        url_final.append(url_temp)
    html = read_file('./api/movie/list.html')
    print(name_list)
    for i in range(len(url_final)):
        n = i+1
        html = html.replace('{%s}' % n, name_list[i])
        html = html.replace('{%s_url}' % n, url_final[i])
        html = html.replace('{%s_address}' % n, address_list[i])
    # print(urls)
    final_time = get_timestamp()
    run_time = str(final_time - begin_time)
    print(run_time)
    html = html.replace('{time}', run_time)
    return html


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        begin_time = get_timestamp()
        path = self.path
        name = path.split('?')[1]
        data = str(index_html(getmovie(name), begin_time))
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(data.encode('utf-8'))
        return
