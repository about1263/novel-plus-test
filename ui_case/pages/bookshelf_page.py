"""
书架页面对象
封装书架页面的元素和操作
"""
import time
from .base_page import BasePage
from selenium.webdriver.common.by import By


class BookshelfPage(BasePage):
    """书架页面"""
    
    # 页面URL
    URL = "/user/favorites.html"
    
    # 元素定位器
    # 阅读按钮（可能不存在，根据实际页面决定）
    READ_BUTTON = (By.CSS_SELECTOR, "td.goread a")  # 与继续阅读按钮相同
    # 继续阅读按钮 - 根据提供的HTML: <td class="goread"><a href="...">继续阅读</a></td>
    CONTINUE_READING_BUTTON = (By.CSS_SELECTOR, "td.goread a")
    # 小说列表项 - 假设每本书是一个表格行<tr>
    BOOK_ITEM = (By.CSS_SELECTOR, "table tbody tr")
    # 小说标题 - 假设在第一个<td>或特定列中
    BOOK_TITLE = (By.CSS_SELECTOR, "tr td:first-child a, .book-title")
    # 书架空状态提示
    EMPTY_BOOKSHELF = (By.CSS_SELECTOR, ".empty-bookshelf, .no-data")
    # 用户昵称显示
    USER_NICKNAME = (By.ID, "user_nickname")
    
    def __init__(self, driver, base_url=None):
        super().__init__(driver)
        self.base_url = base_url or "http://localhost:8080"
    
    def open_bookshelf_page(self):
        """打开书架页面"""
        bookshelf_url = f"{self.base_url}{self.URL}"
        self.open(bookshelf_url)
        return self
    
    def click_read_button(self, book_index=0):
        """点击阅读按钮"""
        # 先找到小说列表项
        book_items = self.find_elements(self.BOOK_ITEM)
        if book_index < len(book_items):
            # 在小说项内查找阅读按钮
            read_button = book_items[book_index].find_element(*self.READ_BUTTON)
            read_button.click()
            self.logger.info(f"点击第{book_index+1}本小说的阅读按钮")
        else:
            raise IndexError(f"书架中没有第{book_index+1}本小说")
        return self
    
    def click_continue_reading_button(self, book_index=0):
        """点击继续阅读按钮"""
        book_items = self.find_elements(self.BOOK_ITEM)
        if book_index < len(book_items):
            # 在小说项内查找继续阅读按钮
            continue_button = book_items[book_index].find_element(*self.CONTINUE_READING_BUTTON)
            continue_button.click()
            self.logger.info(f"点击第{book_index+1}本小说的继续阅读按钮")
        else:
            raise IndexError(f"书架中没有第{book_index+1}本小说")
        return self
    
    def get_book_titles(self):
        """获取所有小说标题"""
        titles = []
        book_titles = self.find_elements(self.BOOK_TITLE)
        for title in book_titles:
            titles.append(title.text)
        return titles
    
    def get_book_count(self):
        """获取书架中的小说数量"""
        book_items = self.find_elements(self.BOOK_ITEM)
        return len(book_items)
    
    def is_bookshelf_empty(self):
        """检查书架是否为空"""
        return self.is_element_visible(self.EMPTY_BOOKSHELF)
    
    def get_user_nickname(self):
        """获取用户昵称"""
        if self.is_element_visible(self.USER_NICKNAME):
            return self.get_text(self.USER_NICKNAME)
        return ""
    
    def wait_for_books_loaded(self, timeout=10):
        """等待书架书籍加载完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            book_items = self.find_elements(self.BOOK_ITEM)
            if len(book_items) > 0:
                return True
            time.sleep(0.5)
        
        self.logger.warning(f"书架书籍加载超时: {timeout}秒")
        return False
    
    def select_book_by_title(self, title):
        """通过标题选择小说"""
        book_items = self.find_elements(self.BOOK_ITEM)
        for i, item in enumerate(book_items):
            try:
                book_title = item.find_element(*self.BOOK_TITLE)
                if title in book_title.text:
                    return i  # 返回索引
            except:
                continue
        return -1
    
    def click_book_by_title(self, title):
        """通过标题点击小说（进入详情页）"""
        index = self.select_book_by_title(title)
        if index >= 0:
            book_items = self.find_elements(self.BOOK_ITEM)
            book_items[index].click()
            self.logger.info(f"点击小说: {title}")
            return True
        return False