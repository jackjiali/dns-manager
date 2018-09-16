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


dns_user_common_parser = reqparse.RequestParser()
dns_user_common_parser.add_argument('role_ids', 
                                type = int, 
                                location = 'json', 
                                action='append')
dns_user_common_parser.add_argument('email', 
                                type = str, 
                                location = 'json')
dns_user_common_parser.add_argument('chinese_name', 
                                type = str, 
                                location = 'json')
dns_user_common_parser.add_argument('cellphone', 
                                type = str, 
                                location = 'json')
dns_user_common_parser.add_argument('position', 
                                type = str, 
                                location = 'json')
dns_user_common_parser.add_argument('location', 
                                type = str, 
                                location = 'json')
dns_user_common_parser.add_argument('actived', 
                                type = int, 
                                location = 'json')


role_fields = {
    'id': fields.Integer,
    'name': fields.String,
}


user_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'username': fields.String,
    'chinese_name': fields.String,
    'cellphone': fields.String,
    'position': fields.String,
    'location': fields.String,
    'member_since': fields.String,
    'last_seen': fields.String,
    'actived': fields.Integer,
    'roles': fields.List(fields.Nested(role_fields)),
}


single_user_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'username': fields.String,
    'chinese_name': fields.String,
    'cellphone': fields.String,
    'position': fields.String,
    'location': fields.String,
    'member_since': fields.String,
    'last_seen': fields.String,
    'can_add_server': fields.Boolean,
    'can_add_view': fields.Boolean,
    'can_add_zone': fields.Boolean,
    'can_edit_bind_conf': fields.Boolean,
    'roles': fields.List(fields.Nested(role_fields)),
}


paginated_user_fields = {
    'total': fields.Integer,
    'users': fields.List(fields.Nested(user_fields)),
    'current_page': fields.Integer
}

