# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

基于 novel-plus 小说网站系统的自动化测试项目，采用 **API 测试 + UI 测试** 双层架构。

- **API 测试层** (`api_case/`): 针对后端 RESTful API，YAML 数据驱动，pytest + requests 实现
- **UI 测试层** (`ui_case/`): Selenium + Page Object 模式，模拟用户浏览器操作

## 完整目录结构

```
G:\novel-plus-test\
├── main.py                          # API测试主运行器（--all_modules / --work_path）
├── conftest.py                      # API测试pytest配置（fixture、标记）
├── pytest.ini                       # pytest全局配置
├── requirements.txt                 # Python依赖清单
├── novel-plus-api.json              # 后端Java接口文档
├── 起源小说平台接口测试用例.xlsx     # Excel测试用例文档
├── CLAUDE.md                        # 本文件
│
├── api_case/                        # ==== API测试用例 ====
│   ├── user_login/                  #  用户登录注册（USER_API）
│   │   └── test_user_login_module.py
│   ├── book_rank/                   #  小说排行榜查询（BDCX_API）
│   │   └── test_book_rank_module.py
│   ├── book_search/                 #  小说搜索（XSJS_API）
│   │   └── test_book_search_module.py
│   ├── book_shelf/                  #  书架管理（YDSG_API_01~10）
│   │   └── test_book_shelf_module.py
│   ├── reading_record/              #  阅读记录（YDSG_API_05~06）
│   │   └── test_reading_record_module.py
│   ├── comment/                     #  评论管理（YDSG_API_08~09）
│   │   └── test_comment_module.py
│   └── novel_management/            #  小说&章节管理（ZZGL_API）
│       └── test_novel_management_module.py
│
├── test_data/                       # ==== YAML测试数据 ====
│   ├── user_login/
│   ├── book_rank/
│   ├── book_search/
│   ├── book_shelf/
│   ├── reading_record/
│   ├── comment/
│   └── novel_management/
│
├── local_lib/                       # ==== 核心支撑库 ====
│   ├── api_client.py                #  NovelAPIClient（封装所有API调用）
│   ├── config.py                    #  ReadWriteConfig（ini配置读写）
│   ├── data_loader.py               #  YAML数据加载器
│   └── script_log.py                #  Logger（文件+控制台日志）
│
├── pro_config/                      # ==== 项目配置 ====
│   ├── pro_config.ini               #  动态配置（环境、账号、超时）
│   └── project_config.py            #  静态常量（API地址、测试用户、分类映射）
│
├── test_lib/                        # ==== 测试资源 ====
│   ├── test.png                     #  正常测试图片
│   ├── wrong_picture.jpg            #  错误格式测试图片
│   └── yuantu.png                   #  原始测试图片
│
├── ui_case/                         # ==== UI自动化测试 ====
│   ├── run_tests.py                 #  UI测试运行器
│   ├── conftest.py                  #  UI测试pytest配置
│   ├── configs/
│   │   ├── ui_config.ini            #  UI配置（浏览器、环境、报告）
│   │   └── test_data.json           #  UI测试数据及元素定位器
│   ├── drivers/
│   │   ├── chromedriver.exe
│   │   └── msedgedriver.exe
│   ├── pages/                       #  Page Object页面对象
│   │   ├── base_page.py             #   页面基类
│   │   ├── login_page.py            #   登录页
│   │   ├── home_page.py             #   首页
│   │   ├── book_detail_page.py      #   小说详情页
│   │   ├── bookshelf_page.py        #   书架页
│   │   ├── read_history_page.py     #   最近阅读页
│   │   └── reader_page.py           #   阅读器页
│   ├── test_cases/
│   │   ├── base_test.py             #   UI测试基类
│   │   ├── test_login.py            #   登录功能测试
│   │   └── test_reading.py          #   阅读功能测试
│   └── utils/
│       ├── browser_manager.py       #   浏览器驱动管理
│       ├── config_manager.py        #   配置管理
│       ├── data_helper.py           #   测试数据管理
│       ├── report_manager.py        #   Allure报告管理
│       └── cleanup_manager.py       #   临时文件清理
│
├── report/                          # API测试Allure HTML报告（自动生成）
└── logs/                            # 日志文件
    └── novel_test.log
```

