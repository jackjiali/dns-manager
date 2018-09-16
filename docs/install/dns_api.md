平安好房DNS管理平台API文档
===========================

# 认证
### 1，LDAP认证接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/auth/login_ldap       |POST 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
username    |string     |是       |无     |user123      |用户名
password    |string     |是       |无     |passwd123      |密码

#### 返回格式：


```json
认证成功
{
    "code": 100000,
    "msg": "认证成功！",
    "data": {
        "token": "eyJ0eXAiOiJKxxxxxxxxxx.eyJ1c2VyIjoiTElKSUFKSUE4NzMiLCJleHAiOjE1MTI0OTUxMzd9.pjTKXo1EPqersjJ4HiN7Jj9mwx50pqCvEMrIL4rGCYM",
        "user_info": {
            "id": 3,
            "username": "LIJIAJIA873",
            "email": "xx",
            "chinese_name": "",
            "cellphone": "xx",
            "position": "xx",
            "location": "",
            "can_add_server": true,
            "can_add_view": true,
            "can_add_zone": true,
            "member_since": "2017-11-23 18:24:22"
        }
    }
}


认证失败
{
    "code": 105000,
    "msg": "认证失败！",
    "data": null
}
```

### 2，本地用户认证接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/auth/login_local       |POST 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
username    |string     |是       |无     |user123      |用户名
password    |string     |是       |无     |passwd123      |密码

#### 返回格式：


```json
认证成功
{
    "code": 100000,
    "msg": "认证成功！",
    "data": {
        "token": "eyJ0eXAiOiJKxxxxxxxxxx.eyJ1c2VyIjoiTElKSUFKSUE4NzMiLCJleHAiOjE1MTI0OTUxMzd9.pjTKXo1EPqersjJ4HiN7Jj9mwx50pqCvEMrIL4rGCYM",
        "user_info": {
            "id": 3,
            "username": "LIJIAJIA873",
            "email": "xx",
            "chinese_name": "",
            "cellphone": "xx",
            "position": "xx",
            "location": "",
            "can_add_server": true,
            "can_add_view": true,
            "can_add_zone": true,
            "member_since": "2017-11-23 18:24:22"
        }
    }
}

认证失败
{
    "code": 105000,
    "msg": "认证失败！",
    "data": null
}
```

### 3，本地新用户注册接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/auth/register_local       |POST 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
username    |string     |是       |无     |user123      |用户名
password    |string     |是       |无     |passwd123      |密码
password2    |string     |是       |无     |passwd123      |两次密码输入要一致
email    |string     |是       |无     |xxx@qq.com      |邮箱

#### 返回格式：


```json
认证成功
{
    "code": 100000,
    "msg": "注册成功！",
    "data": null
}

认证失败
{
    "code": 105000,
    "msg": "用户已存在！",
    "data": null
}
```

# DNS相关资源
## 一，DNS服务器（Server）
### 1.1，DNS服务器列表获取接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/servers        |GET 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
currentPage    |int     |否       |1     |3      |当前是第几页
pageSize    |int     |否       |10     |20      |每页显示的记录数
id    |int     |否       |无     |20      |ID
host    |string     |否       |无     |www      |用户名
ip    |string     |否       |无     |10.2.2.2      |IP地址
env    |string     |否       |无     |env      |环境
dns_server_type    |string     |否       |无     |master      |服务器类型


#### 返回格式：


```json
获取成功
{
    "code": 100000,
    "data": {
        "total": 4,
        "servers": [
            {
                "id": 2,
                "host": "s2",
                "ip": "0.0.0.1",
                "env": "anhouse",
                "dns_server_type": "master",
                "zb_process_itemid": "222",
                "zb_port_itemid": "222",
                "zb_resolve_itemid": "222",
                "zb_resolve_rate_itemid": "189254",
                "can_update": true,
                "can_delete": true
            },
            {
                "id": 1,
                "host": "s1",
                "ip": "0.0.0.0",
                "env": "dev",
                "dns_server_type": "master",
                "zb_process_itemid": "111",
                "zb_port_itemid": "111",
                "zb_resolve_itemid": "111",
                "zb_resolve_rate_itemid": "189243",
                "can_update": true,
                "can_delete": true
            }
        ],
        "current_page": 1
    },
    "msg": "获取成功！"
}

```

