# Template Engine

FastBrace ships a **Jinja2**-based template engine system. Through the `TemplateRender` class it provides reliable template path resolution and rendering, mainly used for email templates, notification messages, and similar scenarios.

## Design Philosophy

### Why a Template System?

Many scenarios in a business system require dynamically generated content:
- **Email notifications**: a welcome email after user registration, containing dynamic information such as the username and password
- **Message notifications**: system notices, approval reminders, etc.
- **Report generation**: periodically generated data reports

The template system separates **content format** from **business data**, making both easier to maintain and modify.

### Path Resolution Strategy

`TemplateRender` uses multi-strategy path resolution to ensure template files are found correctly across deployment environments:

```
Strategy 1: environment variable TEMPLATES_DIR → highest priority
Strategy 2: project root (auto-detected via marker files) / templates /
Strategy 3: current working directory / templates / → fallback
```

The project root is located by walking upward and looking for marker files (`main.py`, `pyproject.toml`, `README.md`).

## Usage Steps

### Step 1: Create Template Files

Create subdirectories and template files by topic under the `templates/` directory:

```
templates/
└── email/                          # topic directory
    ├── create_user_email_subject.j2  # email subject template
    └── create_user_email_body.j2     # email body template
```

Template files use Jinja2 syntax:

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

### Step 2: Use TemplateRender in Code

```python
from infrastructure.utils.template_render import TemplateRender

# Initialize the template manager with a topic directory
template_render = TemplateRender(topic="email")

# Render templates
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

### Step 3: Send Email via the Event System

The framework's email event handler `EmailSendEventHandler` demonstrates the complete template workflow:

```python
# event_handlers/email_send_handler.py
class EmailTemplateManager:
    """Email template manager"""
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
        # Extract template parameters from the event data and render
        ...
```

When a user-created event fires, the email template is rendered automatically and sent via SMTP.

## Email Configuration

Configure SMTP in `infrastructure/config/settings.dev.yaml`:

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

## Extending: Adding a New Template Topic

1. Create a new topic directory under `templates/` (e.g., `templates/notification/`)
2. Add the Jinja2 template files
3. Create a `TemplateRender(topic="notification")` instance in code
4. Call `render_template()` to render the templates
