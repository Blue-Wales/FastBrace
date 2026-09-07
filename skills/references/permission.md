## permission rules

### 背景

权限模块与业务新增/编辑模块强关联，当新增一个多级业务管理模块时，需要同步配置权限信息绑定业务接口

### 工作流

1. 在infrastructure/core/enum_var文件中，找到Permissions枚举类，新建相应模块权限code
2. 在 `infrastructure/utils/permission_constants.py` 中找到 `PERMISSION_MAPPING` 配置，判断业务是新增一个新的业务模块和子模块还是在现有业务模块基础上添加子模块，并完成配置
3. 在api/{module}.py中在相应接口中添加权限配置

### 示例

业务场景：新增一个xx管理模块，包含yy子模块和zz子模块，并分别针对子模块完成相应接口开发

修改内容：按照上述工作流修改相应文件添加配置信息，不需要过多改动其他文件
