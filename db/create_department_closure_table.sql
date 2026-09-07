-- 创建部门层级闭包表
CREATE TABLE IF NOT EXISTS `department_closure` (
  `ancestor` bigint(20) NOT NULL DEFAULT 1 COMMENT '祖先部门ID(实体id)',
  `descendant` bigint(20) NOT NULL COMMENT '后代部门ID(实体id)',
  `depth` int(11) NOT NULL COMMENT '层级深度',
  PRIMARY KEY (`ancestor`, `descendant`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部门层级闭包表';
