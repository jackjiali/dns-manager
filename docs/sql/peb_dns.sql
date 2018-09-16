/*
Date: 2018-01-08 11:54:35
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `account_local_auth`
-- ----------------------------
DROP TABLE IF EXISTS `account_local_auth`;
CREATE TABLE `account_local_auth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) DEFAULT NULL,
  `password_hash` varchar(128) DEFAULT NULL,
  `email` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_account_local_auth_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of account_local_auth
-- ----------------------------
INSERT INTO `account_local_auth` VALUES ('1', 'admin', 'pbkdf2:sha256:50000$B8xHsDQ7$6c01906213113c1fc3e94e897f2128a407da5e9b41dd18bb9799f080230bd95e', 'xxxx@gmail.com');

-- ----------------------------
-- Table structure for `account_privilege`
-- ----------------------------
DROP TABLE IF EXISTS `account_privilege`;
CREATE TABLE `account_privilege` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) DEFAULT NULL,
  `operation` int(11) DEFAULT NULL,
  `resource_type` varchar(64) DEFAULT NULL,
  `resource_id` int(11) DEFAULT NULL,
  `comment` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_account_privilege_resource_id` (`resource_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of account_privilege
-- ----------------------------
INSERT INTO `account_privilege` VALUES ('1', 'SERVER_ADD', null, null, null, null);
INSERT INTO `account_privilege` VALUES ('2', 'ZONE_ADD', null, null, null, null);
INSERT INTO `account_privilege` VALUES ('3', 'VIEW_ADD', null, null, null, null);
INSERT INTO `account_privilege` VALUES ('4', 'BIND_CONF_EDIT', null, null, null, null);
INSERT INTO `account_privilege` VALUES ('5', 'VIEW#default_view#ACCESS', '0', '1', '1', null);
INSERT INTO `account_privilege` VALUES ('6', 'VIEW#default_view#UPDATE', '1', '1', '1', null);
INSERT INTO `account_privilege` VALUES ('7', 'VIEW#default_view#DELETE', '2', '1', '1', null);
INSERT INTO `account_privilege` VALUES ('8', 'ZONE#z1.com#ACCESS', '0', '2', '1', null);
INSERT INTO `account_privilege` VALUES ('9', 'ZONE#z1.com#UPDATE', '1', '2', '1', null);
INSERT INTO `account_privilege` VALUES ('10', 'ZONE#z1.com#DELETE', '2', '2', '1', null);

-- ----------------------------
-- Table structure for `account_role`
-- ----------------------------
DROP TABLE IF EXISTS `account_role`;
CREATE TABLE `account_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of account_role
-- ----------------------------
INSERT INTO `account_role` VALUES ('1', 'admin');
INSERT INTO `account_role` VALUES ('2', 'server_admin');
INSERT INTO `account_role` VALUES ('3', 'server_guest');
INSERT INTO `account_role` VALUES ('4', 'view_admin');
INSERT INTO `account_role` VALUES ('5', 'view_guest');
INSERT INTO `account_role` VALUES ('6', 'zone_admin');
INSERT INTO `account_role` VALUES ('7', 'zone_guest');

-- ----------------------------
-- Table structure for `account_role_privilege`
-- ----------------------------
DROP TABLE IF EXISTS `account_role_privilege`;
CREATE TABLE `account_role_privilege` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `role_id` int(11) DEFAULT NULL,
  `privilege_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_account_role_privilege_privilege_id` (`privilege_id`),
  KEY `ix_account_role_privilege_role_id` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of account_role_privilege
-- ----------------------------
INSERT INTO `account_role_privilege` VALUES ('1', '1', '1');
INSERT INTO `account_role_privilege` VALUES ('2', '2', '1');
INSERT INTO `account_role_privilege` VALUES ('3', '1', '2');
INSERT INTO `account_role_privilege` VALUES ('4', '6', '2');
INSERT INTO `account_role_privilege` VALUES ('5', '1', '3');
INSERT INTO `account_role_privilege` VALUES ('6', '4', '3');
INSERT INTO `account_role_privilege` VALUES ('7', '1', '4');
INSERT INTO `account_role_privilege` VALUES ('8', '1', '5');
INSERT INTO `account_role_privilege` VALUES ('9', '1', '6');
INSERT INTO `account_role_privilege` VALUES ('10', '1', '7');
INSERT INTO `account_role_privilege` VALUES ('11', '4', '5');
INSERT INTO `account_role_privilege` VALUES ('12', '4', '6');
INSERT INTO `account_role_privilege` VALUES ('13', '4', '7');
INSERT INTO `account_role_privilege` VALUES ('14', '5', '5');
INSERT INTO `account_role_privilege` VALUES ('15', '1', '8');
INSERT INTO `account_role_privilege` VALUES ('16', '1', '9');
INSERT INTO `account_role_privilege` VALUES ('17', '1', '10');
INSERT INTO `account_role_privilege` VALUES ('18', '6', '8');
INSERT INTO `account_role_privilege` VALUES ('19', '6', '9');
INSERT INTO `account_role_privilege` VALUES ('20', '6', '10');
INSERT INTO `account_role_privilege` VALUES ('21', '7', '8');

-- ----------------------------
-- Table structure for `account_user`
-- ----------------------------
DROP TABLE IF EXISTS `account_user`;
CREATE TABLE `account_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(64) DEFAULT NULL,
  `username` varchar(64) DEFAULT NULL,
  `chinese_name` varchar(64) DEFAULT NULL,
  `cellphone` varchar(64) DEFAULT NULL,
  `actived` int(11) DEFAULT NULL,
  `position` varchar(64) DEFAULT NULL,
  `location` varchar(64) DEFAULT NULL,
  `member_since` datetime DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_account_user_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of account_user
-- ----------------------------
INSERT INTO `account_user` VALUES ('1', 'xxxx@gmail.com', 'admin', '', '', '1', '', '', '2018-01-08 11:47:22', '2018-01-08 11:47:22');

-- ----------------------------
-- Table structure for `account_user_role`
-- ----------------------------
DROP TABLE IF EXISTS `account_user_role`;
CREATE TABLE `account_user_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_account_user_role_role_id` (`role_id`),
  KEY `ix_account_user_role_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of account_user_role
-- ----------------------------
INSERT INTO `account_user_role` VALUES ('1', '1', '1');

-- ----------------------------
-- Table structure for `alembic_version`
-- ----------------------------
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of alembic_version
-- ----------------------------
INSERT INTO `alembic_version` VALUES ('73e7a686b691');

-- ----------------------------
-- Table structure for `dns_operation_log`
-- ----------------------------
DROP TABLE IF EXISTS `dns_operation_log`;
CREATE TABLE `dns_operation_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `operation_time` datetime DEFAULT NULL,
  `operation_type` varchar(64) DEFAULT NULL,
  `operator` varchar(64) DEFAULT NULL,
  `target_type` varchar(64) DEFAULT NULL,
  `target_name` varchar(64) DEFAULT NULL,
  `target_id` varchar(64) DEFAULT NULL,
  `target_detail` text,
  `gmt_create` datetime DEFAULT NULL,
  `gmt_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of dns_operation_log
-- ----------------------------
INSERT INTO `dns_operation_log` VALUES ('1', '2018-01-08 11:47:51', '添加', 'admin', 'Zone', 'z1.com', '1', 'id: 1\nZone名称: z1.com\nZone归属: 内部域名\nZone类型: master\n关联View: [\'default_view\']\n', '2018-01-08 11:47:51', '2018-01-08 11:47:51');
INSERT INTO `dns_operation_log` VALUES ('2', '2018-01-08 11:48:16', '添加', 'admin', 'Record', 'r1111', '2', 'id: 2\n记录主机: r1111\n记录类型: A\n记录值: 0.0.0.\nTTL: 600\n线路类型: default_view\n备注: asdf\n创建人: None\n创建时间: 2018-01-08 11:48:15.547158', '2018-01-08 11:48:16', '2018-01-08 11:48:16');

-- ----------------------------
-- Table structure for `dns_record`
-- ----------------------------
DROP TABLE IF EXISTS `dns_record`;
CREATE TABLE `dns_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(64) DEFAULT NULL,
  `record_type` varchar(64) DEFAULT NULL,
  `ttl` varchar(64) DEFAULT NULL,
  `value` varchar(64) DEFAULT NULL,
  `view_name` varchar(64) DEFAULT NULL,
  `comment` varchar(64) DEFAULT NULL,
  `creator` varchar(64) DEFAULT NULL,
  `status` varchar(64) DEFAULT NULL,
  `enabled` varchar(64) DEFAULT NULL,
  `alive` varchar(64) DEFAULT NULL,
  `outter_record_id` varchar(64) DEFAULT NULL,
  `zone_id` int(11) DEFAULT NULL,
  `gmt_create` datetime DEFAULT NULL,
  `gmt_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_dns_record_host` (`host`),
  KEY `ix_dns_record_zone_id` (`zone_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of dns_record
-- ----------------------------
INSERT INTO `dns_record` VALUES ('1', '@', 'NS', '86400', 'master.z1.com.', 'default_view', null, 'admin', 'enabled', '1', 'ON', '', '1', '2018-01-08 11:47:51', '2018-01-08 11:47:51');
INSERT INTO `dns_record` VALUES ('2', 'r1111', 'A', '600', '0.0.0.', 'default_view', 'asdf', null, 'enabled', '1', 'ON', '', '1', '2018-01-08 11:48:16', '2018-01-08 11:48:16');

-- ----------------------------
-- Table structure for `dns_server`
-- ----------------------------
DROP TABLE IF EXISTS `dns_server`;
CREATE TABLE `dns_server` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(64) DEFAULT NULL,
  `ip` varchar(64) DEFAULT NULL,
  `env` varchar(64) DEFAULT NULL,
  `dns_server_type` varchar(64) DEFAULT NULL,
  `status` varchar(64) DEFAULT NULL,
  `zb_process_itemid` varchar(64) DEFAULT NULL,
  `zb_port_itemid` varchar(64) DEFAULT NULL,
  `zb_resolve_itemid` varchar(64) DEFAULT NULL,
  `zb_resolve_rate_itemid` varchar(64) DEFAULT NULL,
  `server_log` text,
  `gmt_create` datetime DEFAULT NULL,
  `gmt_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_dns_server_host` (`host`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of dns_server
-- ----------------------------

-- ----------------------------
-- Table structure for `dns_view`
-- ----------------------------
DROP TABLE IF EXISTS `dns_view`;
CREATE TABLE `dns_view` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `acl` text,
  `gmt_create` datetime DEFAULT NULL,
  `gmt_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_dns_view_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of dns_view
-- ----------------------------
INSERT INTO `dns_view` VALUES ('1', 'default_view', '0.0.0.0/0', '2018-01-08 11:47:22', '2018-01-08 11:47:22');

-- ----------------------------
-- Table structure for `dns_view_zone`
-- ----------------------------
DROP TABLE IF EXISTS `dns_view_zone`;
CREATE TABLE `dns_view_zone` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `view_id` int(11) DEFAULT NULL,
  `zone_id` int(11) DEFAULT NULL,
  `gmt_create` datetime DEFAULT NULL,
  `gmt_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_dns_view_zone_view_id` (`view_id`),
  KEY `ix_dns_view_zone_zone_id` (`zone_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of dns_view_zone
-- ----------------------------
INSERT INTO `dns_view_zone` VALUES ('1', '1', '1', '2018-01-08 11:47:51', '2018-01-08 11:47:51');

-- ----------------------------
-- Table structure for `dns_zone`
-- ----------------------------
DROP TABLE IF EXISTS `dns_zone`;
CREATE TABLE `dns_zone` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `zone_group` int(11) DEFAULT NULL,
  `zone_type` varchar(64) DEFAULT NULL,
  `forwarders` varchar(64) DEFAULT NULL,
  `gmt_create` datetime DEFAULT NULL,
  `gmt_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_dns_zone_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of dns_zone
-- ----------------------------
INSERT INTO `dns_zone` VALUES ('1', 'z1.com', '1', 'master', '', '2018-01-08 11:47:51', '2018-01-08 11:47:51');
