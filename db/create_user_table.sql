-- 创建用户表
CREATE TABLE IF NOT EXISTS `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `entity_id` bigint(20) NOT NULL COMMENT '实体id',
  `username` varchar(64) NOT NULL COMMENT '用户名',
  `name` varchar(64) NOT NULL COMMENT '姓名',
  `mobile` varchar(20) NOT NULL COMMENT '手机号',
  `password_hash` varchar(255) NOT NULL COMMENT '密码哈希',
  `gender` tinyint(1) DEFAULT 0 COMMENT '性别(2：女，1：男, 0: 未定义)',
  `email` varchar(120) NOT NULL COMMENT '邮箱',
  `status` tinyint(1) DEFAULT 1 COMMENT '状态(1 已激活，2：已禁用)',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `nick_name` varchar(64) DEFAULT NULL COMMENT '昵称',
  `personal_profile` varchar(255) DEFAULT NULL COMMENT '个人简介',
  `personal_advantage` varchar(255) DEFAULT NULL COMMENT '个人特长',
  `wecom_number` varchar(64) DEFAULT NULL COMMENT '企业微信号',
  `last_operator` varchar(64) DEFAULT NULL COMMENT '最后操作人',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_entity_id` (`entity_id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uix_mobile_status` (`mobile`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
