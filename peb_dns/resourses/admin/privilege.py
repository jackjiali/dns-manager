from flask_restful import Resource, marshal_with, fields, marshal, reqparse, abort
from flask import Blueprint, request, jsonify, current_app, g

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.util import getETCDclient, get_response, get_response_wrapper_fields
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING, ROLE_MAPPINGS, DefaultPrivilege
from peb_dns.common.decorators import token_required, admin_required, resource_exists_required
from peb_dns import db
from sqlalchemy import and_, or_
from datetime import datetime
from peb_dns.common.request_code import RequestCode

privilege_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'operation': fields.Integer,
    'resource_type': fields.Integer,
    'resource_id': fields.Integer,
    'comment': fields.String,
}


paginated_privilege_fields = {
    'total': fields.Integer,
    'privileges': fields.List(fields.Nested(privilege_fields)),
    'current_page': fields.Integer
}


class PrivilegeList(Resource):
    method_decorators = [admin_required, token_required] 

    def get(self):
        """
        功能: 获取权限列表资源
        ---
        security:
          - UserSecurity: []
        tags:
          - Privilege
        parameters:
          - name: currentPage
            in: query
            description: the page of Privilege
            type: integer
            default: 1
          - name: pageSize
            in: query
            description: the max records of page
            type: integer
            default: 10
          - name: id
            in: query
            description: Privilege id
            type: integer
            default: 1
          - name: name
            type: string
            in: query
            description: the name of Privilege
            default: PRIVILEGE_MODIFY
          - name: operation
            in: query
            type: integer
            description: the value of Privilege
            default: 1
            enum: [0, 1, 2]
          - name: role_id
            in: query
            type: integer
            description: the id of role
            default: 1
          - name: resource_type
            in: query
            type: integer
            description: the id of resource_type
            default: 1
            enum: [0, 1, 2, 3]
          - name: resource_id
            in: query
            type: integer
            description: the id of resource
            default: 1
        definitions:
          Privileges:
            properties:
              total:
                type: integer
                description: the count of records
              current_page:
                type: integer
                description: the current page
              privileges:
                type: array
                items:
                  $ref: "#/definitions/Privilege"
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
                  $ref: "#/definitions/Privileges"
            examples:
                {
                    "code": 100000,
                    "data": {
                        "total": 37,
                        "privileges": [
                            {
                                "id": 58,
                                "name": "VIEW#v555#DELETE",
                                "operation": 2,
                                "resource_type": 1,
                                "resource_id": 6,
                                "comment": null
                            },
                            {
                                "id": 57,
                                "name": "VIEW#v555#UPDATE",
                                "operation": 1,
                                "resource_type": 1,
                                "resource_id": 6,
                                "comment": null
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
        role_id = args.get('role_id', type=int)

        id = args.get('id', type=int)
        name = args.get('name', type=str)
        operation = args.get('operation', type=int)
        resource_type = args.get('resource_type', type=int)
        resource_id = args.get('resource_id', type=int)
        privilege_query = DBPrivilege.query
        if id is not None:
            privilege_query = privilege_query.filter_by(id=id)
        if name is not None:
            privilege_query = privilege_query.filter(DBPrivilege.name.like('%'+name+'%'))
        if operation is not None:
            privilege_query = privilege_query.filter_by(operation=operation)
        if resource_type is not None:
            privilege_query = privilege_query.filter_by(resource_type=resource_type)
        if resource_id is not None:
            privilege_query = privilege_query.filter_by(resource_id=resource_id)
        if role_id is not None:
            privilege_query = privilege_query.join(
                DBRolePrivilege, and_(DBRolePrivilege.privilege_id == DBPrivilege.id)) \
                    .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
                    .filter(DBRole.id == role_id)

        marshal_records = marshal(
            privilege_query.order_by(DBPrivilege.id.desc()).paginate(
                current_page, 
                page_size, 
                error_out=False
            ).items, privilege_fields)
        results_wrapper = {
            'total': privilege_query.count(), 
            'privileges': marshal_records, 
            'current_page': current_page
            }
        response_wrapper_fields = get_response_wrapper_fields(fields.Nested(paginated_privilege_fields))
        response_wrapper = get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)
        return marshal(response_wrapper, response_wrapper_fields)

    def post(self):
        """
        功能: 创建新的权限
        ---
        security:
          - UserSecurity: []
        tags:
          - Privilege
        definitions:
          Privilege_Parm:
            properties:
              name:
                type: string
                default: p123
                description: privilege name
              operation:
                type: integer
                default: 100
                description: the value of operation
              resource_type:
                type: integer
                default: 100
                description: the type of resource
              resource_id:
                type: integer
                default: 0
                description: the id of resource
              comment:
                type: string
                default: 权限修改
                description: the comment of privilege
        parameters:
          - in: body
            name: body
            schema:
              id: Add_Privilege
              required:
                - name
              $ref: "#/definitions/Privilege_Parm"
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
                    "msg": "添加成功",
                    "data": null
                }
        """        
        args = request.json
        privilege_name = args['name']
        operation = args.get('operation') if args.get('operation') != '' else 100
        resource_type = args.get('resource_type') if args.get('resource_type') != '' else 100
        resource_id = args.get('resource_id') if args.get('resource_id') != '' else 0
        comment = args.get('comment') if args.get('comment') else ''
        # print(privilege_name, operation, resource_type, resource_id, comment)
        uniq_privilege = DBPrivilege.query.filter_by(name=privilege_name).first()
        if uniq_privilege:
            return get_response(RequestCode.OTHER_FAILED,  "{e} 权限名已存在！".format(e=str(uniq_privilege.name)))
        try:
            new_privilege = DBPrivilege(
                name=privilege_name, 
                operation=operation, 
                resource_type=resource_type, 
                resource_id=resource_id, 
                comment=comment
                )
            db.session.add(new_privilege)
            db.session.flush()
            new_rp = DBRolePrivilege(
                role_id=1, 
                privilege_id=new_privilege.id
                )
            db.session.add(new_rp)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '创建失败！')
        return get_response(RequestCode.SUCCESS, '创建成功！')


class Privilege(Resource):
    method_decorators = [admin_required, token_required]

    # def __init__(self):
    #     self.role_common_parser = reqparse.RequestParser()
    #     self.role_common_parser.add_argument(
    #         'privilege_ids', 
    #         type = int, 
    #         location = 'json', 
    #         action='append', 
    #         required=True
    #         )
    #     super(Privilege, self).__init__()

    @resource_exists_required(ResourceType.PRIVILEGE)
    def get(self, privilege_id):
        """
        功能: 获取指定ID的权限详情
        ---
        security:
          - UserSecurity: []
        tags:
          - Privilege
        parameters:
          - name: privilege_id
            in: path
            description: the id of privilege
            type: integer
            required: true
            default: 1
        definitions:
          Privilege:
            properties:
              id:
                type: integer
                description: the id of privilege
              name:
                type: string
                description: the name of privilege
              operation:
                type: integer
                description: the operationof privilege
              comment:
                type: string
                description: the comment privilege
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
                  $ref: "#/definitions/Privilege"
            examples:
                {
                    "code": 100000,
                    "msg": "获取成功！",
                    "data": {
                        "id": 37,
                        "name": "ZONE#xx1.com#DELETE",
                        "operation": 2,
                        "resource_type": 2,
                        "resource_id": 4,
                        "comment": null
                    }
                }
        """
        current_p = DBPrivilege.query.get(privilege_id)
        results_wrapper = marshal(current_p, privilege_fields)
        return get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)

    @resource_exists_required(ResourceType.PRIVILEGE)
    def put(self, privilege_id):
        """
        功能: 修改指定ID的权限
        ---
        security:
          - UserSecurity: []
        tags:
          - Privilege
        parameters:
          - name: privilege_id
            in: path
            description: the id of privilege
            type: integer
            required: true
            default: 1
          - name: body
            in: body
            schema:
              id: Update_Privilege
              $ref: "#/definitions/Privilege_Parm"
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
                    "msg": "修改成功！",
                    "data": null
                }
        """
        current_privilege = DBPrivilege.query.get(privilege_id)
        args = request.json
        privilege_name = args['name']
        operation = args.get('operation') if args.get('operation') != '' else 100
        resource_type = args.get('resource_type') if args.get('resource_type') != '' else 100
        resource_id = args.get('resource_id') if args.get('resource_id') != '' else 0
        comment = args.get('comment') if args.get('comment') else ''
        current_privilege = DBPrivilege.query.get(privilege_id)
        uniq_privilege = DBPrivilege.query.filter(
            DBPrivilege.name==privilege_name, 
            DBPrivilege.id!=privilege_id
            ).first()
        if uniq_privilege:
            return get_response(RequestCode.OTHER_FAILED,  "{e} 权限名已存在！".format(e=str(uniq_privilege.name)))
        try:
            current_privilege.name = privilege_name
            current_privilege.operation = operation
            current_privilege.resource_type = resource_type
            current_privilege.resource_id = resource_id
            current_privilege.comment = comment
            db.session.add(current_privilege)
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '修改失败！')
        return get_response(RequestCode.SUCCESS, '修改成功！')

    @resource_exists_required(ResourceType.PRIVILEGE)
    def delete(self, privilege_id):
        """
        功能: 删除指定ID的权限
        ---
        security:
          - UserSecurity: []
        tags:
          - Privilege
        parameters:
          - name: privilege_id
            in: path
            description: the id of privilege
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
            examples:
                {
                    "code": 100000,
                    "msg": "删除成功",
                    "data": null
                }
        """
        current_privilege = DBPrivilege.query.get(privilege_id)
        try:
            db.session.delete(current_privilege)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '修改失败！')
        return get_response(RequestCode.SUCCESS, '修改成功！')


