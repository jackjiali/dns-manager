from flask import Flask, Blueprint
from flask_restful import Api

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

auth_api = Api(auth_bp)


from .auth import AuthLDAP, AuthLocal, RegisterLocal
auth_api.add_resource(AuthLDAP, '/login_ldap')
auth_api.add_resource(AuthLocal, '/login_local')
auth_api.add_resource(RegisterLocal, '/register_local')



