
# 标准的RESTFul风格，服务器要返回原生的HTTP状态码，客户端根据HTTP状态码来判断业务状态。
# 由于 URL 会直接定位到资源，访问 URL 如果资源不存在会大量抛 4xx，会引发监控报警
# 为了跟其他项目监控保持一致，所以放弃使用HTTP状态码来判断业务正确和失败。
# 因此本项目严格意义上不属于 RESTFul 风格，在此说明。

class RequestCode(object):
    SUCCESS = 100000            #请求成功
    AUTH_FAILED = 100001        #token认证失败
    LOGIN_FAILED = 100002       #登录失败
    OTHER_FAILED = 105000       #其他原因请求失败

