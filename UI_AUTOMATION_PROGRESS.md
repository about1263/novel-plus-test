# Novel-Plus UI自动化测试进度跟踪

## 项目概述
基于 novel-plus 系统的 UI 自动化测试框架搭建，采用 PO（页面对象）设计模式，使用 Selenium 技术，支持 Chrome 146.0.7680.178 和 Edge 146.0.3856.97 浏览器可配置切换。

## 当前状态
**框架搭建已完成**，等待页面元素定位数据即可运行测试。

## 已完成任务

### 1. 项目结构与需求分析 ✅
- [x] 检查当前项目结构
- [x] 读取 `UI自动化测试用例.txt` 文件了解测试需求
- [x] 设计 UI 测试框架目录结构

### 2. 核心框架搭建 ✅
- [x] 创建页面对象模式基础类 (`ui_case/pages/base_page.py`)
- [x] 创建登录页面对象 (`ui_case/pages/login_page.py`) - 元素定位待补充
- [x] 创建浏览器驱动管理类 (`ui_case/utils/browser_manager.py`)
  - 支持 Chrome/Edge 切换
  - 可配置无头模式、窗口大小、超时等
- [x] 创建配置文件管理 (`ui_case/utils/config_manager.py`)
- [x] 创建配置文件 (`ui_case/configs/ui_config.ini`)
- [x] 创建测试数据管理 (`ui_case/utils/data_helper.py`)
- [x] 创建测试数据文件 (`ui_case/configs/test_data.json`) - 含元素定位结构

### 3. 测试执行与报告 ✅
- [x] 创建测试用例基类 (`ui_case/test_cases/base_test.py`)
- [x] 创建测试报告管理 (`ui_case/utils/report_manager.py`)
- [x] 创建 Pytest 配置 (`ui_case/conftest.py`)
- [x] 创建登录测试用例 (`ui_case/test_cases/test_login.py`)
- [x] 创建测试运行器 (`ui_case/run_tests.py`)

### 4. 目录结构与依赖 ✅
- [x] 创建完整的目录结构
- [x] 添加 `__init__.py` 文件
- [x] 更新 `requirements.txt` 添加 selenium 依赖
- [x] 创建必要的日志、截图、报告目录

## 测试用例实现状态

基于 `UI自动化测试用例.txt` 的测试场景（共14个测试用例）：

### 登录功能测试 (4个) - 已完成 ✅
- [x] `test_normal_login` - YHDL_UI_01 正常登录流程验证
- [x] `test_wrong_password_login` - YHDL_UI_02 错误密码提示验证  
- [x] `test_invalid_phone_login` - YHDL_UI_03 手机号前端校验
- [x] `test_empty_validation_login` - YHDL_UI_04 空值前端校验

### 小说阅读功能测试 (10个) - 已创建 ✅
- [x] `test_bookshelf_to_reading` - XSYD_UI_01 从书架进入阅读页验证
- [x] `test_detail_to_reading` - XSYD_UI_02 从详情页进入阅读页验证
- [x] `test_next_chapter` - XSYD_UI_03 下一章切换验证
- [x] `test_previous_chapter` - XSYD_UI_04 上一章切换验证
- [x] `test_catalog_navigation` - XSYD_UI_05 目录跳转验证
- [x] `test_font_size_adjustment` - XSYD_UI_06 字体大小调整验证
- [x] `test_theme_switching` - XSYD_UI_07 主题切换验证
- [x] `test_comment_entry` - XSYD_UI_08 评论入口验证
- [x] `test_continue_reading` - XSYD_UI_09 继续阅读验证
- [x] `test_page_scrolling` - XSYD_UI_10 页面滚动阅读验证

## 当前阻塞项

### 页面元素定位数据缺失 ❌
需要以下页面的元素定位数据：

#### 1. 登录页面 (`ui_case/pages/login_page.py`)
当前元素定位器为占位符，需要替换为实际定位：
```python
# 需要替换的实际元素定位
PHONE_INPUT = (By.ID, "phone_input")          # 手机号输入框
PASSWORD_INPUT = (By.ID, "password_input")    # 密码输入框  
LOGIN_BUTTON = (By.ID, "login_button")        # 登录按钮
ERROR_MESSAGE = (By.CLASS_NAME, "error_message")  # 错误提示
PHONE_FORMAT_ERROR = (By.ID, "phone_format_error")  # 手机号格式错误提示
EMPTY_VALIDATION_ERROR = (By.ID, "empty_validation_error")  # 空值校验提示
USER_NICKNAME = (By.ID, "user_nickname")      # 用户昵称显示区域
```

#### 2. 书架页面 (待创建)
需要书架页面的元素定位：
- 书架页面URL: `/user/favorites.html`
- "阅读"按钮
- "继续阅读"按钮
- 小说列表项

#### 3. 小说详情页面 (待创建)
需要详情页面的元素定位：
- 详情页面URL: `/book/{bookId}.html`
- "开始阅读"按钮
- 小说标题
- 小说信息

