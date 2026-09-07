# File Management

FastBrace ships with a file upload module that supports uploading files and recording their metadata to the database — useful for user avatars, attachments, and similar scenarios.

## Core Concepts

- **File upload**: Upload files of any type via `multipart/form-data`
- **File type**: A `file_type` parameter must be specified on upload for category management (e.g. `avatar`, `attachment`)
- **File metadata**: After upload, metadata such as file path, type, and size is persisted to the database
- **Authentication**: The file upload endpoint requires a JWT token

## File Locations

| File | Description |
|------|------|
| `api/file.py` | File upload API routes |
| `application/file_app.py` | File application service layer |
| `domain/value_object/file_vo.py` | File value object |
| `domain/repo/file_repo.py` | File repository implementation |
| `infrastructure/models/file.py` | File database model |
| `db/create_file_table.sql` | SQL for creating the file table |

## API Endpoints

| Method | Path | Description |
|------|------|------|
| POST | `/file/upload` | Upload a file (authentication required) |

## Endpoint Details

### Upload a File

```bash
curl -X POST http://localhost:8000/file/upload \
  -H "Authorization: Bearer <token>" \
  -F "file_type=avatar" \
  -F "file=@/path/to/image.png"
```

Example response:

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
