# novel-plus-test 项目文档

## 项目概述

基于 novel-plus 小说网站的自动化测试项目，覆盖 API 接口测试和 UI 界面测试两大领域。

- **Python**: 3.13.3
- **API 测试**: pytest + requests + YAML 数据驱动 + Allure 报告
- **UI 测试**: pytest + selenium + Page Object 模式 + Allure 报告
- **定时监控**: monitor.py 定时执行 API+UI 测试，失败时 QQ 邮件告警

---

## 目录结构

```
novel-plus-test/
├── main.py                          # API测试主运行器
├── conftest.py                      # API测试 pytest 全局配置
├── pytest.ini                       # pytest 配置
├── requirements.txt                 # 依赖清单
├── monitor.py                       # 定时监控脚本（API+UI）
├── read_excel_test_cases.py         # Excel 用例读取工具
├── CLAUDE.md                        # Claude Code 项目指南
│
├── local_lib/                       # API 测试核心库
│   ├── api_client.py                #   HTTP 请求客户端
│   ├── config.py                    #   INI 配置读写
│   ├── data_loader.py               #   YAML 测试数据加载
│   └── script_log.py                #   日志配置
│
├── api_case/                        # API 测试用例（7个模块）
│   ├── user_login/                  #   用户登录模块
│   ├── book_rank/                   #   排行榜模块
│   ├── book_search/                 #   小说搜索模块
│   ├── book_shelf/                  #   书架管理模块
│   ├── comment/                     #   评论模块
│   ├── novel_management/            #   小说管理模块
│   └── reading_record/              #   阅读记录模块
│
├── test_data/                       # API 测试数据（YAML）
│   ├── user_login/
│   ├── book_rank/
│   ├── book_search/
│   ├── book_shelf/
│   ├── comment/
│   ├── novel_management/
│   └── reading_record/
│
├── ui_case/                         # UI 自动化测试
│   ├── conftest.py                  #   pytest 全局配置
│   ├── run_tests.py                 #   测试运行器
│   ├── pages/                       #   页面对象层
│   │   ├── base_page.py             #     页面基类
│   │   ├── login_page.py            #     登录页面
│   │   ├── home_page.py             #     首页
│   │   ├── book_detail_page.py      #     小说详情页
│   │   ├── bookshelf_page.py        #     书架页
│   │   ├── read_history_page.py     #     阅读历史页
│   │   └── reader_page.py           #     阅读器页
│   ├── test_cases/                  #   测试用例层
│   │   ├── base_test.py             #     测试基类
│   │   ├── test_login.py            #     登录测试（6个用例）
│   │   └── test_reading.py          #     阅读测试（10个用例）
│   └── utils/                       #   工具层
│       ├── browser_manager.py       #     浏览器驱动管理
│       ├── cleanup_manager.py       #     清理管理
│       ├── config_manager.py        #     配置管理
│       ├── data_helper.py           #     测试数据辅助
│       └── report_manager.py        #     报告管理
│
├── pro_config/                      # 项目配置
│   ├── pro_config.ini               #   动态配置（API地址、用户、邮件）
│   └── project_config.py            #   静态配置常量
│
├── logs/                            # API 测试日志
├── allure-reports/                  # API 测试报告
├── ui_case/reports/                 # UI 测试报告
├── ui_case/logs/                    # UI 测试日志
├── ui_case/drivers/                 # WebDriver 位置
└── test_lib/                        # 测试资源文件（图片等）
```

---

## 一、根目录核心文件

### 1. main.py — API 测试主运行器

```python
class NovelTestRunner:
```
测试入口，支持单模块、全模块、并发执行。

| 方法 | 说明 |
|------|------|
| `__init__(self, env, work_path)` | 初始化，检测 Allure 路径 |
| `run(self)` | 执行单模块 pytest，生成 Allure 报告 |
| `run_all_modules(self)` | **并发执行全部7个模块**，每个模块独立 allure-results，最后合并 |
| `run_specific_module(self, module_name)` | 执行指定模块 |