#### 4. 阅读器页面 (待创建)
需要阅读器页面的元素定位：
- 阅读器页面URL: 阅读器界面
- "下一章"按钮
- "上一章"按钮
- "目录"按钮
- 设置按钮
- 主题切换按钮
- 评论图标
- 章节标题
- 阅读内容区域
- 字体大小调整控件
- 目录面板和章节列表

## 需要的元素定位信息

请提供以下任一方式的元素定位数据（需覆盖4个页面）：

### 方式一：直接提供定位值
告诉我每个页面的元素实际定位方式（ID、CSS选择器、XPath等），我会更新代码。

### 方式二：填充配置文件
在 `ui_case/configs/test_data.json` 的 `page_elements` 部分填充实际值：
```json
"page_elements": {
  "login_page": {
    "phone_input": {
      "locator_type": "id",      // 可选：id、name、class、css、xpath
      "locator_value": "实际ID或选择器",
      "description": "手机号输入框"
    },
    // ... 其他登录页面元素
  },
  "bookshelf_page": {
    "read_button": {
      "locator_type": "css",
      "locator_value": "实际选择器",
      "description": "阅读按钮"
    },
    // ... 其他书架页面元素
  },
  "book_detail_page": {
    "start_reading_button": {
      "locator_type": "id",
      "locator_value": "实际ID",
      "description": "开始阅读按钮"
    },
    // ... 其他详情页面元素
  },
  "reader_page": {
    "next_chapter_button": {
      "locator_type": "css",
      "locator_value": "实际选择器",
      "description": "下一章按钮"
    },
    // ... 其他阅读器页面元素
  }
}
```

### 方式三：提供页面HTML片段
提供相关页面的HTML代码，我可以从中提取元素定位。

## 运行准备清单

### 已完成 ✅
1. [x] 框架代码已全部编写完成
2. [x] 目录结构已创建
3. [x] 配置文件已设置
4. [x] 测试用例已实现
5. [x] 运行脚本已创建

### 待完成 ❌
1. [ ] **获取页面元素定位数据**（关键阻塞项）
2. [ ] 下载浏览器驱动到 `ui_case/drivers/` 目录
   - ChromeDriver 146.0.7680.178 → `chromedriver.exe`
   - MSEdgeDriver 146.0.3856.97 → `msedgedriver.exe`
3. [ ] 安装依赖：`pip install -r requirements.txt`
4. [ ] 修改 `ui_config.ini` 中的 `base_url` 为实际测试环境地址

## 项目结构

```
ui_case/
├── pages/                    # 页面对象
│   ├── base_page.py         # 页面基类
│   ├── login_page.py        # 登录页面（元素定位待补充）
│   ├── bookshelf_page.py    # 书架页面（待创建）
│   ├── book_detail_page.py  # 小说详情页面（待创建）
│   └── reader_page.py       # 阅读器页面（待创建）
├── test_cases/              # 测试用例
│   ├── base_test.py         # 测试用例基类
│   ├── test_login.py        # 登录测试用例（待更新）
│   └── test_reading.py      # 小说阅读测试用例（待创建）
├── utils/                   # 工具类
│   ├── browser_manager.py   # 浏览器管理（支持Chrome/Edge切换）
│   ├── config_manager.py    # 配置管理
│   ├── data_helper.py       # 测试数据管理
│   └── report_manager.py    # 报告管理
├── configs/                 # 配置文件
│   ├── ui_config.ini        # UI测试配置
│   └── test_data.json       # 测试数据（含元素定位结构，待更新）
├── conftest.py              # Pytest配置
├── run_tests.py             # 测试运行器
├── reports/                 # 测试报告
├── screenshots/             # 截图
├── logs/                    # 日志
└── drivers/                 # 浏览器驱动目录
```

## 运行命令示例

```bash
# 安装依赖
pip install -r requirements.txt

# 运行所有UI测试（Chrome浏览器）
python ui_case/run_tests.py --browser chrome

# 运行登录模块测试
python ui_case/run_tests.py --test_module test_login

# 使用Edge浏览器无头模式
python ui_case/run_tests.py --browser edge --headless

# 生成Allure报告并打开
python ui_case/run_tests.py --report allure
allure serve ui_case/reports/latest
```

## 下一步计划

1. **立即需要**：获取所有页面（登录、书架、详情、阅读器）的元素定位数据
2. **框架更新**：创建小说阅读相关页面对象类
3. **用例更新**：更新登录测试用例，创建小说阅读测试用例
4. **配置调整**：根据实际测试环境修改配置
5. **驱动下载**：下载对应版本的浏览器驱动
6. **测试执行**：运行测试验证框架功能

## 最近更新时间
2026-04-03 - 发现测试用例更新（4个登录+10个小说阅读），需要扩展框架
2026-04-03 - 完成小说阅读功能测试用例创建，更新登录测试用例状态

---

*此文档用于跟踪UI自动化测试项目的进度，每次有重要更新时请更新此文件。*