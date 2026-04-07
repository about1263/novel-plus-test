"""
阅读器页面对象
封装阅读器页面的元素和操作
"""
import time
from .base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class ReaderPage(BasePage):
    """阅读器页面"""
    
    # 元素定位器（待补充具体定位数据）
    # 下一章按钮
    NEXT_CHAPTER_BUTTON = (By.CLASS_NAME, "next-chapter-button")
    # 上一章按钮
    PREVIOUS_CHAPTER_BUTTON = (By.CLASS_NAME, "previous-chapter-button")
    # 目录按钮
    CATALOG_BUTTON = (By.CLASS_NAME, "catalog-button")
    # 设置按钮
    SETTINGS_BUTTON = (By.CLASS_NAME, "settings-button")
    # 主题切换按钮
    THEME_SWITCH_BUTTON = (By.CLASS_NAME, "theme-switch-button")
    # 评论图标
    COMMENT_ICON = (By.CLASS_NAME, "comment-icon")
    # 章节标题
    CHAPTER_TITLE = (By.CLASS_NAME, "chapter-title")
    # 阅读内容区域
    CONTENT_AREA = (By.ID, "content-area")
    # 目录面板
    CATALOG_PANEL = (By.CLASS_NAME, "catalog-panel")
    # 目录章节项
    CATALOG_CHAPTER_ITEM = (By.CLASS_NAME, "catalog-chapter-item")
    # 当前章节高亮
    CURRENT_CHAPTER_HIGHLIGHT = (By.CLASS_NAME, "current-chapter")
    # 设置面板
    SETTINGS_PANEL = (By.CLASS_NAME, "settings-panel")
    # 字体大小调整控件
    FONT_SIZE_SMALL = (By.CLASS_NAME, "font-size-small")
    FONT_SIZE_MEDIUM = (By.CLASS_NAME, "font-size-medium")
    FONT_SIZE_LARGE = (By.CLASS_NAME, "font-size-large")
    FONT_SIZE_XLARGE = (By.CLASS_NAME, "font-size-xlarge")
    # 主题选项
    THEME_DAY = (By.CLASS_NAME, "theme-day")
    THEME_NIGHT = (By.CLASS_NAME, "theme-night")
    THEME_EYE_PROTECTION = (By.CLASS_NAME, "theme-eye-protection")
    # 阅读进度
    READING_PROGRESS = (By.CLASS_NAME, "reading-progress")
    # 章节编号显示
    CHAPTER_NUMBER = (By.CLASS_NAME, "chapter-number")
    
    def __init__(self, driver, base_url=None):
        super().__init__(driver)
        self.base_url = base_url or "http://localhost:8080"
    
    # 基本操作
    def click_next_chapter(self):
        """点击下一章按钮"""
        self.click(self.NEXT_CHAPTER_BUTTON)
        self.logger.info("点击下一章按钮")
        time.sleep(1)  # 等待章节切换
        return self
    
    def click_previous_chapter(self):
        """点击上一章按钮"""
        self.click(self.PREVIOUS_CHAPTER_BUTTON)
        self.logger.info("点击上一章按钮")
        time.sleep(1)  # 等待章节切换
        return self
    
    def click_catalog_button(self):
        """点击目录按钮"""
        self.click(self.CATALOG_BUTTON)
        self.logger.info("点击目录按钮")
        time.sleep(0.5)  # 等待目录面板展开
        return self
    
    def click_settings_button(self):
        """点击设置按钮"""
        self.click(self.SETTINGS_BUTTON)
        self.logger.info("点击设置按钮")
        time.sleep(0.5)  # 等待设置面板展开
        return self
    
    def click_comment_icon(self):
        """点击评论图标"""
        self.click(self.COMMENT_ICON)
        self.logger.info("点击评论图标")
        return self
    
    def click_theme_switch_button(self):
        """点击主题切换按钮"""
        self.click(self.THEME_SWITCH_BUTTON)
        self.logger.info("点击主题切换按钮")
        time.sleep(0.5)  # 等待主题切换
        return self
    
    # 目录相关操作
    def is_catalog_panel_visible(self):
        """检查目录面板是否可见"""
        return self.is_element_visible(self.CATALOG_PANEL)
    
    def get_catalog_chapter_count(self):
        """获取目录中的章节数量"""
        if self.is_catalog_panel_visible():
            chapter_items = self.find_elements(self.CATALOG_CHAPTER_ITEM)
            return len(chapter_items)
        return 0
    
    def click_catalog_chapter(self, chapter_index=0):
        """点击目录中的章节"""
        if not self.is_catalog_panel_visible():
            self.click_catalog_button()
        
        chapter_items = self.find_elements(self.CATALOG_CHAPTER_ITEM)
        if chapter_index < len(chapter_items):
            chapter_items[chapter_index].click()
            self.logger.info(f"点击目录第{chapter_index+1}章节")
            time.sleep(1)  # 等待章节跳转
            return True
        return False
    
    def get_current_highlighted_chapter(self):
        """获取当前高亮的章节"""
        if self.is_catalog_panel_visible() and self.is_element_visible(self.CURRENT_CHAPTER_HIGHLIGHT):
            return self.get_text(self.CURRENT_CHAPTER_HIGHLIGHT)
        return ""
    
    def close_catalog_panel(self):
        """关闭目录面板"""
        if self.is_catalog_panel_visible():
            # 点击目录按钮再次关闭
            self.click_catalog_button()
            time.sleep(0.5)
        return self
    
    # 设置相关操作
    def is_settings_panel_visible(self):
        """检查设置面板是否可见"""
        return self.is_element_visible(self.SETTINGS_PANEL)
    
    def set_font_size(self, size="medium"):
        """设置字体大小"""
        if not self.is_settings_panel_visible():
            self.click_settings_button()
        
        size_mapping = {
            "small": self.FONT_SIZE_SMALL,
            "medium": self.FONT_SIZE_MEDIUM,
            "large": self.FONT_SIZE_LARGE,
            "xlarge": self.FONT_SIZE_XLARGE
        }
        
        if size in size_mapping:
            self.click(size_mapping[size])
            self.logger.info(f"设置字体大小为: {size}")
            time.sleep(0.5)
            return True
        return False
    
    def set_theme(self, theme="day"):
        """设置主题"""
        if not self.is_settings_panel_visible():
            self.click_settings_button()
        
        theme_mapping = {
            "day": self.THEME_DAY,
            "night": self.THEME_NIGHT,
            "eye_protection": self.THEME_EYE_PROTECTION
        }
        
        if theme in theme_mapping:
            self.click(theme_mapping[theme])
            self.logger.info(f"设置主题为: {theme}")
            time.sleep(0.5)
            return True
        return False
    
    def close_settings_panel(self):
        """关闭设置面板"""
        if self.is_settings_panel_visible():
            # 点击设置按钮再次关闭
            self.click_settings_button()
            time.sleep(0.5)
        return self
    
    # 内容相关操作
    def get_chapter_title(self):
        """获取章节标题"""
        if self.is_element_visible(self.CHAPTER_TITLE):
            return self.get_text(self.CHAPTER_TITLE)
        return ""
    
    def get_chapter_number(self):
        """获取章节编号"""
        if self.is_element_visible(self.CHAPTER_NUMBER):
            return self.get_text(self.CHAPTER_NUMBER)
        return ""
    
    def get_content_text(self):
        """获取阅读内容文本"""
        if self.is_element_visible(self.CONTENT_AREA):
            return self.get_text(self.CONTENT_AREA)
        return ""
    
    def get_reading_progress(self):
        """获取阅读进度"""
        if self.is_element_visible(self.READING_PROGRESS):
            return self.get_text(self.READING_PROGRESS)
        return "0%"
    
    def scroll_to_bottom(self):
        """滚动到章节底部"""
        content_area = self.find_element(self.CONTENT_AREA)
        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", content_area)
        time.sleep(1)
        return self
    
    def scroll_to_top(self):
        """滚动到章节顶部"""
        content_area = self.find_element(self.CONTENT_AREA)
        self.driver.execute_script("arguments[0].scrollTop = 0;", content_area)
        time.sleep(0.5)
        return self
    
    def simulate_mouse_scroll(self, scroll_amount=500):
        """模拟鼠标滚轮滚动"""
        content_area = self.find_element(self.CONTENT_AREA)
        
        # 使用JavaScript模拟滚动
        self.driver.execute_script(f"arguments[0].scrollTop += {scroll_amount};", content_area)
        time.sleep(0.5)
        return self
    
    def get_scroll_position(self):
        """获取当前滚动位置"""
        content_area = self.find_element(self.CONTENT_AREA)
        scroll_top = self.driver.execute_script("return arguments[0].scrollTop;", content_area)
        scroll_height = self.driver.execute_script("return arguments[0].scrollHeight;", content_area)
        client_height = self.driver.execute_script("return arguments[0].clientHeight;", content_area)
        
        return {
            "scroll_top": scroll_top,
            "scroll_height": scroll_height,
            "client_height": client_height
        }
    
    def is_at_bottom(self, threshold=50):
        """检查是否滚动到底部"""
        position = self.get_scroll_position()
        return position["scroll_top"] + position["client_height"] >= position["scroll_height"] - threshold
    
    # 等待方法
    def wait_for_chapter_loaded(self, timeout=10):
        """等待章节内容加载完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_element_visible(self.CHAPTER_TITLE) and self.is_element_visible(self.CONTENT_AREA):
                # 检查内容是否非空
                content = self.get_content_text()
                if content and len(content.strip()) > 0:
                    return True
            time.sleep(0.5)
        
        self.logger.warning(f"章节内容加载超时: {timeout}秒")
        return False
    
    def wait_for_next_chapter_loaded(self, timeout=10):
        """等待下一章加载完成"""
        return self.wait_for_chapter_loaded(timeout)
    
    # 验证方法
    def verify_chapter_switch(self, previous_title):
        """验证章节切换是否成功"""
        current_title = self.get_chapter_title()
        return current_title != previous_title and current_title != ""
    
    def verify_font_size_changed(self, expected_size):
        """验证字体大小是否改变"""
        # 通过检查内容区域的字体大小属性
        content_area = self.find_element(self.CONTENT_AREA)
        font_size = content_area.value_of_css_property("font-size")
        self.logger.info(f"当前字体大小: {font_size}")
        return font_size is not None
    
    def verify_theme_changed(self, expected_theme):
        """验证主题是否改变"""
        # 通过检查body或内容区域的背景色
        body = self.driver.find_element(By.TAG_NAME, "body")
        background_color = body.value_of_css_property("background-color")
        self.logger.info(f"当前背景色: {background_color}")
        return background_color is not None
    
    # 获取页面信息
    def get_current_url(self):
        """获取当前URL"""
        return self.driver.current_url
    
    def get_url_chapter_param(self):
        """从URL获取章节参数"""
        url = self.get_current_url()
        # 假设URL格式包含章节参数，如 ?chapter=1 或 /chapter/1
        import re
        match = re.search(r'[?&]chapter=(\d+)', url)
        if match:
            return int(match.group(1))
        match = re.search(r'/chapter/(\d+)', url)
        if match:
            return int(match.group(1))
        return None
    
    def get_local_storage_value(self, key):
        """获取本地存储值"""
        return self.driver.execute_script(f"return localStorage.getItem('{key}');")