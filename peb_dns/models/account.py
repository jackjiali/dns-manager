from flask import current_app, request
from peb_dns.extensions import db
from sqlalchemy import and_, or_
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING, DefaultPrivilege
from .dns import DBZone, DBView, DBRecord, DBDNSServer

RESOURCE_TYPE_MAPPING = {
    ResourceType.ZONE: DBZone,
    ResourceType.VIEW: DBView,
    ResourceType.RECORD: DBRecord,
    ResourceType.SERVER: DBDNSServer
}

class DBUser(db.Model):
    __tablename__ = 'account_user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), default='')
    username = db.Column(db.String(64), unique=True, index=True)
    chinese_name = db.Column(db.String(64), default='')
    cellphone = db.Column(db.String(64), default='')
    actived = db.Column(db.Integer, default=1)
    position = db.Column(db.String(64), default='')
    location = db.Column(db.String(64), default='')
    member_since = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.now)

    def to_json(self):
        json_user = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'chinese_name': self.chinese_name,
            'cellphone': self.cellphone,
            'position': self.position,
            'location': self.location,
            'can_add_server': self.can_add_server,
            'can_add_view': self.can_add_view,
            'can_add_zone': self.can_add_zone,
            'member_since': str(self.member_since)
        }
        return json_user

    def can(self, privilege):
        current_user_privileges = db.session.query(DBPrivilege) \
            .join(DBRolePrivilege, and_(
                DBPrivilege.id == DBRolePrivilege.privilege_id, 
                DBPrivilege.name == privilege)) \
            .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
            .join(DBUserRole, and_(DBUserRole.role_id == DBRole.id)) \
            .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
            .filter(DBUser.id == self.id).all()
        for current_user_privilege in current_user_privileges:
            if privilege == current_user_privilege.name:
                return True
        return False

    def is_admin(self):
        admins = db.session.query(DBRole).join(
            DBUserRole, and_(DBUserRole.role_id == DBRole.id, DBRole.name == "admin")) \
            .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
            .filter(DBUser.id == self.id).all()
        if admins:
            return True
        return False

    @property
    def can_add_server(self):
        return self.can(DefaultPrivilege.SERVER_ADD)

    @property
    def can_add_view(self):
        return self.can(DefaultPrivilege.VIEW_ADD)

    @property
    def can_add_zone(self):
        return self.can(DefaultPrivilege.ZONE_ADD)

    @property
    def can_edit_bind_conf(self):
        return self.can(DefaultPrivilege.BIND_CONF_EDIT)

    def can_access_log(self):
        return self.can(DefaultPrivilege.LOG_PAGE_ACCESS)

    @property
    def roles(self):
        return db.session.query(DBRole).join(
            DBUserRole, and_(DBUserRole.role_id == DBRole.id)) \
            .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
            .filter(DBUser.id == self.id).all()

    @property
    def role_ids(self):
        return [r.id for r in db.session.query(DBRole).join(
            DBUserRole, and_(DBUserRole.role_id == DBRole.id)) \
            .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
            .filter(DBUser.id == self.id).all()]

    @roles.setter
    def roles(self, role_ids):
        for role_id in role_ids:
            current_user_new_role = DBUserRole(user_id=self.id, role_id=role_id)
            db.session.add(current_user_new_role)

    def can_do(self, operation, resource_type, resource_id):
        r = RESOURCE_TYPE_MAPPING.get(resource_type)
        current_user_resources = db.session.query(r) \
            .join(DBPrivilege, and_(
                r.id == resource_id, 
                r.id == DBPrivilege.resource_id, 
                DBPrivilege.resource_type == resource_type, 
                DBPrivilege.operation == operation)) \
            .join(DBRolePrivilege, and_(DBPrivilege.id == DBRolePrivilege.privilege_id)) \
            .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
            .join(DBUserRole, and_(DBUserRole.role_id == DBRole.id)) \
            .join(DBUser, and_(DBUser.id == DBUserRole.user_id)) \
            .filter(DBUser.id == self.id).all()
        if current_user_resources:
            return True
        return False


class DBLocalAuth(db.Model):
    __tablename__ = 'account_local_auth'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128)) 
    email = db.Column(db.String(128)) 

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class DBUserRole(db.Model):
    __tablename__ = 'account_user_role'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    role_id = db.Column(db.Integer, index=True)


class DBRole(db.Model):
    __tablename__ = 'account_role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<DBRole %r>' % self.name

    @property
    def users(self):
        return db.session.query(DBUser).join(
            DBUserRole, and_(DBUserRole.user_id == DBUser.id)) \
            .join(DBRole, and_(DBRole.id == DBUserRole.role_id)) \
            .filter(DBRole.id == self.id).all()

    @property
    def privileges(self):
        return db.session.query(DBPrivilege).join(
            DBRolePrivilege, and_(DBRolePrivilege.privilege_id == DBPrivilege.id)) \
            .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
            .filter(DBRole.id == self.id).all()

    @property
    def privilege_ids(self):
        return [p.id for p in db.session.query(DBPrivilege).join(
            DBRolePrivilege, and_(DBRolePrivilege.privilege_id == DBPrivilege.id)) \
            .join(DBRole, and_(DBRole.id == DBRolePrivilege.role_id)) \
            .filter(DBRole.id == self.id).all()]

    @privileges.setter
    def privileges(self, privilege_ids):
        for privilege_id in privilege_ids:
            current_role_new_privilege = DBRolePrivilege(
                        role_id=self.id, privilege_id=privilege_id)
            db.session.add(current_role_new_privilege)


class DBRolePrivilege(db.Model):
    __tablename__ = 'account_role_privilege'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, index=True)
    privilege_id = db.Column(db.Integer, index=True)


#权限表
class DBPrivilege(db.Model):
    __tablename__ = 'account_privilege'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    operation = db.Column(db.Integer, default=100)
    resource_type = db.Column(db.Integer, default=100)
    resource_id = db.Column(db.Integer, default=0, index=True)
    comment = db.Column(db.String(128))


account_models = {
    ResourceType.USER: DBUser,
    ResourceType.ROLE: DBRole,
    ResourceType.PRIVILEGE: DBPrivilege,
}