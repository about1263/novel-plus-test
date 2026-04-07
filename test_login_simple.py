#!/usr/bin/env python3
"""
极简登录页面元素定位测试脚本（自动驱动管理）
用于验证登录相关元素定位是否正确，自动下载和配置ChromeDriver
"""
import time
import sys
import subprocess

# 尝试导入必要的库
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    print("[OK] Selenium 已安装")
except ImportError as e:
    print(f"[ERROR] 缺少Selenium库: {e}")
    print("请运行: pip install selenium")
    sys.exit(1)

# 尝试导入webdriver-manager，如果失败则尝试安装
try:
    from webdriver_manager.chrome import ChromeDriverManager
    print("[OK] webdriver-manager 已安装")
except ImportError:
    print("[WARN]  未安装webdriver-manager，正在尝试安装...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"])
        from webdriver_manager.chrome import ChromeDriverManager
        print("[OK] webdriver-manager 安装成功")
    except Exception as e:
        print(f"[ERROR] 安装webdriver-manager失败: {e}")
        print("请手动运行: pip install webdriver-manager")
        sys.exit(1)


def get_local_chromedriver_path():
    """获取本地chromedriver路径"""
    import os
    # 检查web_driver目录下的chromedriver.exe
    local_path = os.path.join(os.path.dirname(__file__), "web_driver", "chromedriver.exe")
    if os.path.exists(local_path):
        print(f"[OK] 找到本地ChromeDriver: {local_path}")
        return local_path
    else:
        print(f"[WARN]  未找到本地ChromeDriver: {local_path}")
        return None


def test_login_elements():
    """测试登录页面元素定位"""
    print("=" * 60)
    print("开始测试登录页面元素定位...")
    print("=" * 60)
    
    # 配置选项
    HEADLESS = False  # 是否使用无头模式（不显示浏览器界面）
    WAIT_FOR_USER = False  # 测试完成后是否等待用户按Enter键
    USE_LOCAL_DRIVER = False  # 是否使用本地web_driver目录下的chromedriver.exe
    
    driver = None
    try:
        # 自动下载和管理ChromeDriver
        print("1. 自动下载/查找ChromeDriver...")
        chrome_service = None
        if USE_LOCAL_DRIVER:
            local_driver_path = get_local_chromedriver_path()
            if local_driver_path:
                try:
                    chrome_service = Service(local_driver_path)
                    print(f"   使用本地ChromeDriver: {local_driver_path}")
                except Exception as e:
                    print(f"   使用本地ChromeDriver失败: {e}")
                    chrome_service = None
        
        if not chrome_service:
            print("   使用webdriver-manager自动下载ChromeDriver...")
            chrome_service = Service(ChromeDriverManager().install())
        
        # 配置Chrome浏览器选项
        print("2. 配置Chrome浏览器选项...")
        options = Options()
        options.add_argument('--start-maximized')  # 最大化窗口
        options.add_argument('--window-size=1920,1080')  # 设置窗口大小
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-notifications')
        
        # 可选：添加更多选项以防止检测和卡住
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 无头模式
        if HEADLESS:
            options.add_argument('--headless=new')
        
        # 创建浏览器驱动
        print("3. 创建Chrome浏览器驱动...")
        driver = webdriver.Chrome(service=chrome_service, options=options)
        print("   Chrome浏览器已启动")
        
        # 打开网站首页
        print("\n4. 打开网站首页: http://47.108.213.8/")
        driver.get("http://47.108.213.8/")
        time.sleep(2)  # 等待页面加载
        print("   首页已加载")
        
        # 点击右上角登录链接
        print("\n5. 查找并点击登录链接...")
        try:
            login_link = driver.find_element(By.CSS_SELECTOR, 'a[href="/user/login.html"].mr15')
            print(f"   找到登录链接: {login_link.text}")
            login_link.click()
            print("   已点击登录链接")
            time.sleep(2)  # 等待登录页面加载
        except Exception as e:
            print(f"   [ERROR] 未找到登录链接: {e}")
            print("   尝试直接访问登录页面...")
            driver.get("http://47.108.213.8/user/login.html")
            time.sleep(2)
        
        # 定位手机号输入框
        print("\n6. 定位手机号输入框...")
        try:
            phone_input = driver.find_element(By.ID, "txtUName")
            print(f"   [OK] 找到手机号输入框:")
            print(f"      ID: '{phone_input.get_attribute('id')}'")
            print(f"      name: '{phone_input.get_attribute('name')}'")
            print(f"      placeholder: '{phone_input.get_attribute('placeholder')}'")
            print(f"      class: '{phone_input.get_attribute('class')}'")
        except Exception as e:
            print(f"   [ERROR] 未找到手机号输入框: {e}")
        
        # 定位密码输入框
        print("\n7. 定位密码输入框...")
        try:
            password_input = driver.find_element(By.ID, "txtPassword")
            print(f"   [OK] 找到密码输入框:")
            print(f"      ID: '{password_input.get_attribute('id')}'")
            print(f"      name: '{password_input.get_attribute('name')}'")
            print(f"      placeholder: '{password_input.get_attribute('placeholder')}'")
            print(f"      class: '{password_input.get_attribute('class')}'")
        except Exception as e:
            print(f"   [ERROR] 未找到密码输入框: {e}")
        
        # 定位登录按钮
        print("\n8. 定位登录按钮...")
        try:
            login_button = driver.find_element(By.ID, "btnLogin")
            print(f"   [OK] 找到登录按钮:")
            print(f"      ID: '{login_button.get_attribute('id')}'")
            print(f"      name: '{login_button.get_attribute('name')}'")
            print(f"      value: '{login_button.get_attribute('value')}'")
            print(f"      class: '{login_button.get_attribute('class')}'")
        except Exception as e:
            print(f"   [ERROR] 未找到登录按钮: {e}")
        
        # 测试输入和点击（可选）
        print("\n9. 测试输入和点击功能（使用测试数据）...")
        try:
            phone_input.send_keys("18723968509")
            password_input.send_keys("zxcvbnm.")
            print("   已输入测试数据")
            
            # 点击登录按钮
            login_button.click()
            print("   已点击登录按钮")
            time.sleep(3)  # 等待登录结果
            
            # 检查登录结果
            current_url = driver.current_url
            print(f"\n10. 登录后当前URL: {current_url}")
            
            # 检查是否跳转或显示错误信息
            if "login" not in current_url:
                print("   [OK] 可能登录成功，已跳转到其他页面")
            else:
                print("   [WARN]  可能仍在登录页面，检查错误信息...")
                # 尝试查找错误提示
                try:
                    error_elements = driver.find_elements(By.CSS_SELECTOR, ".error, .tip, .msg, .alert, .warning")
                    if error_elements:
                        for i, error in enumerate(error_elements[:3]):  # 显示前3个错误元素
                            if error.text.strip():
                                print(f"   错误提示 {i+1}: {error.text.strip()}")
                    else:
                        print("   未找到错误提示元素")
                except:
                    print("   查找错误提示时出错")
        except Exception as e:
            print(f"   测试输入时出错: {e}")
        
        print("\n" + "=" * 60)
        print("[OK] 元素定位测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            # 等待用户查看结果
            if WAIT_FOR_USER:
                input("\n按Enter键关闭浏览器...")
            else:
                print("\n等待3秒后自动关闭浏览器...")
                time.sleep(3)
            driver.quit()
            print("浏览器已关闭")
        else:
            print("\n浏览器驱动未创建，无需关闭")


if __name__ == "__main__":
    test_login_elements()