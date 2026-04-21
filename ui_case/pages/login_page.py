"""
登录页面对象
封装登录页面的元素和操作
"""
import time
from .base_page import BasePage
from selenium.webdriver.common.by import By


class LoginPage(BasePage):
    """登录页面"""
    
    # 页面URL
    URL = "/user/login.html"
    
    # 元素定位器（待补充具体定位数据）
    # 手机号输入框
    PHONE_INPUT = (By.ID, "txtUName")
    # 密码输入框  
    PASSWORD_INPUT = (By.ID, "txtPassword")
    # 登录按钮
    LOGIN_BUTTON = (By.ID, "btnLogin")
    # 错误提示信息
    ERROR_MESSAGE = (By.ID, "LabErr")
    # 手机号格式错误提示
    PHONE_FORMAT_ERROR = (By.ID, "phone_format_error")
    # 空值校验提示
    EMPTY_VALIDATION_ERROR = (By.ID, "empty_validation_error")
    # 用户昵称显示区域（登录成功后）
    USER_NICKNAME = (By.ID, "user_nickname")
    
    def __init__(self, driver, base_url=None):
        super().__init__(driver)
        self.base_url = base_url or "http://localhost:8080"
    
    def open_login_page(self):
        """打开登录页面"""
        login_url = f"{self.base_url}{self.URL}"
        self.open(login_url)
        return self
    
    def input_phone(self, phone):
        """输入手机号"""
        self.input_text(self.PHONE_INPUT, phone)
        return self
    
    def input_password(self, password):
        """输入密码"""
        self.input_text(self.PASSWORD_INPUT, password)
        return self
    
    def click_login(self):
        """点击登录按钮"""
        self.click(self.LOGIN_BUTTON)
        return self
    
    def login(self, phone, password):
        """执行登录操作"""
        self.input_phone(phone)
        self.input_password(password)
        self.click_login()
        return self
    
    def get_error_message(self):
        """获取错误提示信息"""
        try:
            element = self.wait_for_element_visible(self.ERROR_MESSAGE, timeout=3)
            return element.text.strip()
        except Exception:
            return ""
    
    def get_phone_format_error(self):
        """获取手机号格式错误提示"""
        if self.is_element_visible(self.PHONE_FORMAT_ERROR):
            return self.get_text(self.PHONE_FORMAT_ERROR)
        return ""
    
    def get_empty_validation_error(self):
        """获取空值校验错误提示"""
        if self.is_element_visible(self.EMPTY_VALIDATION_ERROR):
            return self.get_text(self.EMPTY_VALIDATION_ERROR)
        return ""
    
    def get_user_nickname(self):
        """获取用户昵称（登录成功后）"""
        if self.is_element_visible(self.USER_NICKNAME):
            return self.get_text(self.USER_NICKNAME)
        return ""
    
    def is_login_successful(self):
        """检查是否登录成功"""
        # 检查是否跳转到首页或显示用户昵称
        time.sleep(1)  # 等待页面跳转
        current_url = self.get_current_url()
        if "index" in current_url or "home" in current_url:
            return True
        if self.is_element_visible(self.USER_NICKNAME):
            return True
        return False
    
    def clear_login_form(self):
        """清空登录表单"""
        self.find_element(self.PHONE_INPUT).clear()
        self.find_element(self.PASSWORD_INPUT).clear()
        return self