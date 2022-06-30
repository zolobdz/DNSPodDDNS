# -*- coding:utf-8 -*-

import os
from typing import Optional
import requests
import json

domain = ''  # your domain, for instance: 'google.com'
login_token = '181628,d59e134fbc1a89a61ee8512daaacda8a' # "ID,Token"; see https://docs.dnspod.cn/account/dnspod-token/

#  Core Function  #

new_ip = ''  # notice: don't fill this var

def record_list() -> []:
    url = 'https://dnsapi.cn/Record.List'
    data = {'domain': domain, 'login_token': login_token}
    res = requests.post(url=url, data=data)
    data = json.loads(res.content.decode('utf-8'))
    if 'records' in data:
        list = data['records']
        count = len(list)
        text = 'records' if (count > 1) else 'record'
        print(len(list), text)
        formatPrint(list)
        return list
    else:
        # print('none')
        return None

    # print(data['domain']['name'])


def record_create(sub_domain):
    url = 'https://dnsapi.cn/Record.Create'
    param = {'login_token': login_token, 'domain': domain, "sub_domain": sub_domain, "record_type": "A",
             "record_line": "默认", 'record_line_id': '10=0', "value": new_ip, "ttl": 600, 'format': 'json'}
    res = requests.post(url=url, data=param)
    data = json.loads(res.content.decode('utf-8'))
    formatPrint(data)
    return


def record_create_bacth():
    record_create('*')
    record_create('@')
    record_create('www')


def record_delete(id):
    url = 'https://dnsapi.cn/Record.Remove'
    data = {'record_id': id, 'domain': domain, 'login_token': login_token}
    res = requests.post(url=url, data=data)
    data = json.loads(res.content.decode('utf-8'))
    formatPrint(data)
    return


def record_modify(record_id):
    url = 'https://dnsapi.cn/Batch.Record.Modify'
    data = {'record_id': record_id, 'change': 'value', 'change_to': new_ip, 'format': 'json',
            'login_token': login_token}
    print(data)
    res = requests.post(url=url, data=data)
    data = json.loads(res.content.decode('utf-8'))
    formatPrint(data)
    return


def formatPrint(data):
    y = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
    print(y)


def get_new_ip() -> Optional[str]:
    out = os.popen("ifconfig").read()
    a = out.split('\n')
    has = False
    for line in a:
        if has:
            print(line)
            res = line.split()[1][5:]
            # print(res)
            return res
        if 'pppoe' in line:
            # print(line)
            has = True
    return None

def main_operation():
    # 获取最新ip
    global new_ip
    new_ip = get_new_ip()
    if new_ip is None:
        print('ip is missing, please check your network')
        return
    print('new ip is:', new_ip)
    # 查询
    records = record_list()
    # 如果为空 -> 新增
    if records is None:
        print('no records, creating...')
        record_create_bacth()
    # 如果不为空 -> 批量修改
    if records is not None:
        current_ip = records[0]['value']
        print('old ip is:', current_ip)
        #   如果ip相同 -> return
        #   如果ip不相同 -> 修改
        if current_ip != new_ip:
            print('updating your DDNS...')
            record_ids = ','.join([dict.get('id') for dict in records])
            record_modify(record_ids)
            print('your DDNS is updated')
        else:
            print('your DDNS is the newest version')

main_operation()

