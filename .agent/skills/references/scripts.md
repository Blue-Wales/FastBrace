### scripts rules

基于业务要求需要完善脚本文件时，该脚本文件必须包含：

1. 文件文档说明，在头部标明使用说明， 包含详细的参数信息，诸如：

   ```
   """
   文档说明
   """
   规则：
       规则说明

   用法：
       python scripts/xxx.py
       python scripts/batch_recalculate_apartment_weight.py --dry-run  # 预处理阶段
   """
   ```

2. 脚本必须包含预处理阶段，保证在不修改数据库信息时也能够提前校验排查问题
