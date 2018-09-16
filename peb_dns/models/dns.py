from flask import current_app, request, g
from peb_dns.extensions import db
from sqlalchemy.sql import and_, or_, not_
from datetime import datetime
from collections import OrderedDict
from jinja2 import Template
import jwt
import hashlib
import copy
import requests
import etcd
import time
from peb_dns.common.util import getETCDclient, ZBapi
from peb_dns.common.request_code import RequestCode
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING


ZONE_GROUP_MAPPING = {
    0:"外部域名",
    1:"内部域名",
    2:"劫持域名"
}

class DBView(db.Model):
    __tablename__ = 'dns_view'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    acl = db.Column(db.Text())
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)

    # def __init__(self, **kwargs):
    #     super(DBView, self).__init__(**kwargs)

    def __repr__(self):
        return '<DBView %r>' % self.name

    @property
    def zones(self):
        related_zones = db.session.query(DBZone).join(
            DBViewZone, and_(DBViewZone.zone_id == DBZone.id)) \
            .join(DBView, and_(DBView.id == DBViewZone.view_id)) \
            .filter(DBView.id == self.id).all()
        if not related_zones:
            return []
        return related_zones

    @property
    def zone_name_list(self):
        return [v.name for v in self.zones]

    def get_content_str(self, prefix=None):
        content = 'id: ' + str(self.id) + '\n' \
        + 'View名称: ' + str(self.name) + '\n' \
        + 'ACL: ' + str(self.acl) + '\n'

        if prefix:
            content = prefix + '\n' + content
        return content

    @property
    def can_update(self):
        return g.current_user.can_do(
                Operation.UPDATE, ResourceType.VIEW, self.id)

    @property
    def can_delete(self):
        return g.current_user.can_do(
                Operation.DELETE, ResourceType.VIEW, self.id)

    def make_view(self, action, view_list):
        prevExist = True
        if action == 'create':
            prevExist = False
        etcd_client = getETCDclient()
        if action == 'del':
            view_base_dir = current_app.config.get('ETCD_BASE_DIR') + self.name
            etcd_client.delete(view_base_dir, recursive=True)
            print(view_base_dir)
            time.sleep(0.5)
            # return
        if action == 'create':
            view_zone_conf = current_app.config.get('ETCD_BASE_DIR') + self.name + '/view.conf'
            view_zone_conf_content = Template(
                        current_app.config.get('VIEW_TEMPLATE')).render(view_name=self.name)
            etcd_client.write(view_zone_conf, view_zone_conf_content, prevExist=prevExist)
            time.sleep(0.5)   #连续几个提交速度过快，etcd server检测不到提交

        if action == 'create' or action == 'del':
            view_define_conf_content = Template(
                current_app.config.get('VIEW_DEFINE_TEMPLATE')).render(view_list=view_list)
            etcd_client.write(
                current_app.config.get('VIEW_DEFINE_CONF'), 
                view_define_conf_content, 
                prevExist=True)
            time.sleep(0.5)

        if action == 'create' or action == 'modify':
            acl_conf = current_app.config.get('ETCD_BASE_DIR') + self.name + '/acl.conf'
            acl_conf_content = Template(current_app.config.get('ACL_TEMPLATE')).render(
                view_name=self.name, ip_list=self.acl.split())
            etcd_client.write(acl_conf, acl_conf_content, prevExist=prevExist)
            time.sleep(0.5)


class DBViewZone(db.Model):
    __tablename__ = 'dns_view_zone'
    id = db.Column(db.Integer, primary_key=True)
    view_id = db.Column(db.Integer, index=True)
    zone_id = db.Column(db.Integer, index=True)
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)


