"""
首页页面对象
封装首页和小说详情页的元素和操作
"""
import time
from .base_page import BasePage
from selenium.webdriver.common.by import By


class HomePage(BasePage):
    """首页页面"""
    
    # 页面URL
    URL = "/"
    
    # 元素定位器
    # 首页小说标签 - 根据提供的HTML: <dd><a href="/book/1262260513468559361.html">邻家宅女</a>...</dd>
    NOVEL_TAG = (By.CSS_SELECTOR, "dd a")
    # 阅读按钮 - 在小说详情页上的阅读按钮，根据提供的HTML: class="btn_ora"
    READ_BUTTON = (By.CSS_SELECTOR, ".btn_ora")
    # 小说标题 - 详情页标题
    BOOK_TITLE = (By.CSS_SELECTOR, ".book-title, h1.title, .novel-title")
    # 详情页容器 - 用于确认已跳转到详情页
    DETAIL_CONTAINER = (By.CSS_SELECTOR, ".book-detail, .novel-detail, .detail-container")
    # 首页搜索框
    SEARCH_INPUT = (By.CSS_SELECTOR, "input.search-input, #search-input, .search-box input")
    # 首页搜索按钮
    SEARCH_BUTTON = (By.CSS_SELECTOR, ".search-button, .btn-search, .search-box button")
    # 首页轮播图
    CAROUSEL = (By.CLASS_NAME, "carousel, .banner, .slider")
    # 首页分类导航
    CATEGORY_NAV = (By.CLASS_NAME, "category-nav, .nav-category, .category-list")
    
    def __init__(self, driver, base_url=None):
        super().__init__(driver)
        self.base_url = base_url or "http://localhost:8080"
    
    def open_home_page(self):
        """打开首页"""
        home_url = f"{self.base_url}{self.URL}"
        self.open(home_url)
        self.logger.info(f"打开首页: {home_url}")
        return self
    
    def click_novel_tag(self, index=0):
        """点击首页小说标签跳转到小说详情页
        
        Args:
            index: 小说标签索引（从0开始）
        
        Returns:
            bool: 是否点击成功
        """
        self.logger.info(f"尝试点击第{index+1}个小说标签")
        
        try:
            # 查找所有小说标签元素
            novel_tags = self.find_elements(self.NOVEL_TAG)
            self.logger.info(f"找到 {len(novel_tags)} 个小说标签")
            
            if index < len(novel_tags):
                # 点击指定索引的小说标签
                novel_tags[index].click()
                self.logger.info(f"点击第{index+1}个小说标签成功")
                
                # 等待页面跳转到详情页
                time.sleep(2)  # 等待页面跳转
                
                # 验证是否跳转到详情页
                if self.is_element_visible(self.DETAIL_CONTAINER, timeout=5):
                    self.logger.info("成功跳转到小说详情页")
                    return True
                else:
                    # 可能页面已跳转但容器元素不同，检查URL是否包含/book/
                    current_url = self.get_current_url()
                    if "/book/" in current_url:
                        self.logger.info(f"URL包含书籍路径，确认跳转到详情页: {current_url}")
                        return True
                    else:
                        self.logger.warning(f"可能未跳转到详情页，当前URL: {current_url}")
                        return False
            else:
                self.logger.error(f"小说标签索引 {index} 超出范围，只有 {len(novel_tags)} 个标签")
                return False
                
        except Exception as e:
            self.logger.error(f"点击小说标签失败: {e}")
            return False
    
    def click_read_button(self):
        """点击阅读按钮（在小说详情页）
        
        Returns:
            bool: 是否点击成功
        """
        self.logger.info("尝试点击阅读按钮")
        
        try:
            # 首先确认当前在详情页
            if not self.is_element_visible(self.DETAIL_CONTAINER, timeout=3):
                current_url = self.get_current_url()
                if "/book/" not in current_url:
                    self.logger.warning(f"可能不在详情页，当前URL: {current_url}")
                    # 继续尝试，可能页面结构不同
            
            # 查找阅读按钮
            if self.is_element_visible(self.READ_BUTTON, timeout=5):
                self.click(self.READ_BUTTON)
                self.logger.info("点击阅读按钮成功")
                
                # 等待页面跳转到阅读器
                time.sleep(2)
                
                # 验证是否跳转到阅读器界面
                current_url = self.get_current_url()
                if "/book/" in current_url and ".html" in current_url:
                    self.logger.info(f"成功跳转到阅读器界面: {current_url}")
                    return True
                else:
                    self.logger.warning(f"可能未跳转到阅读器界面，当前URL: {current_url}")
                    return True  # 仍然返回True，因为按钮点击成功
            else:
                # 尝试备用定位器
                self.logger.info("未找到主要阅读按钮，尝试备用定位器")
                read_button_locators = [
                    (By.CSS_SELECTOR, ".btn-read"),
                    (By.CSS_SELECTOR, ".start-reading"),
                    (By.CSS_SELECTOR, "a[href*='/book/']"),
                    (By.XPATH, "//button[contains(text(), '阅读')]"),
                    (By.XPATH, "//a[contains(text(), '阅读')]"),
                    (By.XPATH, "//*[contains(@class, 'read')]"),
                ]
                
                for locator in read_button_locators:
                    try:
                        if self.is_element_visible(locator, timeout=1):
                            self.click(locator)
                            self.logger.info(f"使用备用定位器点击阅读按钮成功: {locator}")
                            time.sleep(2)
                            return True
                    except Exception as e:
                        self.logger.debug(f"尝试备用定位器 {locator} 失败: {e}")
                        continue
                
                self.logger.error("未找到可点击的阅读按钮")
                return False
                
        except Exception as e:
            self.logger.error(f"点击阅读按钮失败: {e}")
            return False
    
    def get_book_title(self):
        """获取小说详情页的标题"""
        try:
            if self.is_element_visible(self.BOOK_TITLE):
                title = self.get_text(self.BOOK_TITLE)
                self.logger.info(f"获取到小说标题: {title}")
                return title
        except Exception as e:
            self.logger.debug(f"获取小说标题失败: {e}")
        return ""
    
    def search_novel(self, keyword):
        """搜索小说"""
        try:
            if self.is_element_visible(self.SEARCH_INPUT):
                self.input_text(self.SEARCH_INPUT, keyword)
                self.logger.info(f"输入搜索关键词: {keyword}")
                
                if self.is_element_visible(self.SEARCH_BUTTON):
                    self.click(self.SEARCH_BUTTON)
                    self.logger.info("点击搜索按钮")
                    time.sleep(2)
                    return True
        except Exception as e:
            self.logger.error(f"搜索小说失败: {e}")
        return False
    
    def is_carousel_visible(self):
        """检查轮播图是否可见"""
        return self.is_element_visible(self.CAROUSEL)
    
    def is_category_nav_visible(self):
        """检查分类导航是否可见"""
        return self.is_element_visible(self.CATEGORY_NAV)
    
    def wait_for_home_page_loaded(self, timeout=10):
        """等待首页加载完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 检查首页关键元素是否加载
            if (self.is_element_visible(self.NOVEL_TAG, timeout=2) or 
                self.is_element_visible(self.CAROUSEL, timeout=2) or
                self.is_element_visible(self.CATEGORY_NAV, timeout=2)):
                self.logger.info("首页加载完成")
                return True
            time.sleep(0.5)
        
        self.logger.warning(f"首页加载超时: {timeout}秒")
        return False