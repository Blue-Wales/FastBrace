## file resource rules

### 背景

项目文件、图片、视频、PDF、附件等资源采用统一上传和统一 `file` 表关联。业务新增/编辑表单可以设计资源字段，但业务主表模型默认不设计图片、附件、文件地址字段。

资源关联规则：

1. 前端先调用 `api/file.py` 的 `/file/upload` 上传资源，获取 `file_name`、`file_path`。
2. 业务接口接收 `api/request_body/file_request.py` 中的 `FileRequest` 列表。
3. 资源统一保存到 `infrastructure/models/file.py` 对应的 `file` 表。
4. 资源通过 `file.master_id + file.file_type` 关联业务实体。
5. `master_id` 为业务实体 `entity_id`，`file_type` 来源于 `FileType` 或 `RoomTypeFileType`。

### 工作流

1. 在 `infrastructure/core/enum_var.py` 中确认或新增资源枚举：

   - 普通业务资源使用 `FileType`。
   - 房型区域类资源使用 `RoomTypeFileType`。
   - 资源字段名必须与枚举名称一致。

2. 请求、实体、响应中声明资源字段：

   - 请求字段使用 `List[FileRequest]`。
   - 领域实体资源字段使用 `List[dict]`。
   - 响应字段使用 `FileResponse` 或项目已有文件响应模型。

3. 业务模型和业务仓储不持久化资源字段：

   - `infrastructure/models/{module}.py` 不新增资源字段。
   - `domain/repo/{module}_repo.py` 保存或更新时排除资源字段。
   - 仓储层不直接操作 `file` 表。

4. 新增业务数据时：

   - 先保存业务实体，确保有 `entity_id`。
   - 调用实体的 `get_file_vo_list()` 生成文件关联。
   - 调用 `FileRepository.save()` 保存到 `file` 表。

5. 编辑业务数据时：

   - 先查询已有业务实体并更新资源字段。
   - 调用 `get_file_vo_list()` 和 `get_file_vo_empty_list()` 获取需要替换或清空的资源类型。
   - 调用 `FileRepository.delete(pair_list=...)` 删除旧关联。
   - 调用 `FileRepository.save()` 保存新关联。

6. 查询业务详情时：

   - 调用实体的 `get_file_type_list()` 获取资源类型。
   - 调用 `FileRepository.get(master_id=..., file_types=...)` 查询文件。
   - 调用实体的 `add_attachments()` 回填资源字段。

7. 查询业务列表时：

   - 如列表不需要资源，不查询 `file` 表。
   - 如列表需要资源，使用 `FileRepository.get_multiple()` 批量查询并按 `master_id` 回填，避免逐条查询。

8. 删除业务数据时：

   - 同步删除 `file` 表关联。
   - 默认不物理删除对象存储文件。

### 参考文件

1. 统一上传：`api/file.py`、`application/file_app.py`
2. 文件模型：`infrastructure/models/file.py`
3. 文件仓储：`domain/repo/file_repo.py`
4. 文件请求/响应：`api/request_body/file_request.py`、`api/response_body/common_response.py`
5. 普通资源参考：`application/city_app.py`、`application/advertise_app.py`
6. 动态资源参考：`domain/entity/room_type.py`、`api/request_body/room_type_request.py`