### 1.2，DNS服务器创建接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/servers        |POST 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
host    |string     |是       |无     |www      |用户名
ip    |string     |是       |无     |10.2.2.2      |IP地址
env    |string     |是       |无     |env      |环境
dns_server_type    |string     |否       |无     |master      |服务器类型
zb_process_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS解析进程的itemid
zb_port_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS服务器端口的itemid
zb_resolve_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS解析的itemid
zb_resolve_rate_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS解析量的itemid


#### 返回格式：


```json
创建成功
{
    "code": 100000,
    "msg": "创建成功！",
    "data": null
}
创建失败
{
    "code": 105000,
    "msg": "创建失败! 重复的Server，相同Host或IP地址已存在！",
    "data": null
}
```

### 1.3，获取指定ID的DNS服务器信息接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/servers/\<int:server_id>        |GET 


#### 参数列表：
无


#### 返回格式：

```json
获取成功
{
    "code": 100000,
    "msg": "获取成功！",
    "data": {
        "id": 2,
        "host": "s2",
        "ip": "0.0.0.1",
        "env": "anhouse",
        "dns_server_type": "master",
        "zb_process_itemid": "222",
        "zb_port_itemid": "222",
        "zb_resolve_itemid": "222",
        "zb_resolve_rate_itemid": "189254",
        "can_update": true,
        "can_delete": true
    }
}
```

### 1.4，修改指定ID的DNS服务器接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/servers/\<int:server_id>        |PUT 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
host    |string     |是       |无     |www      |用户名
ip    |string     |是       |无     |10.2.2.2      |IP地址
env    |string     |是       |无     |env      |环境
dns_server_type    |string     |否       |无     |master      |服务器类型
zb_process_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS解析进程的itemid
zb_port_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS服务器端口的itemid
zb_resolve_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS解析的itemid
zb_resolve_rate_itemid    |string     |是       |无     |321574      |ZABBIX上监控此服务器DNS解析量的itemid

#### 返回格式：


```json
修改成功
{
    "code": 100000,
    "msg": "修改成功！",
    "data": null
}
修改失败
{
    "code": 105000,
    "msg": "修改失败！",
    "data": null
}
```

### 1.5，删除指定ID的DNS服务器接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/servers/\<int:server_id>        |DELETE 


#### 参数列表：
无


#### 返回格式：


```json
删除成功
{
    "code": 100000,
    "msg": "删除成功！",
    "data": null
}
删除失败
{
    "code": 105000,
    "msg": "删除失败！",
    "data": null
}
```


## 二，DNS区域（View）
### 2.1，DNS区域列表获取接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/views        |GET 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
currentPage    |int     |否       |1     |3      |当前是第几页
pageSize    |int     |否       |10     |20      |每页显示的记录数
id    |int     |否       |无     |20      |ID
name    |string     |否       |无     |view1      |View名称

#### 返回格式：


```json
获取成功
{
    "code": 100000,
    "data": {
        "total": 4,
        "views": [
            {
                "id": 2,
                "name": "vvvv111111111",
                "acl": "0.0.0.0",
                "can_update": true,
                "can_delete": true
            },
            {
                "id": 1,
                "name": "wqerqwer",
                "acl": "0.0.0.0\n1.1.1.1",
                "can_update": true,
                "can_delete": true
            }
        ],
        "current_page": 1
    },
    "msg": "获取成功！"
}

```


### 2.2，DNS区域创建接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/views        |POST 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
name    |string     |是       |无     |v6      |view名称
acl    |string     |是       |无     |0.0.0.0\n1.1.1.1      |acl IP地址列表


#### 返回格式：


```json
创建成功
{
    "code": 100000,
    "msg": "创建成功！",
    "data": null
}
创建失败
{
    "code": 105000,
    "msg": "创建失败! 相同名字的view已存在！",
    "data": null
}
```

### 2.3，获取指定ID的DNS区域信息接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/views/\<int:view_id>        |GET 


#### 参数列表：
无


#### 返回格式：


```json
{
    "code": 100000,
    "msg": "获取成功！",
    "data": {
        "id": 1,
        "name": "wqerqwer",
        "acl": "0.0.0.0\n1.1.1.1",
        "can_update": true,
        "can_delete": true
    }
}
```


