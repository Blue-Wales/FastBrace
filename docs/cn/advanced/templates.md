# 模板引擎

FastBrace 内置了基于 **Jinja2** 的模板引擎系统，通过 `TemplateRender` 类提供可靠的模板路径解析和渲染能力，主要用于邮件模板、通知消息等场景。

## 设计思想

### 为什么需要模板系统？

在业务系统中，许多场景需要动态生成内容：
- **邮件通知**：用户注册后发送欢迎邮件，内容包含用户名、密码等动态信息
- **消息通知**：系统通知、审批提醒等
- **报告生成**：定期生成的数据报告

模板系统将**内容格式**与**业务数据**分离，便于维护和修改。

### 路径解析策略

`TemplateRender` 采用多策略路径解析，确保在不同部署环境下都能正确找到模板文件：

```
策略1：环境变量 TEMPLATES_DIR 指定 → 最高优先级
策略2：项目根目录（基于标识文件自动检测）/ templates /
策略3：当前工作目录 / templates / → 兜底
```

项目根目录通过标识文件（`main.py`、`pyproject.toml`、`README.md`）自动向上查找。



## 使用步骤

### 第一步：创建模板文件

在 `templates/` 目录下按主题创建子目录和模板文件：

```
templates/
└── email/                          # 主题目录
    ├── create_user_email_subject.j2  # 邮件主题模板
    └── create_user_email_body.j2     # 邮件正文模板
```

模板文件使用 Jinja2 语法：

```jinja2
{# create_user_email_subject.j2 #}
欢迎加入 {{ company_name }}！
```

```jinja2
{# create_user_email_body.j2 #}
亲爱的 {{ name }}，

您的账号已创建成功！

用户名：{{ username }}
密码：{{ password }}

请登录系统后及时修改密码。
```

### 第二步：在代码中使用 TemplateRender

```python
from infrastructure.utils.template_render import TemplateRender

# 初始化模板管理器，指定主题目录
template_render = TemplateRender(topic="email")

# 渲染模板
subject = template_render.render_template(
    "create_user_email_subject.j2",
    company_name="FastBrace"
)

body = template_render.render_template(
    "create_user_email_body.j2",
    name="张三",
    username="zhangsan",
    password="123456"
)
```



### 第三步：结合事件系统发送邮件

框架中的邮件事件处理器 `EmailSendEventHandler` 展示了完整的模板使用流程：

```python
# event_handlers/email_send_handler.py
class EmailTemplateManager:
    """邮件模板管理器"""
    EMAIL_TYPE_MAP = {
        "user.created": {
            "subject": {
                "template": "create_user_email_subject.j2",
                "params": {"company_name": "company_name"},
            },
            "body": {
                "template": "create_user_email_body.j2",
                "params": {
                    "name": "name",
                    "username": "username",
                    "password": "plain_password",
                },
            },
        }
    }

    def __init__(self):
        self.template_render = TemplateRender(topic="email")

    def render_template(self, event_type, event_data):
        # 从事件数据中提取模板参数并渲染
        ...
```

当用户创建事件触发时，自动渲染邮件模板并通过 SMTP 发送。



## 邮件配置

在 `infrastructure/config/settings.dev.yaml` 中配置 SMTP：

```yaml
email:
  smtp_server: "smtp.example.com"
  smtp_port: 465
  username: "noreply@example.com"
  password: "your_password"
  use_tls: true
  sender_name: "FastBrace"
  company_name: "FastBrace"
```



## 扩展：添加新的模板主题

1. 在 `templates/` 下创建新的主题目录（如 `templates/notification/`）
2. 添加 Jinja2 模板文件
3. 在代码中创建 `TemplateRender(topic="notification")` 实例
4. 调用 `render_template()` 渲染模板
