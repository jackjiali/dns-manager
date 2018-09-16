import logging
import time
import subprocess
import os
import signal
import sys
import etcd
from flask import current_app
import requests
import json
import copy
from datetime import datetime
from collections import OrderedDict
from flask_restful import Api, Resource, url_for, reqparse, abort, marshal_with, fields, marshal
from .request_code import RequestCode


ZONE_GROUP_MAPPING = {
    0:"外部域名",
    1:"内部域名",
    2:"劫持域名"
}


#获取ETCD客户端
def getETCDclient():
    client = etcd.Client(
        host=current_app.config.get('ETCD_SERVER_HOST'), 
        port=int(current_app.config.get('ETCD_SERVER_PORT'))
        )
    return client


def getLogger(log_path):
    # logger初始化
    logger = logging.getLogger('DNS')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_path)
    formatter = logging.Formatter(
                '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def killProcesses(ppid=None):
    ppid = str(ppid)
    pidgrp = []
    def GetChildPids(ppid):
        command = "ps -ef | awk '{if ($3 ==%s) print $2;}'" % str(ppid)
        pids = os.popen(command).read()
        pids = pids.split()
        return pids
    pidgrp.extend(GetChildPids(ppid))
    for pid in pidgrp:
        pidgrp.extend(GetChildPids(pid))

    pidgrp.insert(0, ppid)
    while len(pidgrp) > 0:
        pid = pidgrp.pop()
        try:
            os.kill(int(pid), signal.SIGKILL)
            return True
        except OSError:
            try:
                os.popen("kill -9 %d" % int(pid))
                return True
            except Exception:
                return False


DEFAULT_CMD_TIMEOUT = 1200
def doCMDWithOutput(cmd, time_out = None):
    if time_out is None:
        time_out = DEFAULT_CMD_TIMEOUT
    # LOG.info("Doing CMD: [ %s ]" % cmd)
    pre_time = time.time()
    output = []
    cmd_return_code = 1
    cmd_proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, shell=True)
    while True:
        output_line = cmd_proc.stdout.readline().decode().strip("\r\n")
        cmd_return_code = cmd_proc.poll()
        elapsed_time = time.time() - pre_time
        if cmd_return_code is None:
            if elapsed_time >= time_out:
                killProcesses(ppid=cmd_proc.pid)
                return False
        elif output_line == '' and cmd_return_code is not None:
            break
        sys.stdout.flush()
        if output_line.strip() != '':
            output.append(output_line)
    return (cmd_return_code, output)


def get_response(code, msg, data=None):
    return {
        'code': code,
        'msg': msg,
        'data': data
    }


def get_response_wrapper_fields(f):
    return {
        'code': fields.Integer,
        'data': f,
        'msg': fields.String
    }


# def initServer(cmd, app_object, server_id):
#     with app_object.app_context():
#         # print(server_id)
#         current_server = DBDNSServer.query.get(int(server_id))
#         res = doCMDWithOutput(cmd)
#         if not res:
#             current_server.status = '初始化失败'
#             current_server.logs = '超时！！初始化时间已超过20分钟'
#             db.session.add(current_server)
#             db.session.commit()
#             return False, ['超时！！初始化时间已超过20分钟！']
#         cmd_return_code, output = res
#         if cmd_return_code != 0:
#             print('\n'.join(output))
#             current_server.status = '初始化失败'
#             current_server.logs = '\n'.join(output)
#             db.session.add(current_server)
#             db.session.commit()
#             return False, output
#         else:
#             print('\n'.join(output))
#             current_server.status = 'ONLINE'
#             current_server.logs = '\n'.join(output)
#             db.session.add(current_server)
#             db.session.commit()
#             return True, output