### 2.4，修改指定ID的DNS区域接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/views/\<int:view_id>        |PUT 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
name    |string     |是       |无     |v6      |view名称
acl    |string     |是       |无     |0.0.0.0\n1.1.1.1      |acl IP地址列表


#### 返回格式：


```json
修改成功
{
    "code": 100000,
    "msg": "修改成功！",
    "data": null
}
修改失败
{
    "code": 105000,
    "msg": "修改失败！",
    "data": null
}
```


### 2.5，删除指定ID的DNS区域接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/views/\<int:view_id>        |DELETE 


#### 参数列表：
无


#### 返回格式：


```json
删除成功
{
    "code": 100000,
    "msg": "删除成功！",
    "data": null
}
删除失败
{
    "code": 105000,
    "msg": "删除失败！",
    "data": null
}
```





## 三，DNS域名（Zone）
### 3.1，DNS域名列表获取接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/zones        |GET 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
currentPage    |int     |否       |1     |3      |当前是第几页
pageSize    |int     |否       |10     |20      |每页显示的记录数
id    |int     |否       |无     |20      |ID
name    |string     |否       |无     |z1      |Zone名称
zone_group    |string     |否       |无     |2      |Zone归属， 内部（1）/外部（0）/劫持（2）
zone_type    |string     |否       |无     |master      |Zone类型， master/forward only
	

#### 返回格式：


```json
获取成功
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
```


### 3.2，DNS域名创建接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/zones        |POST 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
name    |string     |是       |无     |v6      |zone名称
zone_group    |string     |否       |无     |2      |Zone归属， 内部（1）/外部（0）/劫持（2）
zone_type    |string     |是      |无     |master      |Zone类型， master/forward only
forwarders    |string     |否       |无     |0.0.0.0\n1.1.1.1      |转发至的地址
view_ids    |list     |是       |无     |[1,2,3]      |关联一个或多个view到当前zone

#### 返回格式：


```json
创建成功
{
    "code": 100000,
    "msg": "创建成功！",
    "data": null
}
创建失败
{
    "code": 105000,
    "msg": "创建失败! 相同名字的Zone已存在！",
    "data": null
}
```

### 3.3，获取指定ID的DNS域名信息接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/zones/\<int:zone_id>        |GET 


#### 参数列表：
无


#### 返回格式：


```json
获取成功
{
    "code": 100000,
    "msg": "获取成功！",
    "data": {
        "id": 5,
        "name": "xx2.com",
        "zone_group": 2,
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
    }
}
```


### 3.4，修改指定ID的DNS域名接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/zones/\<int: zone_id>        |PUT 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
name    |string     |是       |无     |v6      |zone名称
zone_group    |string     |否       |无     |2      |Zone归属， 内部（1）/外部（0）/劫持（2）
zone_type    |string     |是      |无     |master      |Zone类型， master/forward only
forwarders    |string     |否       |无     |0.0.0.0\n1.1.1.1      |转发至的地址
view_ids    |list     |是       |无     |[1,2,3]      |关联一个或多个view到当前zone


#### 返回格式：


```json
修改成功
{
    "code": 100000,
    "msg": "修改成功！",
    "data": null
}
修改失败
{
    "code": 105000,
    "msg": "修改失败！",
    "data": null
}
```


### 3.5，删除指定ID的DNS域名接口
##### 注：删除zone后，zone下面的record也将一并删除
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/zones/\<int:zone_id>        |DELETE 


#### 参数列表：
无


#### 返回格式：


```json
删除成功
{
    "code": 100000,
    "msg": "删除成功！",
    "data": null
}
删除失败
{
    "code": 105000,
    "msg": "删除失败！",
    "data": null
}
```



## 四，DNS域名记录（Record）
### 4.1，DNS域名记录列表获取接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/records        |GET 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
zone_id    |int     |是       |无     |20      |所属的Zone的ID
currentPage    |int     |否       |1     |3      |当前是第几页
pageSize    |int     |否       |10     |20      |每页显示的记录数
id    |int     |否       |无     |20      |ID
host    |string     |否       |无     |www      |用户名
record_type    |string     |否       |无     |A      |记录类型
ttl    |string     |否       |无     |600      |TTL
value    |string     |否       |无     |127.0.0.1      |记录值
view_name    |string     |否       |无     |v1      |线路