class DBZone(db.Model):
    __tablename__ = 'dns_zone'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    zone_group = db.Column(db.Integer, default=1)
    zone_type = db.Column(db.String(64), default='')
    forwarders = db.Column(db.String(64), default='')
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)

    def create(self):
        if self.zone_group in [1, 2]:
            self._create_inner()
        else:
            self._create_outter()

    def modify(self, pre_views):
        if self.zone_group in [1, 2]:
            self._modify_inner(pre_views)
        else:
            self._modify_outter()

    def delete(self):
        if self.zone_group in [1, 2]:
            self._del_inner()
        else:
            self._del_outter()

    @property
    def can_update(self):
        return g.current_user.can_do(Operation.UPDATE, ResourceType.ZONE, self.id)

    @property
    def can_delete(self):
        return g.current_user.can_do(Operation.DELETE, ResourceType.ZONE, self.id)

    @property
    def can_access(self):
        return g.current_user.can_do(Operation.ACCESS, ResourceType.ZONE, self.id)

    @property
    def views(self):
        # print(self.id)
        related_views = DBView.query\
            .join(DBViewZone, and_(DBViewZone.view_id == DBView.id))\
            .join(DBZone, and_(DBZone.id == DBViewZone.zone_id))\
            .filter(DBZone.id == self.id).all()
        # print('xxxxxxxxxxxx -- ' + str(db.session.query(DBView).all()))
        if related_views:
            return related_views
        return []

    @property
    def view_name_list(self):
        return [v.name for v in self.views]

    @property
    def view_ids(self):
        return [v.id for v in self.views]

    def get_content_str(self, prefix=None):
        if self.zone_group == 0:
            related_view_list = ''
        if self.zone_group in [1, 2]:
            related_view_list = str(self.view_name_list)
        content = 'id: ' + str(self.id) + '\n' \
        + 'Zone名称: ' + str(self.name) + '\n' \
        + 'Zone归属: ' + ZONE_GROUP_MAPPING.get(self.zone_group) + '\n' \
        + 'Zone类型: ' + str(self.zone_type) + '\n' \
        + '关联View: ' + related_view_list + '\n' 
        if prefix:
            content = prefix + '\n' + content
        return content

    def _create_inner(self):
        for related_view in self.view_name_list:
            ns_record = DBRecord(host='@', record_type='NS', value='master.'+self.name+'.' ,
                    ttl='86400', view_name=related_view, creator=g.current_user.username, 
                    zone_id=self.id)
            db.session.add(ns_record)
        zone_list = db.session.query(DBZone).filter(
            or_(DBZone.zone_group == 1, DBZone.zone_group == 2)).all()
        for z_view in self.view_name_list:
            self._make_zone('create', z_view, zone_list, [])
            time.sleep(0.5)

    def _create_outter(self):
        create_url = current_app.config.get('DNSPOD_DOMAIN_BASE_URL') + 'Create'
        res = requests.post(create_url,
                    data=dict(login_token=current_app.config.get('DNSPOD_TOKEN'),
                    domain=self.name, 
                    format=current_app.config.get('DNSPOD_DATA_FORMAT')))
        if res.status_code == 200:
            res_json = res.json()
            if res_json.get('status').get('code') == '1':
                return
        raise Exception(str(res_json))

    def _modify_inner(self, pre_views):
        zone_list = db.session.query(DBZone).filter(or_(DBZone.zone_group == 1, 
                    DBZone.zone_group == 2)).all()
        current_views = set(self.view_name_list)
        pre_views = set(pre_views)
        # 清除当前zone 解除绑定view所对应的record
        del_views = pre_views - current_views
        del_records = db.session.query(DBRecord).filter(
            DBRecord.zone_id==self.id, 
            DBRecord.view_name.in_(tuple(del_views))
            ).all()
        for del_record in del_records:
            db.session.delete(del_record)
        # 添加当前zone新增绑定view时候，所对应的默认record （默认host为@的record）
        add_views = current_views - pre_views
        for add_view in add_views:
            ns_record = DBRecord(host='@', record_type='NS', 
                    value='master.'+self.name+'.' , 
                    ttl='86400', view_name=add_view, 
                    creator=g.current_user.username, zone_id=self.id)
            db.session.add(ns_record)
        for del_view in del_views:
            self._make_zone('del', del_view, zone_list, [])
        for z_view in current_views:
            record_list = db.session.query(DBRecord).filter(
                DBRecord.zone_id == self.id, 
                DBRecord.view_name == z_view.strip(), 
                DBRecord.host != '@'
                ).all()
            self._make_zone('modify', z_view, zone_list, record_list)

    def _modify_outter(self):
        raise Exception('外部域名不支持修改！')

    def _del_inner(self):
        zone_list = db.session.query(DBZone).filter(
            or_(DBZone.zone_group == 1, DBZone.zone_group == 2)
            ).all()
        # print("zone_list  --  " + str(zone_list))
        # print("self.view_name_list  --  " + str(self.view_name_list))
        for z_view in self.view_name_list:
            self._make_zone('del', z_view, zone_list, [])

    def _del_outter(self):
        delete_url = current_app.config.get('DNSPOD_DOMAIN_BASE_URL') + 'Remove'
        res = requests.post(delete_url, data=dict(
            login_token=current_app.config.get('DNSPOD_TOKEN'), 
            domain=self.name, 
            format=current_app.config.get('DNSPOD_DATA_FORMAT'))
            )
        if res.status_code == 200:
            res_json = res.json()
            if res_json.get('status').get('code') == '1':
                return
        raise Exception(str(res_json))

    def _make_zone(self, action, view_name, zone_list, record_list):
        etcd_client = getETCDclient()
        view_zone_conf = current_app.config.get('ETCD_BASE_DIR') + view_name + '/view.conf'
        bind_zones = []
        if action == 'del':
            for zz in zone_list:
                if view_name in zz.view_name_list and zz.name != self.name :
                    bind_zones.append(zz)
        else:
            for zz in zone_list:
                if view_name in zz.view_name_list:
                    bind_zones.append(zz)
        # print(view_name)
        # print(bind_zones)
        view_zone_conf_content = Template(
            current_app.config.get('ZONE_TEMPLATE')
            ).render(
            view_name=view_name, zone_list=bind_zones
            )
        etcd_client.write(view_zone_conf, view_zone_conf_content, prevExist=True)
        time.sleep(0.5)
        # view_zone_confiig 文件操作
        # forward only类型的zone，不生成 zone.xx.xx 文件
        # 修改zone不需要更改zone.xx.xx 文件
        if self.zone_type != 'forward only':
            zone_record_conf = current_app.config.get('ZONE_BASE_DIR') + \
                    view_name + '/zone.' + self.name
            if action == 'create' or action == 'modify':
                zone_record_conf_content = Template(
                    current_app.config.get('RECORD_TEMPLATE')).render(
                    zone_name=self.name, record_list=record_list)
                try:
                    etcd_client.write(
                        zone_record_conf, zone_record_conf_content, prevExist=True)
                except etcd.EtcdKeyNotFound:
                    zone_record_conf_content = Template(
                        current_app.config.get('RECORD_TEMPLATE')).render(
                        zone_name=self.name, record_list=[])
                    etcd_client.write(
                        zone_record_conf, zone_record_conf_content, prevExist=False)
                time.sleep(0.5)
            elif action == 'del':
                # print(zone_record_conf)
                etcd_client.delete(zone_record_conf)
                time.sleep(0.5)


