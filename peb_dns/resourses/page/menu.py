from flask_restful import Api, Resource, url_for, reqparse, abort
from flask import current_app, g
from peb_dns.models.dns import DBView, DBViewZone, DBZone, DBOperationLog, DBRecord, DBDNSServer
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBRolePrivilege, DBPrivilege
from peb_dns.common.decorators import token_required, admin_required, permission_required, indicated_privilege_required, resource_exists_required
from peb_dns.common.util import getETCDclient, get_response, get_response_wrapper_fields
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING, ROLE_MAPPINGS, DefaultPrivilege

from peb_dns import db
from sqlalchemy import and_, or_
from datetime import datetime
from peb_dns.common.request_code import RequestCode



class MenuSidebar(Resource):

    method_decorators = [token_required]

    def __init__(self):
        self.get_reqparse = reqparse.RequestParser()
        super(MenuSidebar, self).__init__()

    def get(self):
        """Get the sidebar menu data."""
        menu_group = self._get_zones()
        menu_group['menu'].append({'title':'Zone管理', 'items':None, 'url':'/dns/zones'})
        menu_group['menu'].append({'title':'View管理', 'items':None, 'url':'/dns/views'})
        menu_group['menu'].append({'title':'DNS服务器', 'items':None, 'url':'/dns/servers'})
        if g.current_user.is_admin():
            admin_items = [
                {'item_name':'用户管理', 'url':'/admin/users'},
                {'item_name':'角色管理', 'url':'/admin/roles'},
                {'item_name':'权限管理', 'url':'/admin/privileges'}
            ]
            menu_group['menu'].append({'title':'后台管理', 'items': admin_items})
        menu_group['menu'].append({'title':'操作记录', 'items':None, 'url':'/dns/logs'})
        return get_response(RequestCode.SUCCESS, '获取成功！', menu_group)

    def _get_zones(self):
        zone_query = db.session.query(DBZone) \
            .join(DBPrivilege, and_(
                DBZone.id == DBPrivilege.resource_id, 
                DBPrivilege.resource_type == ResourceType.ZONE, 
                DBPrivilege.operation == Operation.ACCESS
                )) \
            .join(DBRolePrivilege, and_(
                DBPrivilege.id == DBRolePrivilege.privilege_id
                )) \
            .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
            .join(DBUserRole, and_(DBUserRole.role_id == DBRole.id)) \
            .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
            .filter(DBUser.id == g.current_user.id)
        inner_zones = [{'item_name':zone.name, 'url':'/#/dns/records/zoneId/'+ str(zone.id)} 
                for zone in zone_query.filter(DBZone.zone_group == 1).all()]
        intercepted_zones = [{'item_name':zone.name, 'url':'/#/dns/records/zoneId/'+ str(zone.id)} 
                for zone in zone_query.filter(DBZone.zone_group == 2).all()]
        outter_zones = [{'item_name':zone.name, 'url':'/#/dns/records/zoneId/'+ str(zone.id)} 
                for zone in zone_query.filter(DBZone.zone_group == 0).all()]
        zone_groups = {'menu' : [
                {'title':'内部域名', 'items':inner_zones},
                {'title':'劫持域名', 'items':intercepted_zones},
                {'title':'外部域名', 'items':outter_zones}
            ]
        }
        return zone_groups