#### 返回格式：


```json
获取成功
{
    "code": 100000,
    "data": {
        "total": 9,
        "records": [
            {
                "id": 16,
                "host": "xxx333",
                "record_type": "A",
                "ttl": "600",
                "value": "0.0.0.0",
                "view_name": "jtest",
                "comment": "xxx111",
                "zone_id": 4,
                "can_update": true,
                "can_delete": true
            },
            {
                "id": 15,
                "host": "xxx333",
                "record_type": "A",
                "ttl": "600",
                "value": "0.0.0.0",
                "view_name": "vvvv111111111",
                "comment": "xxx111",
                "zone_id": 4,
                "can_update": true,
                "can_delete": true
            }
        ],
        "current_page": 1
    },
    "msg": "获取成功！"
}
```

### 4.2，DNS域名记录创建接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/records        |POST 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
host    |string     |是       |无     |r1      |record名称
record_type    |string     |否       |无     |2      |Zone归属， A/NS/PTR/CNAME
ttl    |string     |是      |无     |600      |TTL值
value    |string     |是       |无     |1.1.1.1      |记录值，必须为ip地址
view_name    |string     |是       |无     |v1      |关联的view名称
comment    |string     |是       |无     |comment      |备注
zone_id    |int     |是       |无     |2     |当前record所属zone的ID

#### 返回格式：


```json
创建成功
{
    "code": 100000,
    "msg": "创建成功！",
    "data": null
}
创建失败
{
    "code": 105000,
    "msg": "创建失败 !重复的记录！！同样的Zone，同样的主机，同样的View 的记录只能存在一个。",
    "data": null
}
```

### 4.3，获取指定ID的DNS域名记录信息接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/records/\<int:record_id>        |GET 


#### 参数列表：
无


#### 返回格式：


```json
获取成功
状态码： 200
{
    "code": 100000,
    "msg": "获取成功！",
    "data": {
        "id": 31,
        "host": "xxx333",
        "record_type": "A",
        "ttl": "600",
        "value": "0.0.0.0",
        "view_name": "wqerqwer",
        "comment": "xxx111",
        "zone_id": 4,
        "can_update": true,
        "can_delete": true
    }
}
```


### 4.4，修改指定ID的DNS域名记录接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/records/\<int:record_id>        |PUT 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
host    |string     |是       |无     |r1      |record名称
record_type    |string     |否       |无     |2      |Zone归属， A/NS/PTR/CNAME
ttl    |string     |是      |无     |600      |TTL值
value    |string     |是       |无     |1.1.1.1      |记录值，必须为ip地址
view_name    |string     |是       |无     |v1      |关联的view名称
comment    |string     |是       |无     |comment      |备注
zone_id    |int     |是       |无     |2     |当前record所属zone的ID


#### 返回格式：


```json
修改成功
{
    "code": 100000,
    "msg": "修改成功！",
    "data": null
}
修改失败
{
    "code": 105000,
    "msg": "修改失败！",
    "data": null
}
```


### 4.5，删除指定ID的DNS域名记录接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/records/\<int:record_id>        |DELETE 


#### 参数列表：
无


#### 返回格式：


```json
删除成功
{
    "code": 100000,
    "msg": "删除成功！",
    "data": null
}
删除失败
{
    "code": 105000,
    "msg": "删除失败！",
    "data": null
}
```


## 五，BIND主配置文件
### 5.1，BIND主配置文件内容获取接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/bind_conf        |GET 


#### 参数列表：
无

#### 返回格式：

```json
获取成功
状态码： 200
{
    "code": 100000,
    "msg": "修改成功！",
    "data": {
        "bind_conf": "bind_conf\nbind_conf\nbind_conf\nbind_conf\nbind_conf\ndf\nasdf\nasd\nfasd\nfads\n\n\n"
    }
}


```

### 5.2，BIND主配置文件内容编辑接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/bind_conf        |POST


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
bind_conf    |string     |是       |无     |line1\nline2\nline3      |BIND主配置文件内容


