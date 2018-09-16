from flask import Flask, Blueprint, request, jsonify
from config.config import config, config_pyfiles
from flask_migrate import Migrate, MigrateCommand
from .extensions import mail, db
from flask_cors import CORS
from .resourses.account import auth_bp
from .resourses.admin import admin
from .resourses.dns import dns_bp
from .resourses.page import page_bp
import os
import click
from .common.util import get_response
from flasgger import Swagger

APP_NAME = 'DNS-Manager'

def configure_extensions(app):
    mail.init_app(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    Swagger(app, template=app.config['SWAGGER_TEMPLATE'])

def configure_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

def configure_error_handlers(app):
    @app.errorhandler(400)
    def valid_request_args(error):
        return jsonify(message='服务器无法理解此请求！'), 400

    @app.errorhandler(401)
    def login_required(error):
        return jsonify(message="请先进行认证！"), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify(message="无权限！"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify(message="您访问的资源/页面不存在！"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return jsonify(message="非常抱歉，服务器内部出错！"), 500

def configure_hooks(app):
    pass

def configure_crossdomain(app):
    CORS(app, supports_credentials=True)

def configure_data(app):
    env = os.environ
    app_config = app.config
    ZABBIX_POST_DATA = {
        "jsonrpc": "2.0",
        "method": "history.get",
        "params": {
            "output": "extend",
            "history": 3,
            "itemids": "",
            "sortfield": "clock",
            "sortorder": "DESC",
            "limit": 1
        },
        "auth": "",
        "id": 1
    }
    SQLALCHEMY_DATABASE_URI = \
    "mysql+mysqlconnector://{db_username}:{db_passwd}@{db_host}/{db_name}?charset=utf8".format(
        db_username = env.get('DB_USERNAME', app_config.get('DB_USERNAME')),
        db_passwd = env.get('DB_PASSWORD', app_config.get('DB_PASSWORD')),
        db_host = env.get('DB_HOST', app_config.get('DB_HOST')),
        db_name = env.get('DB_NAME', app_config.get('DB_NAME')),
    )
    app.config['ZABBIX_POST_DATA'] = ZABBIX_POST_DATA
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

    ETCD_SERVER_HOST = env.get('ETCD_SERVER_HOST')
    ETCD_SERVER_PORT = env.get('ETCD_SERVER_PORT')
    if ETCD_SERVER_HOST:
        app.config['ETCD_SERVER_HOST'] = ETCD_SERVER_HOST
    if ETCD_SERVER_PORT:
        app.config['ETCD_SERVER_PORT'] = ETCD_SERVER_PORT

def create_app(config_name='default'):
    app = Flask(APP_NAME)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config.from_pyfile(config_pyfiles[config_name])
    app.config.from_pyfile('config/dns_templates.tpl')
    configure_data(app)
    configure_extensions(app)
    configure_blueprints(app, [auth_bp, dns_bp, admin, page_bp])
    configure_error_handlers(app)
    # configure_hooks(app)
    configure_crossdomain(app)
    return app