class DNSPod(object):
    @staticmethod
    def getDNSPodLines(domain):
        body_info = {
            "login_token": current_app.config.get('DNSPOD_TOKEN'), 
            "format": current_app.config.get('DNSPOD_DATA_FORMAT'), 
            "domain": domain
            }
        try:
            res = requests.post(
                current_app.config.get('DNSPOD_LINE_URL'),
                data=body_info
                )
        except Exception as e:
            return []
        if res.status_code >= 200 and res.status_code <= 220:
            return res.json()['lines']
        return []

    @staticmethod
    def getDNSPodTypes(domain):
        body_info = {
            "login_token": current_app.config.get('DNSPOD_TOKEN'), 
            "format": current_app.config.get('DNSPOD_DATA_FORMAT'), 
            "domain": domain
            }
        try:
            res = requests.post(
                current_app.config.get('DNSPOD_TYPE_URL'), 
                data=body_info
                )
        except Exception as e:
            return []
        if res.status_code >= 200 and res.status_code <= 220:
            return res.json()['lines']
        return []


class ZBapi(object):
    def __init__(self, server):
        self._url = current_app.config.get('ZABBIX_URL')
        self._header = {"Content-Type":"application/json"}
        self._server = server
        self._num = 30

    def _get_authid(self):
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": current_app.config.get('ZABBIX_USERNAME'),
                "password": current_app.config.get('ZABBIX_PASSWORD')
            },
            "id": 1,
            "auth":None
        }
        try:
            r = requests.post(self._url, 
                    data=json.dumps(data), headers=self._header, timeout=10)
        except Exception as e:
            raise e
        authid = json.loads(r.text).get("result")
        return authid

    def _configure_post_data(self, zb_post_data, itemid, history):
        zb_post_data['auth'] = self._get_authid()
        zb_post_data['params']['itemids'] = itemid
        zb_post_data['params']['history'] = history
        return zb_post_data

    def _get_server_status_by_itemid(self, itemid):
        zb_data_default = copy.deepcopy(
                        current_app.config.get('ZABBIX_POST_DATA'))
        zb_post_data = self._configure_post_data(zb_data_default, itemid, 3)
        try:
            r = requests.post(self._url, 
                    data=json.dumps(zb_post_data), 
                    headers=self._header, timeout=10)
        except Exception as e:
            raise e
        result = json.loads(r.text).get("result")
        if result:
            return result[0].get('value')
        return '0'

    def _get_resolve_rate_by_itemid(self, itemid, limit_num):
        time_slot_minutes = int(limit_num/self._num)
        # all_num = time_slot_minutes * (self._num + 1)
        zb_data_default = copy.deepcopy(current_app.config.get('ZABBIX_POST_DATA'))
        zb_post_data = self._configure_post_data(zb_data_default, itemid, 3)
        zb_post_data['params']['limit'] = limit_num
        try:
            r = requests.post(self._url, 
                    data=json.dumps(zb_post_data), 
                    headers=self._header, timeout=10)
        except Exception as e:
            raise e
        results = json.loads(r.text).get("result")
        results_dct = OrderedDict()
        for i in range(self._num):
            end = time_slot_minutes*(i+1)
            resolving_slot = results[time_slot_minutes*i : end]
            time_flag = results[time_slot_minutes*i]['clock']
            time_flag_str = datetime.fromtimestamp(int(time_flag)).strftime("%m-%d %H:%M")
            resolving_slot_amount = 0
            for ss in resolving_slot:
                resolving_slot_amount += int(ss['value'])
            results_dct[time_flag_str] = resolving_slot_amount
        return {'name':self._server.host, 'data':results_dct}

    def get_server_status(self):
        return {'process':self._get_server_status_by_itemid(self._server.zb_process_itemid),
                'port':self._get_server_status_by_itemid(self._server.zb_port_itemid),
                'resolve':self._get_server_status_by_itemid(self._server.zb_resolve_itemid)}

    def get_resolve_rate(self, start_time, end_time):
        # time_slot = (end_time - start_time)/11
        time_slot = end_time - start_time
        total_minutes = time_slot.total_seconds()/60
        time_slot_minutes = int(total_minutes/self._num)
        # dns_servers = Server.query.all()  
        return self._get_resolve_rate_by_itemid(
                        self._server.zb_resolve_rate_itemid, total_minutes)


