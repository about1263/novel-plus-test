"""
登录功能UI测试用例
基于UI自动化测试用例.txt中的测试场景
"""
import pytest
import allure
import time

from ui_case.test_cases.base_test import BaseUITest


@allure.epic("Novel-Plus UI自动化测试")
@allure.feature("用户登录功能")
class TestLogin(BaseUITest):
    """登录功能测试类"""
    
    @allure.story("正常登录流程验证")
    @allure.title("YHDL_UI_01 - 正常登录流程验证")
    @allure.description("验证使用有效手机号和密码可以成功登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.login
    @pytest.mark.smoke
    def test_normal_login(self, login_page, test_data):
        """正常登录流程验证"""
        with allure.step("1. 打开登录页面"):
            login_page.open_login_page()
            allure.attach(self.driver.get_screenshot_as_png(), 
                         name="登录页面", 
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("2. 输入有效手机号和密码"):
            valid_user = test_data['valid_user']
            login_page.input_phone(valid_user['phone'])
            login_page.input_password(valid_user['password'])
        
        with allure.step("3. 点击登录按钮"):
            login_page.click_login()
            time.sleep(2)  # 等待页面跳转
            allure.attach(self.driver.get_screenshot_as_png(), 
                         name="点击登录后", 
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("4. 验证登录成功"):
            # 验证页面跳转
            current_url = self.get_current_url()
            self.assert_true("index" in current_url or "home" in current_url,
                           "登录后页面未跳转到首页")
            
            # 验证用户昵称显示
            user_nickname = login_page.get_user_nickname()
            self.assert_is_not_none(user_nickname, "用户昵称未显示")
            
            # 验证本地存储包含token（通过JavaScript）
            token = self.driver.execute_script("return localStorage.getItem('token');")
            self.assert_is_not_none(token, "本地存储中未找到token")
            
            allure.attach(self.driver.get_screenshot_as_png(), 
                         name="登录成功页面", 
                         attachment_type=allure.attachment_type.PNG)
    
    @allure.story("错误密码提示验证")
    @allure.title("YHDL_UI_02 - 错误密码提示验证")
    @allure.description("验证输入错误密码时显示正确的错误提示")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.login
    def test_wrong_password_login(self, login_page, test_data):
        """错误密码提示验证"""
        with allure.step("1. 打开登录页面"):
            login_page.open_login_page()
        
        with allure.step("2. 输入正确手机号和错误密码"):
            valid_user = test_data['valid_user']
            login_page.input_phone(valid_user['phone'])
            login_page.input_password("wrongpassword123")
        
        with allure.step("3. 点击登录按钮"):
            login_page.click_login()
            time.sleep(1)  # 等待错误提示显示
        
        with allure.step("4. 验证错误提示"):
            # 验证页面无跳转
            current_url = self.get_current_url()
            self.assert_true("login" in current_url, "输入错误密码后页面不应跳转")
            
            # 验证显示错误提示
            error_message = login_page.get_error_message()
            self.assert_in("账号或密码错误", error_message, 
                          f"错误提示不正确，实际提示: {error_message}")
            
            allure.attach(self.driver.get_screenshot_as_png(), 
                         name="错误密码提示", 
                         attachment_type=allure.attachment_type.PNG)
    
    @allure.story("手机号前端校验")
    @allure.title("YHDL_UI_03 - 手机号前端校验")
    @allure.description("验证输入非11位手机号时显示格式错误提示")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.login
    def test_invalid_phone_login(self, login_page, test_data):
        """手机号前端校验"""
        with allure.step("1. 打开登录页面"):
            login_page.open_login_page()
        
        with allure.step("2. 输入非11位手机号"):
            login_page.input_phone("1380013800")  # 10位手机号
            login_page.input_password("123456")
        
        with allure.step("3. 点击登录按钮"):
            login_page.click_login()
            time.sleep(1)  # 等待校验提示显示
        
        with allure.step("4. 验证手机号格式错误提示"):
            # 验证前端拦截请求（页面无跳转）
            current_url = self.get_current_url()
            self.assert_true("login" in current_url, "输入错误手机号格式后页面不应跳转")
            
            # 验证显示格式错误提示
            format_error = login_page.get_phone_format_error()
            self.assert_in("手机号格式不正确", format_error,
                          f"手机号格式错误提示不正确，实际提示: {format_error}")
            
            allure.attach(self.driver.get_screenshot_as_png(), 
                         name="手机号格式错误提示", 
                         attachment_type=allure.attachment_type.PNG)
    
    @allure.story("空值前端校验")
    @allure.title("YHDL_UI_04 - 空值前端校验")
    @allure.description("验证手机号或密码为空时显示不能为空的提示")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.login
    @pytest.mark.parametrize("phone,password,field", [
        ("", "123456", "手机号"),
        ("13800138000", "", "密码"),
        ("", "", "手机号和密码")
    ])
    def test_empty_validation_login(self, login_page, phone, password, field):
        """空值前端校验"""
        with allure.step("1. 打开登录页面"):
            login_page.open_login_page()
        
        with allure.step(f"2. 输入空值（{field}为空）"):
            if phone:
                login_page.input_phone(phone)
            if password:
                login_page.input_password(password)
        
        with allure.step("3. 点击登录按钮"):
            login_page.click_login()
            time.sleep(1)  # 等待校验提示显示
        
        with allure.step("4. 验证空值校验提示"):
            # 验证前端拦截请求（页面无跳转）
            current_url = self.get_current_url()
            self.assert_true("login" in current_url, f"输入空{field}后页面不应跳转")
            
            # 验证显示空值错误提示
            validation_error = login_page.get_empty_validation_error()
            self.assert_in("不能为空", validation_error,
                          f"空值校验提示不正确，实际提示: {validation_error}")
            
            allure.attach(self.driver.get_screenshot_as_png(), 
                         name=f"空{field}校验提示", 
                         attachment_type=allure.attachment_type.PNG)
    
    @allure.story("登录功能边界测试")
    @allure.title("额外测试 - 超长手机号输入")
    @allure.description("验证输入超长手机号时的处理")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.ui
    @pytest.mark.login
    def test_long_phone_input(self, login_page):
        """超长手机号输入测试"""
        with allure.step("1. 打开登录页面"):
            login_page.open_login_page()
        
        with allure.step("2. 输入超长手机号"):
            long_phone = "1380013800013800138000"  # 超过11位
            login_page.input_phone(long_phone)
            login_page.input_password("123456")
        
        with allure.step("3. 点击登录按钮"):
            login_page.click_login()
            time.sleep(1)
        
        with allure.step("4. 验证处理结果"):
            # 检查是否有错误提示或输入被截断
            current_phone = login_page.get_attribute(login_page.PHONE_INPUT, "value")
            self.assert_less_equal(len(current_phone), 11, 
                                  "手机号输入框应限制最大长度")
            
            allure.attach(self.driver.get_screenshot_as_png(), 
                         name="超长手机号输入", 
                         attachment_type=allure.attachment_type.PNG)
    
    @allure.story("登录功能边界测试")
    @allure.title("额外测试 - 特殊字符密码输入")
    @allure.description("验证输入包含特殊字符的密码")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.ui
    @pytest.mark.login
    def test_special_characters_password(self, login_page, test_data):
        """特殊字符密码输入测试"""
        with allure.step("1. 打开登录页面"):
            login_page.open_login_page()
        
        with allure.step("2. 输入特殊字符密码"):
            valid_user = test_data['valid_user']
            login_page.input_phone(valid_user['phone'])
            login_page.input_password("!@#$%^&*()_+")
        
        with allure.step("3. 点击登录按钮"):
            login_page.click_login()
            time.sleep(2)
        
        with allure.step("4. 验证登录结果"):
            # 检查是否登录成功或显示错误提示
            error_message = login_page.get_error_message()
            if error_message:
                self.logger.info(f"特殊字符密码登录失败，错误提示: {error_message}")
            else:
                # 验证登录成功
                current_url = self.get_current_url()
                self.assert_true("index" in current_url or "home" in current_url,
                               "使用特殊字符密码登录后页面应跳转")
            
            allure.attach(self.driver.get_screenshot_as_png(), 
                         name="特殊字符密码输入", 
                         attachment_type=allure.attachment_type.PNG)


if __name__ == "__main__":
    # 直接运行测试（用于调试）
    pytest.main([__file__, "-v", "--alluredir=ui_case/reports/allure-results"])