-- 创建角色层级闭包表
CREATE TABLE IF NOT EXISTS `role_closure` (
  `ancestor` bigint(20) NOT NULL DEFAULT 1 COMMENT '祖先角色ID(实体id)',
  `descendant` bigint(20) NOT NULL COMMENT '后代角色ID(实体id)',
  `depth` int(11) NOT NULL COMMENT '层级深度',
  PRIMARY KEY (`ancestor`, `descendant`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色层级闭包表';