#### 返回格式：

```json
修改成功
{
    "code": 100000,
    "msg": "修改成功！",
    "data": null
}
修改失败
{
    "code": 105000,
    "msg": "修改失败！",
    "data": null
}
```

## 六，操作日志
### 6.1，操作日志列表获取接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/dns/oplogs        |GET 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
currentPage    |int     |否       |1     |3      |当前是第几页
pageSize    |int     |否       |10     |20      |每页显示的记录数
id    |int     |否       |无     |20      |日志ID
operation_type    |string     |否       |无     |创建      |操作类型，添加/修改/删除
operator    |string     |否       |无     |user1      |操作人
target_type    |string     |否       |无     |2      |资源类型，Server/View/Zone/Record
target_name    |string     |否       |无     |aa.com      |资源名称
target_id    |string     |否       |无     |12      |资源ID


#### 返回格式：

```json
获取成功
{
    "code": 100000,
    "data": {
        "total": 66,
        "operation_logs": [
            {
                "id": 67,
                "operation_time": "2017-12-04 18:22:19",
                "operation_type": "添加",
                "operator": "LIJIAJIA873",
                "target_type": "Record",
                "target_name": "xxx333",
                "target_id": "32",
                "target_detail": "id: 32\n记录主机: xxx333\n记录类型: A\n记录值: 0.0.0.0\nTTL: 600\n线路类型: wqerqwer\n备注: xxx111\n创建人: None\n创建时间: 2017-12-04 18:22:18.805320"
            },
            {
                "id": 66,
                "operation_time": "2017-12-04 18:17:40",
                "operation_type": "添加",
                "operator": "LIJIAJIA873",
                "target_type": "Record",
                "target_name": "xxx333",
                "target_id": "31",
                "target_detail": "id: 31\n记录主机: xxx333\n记录类型: A\n记录值: 0.0.0.0\nTTL: 600\n线路类型: wqerqwer\n备注: xxx111\n创建人: None\n创建时间: 2017-12-04 18:17:40.105156"
            }
        ],
        "current_page": 1
    },
    "msg": "获取成功！"
}

```


# 后台管理系统相关
## 一，用户
##### 注：后台管理相关资源只有 admin 权限才能访问
### 1.1，用户列表获取接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/admin/users        |GET 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
currentPage    |int     |否       |1     |3      |当前是第几页
pageSize    |int     |否       |10     |20      |每页显示的记录数
id    |int     |否       |无     |20      |用户ID
email    |string     |否       |无     |dachui@qq.com      |邮箱
username    |string     |否       |无     |user2      |用户名
chinese_name    |string     |否       |无     |王大锤      |中文名
cellphone    |string     |否       |无     |18666666666      |手机号码


#### 返回格式：


```json
获取成功
状态码： 200
{
    "code": 100000,
    "data": {
        "total": 8,
        "users": [
            {
                "id": 8,
                "email": "xxx@qq.com",
                "username": "test222",
                "chinese_name": "",
                "cellphone": "",
                "position": "",
                "location": "",
                "member_since": "2017-12-04 17:34:25",
                "last_seen": "2017-12-04 17:34:25",
                "roles": []
            },
            {
                "id": 7,
                "email": "xxx@qq.com",
                "username": "test111",
                "chinese_name": "",
                "cellphone": "1371111",
                "position": "",
                "location": "",
                "member_since": "2017-11-29 14:16:27",
                "last_seen": "2017-11-29 14:16:27",
                "roles": []
            }
        ],
        "current_page": 1
    },
    "msg": "获取成功！"
}

```


### 1.2，获取指定ID的用户信息接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/admin/users/\<int: user_id>        |GET 


#### 参数列表：
无


#### 返回格式：


```json
获取成功
状态码： 200
{
    "code": 100000,
    "msg": "获取成功！",
    "data": {
        "id": 7,
        "email": "xxx@qq.com",
        "username": "test111",
        "chinese_name": "",
        "cellphone": "1371111",
        "position": "",
        "location": "",
        "member_since": "2017-11-29 14:16:27",
        "last_seen": "2017-11-29 14:16:27",
        "can_add_server": false,
        "can_add_view": false,
        "can_add_zone": false,
        "can_edit_bind_conf": false,
        "roles": []
    }
}

```


