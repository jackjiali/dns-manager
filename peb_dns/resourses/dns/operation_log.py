from flask_restful import Api, Resource, url_for, reqparse, abort, marshal_with, fields, marshal
from flask import current_app, g, request

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord, DBDNSServer
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.decorators import token_required, admin_required, permission_required, indicated_privilege_required, resource_exists_required
from peb_dns.common.util import getETCDclient, get_response, get_response_wrapper_fields
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING, ROLE_MAPPINGS, DefaultPrivilege
from peb_dns import db
from sqlalchemy import and_, or_
from datetime import datetime
from peb_dns.common.request_code import RequestCode


log_fields = {
    'id': fields.Integer,
    'operation_time': fields.String,
    'operation_type': fields.String,
    'operator': fields.String,
    'target_type': fields.String,
    'target_name': fields.String,
    'target_id': fields.String,
    'target_detail': fields.String,
}

paginated_log_fields = {
    'total': fields.Integer,
    'operation_logs': fields.List(fields.Nested(log_fields)),
    'current_page': fields.Integer
}

class DNSOperationLogList(Resource):
    method_decorators = [token_required] 

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(DNSOperationLogList, self).__init__()

    def get(self):
        """
        功能：获取日志资源列表
        ---
        security:
          - UserSecurity: []
        tags:
          - DNSOperationLog
        parameters:
          - name: currentPage
            in: query
            description: 当前是第几页
            type: integer
            required: false
            default: 1
          - name: pageSize
            in: query
            description: 每页显示的记录数
            type: integer
            required: false
            default: 10
          - name: id
            in: query
            description: 日志ID
            type: integer
            required: false
          - name: operation_type
            in: query
            description: 操作类型，添加/修改/删除
            type: string
            required: false
          - name: operator
            in: query
            description: 操作人
            type: string
            required: false
          - name: target_type
            in: query
            description: 资源类型，Server/View/Zone/Record
            type: string
            required: false
          - name: target_name
            in: query
            description: 资源名称
            type: string
            required: false
          - name: target_id
            in: query
            description: 资源ID
            type: integer
            required: false
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
                  description: response data
            examples:
                {
                    "code": 100000,
                    "data": {
                        "total": 66,
                        "operation_logs": [
                        {
                            "id": 67,
                            "operation_time": "2017-12-04 18:22:19",
                            "operation_type": "添加",
                            "operator": "LIJIAJIA873",
                            "target_type": "Record",
                            "target_name": "xxx333",
                            "target_id": "32",
                            "target_detail": "id: 32\\n记录主机: xxx333\\n记录类型: A\\n记录值: 0.0.0.0\\nTTL: 600\\n线路类型: wqerqwer\\n备注: xxx111\\n创建人: None\\n创建时间: 2017-12-04 18:22:18.805320"
                        }
                        ],
                        "current_page": 1
                    },
                    "msg": "获取成功！"
                }
        """
        args = request.args
        current_page = args.get('currentPage', 1, type=int)
        page_size = args.get('pageSize', 10, type=int)

        id = args.get('id', type=int)
        operation_type = args.get('operation_type', type=str)
        operator = args.get('operator', type=str)
        target_type = args.get('target_type', type=str)
        target_name = args.get('target_name', type=str)
        oplog_query = DBOperationLog.query
        if id is not None:
            oplog_query = oplog_query.filter(DBOperationLog.id==id)
        if operation_type is not None:
            oplog_query = oplog_query.filter(DBOperationLog.operation_type==operation_type)
        if operator is not None:
            oplog_query = oplog_query.filter(DBOperationLog.operator.like('%'+operator+'%'))
        if target_type is not None:
            oplog_query = oplog_query.filter(DBOperationLog.target_type==target_type)
        if target_name is not None:
            oplog_query = oplog_query.filter(DBOperationLog.target_name.like('%'+target_name+'%'))
        marshal_records = marshal(
                    oplog_query.order_by(DBOperationLog.id.desc()).paginate(
                        current_page, 
                        page_size, 
                        error_out=False).items, log_fields
                    )
        results_wrapper = {
            'total': oplog_query.count(), 
            'operation_logs': marshal_records, 
            'current_page': current_page
            }
        response_wrapper_fields = get_response_wrapper_fields(fields.Nested(paginated_log_fields))
        response_wrapper = get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)
        return marshal(response_wrapper, response_wrapper_fields)


class DNSOperationLog(Resource):
    method_decorators = [token_required] 

    def get(self, log_id):
        """
        功能：获取指定ID的日志资源详情
        ---
        security:
          - UserSecurity: []
        tags:
          - DNSOperationLog
        parameters:
          - name: log_id
            in: path
            description:
            type: integer
            required: true
            default: 1
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
                  description: response data
            examples:
                {
                    "code": 100000,
                    "data": {},
                    "msg": "获取成功！"
                }
        """
        current_log = DBOperationLog.query.get(log_id)
        if not current_log:
            return get_response(RequestCode.OTHER_FAILED,  "当前记录 {} 不存在！".format(str(log_id)))
        results_wrapper = marshal(current_log, log_fields)
        return get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)

