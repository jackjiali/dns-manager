from functools import wraps
from flask_restful import Api, Resource, url_for, reqparse, abort
from flask import current_app, g, request
import jwt
from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord, DBDNSServer, dns_models
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege, DBLocalAuth, account_models
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING, DefaultPrivilege
from sqlalchemy import and_, or_
from peb_dns import db
from .util import get_response
from .request_code import RequestCode

dns_models.update(account_models)
all_resources_models = dns_models


def permission_required(resource_type, operation_type):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            resource_id = list(kwargs.values())[0]            
            resource = all_resources_models[resource_type].query.get(resource_id)
            if all_resources_models[resource_type] == DBRecord:
                if not g.current_user.can_do(operation_type, ResourceType.ZONE, resource.zone.id):
                    return get_response(RequestCode.OTHER_FAILED,  '拒绝访问！您无权访问当前资源，如有问题请联系管理员。')
                return f(*args, **kwargs)
            if not g.current_user.can_do(
                        operation_type, 
                        resource_type, 
                        resource_id):
                return get_response(RequestCode.OTHER_FAILED,  '拒绝访问！您无权访问当前资源，如有问题请联系管理员。')
            return f(*args, **kwargs)
        return wrapper
    return decorator

def resource_exists_required(resource_type):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            resource_id = list(kwargs.values())[0]            
            resource = all_resources_models[resource_type].query.get(resource_id)
            if not resource:
                return get_response(RequestCode.OTHER_FAILED,  '你请求的资源不存在！')
            return f(*args, **kwargs)
        return wrapper
    return decorator

def indicated_privilege_required(privilege_name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not g.current_user.can(privilege_name):
                return get_response(RequestCode.OTHER_FAILED,  '拒绝访问！您无权访问当前资源，如有问题请联系管理员。')
            return f(*args, **kwargs)
        return wrapper
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user.is_admin():
            return get_response(RequestCode.OTHER_FAILED,  '拒绝访问！您无权访问当前资源，如有问题请联系管理员。')
        return f(*args, **kwargs)
    return decorated_function


def access_permission_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user.can_access_zone(*args, **kwargs):
            return get_response(RequestCode.OTHER_FAILED,  '拒绝访问！您无权访问当前资源，如有问题请联系管理员。')
        return f(*args, **kwargs)
    return decorated_function


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return get_response(RequestCode.AUTH_FAILED,  '认证失败！')
        try: 
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
        except:
            return get_response(RequestCode.AUTH_FAILED,  '认证失败！')
        g.current_user = DBUser.query.filter_by(username=data.get('user')).first()
        if g.current_user is None:
            return get_response(RequestCode.AUTH_FAILED,  '认证失败！')
        if g.current_user.actived == 0:
            return get_response(RequestCode.AUTH_FAILED,  '对不起，您已经被管理员禁止登陆！')
        return f(*args, **kwargs)
    return decorated


def owner_or_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print(kwargs)
        if not (g.current_user.is_admin() or g.current_user.id == kwargs.get('user_id')):
            return get_response(RequestCode.OTHER_FAILED,  '拒绝访问！您无权访问当前资源，如有问题请联系管理员。')
        return f(*args, **kwargs)
    return decorated
