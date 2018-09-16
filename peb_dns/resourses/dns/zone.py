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



dns_zone_common_parser = reqparse.RequestParser()
dns_zone_common_parser.add_argument('name', 
                                    type = str, 
                                    location = 'json', 
                                    required=True, 
                                    help='zone name.')
dns_zone_common_parser.add_argument('zone_group', 
                                    type = int, 
                                    location = 'json', 
                                    required=True)
dns_zone_common_parser.add_argument('zone_type', 
                                    type = str, 
                                    location = 'json')
dns_zone_common_parser.add_argument('forwarders', 
                                    type = str, 
                                    location = 'json')
dns_zone_common_parser.add_argument('view_ids', 
                                    type = int, 
                                    location = 'json', 
                                    action='append')

zone_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'zone_group': fields.Integer,
    'zone_type': fields.String,
    'forwarders': fields.String,
    'view_name_list': fields.String,
    'can_update': fields.Boolean,
    'can_delete': fields.Boolean,
    'view_ids':fields.List(fields.Integer)
}

paginated_zone_fields = {
    'total': fields.Integer,
    'zones': fields.List(fields.Nested(zone_fields)),
    'current_page': fields.Integer
}

class DNSZoneList(Resource):
    method_decorators = [token_required] 

    def get(self):
        """
        功能：获取Zone资源列表
        ---
        security:
          - UserSecurity: []
        tags:
          - Zone
        parameters:
          - name: currentPage
            in: query
            description: Zone list in current page
            type: integer
            default: 1
          - name: pageSize
            in: query
            description: the number of zones per page.
            type: integer
            default: 30
          - name: id
            in: query
            description: Zone id
            type: integer
            default: 1
          - name: name
            type: string
            in: query
            description: the name of Zone
            default: z1.com
          - name: zone_group
            in: query
            type: integer
            description: the group current zone in.
            default: 1
            enum: [0, 1, 2]
          - name: zone_type
            in: query
            type: integer
            description: the id of role
            default: master
            enum: ['master', 'forward only']
        definitions:
          Zone:
            properties:
              total:
                type: integer
                description: the number of zones
              current_page:
                type: integer
                description: current page number
              zones:
                type: array
                items:
                  $ref: "#/definitions/Zone"
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
                  $ref: "#/definitions/Zone"
            examples:
                {
                    "code": 100000,
                    "data": {
                        "total": 5,
                        "zones": [
                            {
                                "id": 4,
                                "name": "xx1.com",
                                "zone_group": 1,
                                "zone_type": "master",
                                "forwarders": "",
                                "view_name_list": "['wqerqwer', 'vvvv111111111', 'jtest']",
                                "can_update": true,
                                "can_delete": true,
                                "view_ids": [
                                    1,
                                    2,
                                    5
                                ]
                            },
                            {
                                "id": 3,
                                "name": "xxx.com",
                                "zone_group": 1,
                                "zone_type": "forward only",
                                "forwarders": "0.0.0.0; 0.0.0.4;",
                                "view_name_list": "['vvvv111111111', 'wqerqwer']",
                                "can_update": true,
                                "can_delete": true,
                                "view_ids": [
                                    2,
                                    1
                                ]
                            }
                        ],
                        "current_page": 1
                    },
                    "msg": "获取成功！"
                }
        """
        args = request.args
        current_page = request.args.get('currentPage', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)
        id = args.get('id', type=int)
        name = args.get('name', type=str)
        zone_group = args.get('zone_group', type=int)
        zone_type = args.get('zone_type', type=str)
        zone_query = DBZone.query \
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
        if id is not None:
            zone_query = zone_query.filter(DBZone.id==id)
        if name is not None:
            zone_query = zone_query.filter(DBZone.name.like('%'+name+'%'))
        if zone_group is not None:
            zone_query = zone_query.filter(DBZone.zone_group==zone_group)
        if zone_type is not None:
            zone_query = zone_query.filter(DBZone.zone_type==zone_type)
        marshal_records = marshal(
                zone_query.order_by(DBZone.id.desc()).paginate(
                    current_page, 
                    page_size, 
                    error_out=False).items, zone_fields)
        results_wrapper = {
                    'total': zone_query.count(), 
                    'zones': marshal_records, 
                    'current_page': current_page
                    }
        response_wrapper_fields = get_response_wrapper_fields(fields.Nested(paginated_zone_fields))
        response_wrapper = get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)
        return marshal(response_wrapper, response_wrapper_fields)

    @indicated_privilege_required(DefaultPrivilege.ZONE_ADD)
    def post(self):
        """
        功能：创建新的Zone
        ---
        security:
          - UserSecurity: []
        tags:
          - Zone
        definitions:
          Zone_Parm:
            properties:
              name:
                type: string
                default: p123
                description: zone name
              zone_group:
                type: integer
                default: 1
                description: the group of the zone, 0=外部域名，1=内部域名，2=劫持域名
              zone_type:
                type: string
                default: master
                description: the type of zone
                enum: ['master', 'forward only']
              forwarders:
                type: integer
                default: 0.0.0.0
                description: the forwarders' ip when zone_type value is 'forward only'
              view_ids:
                type: array
                description: the id of views which the zone will be related to.
                items:
                  type: integer
        parameters:
          - in: body
            name: body
            schema:
              id: Add_Zone
              required:
                - name
              $ref: "#/definitions/Zone_Parm"
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
        args = dns_zone_common_parser.parse_args()
        zone_group = args['zone_group']
        if zone_group in (1, 2):
            view_ids = args['view_ids']
            unique_zone = db.session.query(DBZone).filter(
                        and_(DBZone.name==args['name'].strip(), 
                        DBZone.zone_group.in_((1,2)))).first()
            if unique_zone:
                return get_response(RequestCode.OTHER_FAILED,  '创建失败！重复的Zone！！相同名字的Zone，\
                            每种类型域名下只能存在一个！')
            if args['zone_type'] == 'forward only':
                args['forwarders'] = '; '.join(
                        [ip.strip() for ip in args['forwarders'].strip().split()]) + ';'
            del args['view_ids']
            new_zone = DBZone(**args)
            db.session.add(new_zone)
            db.session.flush()
            for view_id in view_ids:
                v = DBViewZone(
                        view_id=int(view_id),
                        zone_id=new_zone.id
                        )
                db.session.add(v)
        elif zone_group == 0:
            new_zone = DBZone(name=args['name'], zone_group=zone_group)
            db.session.add(new_zone)
            db.session.flush()
        log = DBOperationLog(
                    operation_type='添加', 
                    operator=g.current_user.username, 
                    target_type='Zone', 
                    target_name=new_zone.name, \
                    target_id=int(new_zone.id), 
                    target_detail=new_zone.get_content_str()
                    )
        db.session.add(log)
        try:
            new_zone.create()
            self._add_privilege_for_zone(new_zone)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  "创建失败！")
        return get_response(RequestCode.SUCCESS, '创建成功！')


    def _add_privilege_for_zone(self, new_zone):
        """Add privilege for the new zone."""
        access_privilege_name =  'ZONE#' + new_zone.name + \
                        '#' + OPERATION_STR_MAPPING[Operation.ACCESS]
        update_privilege_name =  'ZONE#' + new_zone.name + \
                        '#' + OPERATION_STR_MAPPING[Operation.UPDATE]
        delete_privilege_name =  'ZONE#' + new_zone.name + \
                        '#' + OPERATION_STR_MAPPING[Operation.DELETE]
        access_privilege = DBPrivilege(
                            name=access_privilege_name, 
                            resource_type=ResourceType.ZONE, 
                            operation=Operation.ACCESS, 
                            resource_id=new_zone.id
                            )
        update_privilege = DBPrivilege(
                            name=update_privilege_name, 
                            resource_type=ResourceType.ZONE, 
                            operation=Operation.UPDATE, 
                            resource_id=new_zone.id
                            )
        delete_privilege = DBPrivilege(
                            name=delete_privilege_name, 
                            resource_type=ResourceType.ZONE, 
                            operation=Operation.DELETE, 
                            resource_id=new_zone.id
                            )
        db.session.add(access_privilege)
        db.session.add(update_privilege)
        db.session.add(delete_privilege)
        db.session.flush()
        for role in ['admin', 'zone_admin', 'zone_guest']:
            role_access =  DBRolePrivilege(
                                role_id=ROLE_MAPPINGS[role],
                                privilege_id=access_privilege.id)
            db.session.add(role_access)
            if role not in ['zone_guest']:
                role_update =  DBRolePrivilege(
                                    role_id=ROLE_MAPPINGS[role],
                                    privilege_id=update_privilege.id)
                role_delete =  DBRolePrivilege(
                                    role_id=ROLE_MAPPINGS[role],
                                    privilege_id=delete_privilege.id)
                db.session.add(role_update)
                db.session.add(role_delete)


class DNSZone(Resource):
    method_decorators = [token_required]

    @resource_exists_required(ResourceType.ZONE)
    @permission_required(ResourceType.ZONE, Operation.ACCESS)
    def get(self, zone_id):
        """
        功能：获取指定ID的Zone详情
        ---
        security:
          - UserSecurity: []
        tags:
          - Zone
        parameters:
          - name: zone_id
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
        current_zone = DBZone.query.get(zone_id)
        results_wrapper = marshal(current_zone, zone_fields)
        return get_response(RequestCode.SUCCESS, '获取成功！', results_wrapper)
        
    @resource_exists_required(ResourceType.ZONE)
    @permission_required(ResourceType.ZONE, Operation.UPDATE)
    def put(self, zone_id):
        """
        功能：修改指定ID的Zone
        ---
        security:
          - UserSecurity: []
        tags:
          - Zone
        parameters:
          - name: zone_id
            in: path
            description: zone id
            type: integer
            required: true
            default: 1
          - in: body
            name: body
            schema:
              id: Update_Zone
              $ref: "#/definitions/Zone_Parm"
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
        current_zone = DBZone.query.get(zone_id)
        args = dns_zone_common_parser.parse_args()
        try:
            self._update_zone(current_zone, args)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '修改失败！')
        return get_response(RequestCode.SUCCESS, '修改成功！')

    @resource_exists_required(ResourceType.ZONE)
    @permission_required(ResourceType.ZONE, Operation.DELETE)
    def delete(self, zone_id):
        """
        功能: 删除指定ID的Zone
        ---
        security:
          - UserSecurity: []
        tags:
          - Zone
        parameters:
          - name: zone_id
            in: path
            description: Zone id
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
        current_zone = DBZone.query.get(zone_id)
        try:
            self._remove_zone_privileges(current_zone)
            self._delete_zone(current_zone)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return get_response(RequestCode.OTHER_FAILED,  '删除失败！')
        return get_response(RequestCode.SUCCESS, '删除成功！')

    def _update_zone(self, current_zone, args):
        pre_views = current_zone.view_name_list
        log = DBOperationLog(
                    operation_type='修改', 
                    operator=g.current_user.username, 
                    target_type='Zone', 
                    target_name=current_zone.name,
                    target_id=int(current_zone.id), 
                    target_detail=current_zone.get_content_str(prefix="修改前：")
                    )
        db.session.add(log)
        if args['zone_type'] == 'forward only':
            current_zone.forwarders = '; '.join(
                    [ip.strip() for ip in args['forwarders'].strip().split()]) \
                    + ';'
        current_zone.name = args['name']
        current_zone.zone_group = args['zone_group']
        current_zone.zone_type = args['zone_type']
        db.session.add(current_zone)

        current_view_zones = DBViewZone.query.filter(
                    DBViewZone.zone_id==current_zone.id).all()
        for cvz in current_view_zones:
            db.session.delete(cvz)
        for view_id in args['view_ids']:
            vz = DBViewZone(zone_id=current_zone.id, view_id=int(view_id))
            db.session.add(vz)
        db.session.flush()
        current_zone.modify(pre_views)


    def _delete_zone(self, current_zone):
        log = DBOperationLog(
                    operation_type='删除', 
                    operator=g.current_user.username, 
                    target_type='Zone', 
                    target_name=current_zone.name,
                    target_id=int(current_zone.id), 
                    target_detail=current_zone.get_content_str(prefix="修改前：")
                    )
        db.session.add(log)
        current_zone.delete()
        DBViewZone.query.filter(DBViewZone.zone_id==current_zone.id).delete()
        DBRecord.query.filter(DBRecord.zone_id == current_zone.id).delete()
        db.session.delete(current_zone)
        


    def _remove_zone_privileges(self, current_zone):
        """Remove all the privileges from the indicated zone."""
        current_zone_records = DBRecord.query.filter(
                    DBRecord.zone_id == current_zone.id).all()
        for current_zone_record in current_zone_records:
            self._remove_record_privileges(current_zone, current_zone_record)
        current_zone_privileges_query = DBPrivilege.query.filter(
                    DBPrivilege.resource_id==current_zone.id, 
                    DBPrivilege.resource_type==ResourceType.ZONE
                    )
        current_zone_privileges = current_zone_privileges_query.all()
        for zone_privilege in current_zone_privileges:
            DBRolePrivilege.query.filter(
                    DBRolePrivilege.privilege_id == zone_privilege.id
                    ).delete()
        current_zone_privileges_query.delete()


    def _remove_record_privileges(self, current_zone, current_record):
        """Remove privilege from records which belong to the indicated zone."""
        current_record_privileges_query = DBPrivilege.query.filter(
                    DBPrivilege.resource_id==current_record.id, 
                    DBPrivilege.resource_type==ResourceType.RECORD
                    )
        current_record_privileges = current_record_privileges_query.all()
        for record_privilege in current_record_privileges:
            DBRolePrivilege.query.filter(
                    DBRolePrivilege.privilege_id == record_privilege.id
                    ).delete()
        current_record_privileges_query.delete()



