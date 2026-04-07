# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 novel-plus 系统的自动化测试项目，专门用于测试 novel-plus 小说网站系统的 API 接口。项目基于原 novel_test 项目结构改造，覆盖 novel-plus 的 front 和 common 模块接口，未来可能扩展 admin 模块。项目采用模块化设计，支持多环境测试和并发执行。

## 开发命令

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行测试

#### 使用主运行器（推荐）
```bash
# 运行单个模块测试
python main.py --env lane --work_path api_case/user

# 运行所有模块测试
python main.py --env lane --all_modules

# 指定并发工作进程数
python main.py --env lane --work_path api_case/user --workers 2
```

#### 使用pytest直接运行
```bash
# 运行单个测试模块
pytest api_case/user/ -v --alluredir=report

# 运行带标记的测试
pytest -m user -v --alluredir=report

# 并发执行测试
pytest api_case/user/ -v -n 2 --alluredir=report
```

### 查看测试报告
```bash
# 查看最新生成的报告
allure serve allure-reports/latest

# 查看特定时间生成的报告
allure serve allure-reports/report_20260401_143530

# 使用主运行器运行测试时会自动生成带时间戳的报告
# 报告目录格式: allure-reports/report_YYYYMMDD_HHMMSS
# latest目录总是指向最新报告
```

## 项目架构

### 核心模块
- **main.py**: 主测试运行器，支持命令行参数和并发执行
- **conftest.py**: Pytest配置，包含fixture定义和测试标记
- **local_lib/**: 自定义库，包含API客户端、配置管理和日志工具
- **api_case/**: 测试用例目录，按功能模块组织

### 测试模块结构
- **author/**: 作者模块测试（笔名检查、小说发布、章节管理、收入统计等）
- **book/**: 小说模块测试（排行榜、分类查询、搜索、详情、评论等）
- **cache/**: 缓存模块测试（缓存刷新）
- **file/**: 文件模块测试（验证码获取）
- **friendLink/**: 友链模块测试（首页友链列表）
- **news/**: 新闻模块测试（首页新闻、分页查询、阅读量统计）
- **pay/**: 支付模块测试（支付宝支付、支付通知）
- **user/**: 用户模块测试（令牌刷新、书架管理、阅读记录、反馈等）


### 配置管理
- **pro_config/pro_config.ini**: 动态配置文件
- **pro_config/project_config.py**: 项目静态配置
- 环境变量 `NOVEL_ENV` 控制测试环境（online/lane）

### 测试标记
项目支持以下pytest标记（需在conftest.py中定义）：
- `@pytest.mark.author` - 作者模块测试
- `@pytest.mark.book` - 小说模块测试
- `@pytest.mark.cache` - 缓存模块测试
- `@pytest.mark.file` - 文件模块测试
- `@pytest.mark.friendLink` - 友链模块测试
- `@pytest.mark.news` - 新闻模块测试
- `@pytest.mark.pay` - 支付模块测试
- `@pytest.mark.user` - 用户模块测试
- `@pytest.mark.common` - 通用模块测试（预留）
- `@pytest.mark.front` - 前端模块测试（预留）
- `@pytest.mark.admin` - 管理模块测试（预留）

## 关键文件说明

### main.py:17-92
主测试运行器类 `NovelTestRunner`，支持并发执行和模块化测试管理。

### conftest.py:23-100
Pytest fixture定义，包括API客户端、认证客户端和测试数据生成器。

### local_lib/api_client.py
API客户端类 `NovelAPIClient`，封装了所有小说网站API的调用方法。

### pro_config/project_config.py:6-34
项目配置常量，包括API地址、测试用户和小说分类配置。

## 测试数据管理

测试数据通过fixture动态生成，使用Faker库创建真实的中文测试数据。关键fixture包括：
- `test_user_data`: 生成测试用户数据
- `test_book_data`: 生成测试小说数据  
- `test_chapter_data`: 生成测试章节数据

## 注意事项

1. 测试前需确保小说网站服务正在运行
2. API地址配置在 `pro_config/pro_config.ini` 中
3. 部分测试需要预置数据，可能需要调整或跳过
4. 支持多环境测试，通过 `--env` 参数切换