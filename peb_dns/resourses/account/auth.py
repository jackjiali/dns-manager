from flask_restful import Api, Resource, url_for, reqparse, abort
from flask import Blueprint, request, jsonify, current_app
from ldap3 import Connection, ALL
from ldap3 import Server as LDAPServer
import datetime
import jwt
from peb_dns.models.account import DBUser, DBLocalAuth
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING, ROLE_MAPPINGS, DefaultPrivilege
from peb_dns.common.util import getETCDclient, get_response, get_response_wrapper_fields
from peb_dns import db
from peb_dns.common.request_code import RequestCode


class AuthLDAP(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type = str, location = 'json')
        self.reqparse.add_argument('password', type = str, location = 'json')
        super(AuthLDAP, self).__init__()

    def post(self):
        """
        功能: LDAP认证接口
        ---
        security:
          - UserSecurity: []
        tags:
          - Auth
        parameters:
          - in: body
            name: body
            schema:
              id: AuthLDAP_post
              properties:
                username:
                  type: string
                  default: user123
                  description: 用户名
                password:
                  type: string
                  default: passwd123
                  description: 密码
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
                    "msg": "认证失败！",
                    "data": null
                }

        """
        args = self.reqparse.parse_args()
        username, password = args['username'], args['password']
        if self._auth_via_ldap(username, password):
            user = DBUser.query.filter_by(username=username).first()
            if user is not None :
                if user.actived == 0:
                    return get_response(RequestCode.LOGIN_FAILED,  '对不起，您已经被管理员禁止登陆！')
                token = jwt.encode({
                    'user' : user.username, 
                    'exp' : datetime.datetime.now() + datetime.timedelta(hours=24)
                    }, current_app.config['SECRET_KEY'])
                response_data = {
                    'token' : token.decode('UTF-8'), 
                    'user_info': user.to_json()
                    }
                return get_response(RequestCode.SUCCESS, '认证成功！', response_data)
            new_user = DBUser(username=username)
            db.session.add(new_user)
            db.session.commit()
            token = jwt.encode(
                {
                    'user' : new_user.username,
                    'exp' : datetime.datetime.now() + datetime.timedelta(hours=24)
                }, current_app.config['SECRET_KEY'])
            response_data = {
                'token' : token.decode('UTF-8'), 
                'user_info': new_user.to_json()
                }
            return get_response(RequestCode.SUCCESS, '认证成功！', response_data)
        return get_response(RequestCode.LOGIN_FAILED,  '登录失败！账号密码错误！')

    def _auth_via_ldap(self, username, passwd):
        try:
            server = LDAPServer(
                current_app.config.get('LDAP_SERVER'), 
                port=int(current_app.config.get('LDAP_SERVER_PORT')
                ), use_ssl=True, get_info=ALL)
            _connection = Connection(server, 
                'cn=' + username + current_app.config.get('LDAP_CONFIG'), 
                passwd, 
                auto_bind=True
                )
        except Exception as e:
            return False
        return True


class AuthLocal(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type = str, location = 'json')
        self.reqparse.add_argument('password', type = str, location = 'json')
        super(AuthLocal, self).__init__()

    def post(self):
        """
        功能: 本地注册用户认证接口
        ---
        security:
          - UserSecurity: []
        tags:
          - Auth
        parameters:
          - in: body
            name: body
            schema:
              id: AuthLocal_post
              properties:
                username:
                  type: string
                  default: user123
                  description: 用户名
                password:
                  type: string
                  default: passwd123
                  description: 密码
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
                    "code": 105000,
                    "msg": "认证失败！",
                    "data": null
                }
        """
        args = self.reqparse.parse_args()
        username, password = args['username'], args['password']
        auth_user = DBLocalAuth.query.filter_by(
            username = args['username']).first()
        if auth_user is None:
            return get_response(RequestCode.LOGIN_FAILED,  '认证失败！用户不存在！')
        if not auth_user.verify_password(args['password']) :
            return get_response(RequestCode.LOGIN_FAILED,  '认证失败！账号或密码错误！')
        local_user = DBUser.query.filter_by(username=args['username']).first()
        if local_user.actived == 0:
            return get_response(RequestCode.LOGIN_FAILED,  '对不起，您已经被管理员禁止登陆！')
        token = jwt.encode(
            {
                'user' : local_user.username, 
                'exp' : datetime.datetime.now() + datetime.timedelta(hours=24)
            }, current_app.config['SECRET_KEY'])
        response_data = {
            'token' : token.decode('UTF-8'), 
            'user_info': local_user.to_json()
            }
        return get_response(RequestCode.SUCCESS, '认证成功！', response_data)


class RegisterLocal(Resource):
    def __init__(self):
        super(RegisterLocal, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type = str, 
                                    location = 'json', required=True)
        self.reqparse.add_argument('password', type = str, 
                                    location = 'json', required=True)
        self.reqparse.add_argument('password2', type = str, 
                                    location = 'json', required=True)
        self.reqparse.add_argument('email', type = str, 
                                    location = 'json', required=True)

    def post(self):
        """
        功能：本地用户注册接口
        ---
        security:
          - UserSecurity: []
        tags:
          - Auth
        parameters:
          - in: body
            name: body
            schema:
              id: RegisterLocal_post
              properties:
                username:
                  type: string
                  default: user123
                  description: 用户名
                password:
                  type: string
                  default: passwd123
                  description: 密码
                password2:
                  type: string
                  default: passwd123
                  description: 两次密码输入要一致
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
                    "msg": "注册成功！",
                    "data": null
                }
        """
        args = self.reqparse.parse_args()
        auth_user = DBLocalAuth.query.filter_by(
            username = args['username']).first()
        local_user = DBUser.query.filter_by(
            username = args['username']).first()
        if auth_user or local_user:
            return get_response(RequestCode.OTHER_FAILED,  '用户已存在！')
        new_auth_user = DBLocalAuth(
            username=args['username'], email=args['email'])
        new_auth_user.password = args['password']
        new_local_user = DBUser(username=args['username'], email=args['email'])
        db.session.add(new_local_user)
        db.session.add(new_auth_user)
        db.session.commit()
        return get_response(RequestCode.SUCCESS, '注册成功！')


