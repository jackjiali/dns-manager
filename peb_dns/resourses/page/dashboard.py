from flask_restful import Api, Resource, url_for, reqparse, abort
from flask import current_app, g, request
from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord, DBDNSServer
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.decorators import token_required, admin_required, permission_required, indicated_privilege_required, resource_exists_required
from peb_dns.common.util import getETCDclient, get_response, get_response_wrapper_fields
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING, ROLE_MAPPINGS, DefaultPrivilege

from peb_dns import db
from peb_dns.common.util import ZBapi
from sqlalchemy import and_, or_
from datetime import datetime
from peb_dns.common.request_code import RequestCode


class ResourceAmount(Resource):
    method_decorators = [token_required]

    def get(self):
        """
        功能: 获取各个资源总数
        ---
        security:
          - UserSecurity: []
        tags:
          - Page
        responses:
          200:
            description: 请求结果
            schema:
              properties:
                code:
                  type: integer
                  description: response code
                msg:
                  type: string
                  description: response message
                data:
                  type: string
            examples:
                {
                    "code": 100000,
                    "msg": "获取成功！",
                    "data": {
                        "server_amount": 10,
                        "view_amount": 20,
                        "zone_amount": 2,
                        "record_amount": 2
                    }
                }
        """
        resources_amount = dict(
            server_amount=DBDNSServer.query.count(), 
            view_amount=DBView.query.count(), 
            zone_amount=DBZone.query.count(), 
            record_amount=DBRecord.query.count()
            )
        return get_response(RequestCode.SUCCESS, '获取成功！', resources_amount)


class DNSServerResolveRate(Resource):
    """Get the resolve rate of all the dns servers."""
    method_decorators = [token_required]

    def get(self):
        args = request.args
        start_time = datetime.strptime(args['start_time'], "%Y-%m-%d %H:%M:%S") 
        end_time = datetime.now()
        if args.get('end_time'):
            end_time = datetime.strptime(args['end_time'], "%Y-%m-%d %H:%M:%S")
        dns_servers = DBDNSServer.query.all()
        resolve_rates = {}
        try:
            for dns_server in dns_servers:
                resolve_rate = dns_server.get_resolve_rate(start_time, end_time)
                resolve_rates[dns_server.host] = resolve_rate
        except IndexError as ie:
            return get_response(RequestCode.OTHER_FAILED,  '获取数据失败！Zabbix上对应解析量itemid没有足够的记录！或解析量itemid有误！')
        except Exception as e:
            return get_response(RequestCode.OTHER_FAILED,  '获取Zabbix数据失败！')
        return get_response(RequestCode.SUCCESS, '获取成功！', resolve_rates)


class DNSServerStatus(Resource):
    method_decorators = [token_required]

    def get(self):
        """Get the server status by server id."""
        args = request.args
        current_server = DBDNSServer.query.get(int(args['server_id']))
        if not current_server:
            return get_response(RequestCode.OTHER_FAILED,  '你请求的资源不存在！')
        try:
            results = current_server.get_server_status()
        except Exception as e:
            return get_response(RequestCode.OTHER_FAILED, '获取数据异常！')
        return get_response(RequestCode.SUCCESS, '获取成功！', results)