class UserList(Resource):
    method_decorators = [admin_required, token_required] 

    def get(self):
        """
        功能: 获取用户列表资源
        ---
        security:
          - UserSecurity: []
        tags:
          - User
        parameters:
          - name: currentPage
            in: query
            description: the page of User
            type: integer
            default: 1
          - name: pageSize
            in: query
            description: the max records of page
            type: integer
            default: 10
          - name: id
            in: query
            description: User id
            type: integer
            default: 1
          - name: username
            type: string
            in: query
            description: the username of User
            default: test
          - name: chinese_name
            in: query
            type: string
            description: the chinese_name of User
            default: 小李
          - name: cellphone
            in: query
            type: string
            description: the cellphone of User
            default: 186121234
          - name: email
            in: query
            type: string
            description: the email of User
            default: test@163.com
          - name: actived
            in: query
            type: integer
            description: the active status of User
            enum: [0, 1]
            default: 1
        definitions:
          Users:
            properties:
              total:
                type: integer
              current_page:
                type: integer
              groups:
                type: array
                items:
                  $ref: "#/definitions/User"
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
                  $ref: "#/definitions/Users"
            examples:
                {
                    "code": 100000,
                    "data": {
                        "total": 8,
                        "users": [
                            {
                                "id": 8,
                                "email": "xxx@qq.com",
                                "username": "test222",
                                "chinese_name": "",
                                "cellphone": "",
                                "position": "",
                                "location": "",
                                "member_since": "2017-12-04 17:34:25",
                                "last_seen": "2017-12-04 17:34:25",
                                "roles": []
                            },
                            {
                                "id": 7,
                                "email": "xxx@qq.com",
                                "username": "test111",
                                "chinese_name": "",
                                "cellphone": "1371111",
                                "position": "",
                                "location": "",
                                "member_since": "2017-11-29 14:16:27",
                                "last_seen": "2017-11-29 14:16:27",
                                "roles": []
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
        email = args.get('email', type=str)
        username = args.get('username', type=str)
        chinese_name = args.get('chinese_name', type=str)
        cellphone = args.get('cellphone', type=str)
        actived = args.get('actived', type=int)
        user_query = DBUser.query
        if id is not None:
            user_query = user_query.filter_by(id=id)
        if email is not None:
            user_query = user_query.filter(DBUser.email.like('%'+email+'%'))
        if username is not None:
            user_query = user_query.filter(DBUser.username.like('%'+username+'%'))
        if chinese_name is not None:
            user_query = user_query.filter(DBUser.chinese_name.like('%'+chinese_name+'%'))
        if cellphone is not None:
            user_query = user_query.filter(DBUser.cellphone.like('%'+cellphone+'%'))
        if actived is not None:
            user_query = user_query.filter_by(actived=actived)
        marshal_records = marshal(
            user_query.order_by(DBUser.id.desc()).paginate(
                current_page, 
                page_size, 
                error_out=False).items, user_fields
            )
        results_wrapper = {
            'total': user_query.count(), 
            'users': marshal_records, 
            'current_page': current_page
            }
        response_wrapper_fields = get_response_wrapper_fields(fields.Nested(paginated_user_fields))
        response_wrapper = get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)
        return marshal(response_wrapper, response_wrapper_fields)


class User(Resource):
    method_decorators = [token_required]

    @owner_or_admin_required
    def get(self, user_id):
        """
        功能: 获取指定ID的用户详情
        ---
        security:
          - UserSecurity: []
        tags:
          - User
        parameters:
          - name: user_id
            in: path
            description: User id
            type: integer
            required: true
            default: 1
        definitions:
          User:
            properties:
              email:
                type: string
              username:
                type: string
              chinese_name:
                type: string
              cellphone:
                type: string
              position:
                type: string
              location:
                type: string
              member_since:
                type: string
              last_seen:
                type: string
              roles:
                type: array
                items:
                  $ref: "#/definitions/Role"
              can_add_server:
                type: boolean
              can_add_view:
                type: boolean
              can_add_zone:
                type: boolean
              can_edit_bind_conf:
                type: boolean
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
                  $ref: "#/definitions/User"
            examples:
                {
                    "code": 100000,
                    "msg": "请求成功",
                    "data": {
                        "id": 9,
                        "email": "test123@pingan.com.cn",
                        "um_account": null,
                        "username": "test1",
                        "user_pic": null,
                        "chinese_name": "",
                        "cellphone": "",
                        "position": "",
                        "location": "",
                        "member_since": "2017-11-29 15:47:45",
                        "last_seen": "2017-11-29 15:47:45",
                        "group": null,
                        "roles": []
                    }
                }
        """
        current_u = DBUser.query.get(user_id)
        if not current_u:
            return get_response(RequestCode.OTHER_FAILED,  '用户不存在！')
        results_wrapper = marshal(current_u, single_user_fields)
        return get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)

    @owner_or_admin_required
    def put(self, user_id):
        """
        功能: 修改指定ID的用户
        ---
        security:
          - UserSecurity: []
        tags:
          - User
        definitions:
          User_Parm:
            properties:
              email:
                type: string
                description: the email of User
                default: test@163.com
              chinese_name:
                type: string
                description: the chinese_name of User
                default: 小李
              cellphone:
                type: string
                description: the cellphone of User
                default: "186123423"
              position:
                type: string
                description: the position of User
                default: developer
              location:
                type: string
                description: the seat of User
                default: the 12th floor
              role_ids:
                type: array
                description: the role id of user
                items:
                  type: integer
                  default: 1
              actived:
                type: integer
                default: 1
                description: the status of user
        parameters:
          - name: user_id
            in: path
            description: User id
            type: integer
            required: true
            default: 1
          - in: body
            name: body
            schema:
              id: Update_User
              $ref: "#/definitions/User_Parm"
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
        current_u = DBUser.query.get(user_id)
        if not current_u:
            return get_response(RequestCode.OTHER_FAILED,  "用户不存在！")
        args = dns_user_common_parser.parse_args()
        role_ids = args.get('role_ids')
        try:
            current_u.cellphone = args.get('cellphone', current_u.cellphone)
            current_u.chinese_name = args.get('chinese_name', current_u.chinese_name)
            current_u.email = args.get('email', current_u.email)
            current_u.location = args.get('location', current_u.location)
            current_u.position = args.get('position', current_u.position)
            current_u.actived = args.get('actived', current_u.actived)
            db.session.add(current_u)
            if role_ids is not None:
                for del_ur in DBUserRole.query.filter(
                        DBUserRole.user_id==user_id, 
                        DBUserRole.role_id.notin_(role_ids)).all():
                    db.session.delete(del_ur)
                for role_id in role_ids:
                    ur = DBUserRole.query.filter(
                        DBUserRole.role_id==role_id, 
                        DBUserRole.user_id==user_id).first()
                    if not ur:
                        new_user_role = DBUserRole(
                                user_id=user_id, role_id=role_id)
                        db.session.add(new_user_role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '修改失败！')
        return get_response(RequestCode.SUCCESS, '修改成功！')

    @admin_required
    def delete(self, user_id):
        """
        功能: 删除指定ID的用户
        ---
        security:
          - UserSecurity: []
        tags:
          - User
        parameters:
          - name: user_id
            in: path
            description: User id
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
        current_u = DBUser.query.get(user_id)
        if not current_u:
            return get_response(RequestCode.OTHER_FAILED,  "用户不存在！")
        try:
            DBUserRole.query.filter(
                    DBUserRole.user_id==user_id).delete()
            db.session.delete(current_u)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '删除失败！')
        return get_response(RequestCode.SUCCESS, '删除成功！')