**CLI 参数**:
| 参数 | 说明 |
|------|------|
| `--env` | 环境: lane/online (默认 lane) |
| `--work_path` | 测试模块路径 |
| `--module` | 指定模块名 |
| `--all_modules` | 执行所有模块 |
| `--no-report` | 跳过 Allure 报告生成 |

**并发执行**: 使用 `concurrent.futures.ThreadPoolExecutor(max_workers=8)` 并行执行7个模块，每个模块使用独立的 allure-results 目录避免冲突，最后通过 `allure generate --clean -o report dir1 dir2 ...` 合并。

---

### 2. conftest.py — API 测试全局配置

**pytest 钩子**:

| 函数 | 说明 |
|------|------|
| `pytest_configure(config)` | 创建 `allure-results/environment.properties`，写入 Base_URL、TestEnv |
| `pytest_runtest_makereport(item, call)` | 追踪每个用例的 pass/fail 状态 |
| `get_summary()` | 返回测试汇总：总用例数、通过数、失败数、跳过数、失败详情 |

**全局变量**: `modules_count`, `modules_success`, `modules_failures` 用于跨模块统计。

---

### 3. monitor.py — 定时监控脚本

```python
class TestMonitor:
```

| 方法 | 说明 |
|------|------|
| `__init__(self, env, interval)` | 初始化环境、间隔、加载邮件配置 |
| `_load_mail_config(self)` | 从 `pro_config.ini [mail]` 读取 SMTP 配置 |
| `_run_cmd(self, cmd, timeout)` | 执行 shell 命令（subprocess） |
| `_run_api_tests(self)` | 执行 `main.py --all_modules`，解析 stdout 检测 FAILED |
| `_run_ui_tests(self)` | 执行 `ui_case.run_tests --headless`，120秒超时 |
| `_send_alert(self, ...)` | 通过 QQ 邮箱 SMTP_SSL 发送 HTML 告警邮件 |
| `run_once(self, round_num, api_only)` | 执行一轮测试，失败则发邮件 |
| `start(self, api_only)` | 无限循环执行，间隔 self.interval 秒 |

**CLI 参数**:
```
python monitor.py                          # 每小时执行一次
python monitor.py --once                   # 仅执行一次
python monitor.py --once --api-only        # 仅 API 测试
python monitor.py --env online             # 生产环境
python monitor.py --interval 1800          # 30分钟间隔
```

---

### 4. pytest.ini

```ini
testpaths = api_case
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers = api, user, book, ...
```

### 5. requirements.txt

```
allure-pytest==2.12.0
allure-python-commons==2.12.0
pytest==7.3.2
pytest-xdist==3.8.0
PyYAML==6.0.2
requests==2.32.4
selenium==4.21.0
```

---

## 二、local_lib — API 测试核心库

### 1. api_client.py — 通用 API 客户端

```python
class NovelAPIClient:
```

| 方法 | 说明 |
|------|------|
| `__init__(self, base_url, timeout)` | 初始化 requests.Session |
| `request(method, endpoint, data, headers)` | 核心请求方法 |
| `get(endpoint, params, headers)` | GET 请求 |
| `post(endpoint, data, headers)` | POST 请求 |
| `put(endpoint, data, headers)` | PUT 请求 |
| `delete(endpoint, headers)` | DELETE 请求 |
| `patch(endpoint, data, headers)` | PATCH 请求 |
| `login(username, password, endpoint)` | 登录并存储 token 到 session |
| `set_auth_token(token)` | 设置 Authorization 请求头 |
| `upload_file(endpoint, file_path, data, file_field)` | 文件上传 |
| `close()` | 关闭会话 |

**特点**: 自动拼接 URL，token 认证管理，统一异常处理。

---

### 2. config.py — INI 配置读写

```python
class read_write_config:
```

| 方法 | 说明 |
|------|------|
| `getValue(section, option)` | 读取配置项 |
| `setValue(section, option, value)` | 写入配置项 |

