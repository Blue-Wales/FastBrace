-- 创建文件表
CREATE TABLE IF NOT EXISTS `file` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `master_id` bigint(20) NOT NULL COMMENT '文件所属实体的id',
  `file_type` int(11) NOT NULL COMMENT '文件类型',
  `file_path` varchar(2048) NOT NULL COMMENT '文件路径',
  `file_name` varchar(255) NOT NULL COMMENT '文件名称',
  `extra_info` varchar(2048) DEFAULT NULL COMMENT '扩展信息',
  PRIMARY KEY (`id`),
  KEY `idx_master_id` (`master_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文件表';
