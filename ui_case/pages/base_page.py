"""
页面对象模式基类
提供所有页面对象的通用方法和属性
"""
import logging
import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class BasePage:
    """页面基类"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.logger = logging.getLogger(__name__)
    
    def open(self, url):
        """打开指定URL"""
        self.driver.get(url)
        self.logger.info(f"打开页面: {url}")
        return self
    
    def find_element(self, locator):
        """查找单个元素"""
        try:
            element = self.wait.until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            self.logger.error(f"元素未找到: {locator}")
            raise
    
    def find_elements(self, locator):
        """查找多个元素"""
        try:
            elements = self.wait.until(
                EC.presence_of_all_elements_located(locator)
            )
            return elements
        except TimeoutException:
            self.logger.error(f"元素未找到: {locator}")
            raise
    
    def click(self, locator):
        """点击元素"""
        element = self.find_element(locator)
        element.click()
        self.logger.info(f"点击元素: {locator}")
        return self
    
    def input_text(self, locator, text):
        """输入文本"""
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)
        self.logger.info(f"在元素 {locator} 输入文本: {text}")
        return self
    
    def get_text(self, locator):
        """获取元素文本"""
        element = self.find_element(locator)
        return element.text
    
    def get_attribute(self, locator, attribute):
        """获取元素属性"""
        element = self.find_element(locator)
        return element.get_attribute(attribute)
    
    def is_element_present(self, locator, timeout=5):
        """检查元素是否存在"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def is_element_visible(self, locator, timeout=5):
        """检查元素是否可见"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def wait_for_element_visible(self, locator, timeout=10):
        """等待元素可见"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return element
        except TimeoutException:
            self.logger.error(f"元素不可见: {locator}")
            raise
    
    def wait_for_element_clickable(self, locator, timeout=10):
        """等待元素可点击"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return element
        except TimeoutException:
            self.logger.error(f"元素不可点击: {locator}")
            raise
    
    def take_screenshot(self, filename):
        """截取屏幕截图"""
        # 获取项目根目录（ui_case的父目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # 使用基于项目根目录的截图目录
        screenshot_dir = os.path.join(project_root, 'ui_case', 'reports', 'allure-results')
        os.makedirs(screenshot_dir, exist_ok=True)
        
        screenshot_path = os.path.join(screenshot_dir, f"{filename}.png")
        self.driver.save_screenshot(screenshot_path)
        self.logger.info(f"截图已保存: {screenshot_path}")
        return screenshot_path
    
    def switch_to_frame(self, locator):
        """切换到iframe"""
        frame_element = self.find_element(locator)
        self.driver.switch_to.frame(frame_element)
        return self
    
    def switch_to_default_content(self):
        """切换回主文档"""
        self.driver.switch_to.default_content()
        return self
    
    def execute_script(self, script, *args):
        """执行JavaScript脚本"""
        result = self.driver.execute_script(script, *args)
        return result
    
    def refresh_page(self):
        """刷新页面"""
        self.driver.refresh()
        self.logger.info("刷新页面")
        return self
    
    def get_current_url(self):
        """获取当前URL"""
        return self.driver.current_url
    
    def get_page_title(self):
        """获取页面标题"""
        return self.driver.title
    
    def accept_alert(self):
        """接受弹窗"""
        alert = self.driver.switch_to.alert
        alert.accept()
        return self
    
    def dismiss_alert(self):
        """取消弹窗"""
        alert = self.driver.switch_to.alert
        alert.dismiss()
        return self
    
    def get_alert_text(self):
        """获取弹窗文本"""
        alert = self.driver.switch_to.alert
        return alert.text