配置文件: `pro_config/pro_config.ini`

---

### 3. data_loader.py — YAML 测试数据加载器

| 函数 | 说明 |
|------|------|
| `load_test_data(module_name, yaml_file)` | 加载 YAML 测试用例 |
| `get_test_cases(module_name)` | 获取测试用例名称列表 |
| `get_case_data(module_name, case_name)` | 获取指定用例的完整数据 |
| `pytest_generate_tests(metafunc)` | pytest 动态生成测试 |
| `parametrize_test_cases` | `@pytest.mark.parametrize` 标记工厂 |

**工作流**: YAML 文件 → DataLoader → `@pytest.mark.parametrize` → 动态测试用例。

---

### 4. script_log.py — 日志配置

```python
class LogConfig:
```

**单例**: `log = LogConfig().get_logger()`

- 日志文件: `logs/novel_test.log`
- 控制台 + 文件双输出
- 格式: `时间 - 名称 - 级别 - 消息`

---

## 三、api_case — API 测试用例（7 个模块）

### 通用架构

每个模块遵循相同的 Mixin 模式:

```python
class ModuleTestRunner:                 # Mixin 类
    module_name = "user_login"          # 模块名
    test_data_path = "test_data/user_login/module.yaml"  # 数据文件

class TestModule(ModuleTestRunner):     # 测试类
    @pytest.mark.parametrize("case_name", get_test_cases())
    def test_all_cases(self, case_name):
        case_data = get_case_data(case_name)
        # 发送请求 + 验证响应
```

### 模块清单

| 模块 | Mixin 类 | 测试类 | YAML 文件 |
|------|----------|--------|-----------|
| user_login | `UserLoginModuleRunner` | `TestUserLogin` | `user_login_module.yaml` |
| book_rank | `BookRankModuleRunner` | `TestBookRank` | `book_rank_module.yaml` |
| book_search | `BookSearchModuleRunner` | `TestBookSearch` | `book_search_module.yaml` |
| book_shelf | `BookShelfModuleRunner` | `TestBookShelf` | `book_shelf_module.yaml` |
| comment | `CommentModuleRunner` | `TestComment` | `comment_module.yaml` |
| novel_management | `NovelManagementModuleRunner` | `TestNovelManagement` | `novel_management_module.yaml` |
| reading_record | `ReadingRecordModuleRunner` | `TestReadingRecord` | `reading_record_module.yaml` |

---

## 四、test_data — API 测试数据（YAML）

每个 YAML 文件的结构:

```yaml
test_cases:
  - id: "USER_API_01"
    title: "正常登录"
    description: "验证正确手机号和密码可以成功登录"
    request:
      method: POST
      endpoint: "/user/login"
      data:
        phone: "18723968509"
        password: "zxcvbnm."
    expected:
      code: 200
      data_checks:
        - "token 不为空"
        - "nickname 为'测试用户'"
    tags: ["smoke", "login"]
    auth_required: false
```

| 模块 | 用例数 | 用例编号范围 |
|------|--------|-------------|
| user_login | 10 | USER_API_01 ~ USER_API_10 |
| book_rank | 5+ | BOOK_RANK_API_* |
| book_search | 10+ | BOOK_SEARCH_API_* |
| book_shelf | 10+ | BOOK_SHELF_API_* |
| comment | 5+ | COMMENT_API_* |
| novel_management | 5+ | NOVEL_MANAGEMENT_API_* |
| reading_record | 5+ | READING_RECORD_API_* |

**测试场景覆盖**:
- **正常流程**: 成功登录、查询排行榜、搜索小说、添加书架等
- **异常流程**: 错误密码、空参数、不存在的资源、未授权访问等
- **边界条件**: 手机号格式校验、分页参数边界等

---

## 五、ui_case — UI 自动化测试

### 1. conftest.py — UI 测试全局配置

