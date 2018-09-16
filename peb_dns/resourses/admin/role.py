from flask_restful import Resource, marshal_with, fields, marshal, reqparse, abort
from flask import Blueprint, request, jsonify, current_app, g

from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord, DBDNSServer
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.decorators import token_required, admin_required, permission_required, indicated_privilege_required, owner_or_admin_required, resource_exists_required
from peb_dns.common.util import getETCDclient, get_response, get_response_wrapper_fields
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING, ROLE_MAPPINGS, DefaultPrivilege
from peb_dns import db
from sqlalchemy import and_, or_
from datetime import datetime
from peb_dns.common.request_code import RequestCode


dns_role_common_parser = reqparse.RequestParser()
dns_role_common_parser.add_argument('name', 
                                type = str, 
                                location = 'json', 
                                required=True, 
                                help='role name.')
dns_role_common_parser.add_argument('privilege_ids', 
                                type = int, 
                                location = 'json', 
                                action='append', 
                                required=True)


user_fields = {
    'id': fields.Integer,
    'username': fields.String,
}


privilege_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'operation': fields.Integer,
    'resource_type': fields.Integer,
    'resource_id': fields.Integer,
    'comment': fields.String,
}


role_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'privileges': fields.List(fields.Nested(privilege_fields))
}


paginated_role_fields = {
    'total': fields.Integer,
    'roles': fields.List(fields.Nested(role_fields)),
    'current_page': fields.Integer
}


class RoleList(Resource):
    method_decorators = [admin_required, token_required] 

    def get(self):
        """
        功能: 获取角色列表资源
        ---
        security:
          - UserSecurity: []
        tags:
          - Role
        parameters:
          - name: currentPage
            in: query
            description: the page of Role
            type: integer
            default: 1
          - name: pageSize
            in: query
            description: the max records of page
            type: integer
            default: 10
          - name: id
            in: query
            description: Role id
            type: integer
            default: 1
          - name: name
            type: string
            in: query
            description: the name of Role
            default: Guest
          - name: user_id
            in: query
            type: integer
            description: the id of User
            default: 1
        definitions:
          Roles:
            properties:
              total:
                type: integer
              current_page:
                type: integer
              roles:
                type: array
                items:
                  $ref: "#/definitions/Role"
        responses:
          200:
            description: 请求结果
            schema:
              properties:
                code:
                  type: integer
                msg:
                  type: string
                data:
                  $ref: "#/definitions/Roles"
            examples:
                {
                    "code": 100000,
                    "msg": "获取成功！",
                    "data": {
                        "total": 7,
                        "roles": [
                            {
                                "id": 6,
                                "name": "zone_admin",
                                "privileges": [
                                    {
                                        "id": 2,
                                        "name": "ZONE_ADD",
                                        "operation": 0,
                                        "resource_type": 0,
                                        "resource_id": 0,
                                        "comment": null
                                    },
                                    {
                                        "id": 6,
                                        "name": "ZONE#xcvwretwgvrfv3wf.com#UPDATE",
                                        "operation": 1,
                                        "resource_type": 2,
                                        "resource_id": 1,
                                        "comment": null
                                    }
                                ]
                            },
                            {
                                "id": 2,
                                "name": "server_admin",
                                "privileges": [
                                    {
                                        "id": 1,
                                        "name": "SERVER_ADD",
                                        "operation": 0,
                                        "resource_type": 0,
                                        "resource_id": 0,
                                        "comment": null
                                    },
                                    {
                                        "id": 17,
                                        "name": "SERVER#s1#ACCESS",
                                        "operation": 0,
                                        "resource_type": 0,
                                        "resource_id": 1,
                                        "comment": null
                                    }
                                ]
                            }
                        ]
                        },
                        "current_page": 1
                    }
        """
        args = request.args
        current_page = args.get('currentPage', 1, type=int)
        page_size = args.get('pageSize', 10, type=int)
        user_id = args.get('user_id', type=int)

        id = args.get('id', type=int)
        name = args.get('name', type=str)
        role_query = DBRole.query
        if id is not None:
            role_query = role_query.filter_by(id=id)
        if name is not None:
            role_query = role_query.filter(DBRole.name.like('%'+name+'%'))
        if user_id is not None:
            role_query = role_query \
                .join(DBUserRole, and_(DBUserRole.role_id == DBRole.id)) \
                .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
                .filter(DBUser.id == user_id)
        
        marshal_records = marshal(
                role_query.order_by(DBRole.id.desc()).paginate(
                    current_page, 
                    page_size, 
                    error_out=False).items, role_fields)
        results_wrapper = {
            'total': role_query.count(), 
            'roles': marshal_records, 
            'current_page': current_page
            }
        response_wrapper_fields = get_response_wrapper_fields(fields.Nested(paginated_role_fields))
        response_wrapper = get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)
        return marshal(response_wrapper, response_wrapper_fields)
    
    def post(self):
        """
        功能: 添加角色
        ---
        security:
          - UserSecurity: []
        tags:
          - Role
        definitions:
          Role_Parm:
            properties:
              name:
                type: string
                default: Guest
                description: the name of Role
              privilege_ids:
                type: array
                description: the list of privilege
                items:
                  type: integer
                  default: 1
        parameters:
          - in: body
            name: body
            schema:
              id: Add_Role
              required:
                - name
                - privilege_ids
              $ref: "#/definitions/Role_Parm"
        responses:
          200:
            description: 请求结果
            schema:
              properties:
                code:
                  type: integer
                msg:
                  type: string
                data:
                  type: string
            examples:
                {
                    "code": 100000,
                    "msg": "创建成功！",
                    "data": null
                }
        """
        args = dns_role_common_parser.parse_args()
        role_name = args['name']
        privilege_ids = args['privilege_ids']
        try:
            new_role = DBRole(name=role_name)
            db.session.add(new_role)
            db.session.flush()
            for privilege_id in privilege_ids:
                new_rp = DBRolePrivilege(
                    role_id=new_role.id, privilege_id=privilege_id)
                db.session.add(new_rp)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '修改失败！')
        return get_response(RequestCode.SUCCESS, '修改成功！')