## 开发命令

### 安装依赖
```bash
pip install -r requirements.txt
```

### API接口测试

#### 使用主运行器 main.py（推荐）
```bash
# 运行单个模块
python main.py --env lane --work_path api_case/user_login

# 运行多个模块（逗号分隔）
python main.py --env lane --work_path api_case/user_login,api_case/book_shelf

# 运行全部7个模块（并发执行，自动合并报告）
python main.py --env lane --all_modules

# 指定并发进程数
python main.py --env lane --all_modules --workers 3

# 指定环境
python main.py --env online --work_path api_case/book_search

# 使用标记过滤
python main.py --env lane --work_path api_case/user_login --mark user
```

#### 使用pytest直接运行
```bash
# 运行单个模块
pytest api_case/user_login/ -v

# 运行带标记的测试
pytest -m novel -v

# 并发执行
pytest api_case/book_shelf/ -v -n 2
```

#### 查看API测试报告
```bash
# API报告路径: G:\novel-plus-test\report\
allure serve report
```

### UI自动化测试

```bash
# 运行所有UI测试
python -m ui_case.run_tests

# 运行指定模块
python -m ui_case.run_tests --test_module test_login

# 运行指定用例
python -m ui_case.run_tests --test_module test_login --test_case test_normal_login

# 使用Edge浏览器 + 无头模式
python -m ui_case.run_tests --browser edge --headless

# 指定环境
python -m ui_case.run_tests --env online
```

#### 查看UI测试报告
```bash
# UI报告路径: G:\novel-plus-test\ui_case\reports\latest\
allure open ui_case/reports/latest
```

## 测试模块详解

### API测试模块（7个）

| 模块 | 目录 | 测试用例ID | 简介 |
|------|------|-----------|------|
| **用户登录注册** | `api_case/user_login/` | USER_API_01~10 | 正常/异常登录、注册、验证码等 |
| **小说排行榜** | `api_case/book_rank/` | BDCX_API_01~04 | 新书榜单、更新榜单、数据结构验证 |
| **小说搜索** | `api_case/book_search/` | XSJS_API_01~10 | 关键字搜索、分类筛选、排序、分页、作者搜索 |
| **书架管理** | `api_case/book_shelf/` | YDSG_API_01~10 | 查询是否在书架、加入/移出书架、分页查询 |
| **阅读记录** | `api_case/reading_record/` | YDSG_API_05~06 | 添加阅读记录、分页查询阅读历史 |
| **评论管理** | `api_case/comment/` | YDSG_API_08~09 | 评论列表分页、评论点赞/取消 |
| **小说&章节管理** | `api_case/novel_management/` | ZZGL_API | 小说发布、封面修改、章节CRUD、权限控制 |

### UI测试模块（2个）

| 模块 | 文件 | 标记 | 场景 |
|------|------|------|------|
| **登录测试** | `test_login.py` | ui, login, smoke | 正常登录、错误密码、空值校验、手机号格式 |
| **阅读测试** | `test_reading.py` | ui, reading, regression | 进入阅读、翻章、目录跳转、字体/主题切换、继续阅读 |

## 关键文件说明

### main.py
`NovelTestRunner` 主测试运行器：
- `run()` — 运行单个/多个模块，生成Allure报告到 `report/`
- `_run_module()` — 供并发调用的模块级执行（只生成原始结果）
- `run_all_modules()` — 7个模块并发执行，最后合并Allure报告
- 支持 `--env`, `--work_path`, `--mark`, `--workers`, `--all_modules`
- 自动检测 allure 命令路径（`shutil.which`），找不到则跳过报告生成