| Fixture | 说明 |
|---------|------|
| `driver` | 创建 WebDriver 实例（自动清理） |
| `config` | ConfigManager 实例 |
| `test_data` | DataHelper 实例（加载 test_data.json） |
| `login_page` | LoginPage 页面对象 |
| `base_url` | 基础 URL |

**pytest 钩子**:
- `pytest_configure`: 创建 Allure environment.properties（浏览器信息、OS、测试URL）
- `pytest_runtest_makereport`: 失败时自动截图并附加到 Allure 报告

---

### 2. run_tests.py — UI 测试运行器

| CLI 参数 | 说明 |
|----------|------|
| `--headless` | 无头模式 |
| `--browser` | chrome/edge |
| `--env` | lane/online |
| `--tests` | pytest 标记过滤 |

执行 `pytest ui_case/test_cases/`，生成 Allure 报告至 `ui_case/reports/`。

---

### 3. pages/ — 页面对象层（7 个页面）

#### base_page.py — 基类

`BasePage` 是所有页面对象的基类。

| 方法 | 说明 |
|------|------|
| `__init__(self, driver, base_url)` | 初始化 |
| `open(url)` | 导航 |
| `find_element(locator)` | 查找单个元素 |
| `find_elements(locator)` | 查找多个元素 |
| `click(locator)` | 点击 |
| `input_text(locator, text)` | 输入文本 |
| `get_text(locator)` | 获取文本 |
| `get_attribute(locator, attr)` | 获取属性 |
| `is_element_visible(locator)` | 检查可见性 |
| `wait_for_element(locator, timeout)` | 等待元素 |
| `wait_for_page_loaded()` | 等待页面加载 |
| `scroll_to_element(locator)` | 滚动到元素 |
| `execute_script(script, *args)` | 执行 JS |
| `take_screenshot(name)` | 截图 |

#### login_page.py — 登录页

| 方法 | 说明 |
|------|------|
| `open_login_page()` | 导航到登录页 `/user/login.html` |
| `input_phone(phone)` | 输入手机号（id=txtUName） |
| `input_password(password)` | 输入密码（id=txtPassword） |
| `click_login()` | 点击登录（id=btnLogin） |
| `login(phone, password)` | 完整登录流程 |
| `get_error_message()` | 获取错误提示（class=error_message） |
| `get_user_nickname()` | 获取用户昵称（id=user_nickname） |
| `is_login_successful()` | 检查登录是否成功 |

#### home_page.py — 首页

| 方法 | 说明 |
|------|------|
| `open_home_page()` | 导航到首页 `/index.html` |
| `click_novel_tag(index)` | 点击指定小说标签 |
| `click_read_button()` | 点击"阅读"按钮 |
| `get_account_info()` | 获取账户信息 |

#### book_detail_page.py — 小说详情页

| 方法 | 说明 |
|------|------|
| `open_book_detail_page(book_id)` | 导航到详情页 |
| `click_start_reading()` | 点击开始阅读 |
| `get_book_title()` | 获取书名 |
| `get_author_info()` | 获取作者信息 |
| `get_book_category()` | 获取分类 |
| `get_book_description()` | 获取简介 |
| `get_chapter_list()` | 获取章节列表 |
| `get_chapter_count()` | 获取章节数量 |
| `click_chapter_by_index(index)` | 点击指定章节 |

#### bookshelf_page.py — 书架页

| 方法 | 说明 |
|------|------|
| `open_bookshelf_page()` | 导航到书架 `/user/favorites.html` |
| `click_continue_reading_button(book_index)` | 点击继续阅读（css=td.goread a） |
| `get_book_title(book_index)` | 获取书籍标题 |
| `get_book_count()` | 获取书籍数量 |
| `is_bookshelf_empty()` | 检查书架是否为空 |
| `get_book_list()` | 获取所有书籍元素 |

#### read_history_page.py — 阅读历史页