### 1.3，修改指定ID的用户信息接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/admin/users/\<int: user_id>        |GET 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
role_ids    |list     |否      |无     |[1,2,3]      |当前用户关联user id
position    |string     |否       |无     |python工程师      |职位
chinese_name    |string     |否       |无     |王大锤      |中文名
cellphone    |string     |否       |无     |18666666666      |手机号
location    |string     |否       |无     |comment      |家庭住址


#### 返回格式：


```json
修改成功
{
    "code": 100000,
    "msg": "修改成功！",
    "data": null
}
修改失败
{
    "code": 105000,
    "msg": "修改失败！",
    "data": null
}

```

### 1.4，删除指定ID的用户接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/admin/users/\<int: user_id>        |GET 


#### 参数列表：
无


#### 返回格式：


```json
删除成功
{
    "code": 100000,
    "msg": "删除成功！",
    "data": null
}
删除失败
{
    "code": 105000,
    "msg": "删除失败！",
    "data": null
}

```


## 二，角色
##### 注：后台管理相关资源只有 admin 权限才能访问
### 2.1，角色列表获取接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/admin/roles        |GET 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
currentPage    |int     |否       |1     |3      |当前是第几页
pageSize    |int     |否       |10     |20      |每页显示的记录数
id    |int     |否       |无     |20      |角色ID
name    |string     |否       |无     |user2      |角色名


#### 返回格式：


```json
获取成功
状态码： 200
{
    "code": 100000,
    "msg": "获取成功！",
    "data": {
        "total": 7,
        "roles": [
            {
                "id": 6,
                "name": "zone_admin",
                "privileges": [
                    {
                        "id": 2,
                        "name": "ZONE_ADD",
                        "operation": 0,
                        "resource_type": 0,
                        "resource_id": 0,
                        "comment": null
                    },
                    {
                        "id": 6,
                        "name": "ZONE#xcvwretwgvrfv3wf.com#UPDATE",
                        "operation": 1,
                        "resource_type": 2,
                        "resource_id": 1,
                        "comment": null
                    }
                ]
            },
            {
                "id": 2,
                "name": "server_admin",
                "privileges": [
                    {
                        "id": 1,
                        "name": "SERVER_ADD",
                        "operation": 0,
                        "resource_type": 0,
                        "resource_id": 0,
                        "comment": null
                    },
                    {
                        "id": 17,
                        "name": "SERVER#s1#ACCESS",
                        "operation": 0,
                        "resource_type": 0,
                        "resource_id": 1,
                        "comment": null
                    }
                ]
            }
        ],
        "current_page": 1
    }
```

### 2.2，创建新角色接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/admin/roles        |POST 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|-----------|-----------|-----------|-----------
name    |string     |是       |无     |role123      |角色名称
privilege_ids    |list     |是       |无     |[1,2,3]      |新建角色所拥有的权限


#### 返回格式：

```json
创建成功
{
    "code": 100000,
    "msg": "创建成功！",
    "data": null
}
创建失败
{
    "code": 105000,
    "msg": "创建失败! 相同名字的角色已存在！",
    "data": null
}

```

### 2.3，获取指定ID的角色信息接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/admin/roles/\<int:role_id>       |GET 


#### 参数列表：
无


#### 返回格式：


```json
获取成功
状态码： 200
{
    "code": 100000,
    "msg": "获取成功！",
    "data": {
        "id": 3,
        "name": "server_guest",
        "privileges": [
            {
                "id": 17,
                "name": "SERVER#s1#ACCESS",
                "operation": 0,
                "resource_type": 0,
                "resource_id": 1,
                "comment": null
            },
            {
                "id": 20,
                "name": "SERVER#s2#ACCESS",
                "operation": 0,
                "resource_type": 0,
                "resource_id": 2,
                "comment": null
            }
        ]
    }
}
```


### 2.4，修改指定ID的角色接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/admin/roles/\<int:role_id>        |PUT 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
name    |string     |是       |无     |role123      |角色名称
privilege_ids    |list     |是       |无     |[1,2,3]      |新建角色所拥有的权限


#### 返回格式：