class Role(Resource):
    method_decorators = [admin_required, token_required]

    def get(self, role_id):
        """
        功能: 获取指定ID的角色详情
        ---
        security:
          - UserSecurity: []
        tags:
          - Role
        parameters:
          - name: role_id
            in: path
            description: Role id
            type: integer
            required: true
            default: 1
        definitions:
          Role:
            properties:
              id:
                type: integer
              name:
                type: string
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
                msg:
                  type: string
                data:
                  $ref: "#/definitions/Role"
            examples:
                {
                    "code": 100000,
                    "msg": "获取成功！",
                    "data": {
                        "id": 3,
                        "name": "server_guest",
                        "privileges": [
                            {
                                "id": 17,
                                "name": "SERVER#s1#ACCESS",
                                "operation": 0,
                                "resource_type": 0,
                                "resource_id": 1,
                                "comment": null
                            },
                            {
                                "id": 20,
                                "name": "SERVER#s2#ACCESS",
                                "operation": 0,
                                "resource_type": 0,
                                "resource_id": 2,
                                "comment": null
                            }
                        ]
                    }
                }
        """
        current_role = DBRole.query.get(role_id)
        if not current_role:
            return get_response(RequestCode.OTHER_FAILED,  '角色不存在！')
        results_wrapper = marshal(current_role, role_fields)
        return get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)

    def put(self, role_id):
        """
        功能: 修改指定ID的角色
        ---
        security:
          - UserSecurity: []
        tags:
          - Role
        parameters:
          - name: role_id
            in: path
            description: Role id
            type: integer
            required: true
            default: 1
          - in: body
            name: body
            schema:
              id: Update_Role
              $ref: "#/definitions/Role_Parm"
        responses:
          200:
            description: 请求结果
            schema:
              properties:
                code:
                  type: integer
                msg:
                  type: string
                data:
                  type: string
            examples:
                {
                    "code": 100000,
                    "msg": "修改成功",
                    "data": null
                }
        """
        args = dns_role_common_parser.parse_args()
        role_name = args['name']
        privilege_ids = args['privilege_ids']
        current_role = DBRole.query.get(role_id)
        if not current_role:
            return get_response(RequestCode.OTHER_FAILED,  "角色不存在！")
        try:
            current_role.name = role_name
            for del_rp in DBRolePrivilege.query.filter(
                    DBRolePrivilege.role_id==role_id, 
                    DBRolePrivilege.privilege_id.notin_(privilege_ids)
                    ).all():
                db.session.delete(del_rp)
            for privilege_id in privilege_ids:
                rp = DBRolePrivilege.query.filter(
                    DBRolePrivilege.role_id==role_id, 
                    DBRolePrivilege.privilege_id==privilege_id
                    ).first()
                if not rp:
                    new_role_privilege = DBRolePrivilege(
                            role_id=role_id, privilege_id=privilege_id)
                    db.session.add(new_role_privilege)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '修改失败！')
        return get_response(RequestCode.SUCCESS, '修改成功！')

    def delete(self, role_id):
        """
        功能: 删除指定ID的角色
        ---
        security:
          - UserSecurity: []
        tags:
          - Role
        parameters:
          - name: role_id
            in: path
            description: Role id
            type: integer
            required: true
            default: 1
        responses:
          200:
            description: 请求结果
            schema:
              properties:
                code:
                  type: string
                msg:
                  type: string
                data:
                  type: string
            examples:
                {
                    "code": 100000,
                    "msg": "删除成功",
                    "data": null
                }
        """
        current_role = DBRole.query.get(role_id)
        if not current_role:
            return get_response(RequestCode.OTHER_FAILED,  "角色不存在！")
        related_users = current_role.users
        if related_users:
            return get_response(RequestCode.OTHER_FAILED,  "这些用户依然关联当前角色 {e} ，请先解除关联！"
                    .format(e=str([u.username for u in related_users])))
        try:
            DBUserRole.query.filter(DBUserRole.role_id==role_id).delete()
            db.session.delete(current_role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '删除失败！')
        return get_response(RequestCode.SUCCESS, '删除成功！')