| 方法 | 说明 |
|------|------|
| `open_read_history_page()` | 导航到阅读历史页 |
| `wait_for_history_loaded()` | 等待历史加载 |
| `get_book_count()` | 获取书籍数量 |
| `get_book_info(book_index)` | 获取书籍信息（书名、封面、时间、进度） |
| `click_continue_reading(book_index)` | 点击继续阅读（css=td.goread a） |
| `is_history_empty()` | 检查历史是否为空 |

#### reader_page.py — 阅读器页（最复杂的页面）

**导航操作**:
| 方法 | 说明 |
|------|------|
| `click_next_chapter()` | 点击下一章（class=next），自动滚动到底部再点击 |
| `click_previous_chapter()` | 点击上一章，含多个备用定位器 |
| `wait_for_chapter_loaded(timeout)` | 等待章节内容加载（10字符以上判定） |
| `wait_for_next_chapter_loaded(timeout)` | 等待下一章加载 |

**内容获取**:
| 方法 | 说明 |
|------|------|
| `get_chapter_title()` | 获取章节标题（含8个备用定位器: h1/h2/h3/.title等） |
| `get_chapter_number()` | 获取章节编号 |
| `get_url_chapter_param()` | 从 URL 解析章节参数 |
| `verify_chapter_switch(previous_title)` | 验证章节切换 |

**目录操作**:
| 方法 | 说明 |
|------|------|
| `click_catalog_icon()` | 点击目录图标（class=ico_catalog）跳转目录页 |
| `click_all_catalog_link()` | 点击全部目录链接 |
| `is_dir_list_visible()` | 检查目录列表可见 |
| `get_dir_list_chapter_count()` | 获取目录章节数量 |
| `get_dir_list_chapter_titles()` | 获取所有章节标题 |
| `click_chapter_in_dir_list(title, index)` | 按标题或索引点击章节 |

**设置操作**:
| 方法 | 说明 |
|------|------|
| `click_settings_button()` | 点击设置（class=ico_setup） |
| `close_settings_panel()` | **关闭设置面板**（7种方法尝试: 关闭按钮→JS点击→jQuery隐藏→遮罩层→ESC键→点击其他区域→等待自动关闭） |
| `is_settings_panel_visible()` | 检查设置面板可见性 |
| `increase_font_size()` | 增大字体（class=big / A+） |
| `decrease_font_size()` | 减小字体（class=small / A-） |
| `get_current_font_size()` | 获取当前字号（class=current_font） |
| `set_color_theme(color)` | 设置颜色主题（white/green/pink/yellow/gray/night，对应 id=setup_color_*） |
| `verify_theme_changed(color)` | 验证主题切换（检查 body 背景色） |

**评论操作**:
| 方法 | 说明 |
|------|------|
| `click_comment_icon()` | 点击评论图标（class=ico_comment） |
| `click_publish_comment_link()` | 点击发表评论链接（a.fr[href="#txtComment"]） |
| `is_comment_input_visible()` | 检查评论输入栏可见 |

**书签操作**:
| 方法 | 说明 |
|------|------|
| `click_my_bookshelf_link()` | 点击"我的书架"链接（class=sj_link） |
| `click_recent_reading_link()` | 点击"最近阅读"链接 |

**滚动操作**:
| 方法 | 说明 |
|------|------|
| `scroll_to_bottom()` | 分步滚动到底部（步长500px） |
| `scroll_to_top()` | 滚动到顶部 |
| `simulate_mouse_scroll(amount)` | 模拟鼠标滚轮滚动 |
| `get_scroll_position()` | 获取滚动位置信息 |
| `is_at_bottom(threshold)` | 检查是否在底部 |

---

### 4. test_cases/ — 测试用例层

#### base_test.py — 测试基类

```python
class BaseUITest:
```