class DBRecord(db.Model):
    __tablename__ = 'dns_record'
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(64), index=True)
    record_type = db.Column(db.String(64))
    ttl = db.Column(db.String(64))
    value = db.Column(db.String(64))
    view_name = db.Column(db.String(64), default='')
    comment = db.Column(db.String(64))
    creator = db.Column(db.String(64))
    status = db.Column(db.String(64), default='enabled')
    enabled = db.Column(db.String(64), default='1')
    alive = db.Column(db.String(64), default='ON')
    outter_record_id = db.Column(db.String(64), default='')
    zone_id = db.Column(db.Integer, index=True)
    full_domain_name = db.Column(db.String(128), index=True, nullable=False, default='')
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)

    @property
    def can_update(self):
        return g.current_user.can_do(Operation.UPDATE, ResourceType.ZONE, self.zone_id)

    @property
    def can_delete(self):
        return g.current_user.can_do(Operation.DELETE, ResourceType.ZONE, self.zone_id)
    
    @property
    def can_access(self):
        return g.current_user.can_do(Operation.ACCESS, ResourceType.ZONE, self.zone_id)

    @property
    def zone(self):
        return DBZone.query.get(self.zone_id)

    def create(self, current_zone, args, v_name):
        if current_zone.zone_group in [1, 2]:
            record_list = db.session.query(DBRecord).filter(
                DBRecord.zone_id == args['zone_id'], 
                DBRecord.view_name == v_name, DBRecord.host != '@'
                ).all()
            self._make_record(current_zone.name, record_list)
        else:
            create_url = current_app.config.get('DNSPOD_RECORD_BASE_URL') + 'Create'
            dnspod_data = {
                'domain': current_zone.name, 
                'sub_domain':args['host'], 
                'record_type':args['record_type'],
                'record_line':args['view_name'], 
                'value':args['value'], 
                'ttl':args['ttl']
                }
            self._do_dnspod(create_url, dnspod_data)

    def update(self, current_zone, args):
        if current_zone.zone_group in [1, 2]:
            record_list = db.session.query(DBRecord).filter(
                DBRecord.zone_id == args['zone_id'], 
                DBRecord.view_name == args['view_name'], 
                DBRecord.host != '@'
                ).all()
            self._make_record(current_zone.name, record_list)
        else:
            modify_url = current_app.config.get('DNSPOD_RECORD_BASE_URL') + 'Modify'
            dnspod_data = {
                'domain': current_zone.name, 
                'record_id': self.outter_record_id, 
                'sub_domain':args['host'], 
                'record_type':args['record_type'],
                'record_line':args['view_name'], 
                'value':args['value'], 
                'ttl':args['ttl']
                }
            self._do_dnspod(modify_url, dnspod_data)

    def delete(self, current_zone):
        if current_zone.zone_group in [1, 2]:
            record_list = db.session.query(DBRecord).filter(
                DBRecord.zone_id == self.zone_id, 
                DBRecord.view_name == self.view_name, 
                DBRecord.host != '@'
                ).all()
            self._make_record(current_zone.name, record_list)
        else:
            delete_url = current_app.config.get('DNSPOD_RECORD_BASE_URL') + 'Remove'
            dnspod_data = {
                'domain': current_zone.name, 
                'record_id': self.outter_record_id
                }
            self._do_dnspod(delete_url, dnspod_data)

    def _make_record(self, zone_name, record_list):
        etcd_client = getETCDclient()
        zone_record_conf = current_app.config.get('ZONE_BASE_DIR') + \
                self.view_name + '/zone.' + zone_name
        zone_record_conf_content = Template(
            current_app.config.get('RECORD_TEMPLATE')).render(
                zone_name=zone_name, 
                record_list=record_list
                )
        etcd_client.write(
            zone_record_conf, zone_record_conf_content, prevExist=True)
        time.sleep(0.5)

    def _do_dnspod(self, url, data):
        body_info = {
            "login_token": current_app.config.get('DNSPOD_TOKEN'), 
            "format": current_app.config.get('DNSPOD_DATA_FORMAT')
            }
        res = requests.post(url, data=dict(body_info, **data))
        res_json = res.json()
        print(res_json)
        if res.status_code != 200:
            raise Exception(str(res_json))
        if res_json.get('status').get('code') != '1':
            raise Exception(str(res_json))
        if current_app.config.get('DNSPOD_RECORD_BASE_URL') + 'Create' == url:
            self.outter_record_id = res_json.get('record').get('id')
            db.session.add(self)
        
    def get_content_str(self, prefix=None):
        #'修改前内容：'
        content = 'id: ' + str(self.id) + '\n' \
        + '记录主机: ' + str(self.host) + '\n' \
        + '记录类型: ' + str(self.record_type) + '\n' \
        + '记录值: ' + str(self.value) + '\n' \
        + 'TTL: ' + str(self.ttl) + '\n' \
        + '线路类型: ' + str(self.view_name) + '\n' \
        + '备注: ' + str(self.comment) + '\n' \
        + '创建人: ' + str(self.creator) + '\n' \
        + '创建时间: ' + str(self.gmt_create)
        if prefix:
            content = prefix + '\n' + content
        return content

