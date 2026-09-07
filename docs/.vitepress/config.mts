import { defineConfig } from 'vitepress'

// https://vitepress.dev/zh/guide/routing
// 站点采用「基于文件的路由」：源目录为 docs/，中文文档通过 rewrites 重写为
// 语义化路由（源文件不移动）；英文文档位于 docs/en/ 下，路由与最终路径一致。
// 多语言：根路径为简体中文，/en/ 前缀为英文（见 locales 配置）。
export default defineConfig({
  title: 'FastBrace',
  description:
    '基于FastAPI的中后台高性能框架：DDD 分层架构、可靠代码生成与生产级 API',
  cleanUrls: true,

  // 直接复用仓库根目录 assets/ 作为静态资源目录，避免重复拷贝图片
  vite: {
    publicDir: '../assets'
  },

  // 路由重写：中文源文件路径 --> 站点路由
  // 中文文档位于 docs/cn/ 下，通过 rewrites 映射为语义化 URL
  rewrites: {
    // 项目介绍
    'cn/intro/about.md': 'intro/about.md',
    'cn/intro/getting-started.md': 'intro/getting-started.md',
    'cn/intro/why-FastBrace.md': 'intro/why-FastBrace.md',
    // 基础
    'cn/basics/tech-stack.md': 'basics/tech-stack.md',
    'cn/basics/project-structure.md': 'basics/project-structure.md',
    'cn/basics/docs-dev-deploy.md': 'basics/docs-dev-deploy.md',
    // 基础 - 功能概览
    'cn/basics/features/login.md': 'basics/features/login.md',
    'cn/basics/features/users.md': 'basics/features/users.md',
    'cn/basics/features/roles.md': 'basics/features/roles.md',
    'cn/basics/features/permissions.md': 'basics/features/permissions.md',
    'cn/basics/features/files.md': 'basics/features/files.md',
    'cn/basics/features/events.md': 'basics/features/events.md',
    'cn/basics/features/cron-jobs.md': 'basics/features/cron-jobs.md',
    // 进阶 - 架构指南
    'cn/advanced/architecture/api-layer.md': 'advanced/architecture/api-layer.md',
    'cn/advanced/architecture/application-layer.md': 'advanced/architecture/application-layer.md',
    'cn/advanced/architecture/domain-layer.md': 'advanced/architecture/domain-layer.md',
    'cn/advanced/architecture/domain/domain-entity.md': 'advanced/architecture/domain-entity.md',
    'cn/advanced/architecture/domain/domain-repo.md': 'advanced/architecture/domain-repo.md',
    'cn/advanced/architecture/domain/domain-service.md': 'advanced/architecture/domain-service.md',
    'cn/advanced/architecture/domain/domain-value-object.md': 'advanced/architecture/domain-value-object.md',
    'cn/advanced/architecture/infrastructure/infrastructure-core.md': 'advanced/architecture/infrastructure-core.md',
    'cn/advanced/architecture/infrastructure/infrastructure-config.md': 'advanced/architecture/infrastructure-config.md',
    // 进阶 - 功能指南
    'cn/advanced/permission.md': 'advanced/permission.md',
    'cn/advanced/events.md': 'advanced/events.md',
    'cn/advanced/cron-jobs.md': 'advanced/cron-jobs.md',
    'cn/advanced/logging.md': 'advanced/logging.md',
    'cn/advanced/log-monitoring.md': 'advanced/log-monitoring.md',
    'cn/advanced/encryption.md': 'advanced/encryption.md',
    'cn/advanced/templates.md': 'advanced/templates.md',
    // 进阶 - 工程化
    'cn/advanced/engineering/skill.md': 'advanced/engineering/skill.md',
    'cn/advanced/engineering/mcp.md': 'advanced/engineering/mcp.md',
    'cn/advanced/engineering/lint-and-style.md': 'advanced/engineering/lint-and-style.md',
    'cn/advanced/engineering/deployment-guide.md': 'advanced/engineering/deployment-guide.md',
    'cn/advanced/engineering/cicd-pipeline.md': 'advanced/engineering/cicd-pipeline.md',
    // 项目实战
    'cn/practice/vben-admin.md': 'practice/vben-admin.md',
    // 社区与支持
    'cn/community/support.md': 'community/support.md',
    'cn/community/wechat.md': 'community/wechat.md',
    'cn/community/sponsor.md': 'community/sponsor.md'
  },

  // 跨语言共享的主题配置
  themeConfig: {
    logo: {
      src: '/FastBrace-hero-logo.png',
      alt: 'FastBrace Logo',
      height: 36
    },
    socialLinks: [
      {
        icon: 'github',
        link: 'https://github.com/Zhouguangminggit/FastBrace'
      }
    ]
  },

  locales: {
    // ============ 简体中文（根路径） ============
    root: {
      label: '简体中文',
      lang: 'zh-CN',
      themeConfig: {
        nav: [
          { text: '项目介绍', link: '/intro/about', activeMatch: '^/intro/' },
          { text: '基础', link: '/basics/tech-stack', activeMatch: '^/basics/' },
          { text: '进阶', link: '/advanced/permission', activeMatch: '^/advanced/' },
          { text: '项目实战', link: '/practice/vben-admin', activeMatch: '^/practice/' },
          { text: '社区与支持', link: '/community/support', activeMatch: '^/community/' },
          { text: '更新日志', link: '/changelog/' }
        ],

        // 侧边栏：六大分组，支持折叠
        sidebar: [
          // 项目介绍
          {
            text: '项目介绍',
            collapsed: true,
            items: [
              { text: '关于 FastBrace', link: '/intro/about' },
              { text: '为什么选择 FastBrace', link: '/intro/why-FastBrace' },
              { text: '快速开始', link: '/intro/getting-started' }
            ]
          },
          // 基础
          {
            text: '基础',
            collapsed: false,
            items: [
              { text: '技术栈', link: '/basics/tech-stack' },
              { text: '目录结构', link: '/basics/project-structure' },
              { text: '文档', link: '/basics/docs-dev-deploy' },
              {
                text: '功能概览',
                collapsed: true,
                items: [
                  { text: '登录认证', link: '/basics/features/login' },
                  { text: '用户管理', link: '/basics/features/users' },
                  { text: '角色管理', link: '/basics/features/roles' },
                  { text: '权限系统', link: '/basics/features/permissions' },
                  { text: '文件管理', link: '/basics/features/files' },
                  { text: '事件系统', link: '/basics/features/events' },
                  { text: '定时任务', link: '/basics/features/cron-jobs' }
                ]
              }
            ]
          },
          // 进阶
          {
            text: '进阶',
            collapsed: true,
            items: [
              {
                text: '架构指南',
                collapsed: true,
                items: [
                  { text: 'API 层', link: '/advanced/architecture/api-layer' },
                  { text: 'Application 层', link: '/advanced/architecture/application-layer' },
                  { text: 'Domain 层总览', link: '/advanced/architecture/domain-layer' },
                  {
                    text: 'Domain 子专题',
                    collapsed: true,
                    items: [
                      { text: '实体（Entity）', link: '/advanced/architecture/domain-entity' },
                      { text: '仓储（Repository）', link: '/advanced/architecture/domain-repo' },
                      { text: '领域服务（Service）', link: '/advanced/architecture/domain-service' },
                      { text: '值对象（Value Object）', link: '/advanced/architecture/domain-value-object' }
                    ]
                  },
                  { text: 'Infrastructure 核心', link: '/advanced/architecture/infrastructure-core' },
                  { text: 'Infrastructure 配置', link: '/advanced/architecture/infrastructure-config' }
                ]
              },
              { text: '权限系统', link: '/advanced/permission' },
              { text: '事件系统', link: '/advanced/events' },
              { text: '定时任务', link: '/advanced/cron-jobs' },
              { text: '日志系统', link: '/advanced/logging' },
              { text: '线上日志监控', link: '/advanced/log-monitoring' },
              { text: '加密通信', link: '/advanced/encryption' },
              { text: '模板引擎', link: '/advanced/templates' },
              {
                text: '工程化',
                collapsed: true,
                items: [
                  { text: '工程化工具', link: '/advanced/engineering/lint-and-style' },
                  { text: 'Skill', link: '/advanced/engineering/skill' },
                  { text: 'MCP', link: '/advanced/engineering/mcp' },
                  { text: '部署指南', link: '/advanced/engineering/deployment-guide' },
                  { text: 'CI/CD 流水线', link: '/advanced/engineering/cicd-pipeline' }
                ]
              }
            ]
          },
          // 项目实战
          {
            text: '生态',
            collapsed: false,
            items: [
              { text: '对接 vben-vue-admin', link: '/practice/vben-admin' }
            ]
          },
          // 社区与支持
          {
            text: '社区与支持',
            collapsed: true,
            items: [
              { text: '技术支持', link: '/community/support' },
              { text: '加入群聊', link: '/community/wechat' },
              { text: '赞助', link: '/community/sponsor' }
            ]
          },
          // 更新日志
          {
            text: '更新日志',
            collapsed: true,
            items: [{ text: '版本记录', link: '/changelog/' }]
          }
        ],

        // 本地搜索
        search: {
          provider: 'local',
          options: {
            translations: {
              button: { buttonText: '搜索文档', buttonAriaLabel: '搜索文档' },
              modal: {
                noResultsText: '无法找到相关结果',
                resetButtonTitle: '清除查询条件',
                footer: {
                  selectText: '选择',
                  navigateText: '切换',
                  closeText: '关闭'
                }
              }
            }
          }
        },

        // 页面大纲（右侧）
        outline: { level: [2, 3], label: '本页目录' },
        // 允许大纲折叠
        outlineTitle: '目录',
        // 文档底部导航
        docFooter: { prev: '上一篇', next: '下一篇' },
        // 最后更新时间
        lastUpdated: { text: '最后更新于' },
        // 返回顶部
        returnToTopLabel: '回到顶部',
        // 侧边栏菜单标签
        sidebarMenuLabel: '菜单',
        // 主题切换标签
        darkModeSwitchLabel: '主题'
      }
    },

    // ============ 英文（/en/ 前缀） ============
    en: {
      label: 'English',
      lang: 'en-US',
      description:
        'Agent-first FastAPI backend framework: DDD layers, reliable code generation, and production-ready APIs',
      themeConfig: {
        nav: [
          { text: 'Introduction', link: '/en/intro/about', activeMatch: '^/en/intro/' },
          { text: 'Basics', link: '/en/basics/tech-stack', activeMatch: '^/en/basics/' },
          { text: 'Advanced', link: '/en/advanced/permission', activeMatch: '^/en/advanced/' },
          { text: 'Practice', link: '/en/practice/vben-admin', activeMatch: '^/en/practice/' },
          { text: 'Community', link: '/en/community/support', activeMatch: '^/en/community/' },
          { text: 'Changelog', link: '/en/changelog/' }
        ],

        sidebar: [
          // Introduction
          {
            text: 'Introduction',
            collapsed: true,
            items: [
              { text: 'About FastBrace', link: '/en/intro/about' },
              { text: 'Why FastBrace', link: '/en/intro/why-FastBrace' },
              { text: 'Getting Started', link: '/en/intro/getting-started' }
            ]
          },
          // Basics
          {
            text: 'Basics',
            collapsed: false,
            items: [
              { text: 'Tech Stack', link: '/en/basics/tech-stack' },
              { text: 'Project Structure', link: '/en/basics/project-structure' },
              { text: 'Docs Dev & Deploy', link: '/en/basics/docs-dev-deploy' },
              {
                text: 'Feature Overview',
                collapsed: true,
                items: [
                  { text: 'Login & Auth', link: '/en/basics/features/login' },
                  { text: 'User Management', link: '/en/basics/features/users' },
                  { text: 'Role Management', link: '/en/basics/features/roles' },
                  { text: 'Permission System', link: '/en/basics/features/permissions' },
                  { text: 'File Management', link: '/en/basics/features/files' },
                  { text: 'Event System', link: '/en/basics/features/events' },
                  { text: 'Cron Jobs', link: '/en/basics/features/cron-jobs' }
                ]
              }
            ]
          },
          // Advanced
          {
            text: 'Advanced',
            collapsed: true,
            items: [
              {
                text: 'Architecture Guide',
                collapsed: true,
                items: [
                  { text: 'API Layer', link: '/en/advanced/architecture/api-layer' },
                  { text: 'Application Layer', link: '/en/advanced/architecture/application-layer' },
                  { text: 'Domain Layer Overview', link: '/en/advanced/architecture/domain-layer' },
                  {
                    text: 'Domain Sub-topics',
                    collapsed: true,
                    items: [
                      { text: 'Entity', link: '/en/advanced/architecture/domain-entity' },
                      { text: 'Repository', link: '/en/advanced/architecture/domain-repo' },
                      { text: 'Domain Service', link: '/en/advanced/architecture/domain-service' },
                      { text: 'Value Object', link: '/en/advanced/architecture/domain-value-object' }
                    ]
                  },
                  { text: 'Infrastructure Core', link: '/en/advanced/architecture/infrastructure-core' },
                  { text: 'Infrastructure Config', link: '/en/advanced/architecture/infrastructure-config' }
                ]
              },
              { text: 'Permission System', link: '/en/advanced/permission' },
              { text: 'Event System', link: '/en/advanced/events' },
              { text: 'Cron Jobs', link: '/en/advanced/cron-jobs' },
              { text: 'Logging', link: '/en/advanced/logging' },
              { text: 'Log Monitoring', link: '/en/advanced/log-monitoring' },
              { text: 'Encryption', link: '/en/advanced/encryption' },
              { text: 'Templates', link: '/en/advanced/templates' },
              {
                text: 'Engineering',
                collapsed: true,
                items: [
                  { text: 'Lint and Style', link: '/en/advanced/engineering/lint-and-style' },
                  { text: 'Skill', link: '/en/advanced/engineering/skill' },
                  { text: 'MCP', link: '/en/advanced/engineering/mcp' },
                  { text: 'Deployment Guide', link: '/en/advanced/engineering/deployment-guide' },
                  { text: 'CI/CD Pipeline', link: '/en/advanced/engineering/cicd-pipeline' }
                ]
              }
            ]
          },
          // Practice
          {
            text: 'Ecosystems',
            collapsed: false,
            items: [
              { text: 'vben-vue-admin Integration', link: '/en/practice/vben-admin' }
            ]
          },
          // Community
          {
            text: 'Community',
            collapsed: true,
            items: [
              { text: 'Support', link: '/en/community/support' },
              { text: 'Join Group', link: '/en/community/wechat' },
              { text: 'Sponsor', link: '/en/community/sponsor' }
            ]
          },
          // Changelog
          {
            text: 'Changelog',
            collapsed: true,
            items: [{ text: 'Release Notes', link: '/en/changelog/' }]
          }
        ],

        // 本地搜索
        search: {
          provider: 'local'
        },

        outline: { level: [2, 3], label: 'On this page' },
        outlineTitle: 'Contents',
        docFooter: { prev: 'Previous', next: 'Next' },
        lastUpdated: { text: 'Last updated' },
        returnToTopLabel: 'Return to top',
        sidebarMenuLabel: 'Menu',
        darkModeSwitchLabel: 'Appearance'
      }
    }
  }
})
