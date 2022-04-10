import requests
from requests.auth import HTTPProxyAuth
import time
import os
import glob
import validators
import sys


def format_proxy(proxy):
    proxy_format = dict.fromkeys(["ip", "username", "password"])
    p_list = proxy.split(":")
    if(len(p_list) != 4):
        return False
    proxy_format['ip'] = p_list[0] + ":" + p_list[1]
    proxy_format['username'] = p_list[2]
    proxy_format['password'] = p_list[3]
    return proxy_format


def ping_proxy(proxy_format, url):
    info_format = dict.fromkeys(["status", "code", "latency"])
    proxy_format = "http://{}:{}@{}".format(proxy_format['username'], proxy_format['password'], proxy_format['ip'])
    proxy = {
        'http': proxy_format,
        'https': proxy_format
    }

    try:
        start_time = time.time()
        res = requests.get(url, proxies=proxy, timeout=5)
        end_time = time.time()
        if res.status_code // 100 == 2:
            info_format['status'] = True
            info_format['latency'] = str(
                int(round((end_time - start_time), 2) * 1000)) + "ms"
        else:
            info_format['status'] = False
            info_format['latency'] = "none"
        info_format['code'] = res.status_code
        return info_format
    except requests.exceptions.RequestException:
        info_format['status'] = False
        info_format['code'] = "proxy error"
        info_format['latency'] = "none"
        return info_format


def read_proxy_to_lib(file_path, url):
    proxy_list = []
    proxy_file = open(file_path, "r")
    proxies = proxy_file.readlines()
    line_length = len(proxies)
    line_num = 0
    for proxy in proxies:
        if(line_num < line_length-1):
            cleaned_proxy = proxy[:-1]
            line_num += 1
        else:
            cleaned_proxy = proxy
        r = format_proxy(cleaned_proxy)
        if(r):
            proxy_info = dict.fromkeys(["proxy"])
            res = ping_proxy(r, url)
            proxy_info['proxy'] = cleaned_proxy
            proxy_info.update(res)
            proxy_list.append(proxy_info)
        else:
            return False
    return proxy_list


def shuffle_good_proxy(list, file_name):
    os.chdir("./shuffled")
    file = open("shuffled_"+file_name, "w")
    for proxy in list:
        if(proxy['status']):
            file.write(proxy['proxy'])
            file.write("\n")
    file.close()
    os.chdir("../")


def write_proxy_status(list, file_name):
    os.chdir("./status")
    file = open("status_"+file_name, "w")
    for proxy in list:
        file.write(proxy['proxy'])
        file.write("----")
        if(proxy['status']):
            file.write("good")
        else:
            file.write("bad")
            file.write("-error-code:" + str(proxy['code']))
        file.write("----")
        file.write(proxy['latency'])
        file.write("\n")
    file.close()
    os.chdir("../")


def main():
    folders = ["shuffled", "status"]
    for folder in folders:
        if not os.path.isdir(folder):
            os.mkdir(folder)
    proxy_files = glob.glob('*.txt')

    while True:
        url = str(input("Please Give An URL To Test:"))
        if not validators.url(url):
            print("Invalid URL! Please Try Again!\n")
            print("\n")
        else:
            print("\n")
            break

    while True:
        option = int(input(
            "Please Select An Option Below: \n 1. Test All Proxy Lists \n 2. Test A Specific Proxy List \n 3. Reset URL \n 4. Quit Application \n Your Option: \n"))
        if(option == 1):
            for proxy_file in proxy_files:
                proxy_list = read_proxy_to_lib(proxy_file, url)
                if proxy_list:
                    shuffle_good_proxy(proxy_list, proxy_file)
                    write_proxy_status(proxy_list, proxy_file)
                else:
                    print("Wrong Proxy List Format: "+proxy_file+"\n")
            print("\n")
            main()
        elif(option == 2):
            file_name=str(input("Please Enter The File Name With Suffix (For Example, file.txt): \n"))
            if(proxy_files.count(file_name)>0):
                proxy_list = read_proxy_to_lib(file_name, url)
                shuffle_good_proxy(proxy_list, file_name)
                write_proxy_status(proxy_list, file_name)
            else:
                print("File Does not Exist, Please Try Again! \n")
            print("\n")
            main()
        elif(option == 3):
            print("\n")
            main()
        elif(option == 4):
            print("\n")
            print("Successfully Quitted!\n")
            sys.exit(0)
        else:
            print("Invalid Input! Please Try Again!\n")
        print("\n")


if __name__ == '__main__':
    main()
# if __name__ == '__main__':
#     url = "http://www.google.com"
#     folders = ["shuffled", "status"]
#     for folder in folders:
#         if not os.path.isdir(folder):
#             os.mkdir(folder)
#     proxy_list = read_proxy_to_lib('good.txt', url)
#     print(proxy_list)
#     shuffle_good_proxy(proxy_list, 'good.txt')
#     write_proxy_status(proxy_list, 'good.txt')
