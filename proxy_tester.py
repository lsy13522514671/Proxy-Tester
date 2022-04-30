import requests
import time
import os
import glob
import validators
import sys
import concurrent.futures

# PREQUISITE
# needs to have python 3 installed
# needs to install the above modules to run the program to run the program, to install the modules run: pip install requests validators 

# HOW TO RUN:
# write your proxy lists as text files, e.g, proxy_list_name_1.txt, proxy_list_name_2.txt, my_proxy.txt, and etc.
# a proxy in a file should be in the following format: host:port:username:password
# simply enter: python proxy_tester.py
# proxy will be shuffled and output as text files (one for each proxy list you enterred) in shuffled folder
# proxy status will be recorded and output as a text file (one for each proxy list you enterred) in shuffled folder
# IF YOU DO NOT SEE AN EXPECTED OUTPUT PROXY LIST, CHECK THE CORRESPOND INPUT FILE!(THE RESON IS THAT IT CONTAINS A PROXY WITH WRONG FORMAT)

def format_proxy(proxy):
    """
    formats a proxy, which is a text line, into a dictionary 
    with the following key: 
    1. ip(host:port)
    2. username
    3. password
    if the given proxy is in wrong format, returns false
    """
    proxy_format = dict.fromkeys(["ip", "username", "password"])
    p_list = proxy.split(":")
    if(len(p_list) != 4):
        return False
    proxy_format['ip'] = p_list[0] + ":" + p_list[1]
    proxy_format['username'] = p_list[2]
    proxy_format['password'] = p_list[3]
    return proxy_format

def ping_proxy(proxy_format, url):
    """
    uses a formatted proxy to send request to a given url
    there are three situations in general: 
       success (with success status code 200)
       failure (with a response: with error status code, e.g. 407 as below)
       failure (with an error: a serious problem occurs)
    returns a response information correspond to the proxy:
    1. status(a boolean value)
    2. code(success code 2xx, or error code (e.g. 407: authentication fail), or a proxy error(a serious problem: e.g., proxy error)),
    3. latency (specific value in ms: if the proxy works on that url, or none if an error occurs)
    """
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

def ping_one_proxy(proxy, url):
    """
    created for the multi-processing. The function takes one proxy, and a testing url.
    It first checks the proxy format.
    If the format is correct, it pings the proxy. Otherwise, it returns a proxy information
    format as the ping_proxy, except the error code is "wrong format".
    """
    cleaned_proxy = proxy.rstrip('\n')
    r = format_proxy(cleaned_proxy)
    proxy_info = dict.fromkeys(["proxy"])
    if cleaned_proxy == "" or cleaned_proxy.isspace():
        proxy_info['proxy'] = "empty line"
    else:
        proxy_info['proxy'] = cleaned_proxy
    if r!=False:
        res = ping_proxy(r, url)
        proxy_info.update(res)
    else:
        proxy_info['status'] = False
        proxy_info['code'] = "wrong format"
        proxy_info['latency'] = "none"
    return proxy_info

def read_proxy_to_lib(file_path, url):
    """
    uses 50 threads to reads all proxy to a list in the format of a dictionary with keys:
    1. proxy: the actual proxy informat of: host:port:username:password
    2. status(a boolean value)
    3. code(success code 2xx, or error code (e.g. 407: authentication fail), or a proxy error(a serious problem: e.g., proxy error)),
    4. latency (specific value in ms: if the proxy works on that url, or none if an error occurs)
    if the proxy format is wrong, stops reading process
    """
    proxy_file = open(file_path, "r")
    proxies = proxy_file.readlines()
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        proxy_list = list(executor.map(lambda proxy: ping_one_proxy(proxy, url), proxies))
    return proxy_list

def shuffle_good_proxy(list, file_name):
    """
    shuffles the good proxy (only keeps proxies with good status)
    writes them to a file under the shuffled folder
    the file name is shuffle_file_name.txt
    """
    os.chdir("./shuffled")
    file = open("shuffled_"+file_name, "w")
    for proxy in list:
        if(proxy['status']):
            file.write(proxy['proxy'])
            file.write("\n")
    file.close()
    os.chdir("../")

def write_proxy_status(list, file_name):
    """
    retrieves status for every proxy
    writes them to a file under the status folder
    the format is ip(host:port:username:password)----status(good or bd):error code----latency(in ms or none if error occurs)
    the file name is status_file_name.txt
    """
    os.chdir("./status")
    file = open("status_"+file_name, "w")
    for proxy in list:
        file.write(proxy['proxy'])
        file.write("----")
        if(proxy['status']):
            file.write("good")
        else:
            file.write("bad:")
            file.write(str(proxy['code']))
        file.write("----")
        file.write(proxy['latency'])
        file.write("\n")
    file.close()
    os.chdir("../")

def main():
    """
    the main function that infinitely asks for input
    """
    folders = ["shuffled", "status"]
    for folder in folders:
        if not os.path.isdir(folder):
            os.mkdir(folder)
    proxy_files = glob.glob('*.txt')

    while True:
        url = str(input("Enter q To Quit Or Please Give An URL To Test: \n"))
        if url=="q":
            print("\n")
            print("Successfully Quitted!\n")
            sys.exit(0)
        elif not validators.url(url):
            print("Invalid URL! Please Try Again!\n")
            print("\n")
        else:
            print("\n")
            break

    while True:
        option = int(input(
            "Please Select An Option Below: \n 1. Test All Proxy Lists \n 2. Test A Specific Proxy List \n 3. Reset URL \n 4. Quit Application \n Your Option: \n"))
        # tests all proxy lists: shuffles each proxy list, and retrieves proxy status for every proxy
        # if the reading process fail (a wrong proxy format is detected), prints the error file name
        if(option == 1):
            for proxy_file in proxy_files:
                proxy_list = read_proxy_to_lib(proxy_file, url)
                shuffle_good_proxy(proxy_list, proxy_file)
                write_proxy_status(proxy_list, proxy_file)
            print("\n")
            main()
        # tests a specified proxy lists: shuffles each proxy list, and retrieves proxy status for every proxy
        # a name must include the suffix
        # if the reading process fail (a wrong proxy format is detected), prints the error file name
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
        # resets the URL and repeat the process
        elif(option == 3):
            print("\n")
            main()
        # quits the tester application
        elif(option == 4):
            print("\n")
            print("Successfully Quitted!\n")
            sys.exit(0)
        # invalid input
        else:
            print("Invalid Input! Please Try Again!\n")
        print("\n")


if __name__ == '__main__':
    main()