### conftest.py（根目录）
- `env` — 获取 `--env` 参数（online/lane）
- `api_client` — 会话级未登录API客户端
- `authenticated_client` — 登录后带Token的API客户端
- `test_user_data`, `test_book_data`, `test_chapter_data` — Faker生成中文测试数据

### local_lib/api_client.py
`NovelAPIClient` API客户端：
- `user_login()` / `author_login()` — 获取Token
- `set_token()` — 注入认证Token
- 通用 `get()` / `post()` / `delete()` — 自动处理JSON和form-data
- 重试策略：最多3次，针对429/500等状态码

### local_lib/data_loader.py
YAML数据驱动加载：
- `load_yaml_file()` — 加载YAML文件
- `load_test_cases()` / `load_test_cases_for_parametrize()` — 加载测试用例
- `get_test_data_path()` — 按模块名自动定位YAML数据文件

### pro_config/project_config.py
静态配置常量：
- `novel_api_urls` — API地址（online/lane均指向 `http://47.108.213.8`）
- `test_users` — 测试账号（admin/author/reader）
- `book_categories` — 小说分类映射

### ui_case/run_tests.py
UI测试运行器：
- 支持 `--browser`, `--headless`, `--env`, `--report`, `--test_module`, `--test_case`, `--workers`, `--clean`
- 内置 allure 路径查找（`shutil.which` + 已知路径兜底）
- 集成 `CleanupManager` 自动清理历史报告

### ui_case/conftest.py
- 提供 `driver`, `login_page`, `test_data`, `config` 等fixture
- 测试失败时自动截图并附加到Allure报告
- 设置默认 `alluredir` 为 `ui_case/reports/allure-results`

## 数据驱动测试模式

所有API测试遵循统一的数据驱动模式：

1. **YAML数据文件** (`test_data/*/`) 定义测试用例，包含请求参数和预期结果
2. **测试代码** 使用 `@pytest.mark.parametrize` 从YAML加载用例
3. **`execute_test_case()`** 统一执行：发送请求 → 校验响应码 → 校验数据结构 → 校验字段内容

YAML用例结构：
```yaml
test_cases:
  case_id:
    id: "XXX_API_01"
    title: "用例标题"
    description: "用例描述"
    request:
      method: "GET"
      endpoint: "/path"
      params: {...}
    expected:
      code: "200"
      data_checks:
        - check_type: "list_not_empty"
        - check_type: "field_exists"
          field: "xxx"
```

## 配置管理

| 文件 | 说明 | 内容 |
|------|------|------|
| `pro_config/pro_config.ini` | API环境配置 | base_url、timeout、测试账号 |
| `pro_config/project_config.py` | 项目静态常量 | API地址、用户信息、分类映射 |
| `pytest.ini` | pytest运行配置 | 默认参数 `-v --tb=short` |
| `ui_case/configs/ui_config.ini` | UI测试配置 | 浏览器、环境、报告、清理策略 |
| `ui_case/configs/test_data.json` | UI测试数据 | 元素定位器、测试用户数据 |

## 测试标记

项目已在 `conftest.py` 中注册以下标记：
- `novel` — 所有测试项自动添加
- `user`, `book`, `author`, `search`, `news`, `home`, `resource`, `ai`
- `cache`, `file`, `friendLink`, `pay`
- `common`, `front`, `admin`（预留）

UI测试专用标记（在 `ui_case/conftest.py` 中注册）：
- `ui`, `login`, `reading`, `smoke`, `regression`

## 注意事项

1. 测试前需确保 novel-plus 服务正在运行
2. API测试的Allure报告路径: `report/`（单模块）或 `report/`（合并）
3. UI测试的Allure报告路径: `ui_case/reports/allure-report`
4. 两个测试体系的报告完全隔离，不会相互覆盖
5. `novel_management` 模块需要数据库清理（`pymysql`），注意测试数据残留
6. 支持多环境切换：`--env lane`（测试） / `--env online`（生产）