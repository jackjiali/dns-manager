DNS-Manager
===========================
该项目可用于多 IDC 多 View 的 dns 管理。
****
可提issue进行交流

****

# 平台架构图如下：

![dns](/docs/images/dns.jpg "DNS 平台架构图")

功能介绍
------

#### 1. 平台管理方式：

使用 BIND9 作为 DNS 服务器。

使用 ETCD 来管理 DNS 服务器的 BIND 配置文件，包括 VIEW，ZONE，RECORD 的配置文件。

所有BIND DNS 服务器角色均为 `Master`，不存在 `Slave`，服务器配置文件数据都是统一从 ETCD 获取。

利用ETCD本身的订阅发布机制，当ETCD上数据发生变更后，所有 DNS 服务器都会实时获取到变更信息，并将本地配置文件同步到最新，跟ETCD上数据保持一致。

公网域名可托管在DNSPod，通过操作DNSPod Api对公网域名进行管理。

#### 2. 使用技术栈：

后端： Python3.5 + Flask + Mysql + Etcd

前端： Vue.js

架构： 前后端分离，纯 restful 架构，后端只提供 restful api，前端用 vue 框架。


#### 3. 功能简介

* DNS 服务器管理

* BIND 主配置文件管理

* View 管理 （区域）

* Zone 管理 （域名）

* Record 管理 （子域名）

    * 内网域名 Record 管理

    * 劫持域名 Record 管理

    * 公网域名 Record 管理

* 平台权限管理

    * 用户管理

    * 角色管理

    * 权限管理

* 操作记录


#### 4. 安装部署

* 可查看 [项目部署文档](docs/install/dns_install.md)
