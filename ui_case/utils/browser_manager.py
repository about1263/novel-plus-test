"""
浏览器驱动管理类
支持Chrome和Edge浏览器切换
"""
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False


class BrowserManager:
    """浏览器管理类"""
    
    # 浏览器类型常量
    CHROME = "chrome"
    EDGE = "edge"
    
    # 默认浏览器配置
    DEFAULT_BROWSER = CHROME
    DEFAULT_HEADLESS = False
    DEFAULT_WINDOW_SIZE = "1920,1080"
    DEFAULT_IMPLICIT_WAIT = 10
    DEFAULT_PAGE_LOAD_TIMEOUT = 30
    
    def __init__(self, config=None):
        """
        初始化浏览器管理器
        
        Args:
            config: 配置字典，包含以下键：
                - browser_type: 浏览器类型 (chrome/edge)
                - headless: 是否无头模式
                - window_size: 窗口大小，格式 "width,height"
                - implicit_wait: 隐式等待时间（秒）
                - page_load_timeout: 页面加载超时时间（秒）
                - driver_path: 驱动路径（可选，自动检测）
                - download_dir: 下载目录（可选）
                - chrome_version: Chrome版本（可选）
                - edge_version: Edge版本（可选）
        """
        self.config = config or {}
        self.driver = None
        self.logger = logging.getLogger(__name__)
        
        # 设置驱动路径
        config_driver_path = self.config.get('driver_path')
        if config_driver_path and os.path.exists(config_driver_path):
            self.driver_path = config_driver_path
            self.logger.info(f"使用配置文件中指定的驱动路径: {self.driver_path}")
        else:
            if config_driver_path:
                self.logger.warning(f"配置文件中指定的驱动路径不存在: {config_driver_path}，将尝试自动查找")
            self.driver_path = self._get_default_driver_path()
    
    def _get_default_driver_path(self):
        """获取默认驱动路径"""
        # 尝试从项目根目录的web_driver目录查找
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        web_driver_dir = os.path.join(project_root, 'ui_case', 'drivers')
        
        # 如果web_driver目录不存在，则使用系统PATH
        if not os.path.exists(web_driver_dir):
            self.logger.warning(f"驱动目录不存在: {web_driver_dir}，将使用系统PATH")
            return None
        
        browser_type = self.config.get('browser_type', self.DEFAULT_BROWSER)
        
        if browser_type == self.CHROME:
            # 查找Chrome驱动
            chrome_driver = os.path.join(web_driver_dir, 'chromedriver.exe')
            if os.path.exists(chrome_driver):
                return chrome_driver
            else:
                self.logger.warning(f"Chrome驱动未找到: {chrome_driver}，将使用系统PATH")
                return None
        elif browser_type == self.EDGE:
            # 查找Edge驱动
            edge_driver = os.path.join(web_driver_dir, 'msedgedriver.exe')
            if os.path.exists(edge_driver):
                return edge_driver
            else:
                self.logger.warning(f"Edge驱动未找到: {edge_driver}，将使用系统PATH")
                return None
        
        return None
    
    def create_driver(self):
        """创建浏览器驱动实例"""
        # 如果已有驱动实例，先退出
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("已退出之前的浏览器驱动")
            except Exception as e:
                self.logger.warning(f"退出之前的浏览器驱动时出错: {e}")
            finally:
                self.driver = None
        
        browser_type = self.config.get('browser_type', self.DEFAULT_BROWSER)
        headless = self.config.get('headless', self.DEFAULT_HEADLESS)
        window_size = self.config.get('window_size', self.DEFAULT_WINDOW_SIZE)
        implicit_wait = self.config.get('implicit_wait', self.DEFAULT_IMPLICIT_WAIT)
        page_load_timeout = self.config.get('page_load_timeout', self.DEFAULT_PAGE_LOAD_TIMEOUT)
        download_dir = self.config.get('download_dir')
        
        self.logger.info(f"创建{browser_type}浏览器驱动，无头模式: {headless}")
        
        if browser_type == self.CHROME:
            self.driver = self._create_chrome_driver(headless, window_size, download_dir)
        elif browser_type == self.EDGE:
            self.driver = self._create_edge_driver(headless, window_size, download_dir)
        else:
            raise ValueError(f"不支持的浏览器类型: {browser_type}")
        
        # 设置超时时间
        self.driver.implicitly_wait(implicit_wait)
        self.driver.set_page_load_timeout(page_load_timeout)
        
        # 设置窗口大小
        if window_size:
            width, height = map(int, window_size.split(','))
            self.driver.set_window_size(width, height)
        
        return self.driver
    
    def _create_chrome_driver(self, headless=False, window_size=None, download_dir=None):
        """创建Chrome浏览器驱动"""
        options = ChromeOptions()
        
        # 获取Chrome版本配置
        chrome_version = self.config.get('chrome_version', '')
        # 提取主版本号（第一个点前的数字）
        if chrome_version and '.' in chrome_version:
            chrome_major_version = chrome_version.split('.')[0]
        else:
            chrome_major_version = chrome_version
        
        # 无头模式
        if headless:
            options.add_argument('--headless')
        
        # 设置窗口大小
        if window_size:
            options.add_argument(f'--window-size={window_size}')
        
        # 其他常用选项
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument('--start-maximized')
        
        # 设置下载目录
        if download_dir:
            prefs = {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            options.add_experimental_option("prefs", prefs)
        
        # 创建服务
        self.logger.info(f"driver_path: {self.driver_path}, WEBDRIVER_MANAGER_AVAILABLE: {WEBDRIVER_MANAGER_AVAILABLE}")
        if self.driver_path:
            self.logger.info(f"使用指定的ChromeDriver路径: {self.driver_path}")
            service = ChromeService(executable_path=self.driver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            if WEBDRIVER_MANAGER_AVAILABLE:
                self.logger.info("使用webdriver-manager自动下载匹配的ChromeDriver")
                if chrome_major_version:
                    self.logger.info(f"使用Chrome主版本号: {chrome_major_version}")
                    driver_path = ChromeDriverManager(driver_version=chrome_major_version).install()
                else:
                    driver_path = ChromeDriverManager().install()
                self.logger.info(f"webdriver-manager下载的驱动路径: {driver_path}")
                service = ChromeService(executable_path=driver_path)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                self.logger.info("WEBDRIVER_MANAGER不可用，使用系统PATH中的ChromeDriver")
                driver = webdriver.Chrome(options=options)
        
        return driver
    
    def _create_edge_driver(self, headless=False, window_size=None, download_dir=None):
        """创建Edge浏览器驱动"""
        options = EdgeOptions()
        
        # 无头模式
        if headless:
            options.add_argument('--headless')
        
        # 设置窗口大小
        if window_size:
            options.add_argument(f'--window-size={window_size}')
        
        # 其他常用选项
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument('--start-maximized')
        
        # 设置下载目录
        if download_dir:
            prefs = {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            options.add_experimental_option("prefs", prefs)
        
        # 创建服务
        if self.driver_path:
            service = EdgeService(executable_path=self.driver_path)
            driver = webdriver.Edge(service=service, options=options)
        else:
            driver = webdriver.Edge(options=options)
        
        return driver
    
    def quit_driver(self):
        """退出浏览器驱动"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("浏览器驱动已退出")
            except Exception as e:
                self.logger.warning(f"退出浏览器驱动时出错（可能已退出）: {e}")
            finally:
                self.driver = None
    
    def get_driver(self):
        """获取当前驱动实例"""
        return self.driver
    
    def take_screenshot(self, filename):
        """截取屏幕截图"""
        if not self.driver:
            raise RuntimeError("浏览器驱动未初始化")
        
        # 获取项目根目录（ui_case的父目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # 使用基于项目根目录的截图目录
        screenshot_dir = os.path.join(project_root, 'ui_case', 'screenshots')
        os.makedirs(screenshot_dir, exist_ok=True)
        
        screenshot_path = os.path.join(screenshot_dir, f"{filename}.png")
        self.driver.save_screenshot(screenshot_path)
        self.logger.info(f"截图已保存: {screenshot_path}")
        return screenshot_path
    
    def execute_script(self, script, *args):
        """执行JavaScript脚本"""
        if not self.driver:
            raise RuntimeError("浏览器驱动未初始化")
        
        return self.driver.execute_script(script, *args)
    
    def switch_to_new_window(self):
        """切换到新窗口"""
        if not self.driver:
            raise RuntimeError("浏览器驱动未初始化")
        
        # 获取所有窗口句柄
        window_handles = self.driver.window_handles
        if len(window_handles) > 1:
            # 切换到最新打开的窗口
            self.driver.switch_to.window(window_handles[-1])
            return True
        return False
    
    def switch_to_window_by_index(self, index):
        """通过索引切换窗口"""
        if not self.driver:
            raise RuntimeError("浏览器驱动未初始化")
        
        window_handles = self.driver.window_handles
        if 0 <= index < len(window_handles):
            self.driver.switch_to.window(window_handles[index])
            return True
        return False
    
    def close_current_window(self):
        """关闭当前窗口并切换回主窗口"""
        if not self.driver:
            raise RuntimeError("浏览器驱动未初始化")
        
        window_handles = self.driver.window_handles
        if len(window_handles) > 1:
            self.driver.close()
            self.driver.switch_to.window(window_handles[0])
            return True
        return False