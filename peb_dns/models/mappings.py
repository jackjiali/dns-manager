from collections import OrderedDict

class Operation(object):
    ACCESS = 0
    UPDATE = 1
    DELETE = 2


class ResourceType(object):
    SERVER = 0
    VIEW = 1
    ZONE = 2
    RECORD = 3
    USER = 4
    ROLE = 5
    PRIVILEGE = 6
    PAGE = 7


class DefaultPrivilege(object):
    SERVER_ADD = 'SERVER_ADD'
    ZONE_ADD = 'ZONE_ADD'
    VIEW_ADD = 'VIEW_ADD'
    BIND_CONF_EDIT = 'BIND_CONF_EDIT'
    LOG_PAGE_ACCESS = 'LOG_PAGE_ACCESS'


OPERATION_STR_MAPPING = {
    Operation.ACCESS:'ACCESS',
    Operation.UPDATE:'UPDATE',
    Operation.DELETE:'DELETE'
}



ROLE_MAPPINGS = OrderedDict({
    'admin': 1,
    'server_admin': 2,
    'server_guest': 3,
    'view_admin': 4,
    'view_guest': 5,
    'zone_admin': 6,
    'zone_guest': 7
})