| 方法 | 说明 |
|------|------|
| `setup_method(self)` | 测试前准备工作 |
| `teardown_method(self)` | 测试后清理，失败时截图 |
| `assert_true(condition, msg)` | 断言为真 |
| `assert_false(condition, msg)` | 断言为假 |
| `assert_equal(a, b, msg)` | 断言相等 |
| `assert_not_equal(a, b, msg)` | 断言不等 |
| `assert_in(a, b, msg)` | 断言包含 |
| `assert_not_in(a, b, msg)` | 断言不包含 |
| `assert_is_none(obj, msg)` | 断言为 None |
| `assert_is_not_none(obj, msg)` | 断言不为 None |
| `assert_greater(a, b, msg)` | 断言大于 |
| `assert_less(a, b, msg)` | 断言小于 |
| `assert_greater_equal(a, b, msg)` | 断言大于等于 |
| `assert_less_equal(a, b, msg)` | 断言小于等于 |
| `assert_raises(exc_type, func, *args, **kwargs)` | 断言抛出异常 |
| `get_current_url()` | 获取当前 URL |
| `refresh_page()` | 刷新页面 |
| `go_back()` | 浏览器后退 |
| `accept_alert()` | 接受 JS 弹窗 |

---

#### test_login.py — 登录测试（6 个用例）

| 用例 | Allure 标题 | 场景 |
|------|-------------|------|
| `test_normal_login` | YHDL_UI_01 - 正常登录验证 | 正确手机号+密码，验证跳转+昵称 |
| `test_wrong_password_login` | YHDL_UI_02 - 密码错误登录验证 | 密码错误，验证错误提示 |
| `test_invalid_phone_login` | YHDL_UI_03 - 手机号格式错误验证 | 非11位手机号，验证格式提示 |
| `test_empty_validation_login` | YHDL_UI_04 - 空值校验验证 | **参数化**：3种场景（手机号空、密码空、都空） |
| `test_long_phone_input` | — | 超长手机号输入 |
| `test_special_characters_password` | — | 特殊字符密码 |

---

#### test_reading.py — 阅读测试（10 个用例）

| 用例 | Allure 标题 | 场景 | 级别 |
|------|-------------|------|------|
| `test_bookshelf_to_reading` | XSYD_UI_01 - 从书架进入阅读页验证 | 登录→书架→继续阅读 | CRITICAL |
| `test_detail_to_reading` | XSYD_UI_02 - 从首页小说标签进入阅读页验证 | 首页→小说标签→阅读按钮 | CRITICAL |
| `test_next_chapter` | XSYD_UI_03 - 下一章切换验证 | 进入阅读器→下一章→标题变化 | CRITICAL |
| `test_previous_chapter` | XSYD_UI_04 - 上一章切换验证 | 下一章→上一章→回到原章节 | CRITICAL |
| `test_catalog_navigation` | XSYD_UI_05 - 目录跳转验证 | 目录图标→点击章节→跳转 | CRITICAL |
| `test_font_size_adjustment` | XSYD_UI_06 - 字体大小调整验证 | A+/A- 增大缩小验证 | NORMAL |
| `test_theme_switching` | XSYD_UI_07 - 主题切换验证 | 6种颜色主题切换验证 | NORMAL |
| `test_comment_entry` | XSYD_UI_08 - 评论入口验证 | 评论图标→评论页→发表评论链接定位 | NORMAL |
| `test_continue_reading` | XSYD_UI_09 - 继续阅读验证 | 选章节→书架→最近阅读→继续阅读→验证 | NORMAL |
| `test_page_scrolling` | XSYD_UI_10 - 页面滚动阅读验证 | 滚动到底部→下一章→验证 | CRITICAL |

**UI 测试亮点**:

- `test_previous_chapter`: 先点下一章验证切换成功，再点上一章验证回到原章节
- `test_catalog_navigation`: 尝试点击指定章节名（"边界"），不存在则点第一个
- `test_font_size_adjustment`: 数值比较（int 转换），失败则至少验证变化
- `test_continue_reading`: 随机选择章节→书架→阅读历史→继续阅读→验证章节一致性
- `test_page_scrolling`: JS 滚动到底部，验证 scrollY > 0

---

