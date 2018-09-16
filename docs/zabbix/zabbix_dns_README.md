Zabbix 配置说明
===========================
#### 文件说明

文件       |说明    
------------|-----------
[zbx_export_templates.xml](zbx_export_templates.xml)    |zabbix DNS服务监控模板     
[zabbix_monitor_dns.sh](zabbix_monitor_dns.sh)    |zabbix DNS模板使用到的key脚本     


#### 配置说明
* ### 本公司使用的zabbix是3.4 版本，导入DNS模板的时候请注意！！

* DNS bind 模板 自定义的需要两个KEY:
```bash
UserParameter=check_dns[*],/bin/bash /data1/env/zabbix/etc/custon_scripts/zabbix_monitor_dns.sh $1

UserParameter=net.tcp.listen.grep[*],if grep -q $$(printf '%04X.00000000:0000.0A' $1) /proc/net/tcp || grep -q $$(printf '00000000000000000000000000000000:%04X' $1)  /proc/net/tcp6;then echo 1;else echo 0;fi
```

* 获取bind DNS值请参考以下脚本:

* [docs/zabbix/zabbix_monitor_dns.sh](zabbix_monitor_dns.sh)


#### 注意

* 1，需要源文件  /var/named/data/named_stats.txt  此数据的来源是通过bind的命令获取的 /usr/sbin/rndc stats  获取，自行通过在DNS主机上通过crontab每分钟执行生成此文件。 或者通过其他脚本方式

* 2，注意zabbix用户需要有读取 /var/named/data/named_stats.txt的权限，若没有请通过修改权限或者使用其他方式赋权。

