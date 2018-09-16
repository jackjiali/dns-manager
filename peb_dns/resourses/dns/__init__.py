
from flask import Flask, Blueprint
from flask_restful import Api

dns_bp = Blueprint('dns', __name__, url_prefix='/api/dns')

dns_api = Api(dns_bp)


from .server import DNSServerList, DNSServer, DNSBindConf, DNSServerEnvs
dns_api.add_resource(DNSServerList, '/servers')
dns_api.add_resource(DNSServer, '/servers/<int:server_id>')
dns_api.add_resource(DNSBindConf, '/bind_conf')
dns_api.add_resource(DNSServerEnvs, '/server_envs')

from .view import DNSViewList, DNSView
dns_api.add_resource(DNSViewList, '/views')
dns_api.add_resource(DNSView, '/views/<int:view_id>')

from .zone import DNSZoneList, DNSZone
dns_api.add_resource(DNSZoneList, '/zones')
dns_api.add_resource(DNSZone, '/zones/<int:zone_id>')

from .record import DNSRecordList, DNSRecord, DNSRecordsForSearch
dns_api.add_resource(DNSRecordList, '/records')
dns_api.add_resource(DNSRecord, '/records/<int:record_id>')
dns_api.add_resource(DNSRecordsForSearch, '/records_searching')

from .operation_log import DNSOperationLogList, DNSOperationLog
dns_api.add_resource(DNSOperationLogList, '/oplogs')
dns_api.add_resource(DNSOperationLog, '/oplogs/<int:log_id>')

