from peb_dns import create_app
from peb_dns.extensions import mail, db
from peb_dns.models.mappings import Operation, ResourceType, OPERATION_STR_MAPPING, ROLE_MAPPINGS, DefaultPrivilege
from peb_dns.models.account import DBUser, DBUserRole, DBRole, DBLocalAuth, \
                            DBPrivilege, DBRolePrivilege
from peb_dns.models.dns import DBView
from peb_dns.common.util import getETCDclient
import etcd
import time

app = create_app()


def init_privilege():
    """init the default privilege data when you first time start the app."""
    privilege_count = db.session.query(DBPrivilege).count()
    if privilege_count < 1:
        print('initing the default privileges...')
        default_privileges = [
            DefaultPrivilege.SERVER_ADD,
            DefaultPrivilege.ZONE_ADD,
            DefaultPrivilege.VIEW_ADD,
            DefaultPrivilege.BIND_CONF_EDIT
            ]
        for p in default_privileges:
            new_p = DBPrivilege(name=p)
            db.session.add(new_p)
            db.session.flush()
            admin_rp =  DBRolePrivilege(
                                role_id=ROLE_MAPPINGS['admin'],
                                privilege_id=new_p.id
                                )
            db.session.add(admin_rp)
            if p == DefaultPrivilege.SERVER_ADD:
                server_admim_rp =  DBRolePrivilege(
                                    role_id=ROLE_MAPPINGS['server_admin'],
                                    privilege_id=new_p.id
                                    )
                db.session.add(server_admim_rp)
            if p == DefaultPrivilege.ZONE_ADD:
                zone_admin_rp =  DBRolePrivilege(
                                    role_id=ROLE_MAPPINGS['zone_admin'],
                                    privilege_id=new_p.id
                                    )
                db.session.add(zone_admin_rp)
            if p == DefaultPrivilege.VIEW_ADD:
                view_admin_rp =  DBRolePrivilege(
                                    role_id=ROLE_MAPPINGS['view_admin'],
                                    privilege_id=new_p.id
                                    )
                db.session.add(view_admin_rp)

def init_user_role(app):
    """init the default user and role data when you first time start the app."""
    auth_user_count = db.session.query(DBLocalAuth).count()
    local_user_count = db.session.query(DBUser).count()
    if auth_user_count < 1 and local_user_count < 1:
        print('initing the default users...')
        default_admin = DBLocalAuth(
            id=ROLE_MAPPINGS['admin'], 
            username=app.config.get("DEFAULT_ADMIN_USERNAME"),
            email=app.config.get("DEFAULT_ADMIN_EMAIL")
            )
        default_admin.password = app.config.get("DEFAULT_ADMIN_PASSWD")
        default_admin_local = DBUser(
            id=ROLE_MAPPINGS['admin'], 
            username=app.config.get("DEFAULT_ADMIN_USERNAME"),
            email=app.config.get("DEFAULT_ADMIN_EMAIL")
            )
        db.session.add(default_admin)
        db.session.add(default_admin_local)
    role_count = db.session.query(DBRole).count()
    if role_count < 1:
        print('initing the default roles...')
        for k,v in ROLE_MAPPINGS.items():
            new_role = DBRole(id=v, name=k)
            db.session.add(new_role)
    user_role_count = db.session.query(DBUserRole).count()
    if role_count < 1:
        admin_user_role = DBUserRole(
            id=ROLE_MAPPINGS['admin'], 
            user_id=ROLE_MAPPINGS['admin'], 
            role_id=ROLE_MAPPINGS['admin'], 
            )
        db.session.add(admin_user_role)


def add_privilege_for_view(new_view):
    """Add privilege for the new view."""
    access_privilege_name =  'VIEW#' + new_view.name + \
                '#' + OPERATION_STR_MAPPING[Operation.ACCESS]
    update_privilege_name =  'VIEW#' + new_view.name + \
                '#' + OPERATION_STR_MAPPING[Operation.UPDATE]
    delete_privilege_name =  'VIEW#' + new_view.name + \
                '#' + OPERATION_STR_MAPPING[Operation.DELETE]
    access_privilege = DBPrivilege(
                        name=access_privilege_name, 
                        resource_type=ResourceType.VIEW, 
                        operation=Operation.ACCESS, 
                        resource_id=new_view.id
                        )
    update_privilege = DBPrivilege(
                        name=update_privilege_name, 
                        resource_type=ResourceType.VIEW, 
                        operation=Operation.UPDATE, 
                        resource_id=new_view.id
                        )
    delete_privilege = DBPrivilege(
                        name=delete_privilege_name, 
                        resource_type=ResourceType.VIEW, 
                        operation=Operation.DELETE, 
                        resource_id=new_view.id
                        )
    db.session.add(access_privilege)
    db.session.add(update_privilege)
    db.session.add(delete_privilege)
    db.session.flush()
    for role in ['admin', 'view_admin', 'view_guest']:
        role_access =  DBRolePrivilege(
                            role_id=ROLE_MAPPINGS[role],
                            privilege_id=access_privilege.id)
        db.session.add(role_access)
        if role not in ['view_guest']:
            role_update =  DBRolePrivilege(
                                role_id=ROLE_MAPPINGS[role],
                                privilege_id=update_privilege.id)
            role_delete =  DBRolePrivilege(
                                role_id=ROLE_MAPPINGS[role],
                                privilege_id=delete_privilege.id)
            db.session.add(role_update)
            db.session.add(role_delete)

def init_view(app):
    view_count = db.session.query(DBView).count()
    if view_count < 1:
        print('initing the default views...')
        default_view = DBView(
            id=1,
            name='default_view',
            acl='0.0.0.0/0'
        )
        db.session.add(default_view)
        add_privilege_for_view(default_view)
        view_list = db.session.query(DBView).all()
        default_view.make_view('create', view_list)

def init_bind_config(app):
    client = getETCDclient()
    print('initing etcd data...')
    try:
        client.read(app.config.get('BIND_CONF'))
    except etcd.EtcdKeyNotFound:
        client.write(app.config.get('BIND_CONF'),
                    app.config.get('DEFAULT_BIND_CONF_CONTENT'), 
                    prevExist=False)
        time.sleep(1)
    try:
        client.read(app.config.get('VIEW_DEFINE_CONF'))
    except etcd.EtcdKeyNotFound:
        client.write(app.config.get('VIEW_DEFINE_CONF'), 
                    '', 
                    prevExist=False)
        time.sleep(1)

@app.cli.command('initdb')
def initdb_command():
    """init the default data in database when you first time start the app."""
    with app.app_context(): 
        init_user_role(app)
        init_privilege()
        db.session.flush()
        init_bind_config(app)
        init_view(app)
        db.session.commit()
    print('done.')


@app.cli.command('init_etcd')
def init_etcd_command():
    """init the default data in etcd when you first time start the app."""
    with app.app_context(): 
        init_bind_config(app)
    print('done.')