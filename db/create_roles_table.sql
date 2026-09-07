-- 创建角色表
CREATE TABLE IF NOT EXISTS `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `entity_id` bigint(20) NOT NULL COMMENT '实体id',
  `code` varchar(64) NOT NULL COMMENT '角色唯一编码',
  `name` varchar(50) NOT NULL COMMENT '角色名称',
  `permissions` json COMMENT '权限配置信息',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_entity_id` (`entity_id`),
  UNIQUE KEY `uk_code` (`code`),
  UNIQUE KEY `uk_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';
