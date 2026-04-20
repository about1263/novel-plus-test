"""
UI测试pytest配置文件
定义UI测试专用的fixture和配置
"""
import pytest
import logging
import allure
from datetime import datetime
from logging.handlers import RotatingFileHandler

from ui_case.utils.config_manager import ConfigManager
from ui_case.utils.browser_manager import BrowserManager
from ui_case.utils.data_helper import DataHelper
from ui_case.utils.report_manager import ReportManager


def pytest_addoption(parser):
    """添加命令行选项"""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="浏览器类型: chrome 或 edge"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="是否启用无头模式"
    )
    parser.addoption(
        "--report",
        action="store",
        default="allure",
        help="报告类型: allure 或 html"
    )


def pytest_configure(config):
    """pytest配置"""
    # 注册自定义标记
    config.addinivalue_line(
        "markers", "ui: UI自动化测试"
    )
    config.addinivalue_line(
        "markers", "login: 登录功能测试"
    )
    config.addinivalue_line(
        "markers", "reading: 小说阅读功能测试"
    )
    config.addinivalue_line(
        "markers", "smoke: 冒烟测试"
    )
    config.addinivalue_line(
        "markers", "regression: 回归测试"
    )
    
    # 设置Allure报告
    if config.getoption("--report") == "allure":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        allure_report_dir = "ui_case/reports/allure-report"
        allure_results_dir = f"ui_case/reports/allure-results"
        
        # 创建目录
        import os
        os.makedirs(allure_report_dir, exist_ok=True)
        os.makedirs(allure_results_dir, exist_ok=True)
        
        # 设置Allure环境变量
        os.environ['ALLURE_RESULTS'] = allure_results_dir
        
        # 配置Allure
        config.option.allure_report_dir = allure_report_dir


@pytest.fixture(scope="session")
def config_manager(request):
    """配置管理器fixture"""
    config_file = request.config.getoption("--config", default=None)
    return ConfigManager(config_file)


@pytest.fixture(scope="session")
def browser_manager(config_manager, request):
    """浏览器管理器fixture"""
    # 从命令行参数获取浏览器配置
    browser_type = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    
    # 获取配置
    browser_config = config_manager.get_browser_config()
    
    # 覆盖命令行参数
    if browser_type:
        browser_config['browser_type'] = browser_type
    if headless:
        browser_config['headless'] = headless
    
    manager = BrowserManager(browser_config)
    yield manager
    
    # 测试会话结束后退出浏览器
    manager.quit_driver()


@pytest.fixture(scope="function")
def driver(browser_manager):
    """浏览器驱动fixture"""
    driver = browser_manager.create_driver()
    yield driver
    
    # 测试结束后截图
    try:
        test_name = request.node.name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        browser_manager.take_screenshot(f"{test_name}_{timestamp}")
    except:
        pass


@pytest.fixture(scope="session")
def data_helper():
    """测试数据助手fixture"""
    return DataHelper()


@pytest.fixture(scope="session")
def report_manager(config_manager):
    """报告管理器fixture"""
    return ReportManager(config_manager)


@pytest.fixture(scope="function")
def setup_test(request, driver, config_manager):
    """测试设置fixture"""
    test_name = request.node.name
    start_time = datetime.now()
    
    # Allure测试步骤
    allure.dynamic.title(f"UI测试: {test_name}")
    allure.dynamic.description(f"测试开始时间: {start_time}")
    
    # 日志
    logger = logging.getLogger(test_name)
    logger.info(f"开始测试: {test_name}")
    
    yield {
        'driver': driver,
        'config': config_manager,
        'logger': logger,
        'start_time': start_time
    }
    
    # 测试结束处理
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"测试结束: {test_name}, 耗时: {duration:.2f}秒")
    
    # 如果测试失败，保存截图
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        screenshot_on_failure = config_manager.get_test_config().get('screenshot_on_failure', True)
        if screenshot_on_failure:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_dir = config_manager.get_screenshot_dir()
                screenshot_path = f"{screenshot_dir}/{test_name}_{timestamp}.png"
                driver.save_screenshot(screenshot_path)
                logger.info(f"测试失败截图已保存: {screenshot_path}")
                
                # 附加到Allure报告
                allure.attach.file(screenshot_path, name=f"失败截图_{test_name}",
                                  attachment_type=allure.attachment_type.PNG)
            except Exception as e:
                logger.error(f"保存截图失败: {e}")


@pytest.fixture(scope="function")
def login_page(driver, config_manager):
    """登录页面fixture"""
    from ui_case.pages.login_page import LoginPage
    base_url = config_manager.get_environment_config()['base_url']
    return LoginPage(driver, base_url)


@pytest.fixture(scope="function")
def test_data(data_helper):
    """测试数据fixture"""
    return {
        'valid_user': data_helper.get_valid_user(),
        'invalid_users': data_helper.get_invalid_users(),
        'login_cases': data_helper.get_login_test_cases()
    }


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """生成测试报告"""
    outcome = yield
    rep = outcome.get_result()
    
    # 设置测试结果
    setattr(item, f"rep_{rep.when}", rep)
    
    # 添加Allure步骤
    if rep.when == "call" and rep.failed:
        # 添加失败信息到Allure
        if hasattr(rep, 'longrepr') and rep.longrepr:
            allure.dynamic.description(str(rep.longrepr))
        
        # 添加错误截图
        if hasattr(item, 'funcargs') and 'driver' in item.funcargs:
            driver = item.funcargs['driver']
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot = driver.get_screenshot_as_png()
                allure.attach(screenshot, name=f"失败截图_{item.name}_{timestamp}",
                            attachment_type=allure.attachment_type.PNG)
            except:
                pass


@pytest.fixture(scope="function", autouse=True)
def setup_logging(config_manager):
    """日志设置fixture"""
    logging_config = config_manager.get_logging_config()
    
    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, logging_config['log_level']))
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 文件处理器
    log_file = config_manager.get_log_file()
    file_handler = RotatingFileHandler(log_file, maxBytes=logging_config['max_bytes'], backupCount=logging_config['backup_count'], encoding='utf-8')
    file_handler.setLevel(getattr(logging, logging_config['log_level']))
    file_formatter = logging.Formatter(logging_config['log_format'])
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 控制台处理器
    if logging_config['console_output']:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, logging_config['log_level']))
        console_formatter = logging.Formatter(logging_config['log_format'])
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    yield logger