class DBDNSServer(db.Model):
    __tablename__ = 'dns_server'
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(64), index=True)
    ip = db.Column(db.String(64))
    env = db.Column(db.String(64))
    dns_server_type = db.Column(db.String(64))
    status = db.Column(db.String(64), default='INITING')
    zb_process_itemid = db.Column(db.String(64))
    zb_port_itemid = db.Column(db.String(64))
    zb_resolve_itemid = db.Column(db.String(64))
    zb_resolve_rate_itemid = db.Column(db.String(64))
    server_log = db.Column(db.Text())
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)

    @property
    def can_update(self):
        return g.current_user.can_do(
                    Operation.UPDATE, ResourceType.SERVER, self.id)

    @property
    def can_delete(self):
        return g.current_user.can_do(
                    Operation.DELETE, ResourceType.SERVER, self.id)

    def to_json(self):
        json_server = {
            'id': self.id,
            'host': self.host,
            'ip': self.ip,
            'env': self.env,
            'dns_type': self.dns_type,
            'status': self.status,
            'logs': self.logs
        }
        return json_server

    def get_server_status(self):        
        zb = ZBapi(self)
        server_status = zb.get_server_status()
        return server_status

    def get_resolve_rate(self, start_time, end_time):
        zb = ZBapi(self)
        resolve_rate = zb.get_resolve_rate(start_time, end_time)
        # resolve_rates.append({dns_server.host: resolve_rate})
        return resolve_rate

    def get_content_str(self, prefix=None):
        #'修改前内容：'
        content = 'id: ' + str(self.id) + '\n' \
        + '主机名: ' + str(self.host) + '\n' \
        + 'IP地址: ' + str(self.ip) + '\n' \
        + '环境: ' + str(self.env) + '\n' \
        + 'DNS类型: ' + str(self.dns_server_type) + '\n'
        if prefix:
            content = prefix + '\n' + content
        return content


class DBOperationLog(db.Model):
    __tablename__ = 'dns_operation_log'
    id = db.Column(db.Integer, primary_key=True)
    operation_time = db.Column(db.DateTime(), default=datetime.now)
    operation_type = db.Column(db.String(64))
    operator = db.Column(db.String(64))
    target_type = db.Column(db.String(64))
    target_name = db.Column(db.String(64))
    target_id = db.Column(db.String(64))
    target_detail = db.Column(db.Text())
    gmt_create = db.Column(db.DateTime(), default=datetime.now)
    gmt_modified = db.Column(db.DateTime(), default=datetime.now)

dns_models = {
    ResourceType.SERVER: DBDNSServer,
    ResourceType.VIEW: DBView,
    ResourceType.ZONE: DBZone,
    ResourceType.RECORD: DBRecord
}