```json
修改成功
{
    "code": 100000,
    "msg": "修改成功！",
    "data": null
}
修改失败
{
    "code": 105000,
    "msg": "修改失败！",
    "data": null
}
```


### 2.5，删除指定ID的角色接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/admin/roles/\<int:role_id>        |DELETE 


#### 参数列表：
无


#### 返回格式：


```json
删除成功
{
    "code": 100000,
    "msg": "删除成功！",
    "data": null
}
删除失败
{
    "code": 105000,
    "msg": "删除失败！",
    "data": null
}
```





## 三，权限
##### 注：后台管理相关资源只有 admin 权限才能访问
### 3.1，权限列表获取接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/admin/privileges        |GET 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
currentPage    |int     |否       |1     |3      |当前是第几页
pageSize    |int     |否       |10     |20      |每页显示的记录数
id    |int     |否       |无     |20      |权限ID
name    |string     |否       |无     |p1      |权限名
operation    |string     |否       |无     |4      |操作类型，访问（0），修改（1），删除（2）
resource_type    |string     |否       |无     |3      |操作资源类型，服务器（0），View(1), Zone(2), Record(3)
resource_id    |int     |否       |无     |2      |资源ID


#### 返回格式：


```json
获取成功
状态码： 200
{
    "code": 100000,
    "data": {
        "total": 37,
        "privileges": [
            {
                "id": 58,
                "name": "VIEW#v555#DELETE",
                "operation": 2,
                "resource_type": 1,
                "resource_id": 6,
                "comment": null
            },
            {
                "id": 57,
                "name": "VIEW#v555#UPDATE",
                "operation": 1,
                "resource_type": 1,
                "resource_id": 6,
                "comment": null
            }
        ],
        "current_page": 1
    },
    "msg": "获取成功！"
}
```

### 3.2，创建新权限接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/admin/privileges        |POST 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|-----------|-----------|-----------|-----------
name    |string     |是       |无     |p123      |角色名称
operation    |int     |否       |无     |0      |操作类型，访问（0），修改（1），删除（2）
resource_type    |int     |否       |无     |6      |操作资源类型，服务器（0），View(1), Zone(2), Record(3)
resource_id    |int     |否       |无     |5      |资源ID
comment    |string     |否       |无     |aa.com的删除权限      |备注


#### 返回格式：

```json
创建成功
{
    "code": 100000,
    "msg": "创建成功！",
    "data": null
}
创建失败
{
    "code": 105000,
    "msg": "创建失败! 相同名字的权限已存在！",
    "data": null
}

```

### 3.3，获取指定ID的权限信息接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/admin/privileges/\<int:privilege_id>       |GET 


#### 参数列表：
无


#### 返回格式：


```json
获取成功
状态码： 200
{
    "code": 100000,
    "msg": "获取成功！",
    "data": {
        "id": 37,
        "name": "ZONE#xx1.com#DELETE",
        "operation": 2,
        "resource_type": 2,
        "resource_id": 4,
        "comment": null
    }
}
```


### 3.4，修改指定ID的权限接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/admin/privileges/\<int:privilege_id>        |PUT 


#### 参数列表：
字段       |字段类型    |必须    |默认值    |示例   |备注
------------|-----------|----------- |-----------|-----------|-----------
name    |string     |是       |无     |p123      |角色名称
operation    |int     |否       |无     |0      |操作类型，访问（0），修改（1），删除（2）
resource_type    |int     |否       |无     |6      |操作资源类型，服务器（0），View(1), Zone(2), Record(3)
resource_id    |int     |否       |无     |5      |资源ID
comment    |string     |否       |无     |aa.com的删除权限      |备注

#### 返回格式：


```json
修改成功
{
    "code": 100000,
    "msg": "修改成功！",
    "data": null
}
修改失败
{
    "code": 105000,
    "msg": "修改失败！",
    "data": null
}
```


### 3.5，删除指定ID的权限接口
#### 请求方式：
URL       |请求方式       
------------|-----------
/admin/privileges/\<int:privilege_id>        |DELETE 


#### 参数列表：
无


#### 返回格式：


```json
删除成功
{
    "code": 100000,
    "msg": "删除成功！",
    "data": null
}
删除失败
{
    "code": 105000,
    "msg": "删除失败！",
    "data": null
}
```

