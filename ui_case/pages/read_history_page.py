"""
最近阅读页面对象
封装最近阅读页面的元素和操作
"""
import time
from .base_page import BasePage
from selenium.webdriver.common.by import By


class ReadHistoryPage(BasePage):
    """最近阅读页面"""
    
    # 页面URL
    URL = "/user/read_history.html"
    
    # 元素定位器
    # 最近阅读列表项 - 根据用户提供的HTML: <tr class="book_list" vals="291">
    BOOK_LIST_ITEM = (By.CSS_SELECTOR, "tr.book_list")
    # 小说标题链接 - <a href="/book/1262260513468559361.html">邻家宅女</a>
    BOOK_TITLE_LINK = (By.CSS_SELECTOR, "tr.book_list td.name a")
    # 章节链接 - <a href="/book/1262260513468559361/2026913037218246656.html">风暴</a>
    CHAPTER_LINK = (By.CSS_SELECTOR, "tr.book_list td.chapter a")
    # 继续阅读链接 - <a href="/book/1262260513468559361/2026912779285327872.html">继续阅读</a>
    CONTINUE_READING_LINK = (By.CSS_SELECTOR, "tr.book_list td.goread a")
    # 阅读时间 - <td class="time">02/26 14:51</td>
    READING_TIME = (By.CSS_SELECTOR, "tr.book_list td.time")
    # 小说分类 - <a href="/book/bookclass.html?c=3">[都市言情]</a>
    BOOK_CATEGORY = (By.CSS_SELECTOR, "tr.book_list td.bookclass a")
    # 空状态提示
    EMPTY_HISTORY = (By.CSS_SELECTOR, ".empty-history, .no-data")
    
    def __init__(self, driver, base_url=None):
        super().__init__(driver)
        self.base_url = base_url or "http://localhost:8080"
    
    def open_read_history_page(self):
        """打开最近阅读页面"""
        history_url = f"{self.base_url}{self.URL}"
        self.open(history_url)
        self.logger.info(f"打开最近阅读页面: {history_url}")
        return self
    
    def get_book_count(self):
        """获取最近阅读列表中的小说数量"""
        book_items = self.find_elements(self.BOOK_LIST_ITEM)
        return len(book_items)
    
    def get_book_titles(self):
        """获取所有小说标题"""
        titles = []
        title_links = self.find_elements(self.BOOK_TITLE_LINK)
        for link in title_links:
            titles.append(link.text)
        return titles
    
    def get_chapter_titles(self):
        """获取所有章节标题"""
        titles = []
        chapter_links = self.find_elements(self.CHAPTER_LINK)
        for link in chapter_links:
            titles.append(link.text)
        return titles
    
    def get_reading_times(self):
        """获取所有阅读时间"""
        times = []
        time_elements = self.find_elements(self.READING_TIME)
        for element in time_elements:
            times.append(element.text)
        return times
    
    def get_book_categories(self):
        """获取所有小说分类"""
        categories = []
        category_links = self.find_elements(self.BOOK_CATEGORY)
        for link in category_links:
            categories.append(link.text)
        return categories
    
    def click_continue_reading(self, book_index=0):
        """点击继续阅读链接
        Args:
            book_index: 小说索引（从0开始）
        Returns:
            bool: 是否点击成功
        """
        self.logger.info(f"尝试点击第{book_index+1}本小说的继续阅读链接")
        book_items = self.find_elements(self.BOOK_LIST_ITEM)
        if book_index < len(book_items):
            # 在小说项内查找继续阅读链接
            continue_links = book_items[book_index].find_elements(*self.CONTINUE_READING_LINK)
            if continue_links:
                continue_links[0].click()
                self.logger.info(f"点击第{book_index+1}本小说的继续阅读链接成功")
                time.sleep(2)  # 等待跳转到阅读页
                return True
            else:
                self.logger.error(f"第{book_index+1}本小说没有找到继续阅读链接")
                return False
        else:
            self.logger.error(f"最近阅读列表中没有第{book_index+1}本小说")
            return False
    
    def click_book_title(self, book_index=0):
        """点击小说标题（进入小说详情页）"""
        book_items = self.find_elements(self.BOOK_LIST_ITEM)
        if book_index < len(book_items):
            title_link = book_items[book_index].find_element(*self.BOOK_TITLE_LINK)
            title_link.click()
            self.logger.info(f"点击第{book_index+1}本小说标题")
            time.sleep(2)  # 等待跳转到详情页
            return True
        return False
    
    def click_chapter_link(self, book_index=0):
        """点击章节链接（进入章节阅读页）"""
        book_items = self.find_elements(self.BOOK_LIST_ITEM)
        if book_index < len(book_items):
            chapter_link = book_items[book_index].find_element(*self.CHAPTER_LINK)
            chapter_link.click()
            self.logger.info(f"点击第{book_index+1}本小说的章节链接")
            time.sleep(2)  # 等待跳转到阅读页
            return True
        return False
    
    def is_history_empty(self):
        """检查最近阅读列表是否为空"""
        return self.is_element_visible(self.EMPTY_HISTORY)
    
    def get_book_info(self, book_index=0):
        """获取小说完整信息
        Args:
            book_index: 小说索引（从0开始）
        Returns:
            dict: 包含小说标题、章节标题、阅读时间、分类等信息
        """
        book_items = self.find_elements(self.BOOK_LIST_ITEM)
        if book_index < len(book_items):
            book_item = book_items[book_index]
            info = {}
            try:
                title_link = book_item.find_element(*self.BOOK_TITLE_LINK)
                info['title'] = title_link.text
                info['title_href'] = title_link.get_attribute('href')
            except:
                info['title'] = ''
                info['title_href'] = ''
            
            try:
                chapter_link = book_item.find_element(*self.CHAPTER_LINK)
                info['chapter_title'] = chapter_link.text
                info['chapter_href'] = chapter_link.get_attribute('href')
            except:
                info['chapter_title'] = ''
                info['chapter_href'] = ''
            
            try:
                time_element = book_item.find_element(*self.READING_TIME)
                info['reading_time'] = time_element.text
            except:
                info['reading_time'] = ''
            
            try:
                category_link = book_item.find_element(*self.BOOK_CATEGORY)
                info['category'] = category_link.text
                info['category_href'] = category_link.get_attribute('href')
            except:
                info['category'] = ''
                info['category_href'] = ''
            
            return info
        return {}
    
    def wait_for_history_loaded(self, timeout=10):
        """等待最近阅读列表加载完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            book_items = self.find_elements(self.BOOK_LIST_ITEM)
            if len(book_items) > 0 or self.is_history_empty():
                return True
            time.sleep(0.5)
        
        self.logger.warning(f"最近阅读列表加载超时: {timeout}秒")
        return False
    
    def select_book_by_title(self, title):
        """通过标题选择小说"""
        book_items = self.find_elements(self.BOOK_LIST_ITEM)
        for i, item in enumerate(book_items):
            try:
                title_link = item.find_element(*self.BOOK_TITLE_LINK)
                if title in title_link.text:
                    return i  # 返回索引
            except:
                continue
        return -1
    
    def click_continue_reading_by_title(self, title):
        """通过小说标题点击继续阅读链接"""
        index = self.select_book_by_title(title)
        if index >= 0:
            return self.click_continue_reading(index)
        return False