### 5. utils/ — 工具层

#### browser_manager.py — 浏览器驱动管理

```python
class BrowserManager:
```

| 方法 | 说明 |
|------|------|
| `__init__(self, config)` | 从 ui_config.ini 加载配置 |
| `_get_default_driver_path()` | 查找 drivers/ 下的 chromedriver.exe |
| `create_driver()` | 创建 Chrome/Edge WebDriver |
| `_create_chrome_driver(headless, window_size)` | Chrome 配置（含 webdriver-manager 自动下载） |
| `_create_edge_driver(headless, window_size)` | Edge 配置 |
| `quit_driver()` | 退出浏览器 |
| `take_screenshot(filename)` | 截图保存到 allure-results/ |
| `switch_to_new_window()` | 切换到最新窗口 |

**Chrome 选项**: `--headless`, `--no-sandbox`, `--disable-gpu`, `--disable-dev-shm-usage`, `window-size=1920,1080`

---

#### config_manager.py — 配置管理

```python
class ConfigManager:
```

| 方法 | 说明 |
|------|------|
| `get_browser_config()` | 浏览器配置字典 |
| `get_environment_config()` | 环境配置（base_url 等） |
| `get_test_config()` | 测试配置（用户、截图目录） |
| `get_timeout_config()` | 超时配置 |
| `get_logging_config()` | 日志配置 |
| `get_report_config()` | 报告配置 |
| `get_full_url(path)` | 拼接完整 URL |
| `get_login_url()`, `get_home_url()` | 特定 URL 快捷方法 |
| `update_config(section, key, value)` | 写入配置 |
| `save_to_json(json_file)` | 导出为 JSON |
| `load_from_json(json_file)` | 从 JSON 导入 |

---

#### data_helper.py — 测试数据辅助

```python
class DataHelper:
```

| 方法 | 说明 |
|------|------|
| `get_valid_user()` | 获取有效用户数据 |
| `get_invalid_users()` | 获取无效用户列表 |
| `get_user_by_type(type)` | 按类型获取用户 |
| `get_test_case(module, case_name)` | 获取指定测试用例 |
| `get_login_test_cases()` | 获取登录测试用例 |
| `generate_phone_number()` | 生成随机手机号 |
| `generate_password()` | 生成随机密码 |
| `generate_nickname()` | 生成随机昵称 |
| `generate_email()` | 生成随机邮箱 |
| `generate_date()` | 生成随机日期 |
| `generate_text()` | 生成随机文本 |
| `add_user(user_dict)` | 添加用户 |
| `add_test_case(module, case_dict)` | 添加测试用例 |
| `export_to_json(file_path)` | 导出数据到 JSON |
| `import_from_json(file_path)` | 从 JSON 导入数据 |

---

#### cleanup_manager.py — 清理管理

```python
class CleanupManager:
```

| 方法 | 说明 |
|------|------|
| `increment_and_check()` | 自增运行计数，返回是否需要清理 |
| `cleanup_all()` | 执行所有清理 |
| `cleanup_screenshots(keep_last)` | 保留最近N张截图 |
| `cleanup_logs()` | 日志轮转（超10MB） |
| `cleanup_old_reports(keep_days)` | 删除过期报告（3天） |
| `cleanup_temp_files()` | 删除 `__pycache__` |
| `cleanup_on_demand(screenshot_days, report_days)` | 按需清理 |

---

#### report_manager.py — 报告管理

```python
class ReportManager:
```

| 方法 | 说明 |
|------|------|
| `setup_allure(report_dir)` | 创建 allure-results 目录 |
| `generate_allure_report(results_dir, report_dir, clean)` | 生成 Allure 报告 |
| `open_allure_report(report_dir)` | 打开 Allure 报告 |
| `generate_html_report(test_results, report_file)` | 生成自定义 HTML 报告 |
| `save_test_results(results, results_file)` | 保存测试结果到 JSON |
| `attach_screenshot_to_allure(screenshot_path, name)` | 附加截图到 Allure |
| `attach_log_to_allure(log_file, name)` | 附加日志到 Allure |
| `create_environment_file(env_data, env_file)` | 创建 environment.properties |
| `cleanup_old_reports(keep_days)` | 清理旧报告 |

