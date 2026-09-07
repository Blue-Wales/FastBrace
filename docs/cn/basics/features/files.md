# 文件管理

FastBrace 内置了文件模块，支持文件上传并记录文件元信息到数据库，可用于用户头像、附件、图片等场景。



## 核心概念

- **文件上传**：支持通过 `multipart/form-data` 上传任意类型文件
- **文件类型**：上传时需指定 `file_type` 参数，用于分类管理（如 `avatar`、`attachment`）
- **文件元信息**：上传后文件路径、类型、大小等元信息持久化到数据库
- **认证保护**：文件上传接口需要携带 JWT Token



## 文件位置

| 文件 | 说明 |
|------|------|
| `api/file.py` | 文件上传 API 路由 |
| `application/file_app.py` | 文件应用服务层 |
| `domain/value_object/file_vo.py` | 文件值对象 |
| `domain/repo/file_repo.py` | 文件仓储实现 |
| `infrastructure/models/file.py` | 文件数据库模型 |
| `db/create_file_table.sql` | 文件表建表 SQL |

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/file/upload` | 上传文件（需认证） |



## 接口详情

### 上传文件

```bash
curl -X POST http://localhost:8000/file/upload \
  -H "Authorization: Bearer <token>" \
  -F "file_type=avatar" \
  -F "file=@/path/to/image.png"
```

返回示例：

```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "file_id": 1,
    "file_url": "/static/uploads/xxx.png",
    "file_name": "image.png",
    "file_type": "avatar"
  }
}
```
