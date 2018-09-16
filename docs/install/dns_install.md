# 部署
## 一，本地部署
### 后端Python工程部署

* #### 本教程部署基于 Ubuntu/Debian 平台，其他平台亦可作为参考。

* #### Python3.5 安装（已安装 Python3.5 环境的请跳过）
```bash
# 安装python3.5
sudo add-apt-repository ppa:fkrull/deadsnakes
sudo apt-get update
sudo apt-get install python3.5
    
# 安装pip
sudo apt-get install python3-pip python-pip

# 设置python3.5为默认python程序
sudo mv /usr/bin/python /usr/bin/python.bak
sudo ln -s python3.5 python

```

* #### 工具安装
```bash
# 安装 mysql 略  (请安装mysql5.7版本)
sudo apt-get install mysql-server
# 安装 etcd 略  （请参考官方文档）
sudo apt-get install etcd
```


* #### 克隆项目代码到本地
```bash
# 将本仓库clone到本地
git clone git@github.com:pahf-ops/peb-dns.git
```


* #### 安装依赖

```bash
# 首先进入当前目录下
# 使用pip3为python3.5安装依赖包
sudo pip3 install -r requirements.txt
# 若安装过程中出现区域报错，locale.Error: unsupported locale setting
# export LC_ALL=C

# 安装 mysql 驱动
wget https://cdn.mysql.com//Downloads/Connector-Python/mysql-connector-python-2.1.7.tar.gz
tar -zxf mysql-connector-python-2.1.7.tar.gz
cd mysql-connector-python-2.1.7/   
sudo python3.5 setup.py install

```


* #### 初始化数据库

1，将Mysql数据库编码设置为UTF-8
```bash
# 登入mysql
❯ mysql -u root -p
# 查看编码
❯ show variables like '%character%';
  
| Variable_name            | Value                      |
+--------------------------+----------------------------+
| character_set_client     | utf8                       |
| character_set_connection | utf8                       |
| character_set_database   | utf8                       |
| character_set_filesystem | binary                     |
| character_set_results    | utf8                       |
| character_set_server     | utf8                       |
| character_set_system     | utf8                       |
| character_sets_dir       | /usr/share/mysql/charsets/ |
+--------------------------+----------------------------+
  
若编码不是utf8
在/etc/mysql/mysql.conf.d/mysqld.cnf文件中[mysqld]加入变量，如：
character_set_database = utf8
character-set-server = utf8

修改完之后， 通过service mysql restart重启 mysql
```

2，创建数据库
```bash
# 创建数据库实例
❯ mysql -u root -p

mysql> create database <your_db_name>;
Query OK, 1 row affected (0.01 sec)

mysql> ^DBye
```

3，修改项目配置文件 
```bash
# 配置文件路径如下：
peb-dns/config/peb_dns.cfg.sample
# 先拷贝一份配置文件并重命名，去掉 .sample 后缀:
cp peb-dns/config/peb_dns.cfg.sample peb-dns/config/peb_dns.cfg
# 然后所有字段都有详细说明，请严格按照说明一一配好。
```

4，配置应用环境变量
```bash
#设置 FLASK_APP 环境变量，值为本项目根目录下 app.py 的绝对路径
#首先进入当前项目根目录下，即 app.py 同级目录，然后执行以下语句
export FLASK_APP=${PWD}/app.py
```

5，初始化数据库
```bash
flask db init
flask db migrate
flask db upgrade
flask initdb
```

* #### 简单快速部署方式

```bash
# 进入当前项目根目录下，运行以下命令部署
nohup gunicorn -w 4 app:app -b 0.0.0.0:8080 --log-level=debug &
# PS: 上面 -w 为 开启workers数，公式：（系统内核数*2 + 1)， 8080 为端口号
```

* #### 配置您的Zabbix
Zabbix 配置请参考 [这里](../zabbix/zabbix_dns_README.md)


### 前端vue工程部署

* #### 前端配置文件

```javascript
前端工程需要配置后端项目的base url
文件路径：static/static/js/app.*.js
  
找到以下内容，并配置baseURL
var instance = __WEBPACK_IMPORTED_MODULE_2_axios___default.a.create({
    baseURL: '<后端URL>/api/',
    timeout: 10000,
    withCredentials: true
});
```

* #### 安装和配置nginx
```json
首先安装 nginx
sudo apt-get install nginx

然后添加
/etc/nginx/conf.d/peb_dns.conf
配置文件

内容如下：
  
server {
    listen 80  default;
    server_name _;
    location / {
        index /index.html;
        root /home/ubuntu/peb-dns/static;  //peb-dns项目下static文件夹的绝对路径
    }
    location /static {
        index index.html;
        root /home/ubuntu/peb-dns/static;  //peb-dns项目下static文件夹的绝对路径
    }
 
    location /api {
        proxy_pass http://<后端URL>;   //这里配置为 后端项目部署成功之后的访问地址
    }
}

重新加载nginx配置
sudo service nginx reload
```

* #### 部署bind服务器端脚本

```bash
启动etcd客户端
拷贝代码目录下脚本到服务器root目录下：
etcd_client/hfdns_client_etcd_config.sh

配置默认ETCD地址: 
ETCD_SERVER_NAME="http://1.1.1.1:2379/v2/keys/opscmdb"
  
如公司有多套环境，根据自身情况，配置每个环境对应的ETCD地址:
#ETCD集群服务器
#[ "x${ETCD_ENV}" == "xdev" ] &&  ETCD_SERVER_NAME="http://dev-etcd01:2379/v2/keys/opscmdb"
#[ "x${ETCD_ENV}" == "xanhouse" ] &&  ETCD_SERVER_NAME="http://shzr-etcd01:2379/v2/keys/opscmdb"
#[ "x${ETCD_ENV}" == "xga" ] &&  ETCD_SERVER_NAME="http://shbx-etcd01:2379/v2/keys/opscmdb"
[ "x${ETCD_ENV}" == "xsingle" ] &&  ETCD_SERVER_NAME="2.2.2.2:2379/v2/keys/opscmdb"
  
root用户下添加计划任务:
*/1 * * * * /bin/bash /root/hfdns_client_etcd_config.sh single >/dev/null 2>&1
```


## 二，docker一键部署

* 本教程基于已经安装docker和docker-compose的用户，两者安装教程，请参考官方文档。

* 克隆项目代码到本地
```bash
# 将本仓库clone到本地
git clone git@github.com:pahf-ops/peb-dns.git
```

* 部署
```bash
# 1，修改项目配置文件
配置文件路径如下：
peb-dns/config/peb_dns.cfg.sample
先将将配置文件重命名，去掉.sample后缀:
mv peb-dns/config/peb_dns.cfg.sample peb-dns/config/peb_dns.cfg
然后所有字段都有详细说明，请严格按照说明一一配好。

# 2, 切换目录至 peb-dns 文件夹 平级目录，然后执行：
cp peb-dns/docker_file/docker-compose.yml .

# 3，初始化操作
docker-compose down
rm -rf .data
rm -rf peb-dns/migrations/
chmod 755 peb-dns/docker_start.sh

# 4，部署项目
docker-compose up

```