---

## 六、pro_config — 项目配置

### 1. pro_config.ini

| Section | Key | 说明 |
|---------|-----|------|
| `[projectConfig]` | `python_env`, `project_path` | 项目路径配置 |
| `[novelConfig]` | `api_base_url` | API 基础地址 |
| `[testData]` | 用户数据 | 测试账号 |
| `[mail]` | `smtp_server`, `smtp_port`, `sender`, `password`, `receiver` | QQ 邮箱 SMTP 配置 |

### 2. project_config.py — 静态常量

| 常量 | 说明 |
|------|------|
| `novel_api_urls` | online/lane 环境 API 地址（均指向 http://47.108.213.8） |
| `test_users` | admin/author/reader/mobile_reader/test_reader 五个测试用户 |
| `book_categories` | 小说分类列表 |
| `book_status` | 小说状态（连载中/已完结） |

---

## 七、测试用例汇总

### API 测试（7 个模块）

| 模块 | 测试内容 | 用例数 |
|------|----------|--------|
| user_login | 登录、注册、校验 | ~10 |
| book_rank | 排行榜查询 | ~5 |
| book_search | 搜索小说 | ~10 |
| book_shelf | 书架增删改查 | ~10 |
| comment | 评论查询、提交 | ~5 |
| novel_management | 小说分类、详情、章节 | ~5 |
| reading_record | 阅读记录查询 | ~5 |
| **合计** | | **~50+** |

### UI 测试（2 个测试类）

| 测试类 | 测试内容 | 用例数 |
|--------|----------|--------|
| test_login | 正常登录、错误密码、手机号格式、空值校验 | 6 |
| test_reading | 书架→阅读、首页→阅读、上下章、目录、字体、主题、评论、继续阅读、滚动 | 10 |
| **合计** | | **16** |

---

## 八、运行指南

### API 测试

```bash
# 安装依赖
pip install -r requirements.txt

# 运行单个模块
python main.py --env lane --work_path api_case/user_login

# 运行所有模块
python main.py --env lane --all_modules

# 使用 pytest 直接运行
pytest api_case/user_login/ -v --alluredir=report

# 查看报告
allure serve allure-reports/latest
```

### UI 测试

```bash
# 运行所有 UI 测试（有头模式）
python -m ui_case.run_tests

# 无头模式
python -m ui_case.run_tests --headless

# 指定浏览器
python -m ui_case.run_tests --browser edge

# 运行指定标记的测试
pytest ui_case/test_cases/ -m smoke -v --alluredir=ui_case/reports/allure-results
```

### 定时监控

```bash
# 每小时执行一次
python monitor.py

# 仅执行一次
python monitor.py --once

# 仅 API 测试
python monitor.py --once --api-only
```

---

## 九、关键技术点

### API 测试架构
- **数据驱动**: YAML 文件定义请求数据和期望结果
- **Mixin 模式**: ModuleTestRunner 混入类提供模块名和数据路径
- **并发执行**: 7 个模块通过 ThreadPoolExecutor 并行运行
- **独立报告**: 每个模块独立的 allure-results 目录，最后合并

### UI 测试架构
- **Page Object**: 7 个页面对象封装元素定位和操作
- **链式调用**: 方法返回 self，支持 `.click().wait().verify()` 链式
- **健壮定位**: 每个元素/操作含多个备用定位器
- **Fallback 机制**: close_settings_panel() 含 7 种方法
- **Allure 集成**: 每个步骤截图，失败自动截图

### 监控系统
- 定时执行 API+UI 测试
- 失败时通过 QQ 邮箱 SMTP_SSL 发送 HTML 告警
- 支持 API-only 模式
- 完整的日志记录
