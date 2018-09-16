#!/bin/bash
#
#Auth: 平安好房
#URL: http://www.pinganfang.com
#USE: 结合ETCD配置本地文件
#
# 脚本使用说明如下:
:<<!
1. 需要手动出创建日志目录: mkdir -p /data1/logs/etcd_config
2. 此脚本的运行权限为root,可以结合自己dns运行的权限,自行更改 
3. 需要更改此脚本的变量: ETCD_SERVER_NAME 更改为贵公司自己的etcd服务URL,ENV 表示的是IDC机房环境，比如多IDC。
4. 脚本启动方式: /bin/bash hfdns_client_etcd_config.sh dev &>/dev/null
5. 脚本stop方式: /bin/bash hfdns_client_etcd_config.sh dev stop
6. 脚本依赖linux jq命令进行解析json文件, 请使用前安装 yum install -y jq
7. 问题定位 查看日志如: tail -f /data1/logs/etcd_config/etcd_config_2017-09-06_access.log
8. 此脚本可以放到crontab 中每分钟运行以防止脚本挂掉
!

#ETCD 环境
ETCD_ENV=${1}

if [ ${#ETCD_ENV} -eq 0 ];then
    echo "请提供环境参数...如{dev|anhouse|ga}"
    exit
fi

#ETCD Log目录
ETCD_LOG_DIR="/data1/logs/etcd_config"

#脚本锁
ETCD_LOCK="/tmp/.${ETCD_ENV}_etcd_config.lock"

#服务本身名称
ETCD_JOBS_NAME=$(/bin/basename $BASH_SOURCE)

#打印信息
PRINT_INFO(){
    /bin/echo "$(/bin/date +%F' '%T) ${1}" >> ${ETCD_LOG_DIR}/etcd_config_$(/bin/date +%F)_access.log
}

#关闭进程
ETCD_STOP=${2}
if [ "x${ETCD_STOP}" == "xstop" ];then

    #打印信息
    PRINT_INFO "${ETCD_JOBS_NAME} 服务已关闭..."

    #关闭监听ETCD
    /bin/ps -ef |/bin/egrep "(opscmdb|${ETCD_JOBS_NAME})" |/bin/grep -v grep | /bin/awk '{print $2}' | /usr/bin/xargs kill -9 

    #退出
    exit
fi

#默认ETCD配置
ETCD_SERVER_NAME="http://10.59.87.121:2379/v2/keys/opscmdb"

echo "-------------------${DOCKER_ETCD_ADDRESS}--------------------"
#ETCD集群服务器
if [ -z "${DOCKER_ETCD_ADDRESS}" ];then
    [ "x${ETCD_ENV}" == "xdev" ] &&  ETCD_SERVER_NAME="http://dev-etcd01:2379/v2/keys/opscmdb"
    [ "x${ETCD_ENV}" == "xanhouse" ] &&  ETCD_SERVER_NAME="http://shzr-etcd01:2379/v2/keys/opscmdb"
    [ "x${ETCD_ENV}" == "xga" ] &&  ETCD_SERVER_NAME="http://shbx-etcd01:2379/v2/keys/opscmdb"
else
    ETCD_SERVER_NAME="http://${DOCKER_ETCD_ADDRESS}/v2/keys/opscmdb"
fi

#日志路径创建
if [ ! -d ${ETCD_LOG_DIR} ];then

    #创建日志路径
    /bin/mkdir -p ${ETCD_LOG_DIR} >/dev/null 2>&1

    #返回状态
    if [ $? -ne 0 ];then

        #打印信息
        PRINT_INFO "${ETCD_LOG_DIR} 创建日志路径失败,查看是否权限有问题"
        exit
    fi
fi

#安装依赖包
if [ ! -x /usr/bin/jq ];then

    #打印信息
    PRINT_INFO "${ETCD_JOBS_NAME} 依赖jq.x86_64安装包"
    exit
fi

#默认ID号，用于临时文件
ETCD_ID=0

#获取ETCD配置文件列表 
_ETCD_ENV_DOWNLOAD_CONFIG() {

    #ETCD 配置文件临时
    ETCD_ENV_CONFIG_FILE="/tmp/.${ETCD_ENV}_${ETCD_ID}_dns_etcd_config.json"

    #初始化数据   无需区分环境
    #/usr/bin/curl -s "${ETCD_SERVER_NAME}/${ETCD_ENV}?recursive=true&wait=true" > ${ETCD_ENV_CONFIG_FILE}

    /usr/bin/curl -s "${ETCD_SERVER_NAME}/?recursive=true&wait=true" > ${ETCD_ENV_CONFIG_FILE}
}

#获取ETCD内容
_ETCD_ENV_VALUE_INFO(){

    #获取INDEX DIR
    _ETCD_ENV_FILE=$(/bin/cat ${ETCD_ENV_CONFIG_FILE} | /usr/bin/jq .node.key |/bin/sed -e 's/\"//g' -e "s#/opscmdb/dns##g")

    #获取INDEX VALUE  #去除文件开始结尾引号，回车，双引号(默认双引号ETCD会加\，)
    #_ETCD_ENV_VALUE=$(/bin/cat ${ETCD_ENV_CONFIG_FILE} | /usr/bin/jq .node.value |/bin/sed -e 's/^"//' -e 's/"$//' -e 's/\\n/\n/g' -e 's/\\//g')
    _ETCD_ENV_VALUE=$(/bin/cat ${ETCD_ENV_CONFIG_FILE} | /usr/bin/jq .node.value |/bin/sed -e 's/^"//' -e 's/"$//' -e 's/\\n/\n/g' -e 's/\\"/"/g')

    ##
    echo "$_ETCD_ENV_VALUE"
    
    #获取空内容
    if [ ${#_ETCD_ENV_FILE} -eq 0 ];then
        
        #打印信息
        PRINT_INFO "${ETCD_SERVER_NAME} 获取了内容为空..."

        #初始删除文件
        #/bin/rm -f ${ETCD_ENV_CONFIG_FILE} >/dev/null 2>&1

        #退出
        exit
    fi

    #第一次创建文件
    if [ ! -f ${_ETCD_ENV_FILE} ];then

        #获取配置文件目录 去除前缀
        ETCD_ENV_DIR=$(/usr/bin/dirname ${_ETCD_ENV_FILE})
        #ETCD_ENV_DIR=$(/usr/bin/dirname ${_ETCD_ENV_FILE}) | sed 's#/opscmdb/dns##g'

        #创建目录
        [ ! -d ${ETCD_ENV_DIR} ] && /bin/mkdir -p ${ETCD_ENV_DIR} >/dev/null 2>&1
    fi

    #导入配置文件
    echo "$_ETCD_ENV_VALUE" > ${_ETCD_ENV_FILE}

    #打印信息
    PRINT_INFO "更新配置文件 ${_ETCD_ENV_FILE}"

    #初始删除文件
    #/bin/rm -f ${ETCD_ENV_CONFIG_FILE} >/dev/null 2>&1
}


## DNS 配置文件reload
_DNS_RELOAD() {
    ## 修改配置文件权限
    chown root.named /etc/named.conf
    chown named.named -R /etc/named 
    chown named.named -R /var/named

    /usr/sbin/named-checkconf 
    [ $? -ne 0 ] && PRINT_INFO "DNS named-checkconf 配置文件检测失败"
    PRINT_INFO "DNS named-checkconf 配置文件检测成功"
    ## 自带检测功能 配置文件检测失败 无法reload成功 但不会停止DNS解析服务
    /usr/sbin/rndc reload
    [ $? -ne 0 ] && PRINT_INFO "DNS reload 失败"
    [ $? -ne 0 ] && PRINT_INFO "DNS reload 成功" 
}

#判断锁文件 
if [ -f ${ETCD_LOCK} ];then
   [ ! -z "$(/usr/sbin/lsof -p $(/bin/cat ${ETCD_LOCK}))" ] && exit 
fi

#创建锁文件 
echo $$ > ${ETCD_LOCK}

#创建锁文件出错
if [ $? -ne 0 ];then
   exit
fi


#打印信息
PRINT_INFO "${ETCD_JOBS_NAME} 服务已启动..."

#获取任务列表
while true
do
    #监听是否有配置文件更新
    _ETCD_ENV_DOWNLOAD_CONFIG

    #解析配置文件
    _ETCD_ENV_VALUE_INFO &

    ## DNS配置文件权限修改和检查 reload
    _DNS_RELOAD

    #ETCD自增ID
    ETCD_ID=$((${ETCD_ID}+1))

done
