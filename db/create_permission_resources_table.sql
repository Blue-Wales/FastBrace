-- 创建权限资源表
CREATE TABLE IF NOT EXISTS `permission_resources` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `entity_id` bigint(20) NOT NULL COMMENT '权限资源id',
  `name` varchar(255) NOT NULL COMMENT '权限资源名称',
  `code` varchar(255) NOT NULL COMMENT '权限资源编码',
  `description` varchar(255) DEFAULT NULL COMMENT '权限资源描述',
  `resource_type` varchar(32) NOT NULL COMMENT '权限资源类型',
  `parent_id` bigint(20) DEFAULT NULL COMMENT '父权限资源id',
  `depth` int(11) NOT NULL DEFAULT 1 COMMENT '权限资源深度',
  `level` int(11) NOT NULL DEFAULT 1 COMMENT '权限资源级别',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_entity_id` (`entity_id`),
  UNIQUE KEY `uk_code` (`code`),
  KEY `idx_parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限资源表';
