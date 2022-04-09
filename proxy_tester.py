from urllib import response
import requests
import asyncio
from requests.auth import HTTPProxyAuth

# proxy_file = open('proxy.txt', 'r')
# proxies = proxy_file.readlines()
# proxy_dic = {}

url = "http://www.google.com"


def ping():
    proxy = {
        'http': '207.202.130.186:5696',
        'https': '207.202.130.186:5696'
    }

    auth = HTTPProxyAuth('Na2wCBfHX0', '3Kofo4VRwr')
    try:
        res = requests.get(url, proxies=proxy, auth=auth, timeout=5)
        if res.status_code //100 == 2:
            print("good status: ", res.status_code)
        else:
            print("error with code: ", res.status_code)
    except requests.exceptions.RequestException:
        print("proxy error")

ping()
