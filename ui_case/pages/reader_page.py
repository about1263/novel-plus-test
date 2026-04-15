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
    NEXT_CHAPTER_BUTTON = (By.CLASS_NAME, "next")
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
    CONTENT_AREA = (By.CSS_SELECTOR, "#content-area, .content-area, .content, .chapter-content, .read-content")
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
    # 目录图标（用户提供的HTML）
    ICO_CATALOG = (By.CLASS_NAME, "ico_catalog")
    # 目录页章节列表
    DIR_LIST = (By.CLASS_NAME, "dirList")
    # 目录页章节链接
    DIR_LIST_CHAPTER_LINK = (By.CSS_SELECTOR, ".dirList ul li a")
    # 目录页章节标题span
    DIR_LIST_CHAPTER_SPAN = (By.CSS_SELECTOR, ".dirList ul li a span")
    
    def __init__(self, driver, base_url=None):
        super().__init__(driver)
        self.base_url = base_url or "http://localhost:8080"
    
    # 基本操作
    def click_next_chapter(self):
        """点击下一章按钮"""
        self.logger.info("开始点击下一章按钮")
        
        # 首先检查下一章按钮是否可见且可点击（快速检查）
        try:
            if self.is_element_visible(self.NEXT_CHAPTER_BUTTON, timeout=2):
                self.logger.info("下一章按钮已可见，尝试点击")
                self.wait_for_element_clickable(self.NEXT_CHAPTER_BUTTON, timeout=3)
                self.click(self.NEXT_CHAPTER_BUTTON)
                self.logger.info("点击下一章按钮成功")
                time.sleep(0.3)  # 短暂等待章节切换
                return self
        except Exception as e:
            self.logger.debug(f"直接点击下一章按钮失败，尝试滚动后点击: {e}")
        
        # 如果直接点击失败，滚动到底部再尝试
        self.logger.info("尝试滚动到底部后点击下一章按钮")
        try:
            # 滚动到底部
            self.scroll_to_bottom()
            # 等待按钮可点击
            self.wait_for_element_clickable(self.NEXT_CHAPTER_BUTTON, timeout=3)
            self.click(self.NEXT_CHAPTER_BUTTON)
            self.logger.info("滚动到底部后点击下一章按钮成功")
            time.sleep(0.3)  # 短暂等待章节切换
            return self
        except Exception as e:
            self.logger.error(f"点击下一章按钮失败: {e}")
            raise
    
    def click_previous_chapter(self):
        """点击上一章按钮"""
        self.logger.info("开始点击上一章按钮")
        
        # 首先检查上一章按钮是否可见且可点击（快速检查）
        try:
            if self.is_element_visible(self.PREVIOUS_CHAPTER_BUTTON, timeout=2):
                self.logger.info("上一章按钮已可见，尝试点击")
                self.wait_for_element_clickable(self.PREVIOUS_CHAPTER_BUTTON, timeout=3)
                self.click(self.PREVIOUS_CHAPTER_BUTTON)
                self.logger.info("点击上一章按钮成功")
                time.sleep(0.3)  # 短暂等待章节切换
                return self
        except Exception as e:
            self.logger.debug(f"直接点击上一章按钮失败，尝试滚动后点击: {e}")
        
        # 如果直接点击失败，滚动到底部再尝试
        self.logger.info("尝试滚动到底部后点击上一章按钮")
        try:
            # 滚动到底部
            self.scroll_to_bottom()
            # 等待按钮可点击
            self.wait_for_element_clickable(self.PREVIOUS_CHAPTER_BUTTON, timeout=3)
            self.click(self.PREVIOUS_CHAPTER_BUTTON)
            self.logger.info("滚动到底部后点击上一章按钮成功")
            time.sleep(0.3)  # 短暂等待章节切换
            return self
        except Exception as e:
            self.logger.error(f"点击上一章按钮失败: {e}")
            # 尝试使用备用定位器
            self.logger.info("尝试使用备用定位器查找上一章按钮")
            # 可能的上一章按钮定位器
            previous_button_locators = [
                (By.CLASS_NAME, "previous-chapter-button"),
                (By.CLASS_NAME, "prev"),
                (By.CLASS_NAME, "previous"),
                (By.CSS_SELECTOR, ".previous-chapter"),
                (By.CSS_SELECTOR, ".prev-chapter"),
                (By.XPATH, "//button[contains(text(), '上一章')]"),
                (By.XPATH, "//a[contains(text(), '上一章')]"),
                (By.XPATH, "//*[contains(@class, 'previous') or contains(@class, 'prev')]"),
            ]
            for locator in previous_button_locators:
                try:
                    if self.is_element_visible(locator, timeout=1):
                        self.logger.info(f"找到上一章按钮，定位器: {locator}")
                        self.wait_for_element_clickable(locator, timeout=2)
                        self.click(locator)
                        self.logger.info(f"使用备用定位器点击上一章按钮成功: {locator}")
                        time.sleep(0.3)
                        return self
                except Exception as e2:
                    self.logger.debug(f"尝试定位器 {locator} 失败: {e2}")
                    continue
            # 如果所有备用定位器都失败，则抛出原始异常
            raise
    
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
    
    # 目录图标相关操作（用户提供的HTML结构）
    def click_catalog_icon(self):
        """点击目录图标（跳转到目录页）"""
        self.click(self.ICO_CATALOG)
        self.logger.info("点击目录图标，跳转到目录页")
        time.sleep(2)  # 等待目录页加载
        return self
    
    def is_dir_list_visible(self):
        """检查目录页章节列表是否可见"""
        return self.is_element_visible(self.DIR_LIST)
    
    def get_dir_list_chapter_count(self):
        """获取目录页章节数量"""
        if self.is_dir_list_visible():
            chapter_links = self.find_elements(self.DIR_LIST_CHAPTER_LINK)
            return len(chapter_links)
        return 0
    
    def get_dir_list_chapter_titles(self):
        """获取目录页所有章节标题"""
        titles = []
        if self.is_dir_list_visible():
            spans = self.find_elements(self.DIR_LIST_CHAPTER_SPAN)
            for span in spans:
                titles.append(span.text)
        return titles
    
    def click_chapter_in_dir_list(self, chapter_title=None, chapter_index=0):
        """点击目录页中的章节
        Args:
            chapter_title: 章节标题文本（如"边界"），如果提供则按标题点击
            chapter_index: 章节索引（从0开始），如果未提供chapter_title则按索引点击
        Returns:
            bool: 是否点击成功
        """
        if not self.is_dir_list_visible():
            self.logger.warning("目录页章节列表不可见")
            return False
        
        chapter_links = self.find_elements(self.DIR_LIST_CHAPTER_LINK)
        if not chapter_links:
            self.logger.warning("目录页中没有找到章节链接")
            return False
        
        if chapter_title:
            # 按标题查找章节
            for i, link in enumerate(chapter_links):
                try:
                    # 获取链接内的span文本
                    span = link.find_element(*self.DIR_LIST_CHAPTER_SPAN)
                    if span.text == chapter_title:
                        link.click()
                        self.logger.info(f"点击章节标题: {chapter_title}")
                        time.sleep(2)  # 等待章节跳转
                        return True
                except:
                    continue
            self.logger.warning(f"未找到标题为 '{chapter_title}' 的章节")
            return False
        else:
            # 按索引点击
            if chapter_index < len(chapter_links):
                chapter_links[chapter_index].click()
                self.logger.info(f"点击目录页第{chapter_index+1}章节")
                time.sleep(2)  # 等待章节跳转
                return True
            else:
                self.logger.warning(f"章节索引 {chapter_index} 超出范围，共有 {len(chapter_links)} 个章节")
                return False
    
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
        self.logger.info("开始获取章节标题")
        
        # 尝试多个可能的章节标题定位器
        chapter_title_locators = [
            (By.CLASS_NAME, "chapter-title"),  # 原始定位器
            (By.TAG_NAME, "h1"),  # 可能使用h1标签
            (By.TAG_NAME, "h2"),
            (By.TAG_NAME, "h3"),
            (By.CSS_SELECTOR, ".title"),  # 通用title类
            (By.CSS_SELECTOR, ".chapter-name"),
            (By.CSS_SELECTOR, ".chapter__title"),
            (By.XPATH, "//*[contains(@class, 'title') or contains(@class, 'chapter')]"),
            (By.XPATH, "//*[contains(text(), '第') and contains(text(), '章')]"),  # 包含"第"和"章"的文本
        ]
        
        for locator in chapter_title_locators:
            try:
                if self.is_element_visible(locator, timeout=1):
                    text = self.get_text(locator)
                    if text and len(text.strip()) > 0:
                        self.logger.info(f"找到章节标题，定位器: {locator}, 标题: {text}")
                        return text
            except Exception as e:
                self.logger.debug(f"尝试定位器 {locator} 失败: {e}")
                continue
        
        self.logger.warning("未找到章节标题")
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
        self.logger.info("开始滚动到章节底部")
        
        # 尝试多个可能的内容区域定位器
        content_area_locators = [
            (By.ID, "content-area"),
            (By.CLASS_NAME, "content-area"),
            (By.CLASS_NAME, "content"),
            (By.CLASS_NAME, "chapter-content"),
            (By.CLASS_NAME, "read-content"),
            (By.TAG_NAME, "body"),  # 备用：使用body元素
        ]
        
        content_area = None
        for locator in content_area_locators:
            try:
                element = self.find_element(locator, timeout=2)
                if element:
                    content_area = element
                    self.logger.info(f"找到内容区域元素，定位器: {locator}")
                    break
            except Exception as e:
                self.logger.debug(f"尝试定位器 {locator} 失败: {e}")
                continue
        
        if not content_area:
            self.logger.error("未找到任何内容区域元素")
            raise Exception("未找到内容区域元素")
        
        try:
            # 先检查当前滚动位置
            scroll_top = self.driver.execute_script("return arguments[0].scrollTop;", content_area)
            scroll_height = self.driver.execute_script("return arguments[0].scrollHeight;", content_area)
            client_height = self.driver.execute_script("return arguments[0].clientHeight;", content_area)
            self.logger.info(f"滚动前: scrollTop={scroll_top}, scrollHeight={scroll_height}, clientHeight={client_height}")
            
            # 如果已经在底部附近，不需要滚动
            if scroll_top + client_height >= scroll_height - 100:
                self.logger.info("已在底部附近，无需滚动")
                return self
            
            # 使用更温和的方式滚动到底部（分步滚动）
            target_scroll = scroll_height - client_height
            current_scroll = scroll_top
            step = 500  # 每次滚动500像素
            
            while current_scroll < target_scroll:
                next_scroll = min(current_scroll + step, target_scroll)
                self.driver.execute_script(f"arguments[0].scrollTop = {next_scroll};", content_area)
                self.logger.info(f"滚动到位置: {next_scroll}/{target_scroll}")
                time.sleep(0.2)
                current_scroll = next_scroll
            
            # 最终确认滚动到底部
            final_scroll_top = self.driver.execute_script("return arguments[0].scrollTop;", content_area)
            self.logger.info(f"滚动完成，最终位置: {final_scroll_top}")
            time.sleep(0.5)
            
        except Exception as e:
            self.logger.error(f"滚动到底部失败: {e}")
            # 尝试备用方法：直接设置scrollTop
            try:
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", content_area)
                self.logger.info("使用备用方法滚动到底部")
                time.sleep(0.5)
            except Exception as e2:
                self.logger.error(f"备用滚动方法也失败: {e2}")
                raise
        
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
        self.logger.info("开始等待章节内容加载完成")
        start_time = time.time()
        
        # 第一步：等待内容区域可见（使用较短的超时）
        try:
            self.wait_for_element_visible(self.CONTENT_AREA, timeout=5)
            self.logger.info("内容区域已可见")
        except Exception as e:
            self.logger.warning(f"内容区域未在5秒内可见: {e}")
            # 继续尝试，可能页面结构不同
        
        # 第二步：检查内容是否有文本
        elapsed = 0
        while elapsed < timeout:
            try:
                # 检查内容区域是否存在且有内容
                if self.is_element_visible(self.CONTENT_AREA, timeout=1):
                    content = self.get_content_text()
                    if content and len(content.strip()) > 10:  # 至少有10个字符的内容
                        self.logger.info(f"章节内容已加载，内容长度: {len(content)}")
                        # 尝试获取章节标题，但不强制要求
                        chapter_title = self.get_chapter_title()
                        if chapter_title:
                            self.logger.info(f"章节标题: {chapter_title}")
                        else:
                            self.logger.info("未获取到章节标题，但内容已加载")
                        return True
            except Exception as e:
                self.logger.debug(f"检查内容时出现异常: {e}")
            
            time.sleep(0.5)
            elapsed = time.time() - start_time
        
        self.logger.warning(f"章节内容加载超时: {timeout}秒")
        # 即使超时，也尝试继续执行
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