"""
小说详情页面对象
封装小说详情页面的元素和操作
"""
import time
from .base_page import BasePage
from selenium.webdriver.common.by import By


class BookDetailPage(BasePage):
    """小说详情页面"""
    
    # 页面URL模板
    URL_TEMPLATE = "/book/{book_id}.html"
    
    # 元素定位器（待补充具体定位数据）
    # 开始阅读按钮
    START_READING_BUTTON = (By.ID, "start-reading-button")
    # 小说标题
    BOOK_TITLE = (By.CLASS_NAME, "book-detail-title")
    # 作者信息
    AUTHOR_INFO = (By.CLASS_NAME, "author-info")
    # 小说分类
    BOOK_CATEGORY = (By.CLASS_NAME, "book-category")
    # 小说简介
    BOOK_DESCRIPTION = (By.CLASS_NAME, "book-description")
    # 章节列表
    CHAPTER_LIST = (By.CLASS_NAME, "chapter-list")
    # 章节项
    CHAPTER_ITEM = (By.CLASS_NAME, "chapter-item")
    # 阅读人数
    READ_COUNT = (By.CLASS_NAME, "read-count")
    # 收藏按钮
    COLLECT_BUTTON = (By.CLASS_NAME, "collect-button")
    # 分享按钮
    SHARE_BUTTON = (By.CLASS_NAME, "share-button")
    
    def __init__(self, driver, base_url=None):
        super().__init__(driver)
        self.base_url = base_url or "http://localhost:8080"
    
    def open_book_detail_page(self, book_id):
        """打开指定小说详情页面"""
        detail_url = f"{self.base_url}{self.URL_TEMPLATE.format(book_id=book_id)}"
        self.open(detail_url)
        return self
    
    def click_start_reading(self):
        """点击开始阅读按钮"""
        self.click(self.START_READING_BUTTON)
        self.logger.info("点击开始阅读按钮")
        return self
    
    def get_book_title(self):
        """获取小说标题"""
        if self.is_element_visible(self.BOOK_TITLE):
            return self.get_text(self.BOOK_TITLE)
        return ""
    
    def get_author_info(self):
        """获取作者信息"""
        if self.is_element_visible(self.AUTHOR_INFO):
            return self.get_text(self.AUTHOR_INFO)
        return ""
    
    def get_book_category(self):
        """获取小说分类"""
        if self.is_element_visible(self.BOOK_CATEGORY):
            return self.get_text(self.BOOK_CATEGORY)
        return ""
    
    def get_book_description(self):
        """获取小说简介"""
        if self.is_element_visible(self.BOOK_DESCRIPTION):
            return self.get_text(self.BOOK_DESCRIPTION)
        return ""
    
    def get_read_count(self):
        """获取阅读人数"""
        if self.is_element_visible(self.READ_COUNT):
            return self.get_text(self.READ_COUNT)
        return "0"
    
    def get_chapter_count(self):
        """获取章节数量"""
        chapter_items = self.find_elements(self.CHAPTER_ITEM)
        return len(chapter_items)
    
    def get_chapter_titles(self):
        """获取所有章节标题"""
        titles = []
        chapter_items = self.find_elements(self.CHAPTER_ITEM)
        for chapter in chapter_items:
            try:
                # 假设章节标题在章节项内部
                title = chapter.text
                titles.append(title)
            except:
                continue
        return titles
    
    def click_chapter(self, chapter_index=0):
        """点击指定章节"""
        chapter_items = self.find_elements(self.CHAPTER_ITEM)
        if chapter_index < len(chapter_items):
            chapter_items[chapter_index].click()
            self.logger.info(f"点击第{chapter_index+1}章节")
            return True
        return False
    
    def click_collect_button(self):
        """点击收藏按钮"""
        if self.is_element_visible(self.COLLECT_BUTTON):
            self.click(self.COLLECT_BUTTON)
            self.logger.info("点击收藏按钮")
            return True
        return False
    
    def click_share_button(self):
        """点击分享按钮"""
        if self.is_element_visible(self.SHARE_BUTTON):
            self.click(self.SHARE_BUTTON)
            self.logger.info("点击分享按钮")
            return True
        return False
    
    def wait_for_page_loaded(self, timeout=10):
        """等待详情页面加载完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 检查关键元素是否加载
            if self.is_element_visible(self.BOOK_TITLE) and self.is_element_visible(self.START_READING_BUTTON):
                return True
            time.sleep(0.5)
        
        self.logger.warning(f"详情页面加载超时: {timeout}秒")
        return False
    
    def scroll_to_start_reading_button(self):
        """滚动到开始阅读按钮"""
        button = self.find_element(self.START_READING_BUTTON)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(0.5)
        return self
    
    def is_book_collected(self):
        """检查小说是否已收藏"""
        if self.is_element_visible(self.COLLECT_BUTTON):
            # 检查按钮文本或类名判断是否已收藏
            button_text = self.get_text(self.COLLECT_BUTTON)
            return "已收藏" in button_text
        return False