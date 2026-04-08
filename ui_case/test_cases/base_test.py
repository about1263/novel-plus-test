"""
UI测试用例基类
所有UI测试用例应继承此类
"""
import pytest
import logging
import allure
import time
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver

from ui_case.utils.browser_manager import BrowserManager
from ui_case.utils.config_manager import ConfigManager
from ui_case.pages.login_page import LoginPage


class BaseUITest:
    """UI测试基类"""
    
    @pytest.fixture(scope="class", autouse=True)
    def config(self):
        """配置管理器fixture"""
        return ConfigManager()
    
    @pytest.fixture(scope="class", autouse=True)
    def browser_manager(self, config):
        """浏览器管理器fixture"""
        browser_config = config.get_browser_config()
        manager = BrowserManager(browser_config)
        yield manager
        manager.quit_driver()
    
    @pytest.fixture(scope="function", autouse=True)
    def driver(self, browser_manager):
        """浏览器驱动fixture"""
        driver = browser_manager.create_driver()
        yield driver
        
        # 测试结束后截图（如果配置允许）
        try:
            test_name = self._get_test_name()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            browser_manager.take_screenshot(f"{test_name}_{timestamp}")
        except:
            pass
        finally:
            # 确保每个测试结束后关闭浏览器驱动
            browser_manager.quit_driver()
    
    @pytest.fixture(scope="function", autouse=True)
    def login_page(self, driver, config):
        """登录页面fixture"""
        base_url = config.get_environment_config()['base_url']
        return LoginPage(driver, base_url)
    
    @pytest.fixture(scope="function", autouse=True)
    def setup_logging(self, config):
        """日志设置fixture"""
        logging_config = config.get_logging_config()
        
        # 创建日志记录器
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, logging_config['log_level']))
        
        # 清除现有处理器
        logger.handlers.clear()
        
        # 文件处理器
        log_file = config.get_log_file()
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
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
        
        self.logger = logger
        yield logger
    
    @pytest.fixture(scope="function", autouse=True)
    def setup_test(self, request, driver, config):
        """测试设置fixture"""
        self.driver = driver
        self.config = config
        self.test_name = request.node.name
        self.start_time = time.time()
        
        # Allure测试步骤
        allure.dynamic.title(f"UI测试: {self.test_name}")
        allure.dynamic.description(f"测试开始时间: {datetime.now()}")
        
        self.logger.info(f"开始测试: {self.test_name}")
        
        yield
        
        # 测试结束处理
        end_time = time.time()
        duration = end_time - self.start_time
        self.logger.info(f"测试结束: {self.test_name}, 耗时: {duration:.2f}秒")
        
        # 如果测试失败，保存截图
        if request.node.rep_call.failed and config.get_test_config()['screenshot_on_failure']:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"{config.get_screenshot_dir()}/{self.test_name}_{timestamp}.png"
                driver.save_screenshot(screenshot_path)
                self.logger.info(f"测试失败截图已保存: {screenshot_path}")
                
                # 附加到Allure报告
                allure.attach.file(screenshot_path, name=f"失败截图_{self.test_name}",
                                  attachment_type=allure.attachment_type.PNG)
            except Exception as e:
                self.logger.error(f"保存截图失败: {e}")
    
    def _get_test_name(self):
        """获取测试名称"""
        import inspect
        stack = inspect.stack()
        for frame in stack:
            if frame.function.startswith('test_'):
                return frame.function
        return "unknown_test"
    
    # 断言方法
    def assert_equal(self, actual, expected, message=""):
        """断言相等"""
        assert actual == expected, f"{message} 实际值: {actual}, 期望值: {expected}"
    
    def assert_not_equal(self, actual, expected, message=""):
        """断言不相等"""
        assert actual != expected, f"{message} 实际值: {actual}, 期望值: {expected}"
    
    def assert_true(self, condition, message=""):
        """断言为真"""
        assert condition, f"{message} 条件为假"
    
    def assert_false(self, condition, message=""):
        """断言为假"""
        assert not condition, f"{message} 条件为真"
    
    def assert_in(self, member, container, message=""):
        """断言包含"""
        assert member in container, f"{message} {member} 不在 {container} 中"
    
    def assert_not_in(self, member, container, message=""):
        """断言不包含"""
        assert member not in container, f"{message} {member} 在 {container} 中"
    
    def assert_is_none(self, obj, message=""):
        """断言为None"""
        assert obj is None, f"{message} 对象不为None: {obj}"
    
    def assert_is_not_none(self, obj, message=""):
        """断言不为None"""
        assert obj is not None, f"{message} 对象为None"
    
    def assert_greater(self, a, b, message=""):
        """断言大于"""
        assert a > b, f"{message} {a} 不大于 {b}"
    
    def assert_greater_equal(self, a, b, message=""):
        """断言大于等于"""
        assert a >= b, f"{message} {a} 不大于等于 {b}"
    
    def assert_less(self, a, b, message=""):
        """断言小于"""
        assert a < b, f"{message} {a} 不小于 {b}"
    
    def assert_less_equal(self, a, b, message=""):
        """断言小于等于"""
        assert a <= b, f"{message} {a} 不小于等于 {b}"
    
    # 页面操作方法
    def open_url(self, url):
        """打开URL"""
        self.driver.get(url)
        self.logger.info(f"打开URL: {url}")
    
    def get_current_url(self):
        """获取当前URL"""
        return self.driver.current_url
    
    def get_page_title(self):
        """获取页面标题"""
        return self.driver.title
    
    def refresh_page(self):
        """刷新页面"""
        self.driver.refresh()
        self.logger.info("刷新页面")
    
    def navigate_back(self):
        """后退"""
        self.driver.back()
        self.logger.info("后退")
    
    def navigate_forward(self):
        """前进"""
        self.driver.forward()
        self.logger.info("前进")
    
    def switch_to_new_window(self):
        """切换到新窗口"""
        window_handles = self.driver.window_handles
        if len(window_handles) > 1:
            self.driver.switch_to.window(window_handles[-1])
            return True
        return False
    
    def switch_to_window_by_index(self, index):
        """通过索引切换窗口"""
        window_handles = self.driver.window_handles
        if 0 <= index < len(window_handles):
            self.driver.switch_to.window(window_handles[index])
            return True
        return False
    
    def close_current_window(self):
        """关闭当前窗口"""
        window_handles = self.driver.window_handles
        if len(window_handles) > 1:
            self.driver.close()
            self.driver.switch_to.window(window_handles[0])
            return True
        return False
    
    # 等待方法
    def wait(self, seconds):
        """等待指定秒数"""
        time.sleep(seconds)
    
    def wait_for_page_load(self, timeout=30):
        """等待页面加载完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            page_state = self.driver.execute_script("return document.readyState")
            if page_state == "complete":
                return True
            time.sleep(0.5)
        raise TimeoutError(f"页面加载超时: {timeout}秒")
    
    # 截图方法
    def take_screenshot(self, name=None):
        """截取屏幕截图"""
        if name is None:
            name = self.test_name
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_dir = self.config.get_screenshot_dir()
        screenshot_path = f"{screenshot_dir}/{name}_{timestamp}.png"
        
        self.driver.save_screenshot(screenshot_path)
        self.logger.info(f"截图已保存: {screenshot_path}")
        
        # 附加到Allure报告
        allure.attach.file(screenshot_path, name=f"截图_{name}",
                          attachment_type=allure.attachment_type.PNG)
        
        return screenshot_path