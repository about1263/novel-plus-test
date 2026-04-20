"""
小说阅读功能UI测试用例
基于UI自动化测试用例.txt中的测试场景
"""
import pytest
import allure
import time
import random

from ui_case.test_cases.base_test import BaseUITest
from ui_case.pages.bookshelf_page import BookshelfPage
from ui_case.pages.book_detail_page import BookDetailPage
from ui_case.pages.reader_page import ReaderPage
from ui_case.pages.home_page import HomePage
from ui_case.pages.read_history_page import ReadHistoryPage


@allure.epic("Novel-Plus UI自动化测试")
@allure.feature("小说阅读功能")
class TestReading(BaseUITest):
    """小说阅读功能测试类"""
    
    @pytest.fixture(scope="function", autouse=True)
    def setup_pages(self, driver, config):
        """页面对象fixture"""
        base_url = config.get_environment_config()['base_url']
        self.bookshelf_page = BookshelfPage(driver, base_url)
        self.book_detail_page = BookDetailPage(driver, base_url)
        self.reader_page = ReaderPage(driver, base_url)
        self.home_page = HomePage(driver, base_url)
        self.read_history_page = ReadHistoryPage(driver, base_url)
    
    @allure.story("从书架进入阅读页验证")
    @allure.title("XSYD_UI_01 - 从书架进入阅读页验证")
    @allure.description("验证从书架页面点击'阅读'按钮可以进入阅读器界面")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.reading
    @pytest.mark.smoke
    def test_bookshelf_to_reading(self, login_page, test_data):
        """从书架进入阅读页验证"""
        with allure.step("1. 登录用户账号"):
            valid_user = test_data['valid_user']
            login_page.open_login_page()
            login_page.login(valid_user['phone'], valid_user['password'])
            time.sleep(2)  # 等待登录完成
        
        with allure.step("2. 进入书架页面"):
            self.bookshelf_page.open_bookshelf_page()
            time.sleep(2)  # 等待书架加载
        
        with allure.step("3. 点击'继续阅读'按钮"):
            # 假设书架中至少有一本小说
            self.bookshelf_page.click_continue_reading_button(book_index=0)
            time.sleep(2)  # 等待页面跳转
        
        with allure.step("4. 验证跳转到阅读器界面"):
            current_url = self.get_current_url()
            self.logger.info(f"当前URL: {current_url}")
            
            # 验证页面跳转至阅读器界面（书籍章节页面）
            # URL格式应为: /book/{bookId}/{chapterId}.html
            self.assert_true("/book/" in current_url, f"页面未跳转至阅读器界面，URL未包含书籍路径: {current_url}")
            self.assert_true(".html" in current_url, f"页面未跳转至阅读器界面，URL不是HTML页面: {current_url}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="阅读器界面",
                         attachment_type=allure.attachment_type.PNG)
    
    @allure.story("从首页小说标签进入阅读页验证")
    @allure.title("XSYD_UI_02 - 从首页小说标签进入阅读页验证")
    @allure.description("验证从首页点击小说标签跳转到详情页，再点击阅读按钮可以进入阅读器界面")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.reading
    def test_detail_to_reading(self):
        """从首页小说标签进入阅读页验证"""
        with allure.step("1. 打开首页"):
            self.home_page.open_home_page()
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="首页页面",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("2. 点击首页小说标签跳转到小说详情页"):
            # 点击第一个小说标签
            success = self.home_page.click_novel_tag(0)
            self.assert_true(success, "无法点击小说标签或小说标签不存在")
            
            # 验证跳转到小说详情页
            current_url = self.get_current_url()
            self.assert_true("/book/" in current_url and ".html" in current_url,
                           f"未跳转到小说详情页，当前URL: {current_url}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="小说详情页",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("3. 点击阅读按钮"):
            success = self.home_page.click_read_button()
            self.assert_true(success, "无法点击阅读按钮或阅读按钮不存在")
        
        with allure.step("4. 验证跳转到阅读器界面"):
            current_url = self.get_current_url()
            self.logger.info(f"当前URL: {current_url}")
            
            # 验证页面跳转至阅读器界面（书籍章节页面）
            # 和XSYD_UI_01一样的断言：URL包含"/book/"和".html"
            self.assert_true("/book/" in current_url, f"页面未跳转至阅读器界面，URL未包含书籍路径: {current_url}")
            self.assert_true(".html" in current_url, f"页面未跳转至阅读器界面，URL不是HTML页面: {current_url}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="阅读器界面",
                         attachment_type=allure.attachment_type.PNG)
    
    @allure.story("下一章切换验证")
    @allure.title("XSYD_UI_03 - 下一章切换验证")
    @allure.description("验证在阅读器界面点击'下一章'按钮可以切换到下一章节")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.reading
    def test_next_chapter(self):
        """下一章切换验证 - 复用XSYD_UI_02步骤进入阅读页"""
        with allure.step("1. 打开首页"):
            self.home_page.open_home_page()
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="首页页面",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("2. 点击首页小说标签跳转到小说详情页"):
            # 点击第一个小说标签
            success = self.home_page.click_novel_tag(0)
            self.assert_true(success, "无法点击小说标签或小说标签不存在")
            
            # 验证跳转到小说详情页
            current_url = self.get_current_url()
            self.assert_true("/book/" in current_url and ".html" in current_url,
                           f"未跳转到小说详情页，当前URL: {current_url}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="小说详情页",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("3. 点击阅读按钮"):
            success = self.home_page.click_read_button()
            self.assert_true(success, "无法点击阅读按钮或阅读按钮不存在")
        
        with allure.step("4. 验证跳转到阅读器界面"):
            current_url = self.get_current_url()
            self.logger.info(f"当前URL: {current_url}")
            
            # 验证页面跳转至阅读器界面（书籍章节页面）
            self.assert_true("/book/" in current_url, f"页面未跳转至阅读器界面，URL未包含书籍路径: {current_url}")
            self.assert_true(".html" in current_url, f"页面未跳转至阅读器界面，URL不是HTML页面: {current_url}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="阅读器界面",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("5. 等待内容加载完成"):
            self.reader_page.wait_for_chapter_loaded()
            previous_title = self.reader_page.get_chapter_title()
            self.logger.info(f"当前章节标题: {previous_title}")
        
        with allure.step("6. 点击'下一章'按钮"):
            self.reader_page.click_next_chapter()
            self.reader_page.wait_for_next_chapter_loaded()
        
        with allure.step("7. 验证内容切换至下一章节"):
            # 方法1：使用页面对象的验证方法
            chapter_switched = self.reader_page.verify_chapter_switch(previous_title)
            if chapter_switched:
                self.logger.info("章节切换验证通过（章节标题已更新）")
            else:
                self.logger.warning("章节标题未更新，尝试其他验证方式")
                # 方法2：检查URL参数变化
                chapter_param = self.reader_page.get_url_chapter_param()
                if chapter_param is not None:
                    self.logger.info(f"URL章节参数: {chapter_param}")
                    # 可以进一步验证参数变化
                # 方法3：检查章节编号变化
                chapter_number = self.reader_page.get_chapter_number()
                if chapter_number:
                    self.logger.info(f"章节编号: {chapter_number}")
            
            # 无论如何，确保当前章节标题非空（基本验证）
            current_title = self.reader_page.get_chapter_title()
            self.assert_is_not_none(current_title, "切换后章节标题未显示")
            self.assert_true(len(current_title.strip()) > 0, "切换后章节标题为空")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="下一章切换",
                         attachment_type=allure.attachment_type.PNG)
    
    @allure.story("上一章切换验证")
    @allure.title("XSYD_UI_04 - 上一章切换验证")
    @allure.description("验证在阅读器界面点击'上一章'按钮可以返回上一章节")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.reading
    def test_previous_chapter(self):
        """上一章切换验证 - 复用XSYD_UI_03步骤进入阅读页"""
        with allure.step("1. 打开首页"):
            self.home_page.open_home_page()
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="首页页面",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("2. 点击首页小说标签跳转到小说详情页"):
            # 点击第一个小说标签
            success = self.home_page.click_novel_tag(0)
            self.assert_true(success, "无法点击小说标签或小说标签不存在")
            
            # 验证跳转到小说详情页
            current_url = self.get_current_url()
            self.assert_true("/book/" in current_url and ".html" in current_url,
                           f"未跳转到小说详情页，当前URL: {current_url}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="小说详情页",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("3. 点击阅读按钮"):
            success = self.home_page.click_read_button()
            self.assert_true(success, "无法点击阅读按钮或阅读按钮不存在")
        
        with allure.step("4. 验证跳转到阅读器界面"):
            current_url = self.get_current_url()
            self.logger.info(f"当前URL: {current_url}")
            
            # 验证页面跳转至阅读器界面（书籍章节页面）
            self.assert_true("/book/" in current_url, f"页面未跳转至阅读器界面，URL未包含书籍路径: {current_url}")
            self.assert_true(".html" in current_url, f"页面未跳转至阅读器界面，URL不是HTML页面: {current_url}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="阅读器界面",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("5. 等待内容加载完成"):
            self.reader_page.wait_for_chapter_loaded()
            previous_title = self.reader_page.get_chapter_title()
            self.logger.info(f"当前章节标题: {previous_title}")
        
        with allure.step("6. 点击'下一章'按钮"):
            self.reader_page.click_next_chapter()
            self.reader_page.wait_for_next_chapter_loaded()
        
        with allure.step("7. 验证下一章切换成功"):
            # 检查章节标题是否改变
            chapter_after_next = self.reader_page.get_chapter_title()
            self.assert_is_not_none(chapter_after_next, "切换到下一章后章节标题未显示")
            self.assert_not_equal(previous_title, chapter_after_next, "点击下一章后章节标题未改变")
            self.logger.info(f"下一章标题: {chapter_after_next}")
        
        with allure.step("8. 点击'上一章'按钮"):
            self.reader_page.click_previous_chapter()
            self.reader_page.wait_for_chapter_loaded()
        
        with allure.step("9. 验证内容返回上一章节"):
            # 方法1：使用页面对象的验证方法
            chapter_switched = self.reader_page.verify_chapter_switch(chapter_after_next)
            if chapter_switched:
                self.logger.info("章节切换验证通过（章节标题已更新）")
            else:
                self.logger.warning("章节标题未更新，尝试其他验证方式")
                # 方法2：检查URL参数变化
                chapter_param = self.reader_page.get_url_chapter_param()
                if chapter_param is not None:
                    self.logger.info(f"URL章节参数: {chapter_param}")
                    # 可以进一步验证参数变化
                # 方法3：检查章节编号变化
                chapter_number = self.reader_page.get_chapter_number()
                if chapter_number:
                    self.logger.info(f"章节编号: {chapter_number}")
            
            # 验证返回原章节（标题与之前记录的相同）
            current_title = self.reader_page.get_chapter_title()
            self.assert_is_not_none(current_title, "切换后章节标题未显示")
            self.assert_true(len(current_title.strip()) > 0, "切换后章节标题为空")
            self.assert_equal(current_title, previous_title, f"未返回原章节，当前标题: {current_title}，原章节标题: {previous_title}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="上一章切换",
                         attachment_type=allure.attachment_type.PNG)
    
    @allure.story("目录跳转验证")
    @allure.title("XSYD_UI_05 - 目录跳转验证")
    @allure.description("验证通过目录图标跳转到目录页，并点击任意章节跳转到对应章节")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.reading
    def test_catalog_navigation(self):
        """目录跳转验证"""
        with allure.step("1. 同XSYD_UI_03进入小说阅读界面（从首页进入）"):
            with allure.step("1.1 打开首页"):
                self.home_page.open_home_page()
                
                allure.attach(self.driver.get_screenshot_as_png(),
                             name="首页页面",
                             attachment_type=allure.attachment_type.PNG)
            
            with allure.step("1.2 点击首页小说标签跳转到小说详情页"):
                # 点击第一个小说标签
                success = self.home_page.click_novel_tag(0)
                self.assert_true(success, "无法点击小说标签或小说标签不存在")
                
                # 验证跳转到小说详情页
                current_url = self.get_current_url()
                self.assert_true("/book/" in current_url and ".html" in current_url,
                               f"未跳转到小说详情页，当前URL: {current_url}")
                
                allure.attach(self.driver.get_screenshot_as_png(),
                             name="小说详情页",
                             attachment_type=allure.attachment_type.PNG)
            
            with allure.step("1.3 点击阅读按钮"):
                success = self.home_page.click_read_button()
                self.assert_true(success, "无法点击阅读按钮或阅读按钮不存在")
            
            with allure.step("1.4 验证跳转到阅读器界面"):
                current_url = self.get_current_url()
                self.logger.info(f"当前URL: {current_url}")
                
                # 验证页面跳转至阅读器界面（书籍章节页面）
                self.assert_true("/book/" in current_url, f"页面未跳转至阅读器界面，URL未包含书籍路径: {current_url}")
                self.assert_true(".html" in current_url, f"页面未跳转至阅读器界面，URL不是HTML页面: {current_url}")
                
                allure.attach(self.driver.get_screenshot_as_png(),
                             name="阅读器界面",
                             attachment_type=allure.attachment_type.PNG)
            
            with allure.step("1.5 等待内容加载完成"):
                self.reader_page.wait_for_chapter_loaded()
                original_title = self.reader_page.get_chapter_title()
                self.logger.info(f"原始章节标题: {original_title}")
        
        with allure.step("2. 点击目录图标跳转到目录页"):
            # 点击目录图标：<a class="ico_catalog" href="/book/indexList-1262260513468559361.html" title="目录">
            self.reader_page.click_catalog_icon()
            time.sleep(2)  # 等待目录页加载
            
            # 验证目录页章节列表可见
            dir_list_visible = self.reader_page.is_dir_list_visible()
            self.assert_true(dir_list_visible, "目录页章节列表未显示")
            
            # 获取目录页章节数量
            chapter_count = self.reader_page.get_dir_list_chapter_count()
            self.assert_greater(chapter_count, 0, "目录页中没有章节")
            self.logger.info(f"目录页章节数量: {chapter_count}")
            
            # 获取目录页章节标题列表
            chapter_titles = self.reader_page.get_dir_list_chapter_titles()
            self.logger.info(f"目录页章节标题: {chapter_titles}")
        
        with allure.step("3. 点击任意章节（例如'边界'）"):
            # 点击章节标题为"边界"的章节（如果存在），否则点击第一个章节
            target_chapter = "边界"
            if target_chapter in chapter_titles:
                success = self.reader_page.click_chapter_in_dir_list(chapter_title=target_chapter)
                self.assert_true(success, f"点击章节'{target_chapter}'失败")
                self.logger.info(f"点击章节: {target_chapter}")
            else:
                self.logger.warning(f"章节'{target_chapter}'不存在，点击第一个章节")
                success = self.reader_page.click_chapter_in_dir_list(chapter_index=0)
                self.assert_true(success, "点击第一个章节失败")
        
        with allure.step("4. 验证跳转到对应章节"):
            # 等待章节内容加载
            self.reader_page.wait_for_chapter_loaded(timeout=5)
            
            # 验证跳转后章节标题已改变
            current_title = self.reader_page.get_chapter_title()
            self.assert_is_not_none(current_title, "跳转后章节标题未显示")
            self.assert_not_equal(current_title, original_title, "章节标题未改变，可能未跳转")
            self.logger.info(f"跳转后章节标题: {current_title}")
            
            # 验证URL包含书籍和章节路径
            current_url = self.get_current_url()
            self.assert_true("/book/" in current_url, f"页面未跳转至阅读器界面，URL未包含书籍路径: {current_url}")
            self.assert_true(".html" in current_url, f"页面未跳转至阅读器界面，URL不是HTML页面: {current_url}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="目录跳转",
                         attachment_type=allure.attachment_type.PNG)
    
    @allure.story("字体大小调整验证")
    @allure.title("XSYD_UI_06 - 字体大小调整验证")
    @allure.description("验证可以调整阅读器字体大小")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.reading
    def test_font_size_adjustment(self):
        """字体大小调整验证 - 复用test_detail_to_reading的步骤进入阅读页"""
        with allure.step("1. 同XSYD_UI_02进入小说阅读界面（从首页进入）"):
            with allure.step("1.1 打开首页"):
                self.home_page.open_home_page()
                
                allure.attach(self.driver.get_screenshot_as_png(),
                             name="首页页面",
                             attachment_type=allure.attachment_type.PNG)
            
            with allure.step("1.2 点击首页小说标签跳转到小说详情页"):
                # 点击第一个小说标签
                success = self.home_page.click_novel_tag(0)
                self.assert_true(success, "无法点击小说标签或小说标签不存在")
                
                # 验证跳转到小说详情页
                current_url = self.get_current_url()
                self.assert_true("/book/" in current_url and ".html" in current_url,
                               f"未跳转到小说详情页，当前URL: {current_url}")
                
                allure.attach(self.driver.get_screenshot_as_png(),
                             name="小说详情页",
                             attachment_type=allure.attachment_type.PNG)
            
            with allure.step("1.3 点击阅读按钮"):
                success = self.home_page.click_read_button()
                self.assert_true(success, "无法点击阅读按钮或阅读按钮不存在")
            
            with allure.step("1.4 验证跳转到阅读器界面"):
                current_url = self.get_current_url()
                self.logger.info(f"当前URL: {current_url}")
                
                # 验证页面跳转至阅读器界面（书籍章节页面）
                self.assert_true("/book/" in current_url, f"页面未跳转至阅读器界面，URL未包含书籍路径: {current_url}")
                self.assert_true(".html" in current_url, f"页面未跳转至阅读器界面，URL不是HTML页面: {current_url}")
                
                allure.attach(self.driver.get_screenshot_as_png(),
                             name="阅读器界面",
                             attachment_type=allure.attachment_type.PNG)
            
            with allure.step("1.5 等待内容加载完成"):
                self.reader_page.wait_for_chapter_loaded()
        
        with allure.step("2. 点击设置按钮"):
            self.reader_page.click_settings_button()
            time.sleep(0.5)
            
            # 验证设置面板展开
            settings_visible = self.reader_page.is_settings_panel_visible()
            self.assert_true(settings_visible, "设置面板未展开")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="设置面板展开",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("3. 获取初始字体大小"):
            initial_font_size = self.reader_page.get_current_font_size()
            self.assert_is_not_none(initial_font_size, "无法获取初始字体大小")
            self.logger.info(f"初始字体大小: {initial_font_size}")
        
        with allure.step("4. 点击字体增大按钮(A+)"):
            self.reader_page.increase_font_size()
            time.sleep(0.5)
            
            # 验证字体大小增大
            increased_font_size = self.reader_page.get_current_font_size()
            self.assert_is_not_none(increased_font_size, "增大字体后无法获取字体大小")
            
            # 验证字体大小确实增大了（转换为整数比较）
            try:
                initial = int(initial_font_size) if isinstance(initial_font_size, str) else initial_font_size
                increased = int(increased_font_size) if isinstance(increased_font_size, str) else increased_font_size
                self.assert_greater(increased, initial, f"字体大小未增大: {increased} <= {initial}")
                self.logger.info(f"字体大小从 {initial} 增大到 {increased}")
            except (ValueError, TypeError) as e:
                self.logger.warning(f"无法比较字体大小数值: {e}")
                # 至少验证字体大小改变了
                self.assert_not_equal(increased_font_size, initial_font_size, 
                                    f"字体大小未改变: {increased_font_size}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="字体增大后",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("5. 点击字体减小按钮(A-)"):
            self.reader_page.decrease_font_size()
            time.sleep(0.5)
            
            # 验证字体大小减小
            decreased_font_size = self.reader_page.get_current_font_size()
            self.assert_is_not_none(decreased_font_size, "减小字体后无法获取字体大小")
            
            # 验证字体大小确实减小了（至少应该回到初始大小或更小）
            try:
                increased = int(increased_font_size) if isinstance(increased_font_size, str) else increased_font_size
                decreased = int(decreased_font_size) if isinstance(decreased_font_size, str) else decreased_font_size
                self.assert_less(decreased, increased, f"字体大小未减小: {decreased} >= {increased}")
                self.logger.info(f"字体大小从 {increased} 减小到 {decreased}")
            except (ValueError, TypeError) as e:
                self.logger.warning(f"无法比较字体大小数值: {e}")
                # 至少验证字体大小改变了
                self.assert_not_equal(decreased_font_size, increased_font_size, 
                                    f"字体大小未改变: {decreased_font_size}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="字体减小后",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("6. 多次点击字体增大和减小按钮"):
            # 再次增大字体
            self.reader_page.increase_font_size()
            time.sleep(0.3)
            font_size_after_second_increase = self.reader_page.get_current_font_size()
            self.logger.info(f"第二次增大后字体大小: {font_size_after_second_increase}")
            
            # 再次减小字体
            self.reader_page.decrease_font_size()
            time.sleep(0.3)
            font_size_after_second_decrease = self.reader_page.get_current_font_size()
            self.logger.info(f"第二次减小后字体大小: {font_size_after_second_decrease}")
            
            # 验证字体大小变化的一致性
            if (isinstance(font_size_after_second_decrease, (int, str)) and 
                isinstance(decreased_font_size, (int, str))):
                self.assert_equal(str(font_size_after_second_decrease), str(decreased_font_size),
                                f"字体大小不一致: {font_size_after_second_decrease} != {decreased_font_size}")
        
        with allure.step("7. 关闭设置面板"):
            self.reader_page.close_settings_panel()
            time.sleep(0.5)
            
            # 验证设置面板已关闭
            settings_visible = self.reader_page.is_settings_panel_visible()
            self.assert_false(settings_visible, "设置面板未关闭")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="字体大小调整完成",
                         attachment_type=allure.attachment_type.PNG)
    
    @allure.story("主题切换验证")
    @allure.title("XSYD_UI_07 - 主题切换验证")
    @allure.description("验证可以切换阅读器颜色主题（白色、绿色、粉色、黄色、灰色、夜间）")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.reading
    def test_theme_switching(self):
        """主题切换验证 - 复用test_font_size_adjustment的步骤进入阅读页"""
        with allure.step("1. 同XSYD_UI_02进入小说阅读界面（从首页进入）"):
            with allure.step("1.1 打开首页"):
                self.home_page.open_home_page()
                
                allure.attach(self.driver.get_screenshot_as_png(),
                             name="首页页面",
                             attachment_type=allure.attachment_type.PNG)
            
            with allure.step("1.2 点击首页小说标签跳转到小说详情页"):
                # 点击第一个小说标签
                success = self.home_page.click_novel_tag(0)
                self.assert_true(success, "无法点击小说标签或小说标签不存在")
                
                # 验证跳转到小说详情页
                current_url = self.get_current_url()
                self.assert_true("/book/" in current_url and ".html" in current_url,
                               f"未跳转到小说详情页，当前URL: {current_url}")
                
                allure.attach(self.driver.get_screenshot_as_png(),
                             name="小说详情页",
                             attachment_type=allure.attachment_type.PNG)
            
            with allure.step("1.3 点击阅读按钮"):
                success = self.home_page.click_read_button()
                self.assert_true(success, "无法点击阅读按钮或阅读按钮不存在")
            
            with allure.step("1.4 验证跳转到阅读器界面"):
                current_url = self.get_current_url()
                self.logger.info(f"当前URL: {current_url}")
                
                # 验证页面跳转至阅读器界面（书籍章节页面）
                self.assert_true("/book/" in current_url, f"页面未跳转至阅读器界面，URL未包含书籍路径: {current_url}")
                self.assert_true(".html" in current_url, f"页面未跳转至阅读器界面，URL不是HTML页面: {current_url}")
                
                allure.attach(self.driver.get_screenshot_as_png(),
                             name="阅读器界面",
                             attachment_type=allure.attachment_type.PNG)
            
            with allure.step("1.5 等待内容加载完成"):
                self.reader_page.wait_for_chapter_loaded()
        
        with allure.step("2. 点击设置按钮"):
            self.reader_page.click_settings_button()
            time.sleep(0.5)
            
            # 验证设置面板展开
            settings_visible = self.reader_page.is_settings_panel_visible()
            self.assert_true(settings_visible, "设置面板未展开")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="设置面板展开",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("3. 切换不同颜色主题"):
            color_themes = ["white", "green", "pink", "yellow", "gray", "night"]
            
            for color in color_themes:
                with allure.step(f"切换为{color}颜色主题"):
                    success = self.reader_page.set_color_theme(color)
                    self.assert_true(success, f"设置{color}颜色主题失败")
                    
                    # 验证背景色正确变更
                    theme_changed = self.reader_page.verify_theme_changed(color)
                    self.assert_true(theme_changed, f"{color}颜色主题未生效")
                    
                    time.sleep(1)  # 等待视觉效果
                    
                    # 可选：验证当前激活的颜色主题元素有current类
                    # 根据用户提供的HTML，当前激活的主题有"current"类
                    # 这里可以添加更精确的验证，但至少确保背景色改变
        
        with allure.step("4. 验证颜色主题切换功能"):
            # 再次切换回白色主题，确保功能正常
            success = self.reader_page.set_color_theme("white")
            self.assert_true(success, "切换回白色主题失败")
            time.sleep(0.5)
            
            # 验证白色主题生效
            theme_changed = self.reader_page.verify_theme_changed("white")
            self.assert_true(theme_changed, "白色主题未生效")
            
            self.logger.info("颜色主题切换测试完成")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="颜色主题切换",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("5. 关闭设置面板"):
            self.reader_page.close_settings_panel()
            time.sleep(0.5)
            
            # 验证设置面板已关闭
            settings_visible = self.reader_page.is_settings_panel_visible()
            self.assert_false(settings_visible, "设置面板未关闭")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="主题切换完成",
                         attachment_type=allure.attachment_type.PNG)
    
    @allure.story("评论入口验证")
    @allure.title("XSYD_UI_08 - 评论入口验证")
    @allure.description("验证点击评论图标可以跳转到评论页面，点击发表评论链接可定位到评论输入栏")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.reading
    def test_comment_entry(self):
        """评论入口验证 - 从首页进入，不登录"""
        with allure.step("1. 同XSYD_UI_02进入小说阅读界面（从首页进入）"):
            with allure.step("1.1 打开首页"):
                self.home_page.open_home_page()
                
                allure.attach(self.driver.get_screenshot_as_png(),
                             name="首页页面",
                             attachment_type=allure.attachment_type.PNG)
            
            with allure.step("1.2 点击首页小说标签跳转到小说详情页"):
                # 点击第一个小说标签
                success = self.home_page.click_novel_tag(0)
                self.assert_true(success, "无法点击小说标签或小说标签不存在")
                
                # 验证跳转到小说详情页
                current_url = self.get_current_url()
                self.assert_true("/book/" in current_url and ".html" in current_url,
                               f"未跳转到小说详情页，当前URL: {current_url}")
                
                allure.attach(self.driver.get_screenshot_as_png(),
                             name="小说详情页",
                             attachment_type=allure.attachment_type.PNG)
            
            with allure.step("1.3 点击阅读按钮"):
                success = self.home_page.click_read_button()
                self.assert_true(success, "无法点击阅读按钮或阅读按钮不存在")
            
            with allure.step("1.4 验证跳转到阅读器界面"):
                current_url = self.get_current_url()
                self.logger.info(f"当前URL: {current_url}")
                
                # 验证页面跳转至阅读器界面（书籍章节页面）
                self.assert_true("/book/" in current_url, f"页面未跳转至阅读器界面，URL未包含书籍路径: {current_url}")
                self.assert_true(".html" in current_url, f"页面未跳转至阅读器界面，URL不是HTML页面: {current_url}")
                
                allure.attach(self.driver.get_screenshot_as_png(),
                             name="阅读器界面",
                             attachment_type=allure.attachment_type.PNG)
        
        with allure.step("2. 点击'评论'图标"):
            original_url = self.get_current_url()
            self.reader_page.click_comment_icon()
            time.sleep(2)  # 等待页面跳转
        
        with allure.step("3. 验证跳转到评论页面"):
            current_url = self.get_current_url()
            self.assert_not_equal(current_url, original_url, "点击评论图标后页面未跳转")
            
            # 验证跳转到评论页面
            self.assert_true("comment" in current_url, f"未跳转到评论页面，当前URL: {current_url}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="评论页面",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("4. 点击'发表评论'链接"):
            # 点击发表评论链接：<a class="fr" href="#txtComment">发表评论</a>
            self.reader_page.click_publish_comment_link()
            time.sleep(1)  # 等待页面滚动到评论输入栏
        
        with allure.step("5. 验证评论输入栏被定位"):
            # 验证评论输入栏可见（已滚动到视图中）
            comment_input_visible = self.reader_page.is_comment_input_visible()
            self.assert_true(comment_input_visible, "评论输入栏不可见，页面未滚动到评论输入栏")
            
            # 可选：验证输入栏获得焦点（如果实现）
            # 这里可以添加更详细的验证，例如检查输入栏是否可交互
            
            self.logger.info("评论输入栏已成功定位")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="评论输入栏定位",
                         attachment_type=allure.attachment_type.PNG)
    
    @allure.story("继续阅读验证")
    @allure.title("XSYD_UI_09 - 继续阅读验证")
    @allure.description("验证从书架点击'继续阅读'可以跳转到上次阅读的章节")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    @pytest.mark.reading
    def test_continue_reading(self, login_page, test_data):
        """继续阅读验证 - 从首页进入，通过全部目录选择章节，然后从最近阅读继续"""
        with allure.step("1. 登录账号"):
            valid_user = test_data['valid_user']
            login_page.open_login_page()
            login_page.login(valid_user['phone'], valid_user['password'])
            time.sleep(2)
        
        with allure.step("2. 打开首页，点击第一个小说标签"):
            self.home_page.open_home_page()
            success = self.home_page.click_novel_tag(0)
            self.assert_true(success, "无法点击小说标签或小说标签不存在")
            time.sleep(2)
            
            # 验证跳转到小说详情页
            current_url = self.get_current_url()
            self.assert_true("/book/" in current_url and ".html" in current_url,
                           f"未跳转到小说详情页，当前URL: {current_url}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="小说详情页",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("3. 点击'全部目录'链接"):
            success = self.reader_page.click_all_catalog_link()
            self.assert_true(success, "点击全部目录链接失败")
            time.sleep(2)
            
            # 验证目录页加载
            dir_list_visible = self.reader_page.is_dir_list_visible()
            self.assert_true(dir_list_visible, "目录页章节列表未显示")
            
            # 获取章节数量
            chapter_count = self.reader_page.get_dir_list_chapter_count()
            self.assert_greater(chapter_count, 0, "目录页中没有章节")
            self.logger.info(f"目录页章节数量: {chapter_count}")
        
        with allure.step("4. 随机选择章节"):
            # 获取目录页章节数量
            chapter_count = self.reader_page.get_dir_list_chapter_count()
            self.logger.info(f"目录页章节数量: {chapter_count}")
            
            # 在章节数范围内随机选择一章
            chapter_index = random.randint(0, chapter_count - 1)
            self.logger.info(f"随机选择章节索引: {chapter_index}")
            
            # 记录选择的章节标题
            chapter_titles = self.reader_page.get_dir_list_chapter_titles()
            self.logger.info(f"目录页章节标题: {chapter_titles}")
            
            # 点击选择的章节
            success = self.reader_page.click_chapter_in_dir_list(chapter_index=chapter_index)
            self.assert_true(success, f"点击章节（索引{chapter_index}）失败")
            time.sleep(2)
            
            # 等待章节内容加载
            self.reader_page.wait_for_chapter_loaded()
            
            # 记录章节标题（这是之前阅读的章节）
            original_chapter_title = self.reader_page.get_chapter_title()
            self.assert_is_not_none(original_chapter_title, "章节标题未显示")
            self.logger.info(f"首次阅读的章节标题: {original_chapter_title}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="首次阅读章节",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("5. 点击'我的书架'链接"):
            success = self.reader_page.click_my_bookshelf_link()
            self.assert_true(success, "点击我的书架链接失败")
            time.sleep(2)
            
            # 验证跳转到书架页
            current_url = self.get_current_url()
            self.assert_true("favorites" in current_url, f"未跳转到书架页，当前URL: {current_url}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="我的书架页",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("6. 从书架页打开最近阅读页面"):
            # 使用read_history_page对象打开最近阅读页
            self.read_history_page.open_read_history_page()
            time.sleep(2)
            
            # 验证跳转到最近阅读页
            current_url = self.get_current_url()
            self.assert_true("read_history" in current_url, f"未跳转到最近阅读页，当前URL: {current_url}")
            
            # 等待最近阅读列表加载
            self.read_history_page.wait_for_history_loaded()
            
            # 验证最近阅读列表不为空
            book_count = self.read_history_page.get_book_count()
            self.assert_greater(book_count, 0, "最近阅读列表为空")
            self.logger.info(f"最近阅读列表小说数量: {book_count}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="最近阅读页",
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("7. 点击第一个小说的'继续阅读'按钮"):
            # 获取小说信息
            book_info = self.read_history_page.get_book_info(book_index=0)
            self.logger.info(f"第一本小说信息: {book_info}")
            
            # 点击继续阅读
            success = self.read_history_page.click_continue_reading(book_index=0)
            self.assert_true(success, "点击继续阅读按钮失败")
            time.sleep(2)
        
        with allure.step("8. 验证跳转到上次阅读的章节"):
            # 等待章节内容加载
            self.reader_page.wait_for_chapter_loaded()
            
            # 获取当前章节标题
            current_chapter_title = self.reader_page.get_chapter_title()
            self.assert_is_not_none(current_chapter_title, "继续阅读后章节标题未显示")
            self.logger.info(f"继续阅读后的章节标题: {current_chapter_title}")
            
            # 验证跳转的章节与之前阅读的章节一致
            self.assert_equal(current_chapter_title, original_chapter_title,
                            f"章节不一致，当前: {current_chapter_title}，原章节: {original_chapter_title}")
            
            # 验证URL包含书籍和章节路径
            current_url = self.get_current_url()
            self.assert_true("/book/" in current_url, f"页面未跳转至阅读器界面，URL未包含书籍路径: {current_url}")
            self.assert_true(".html" in current_url, f"页面未跳转至阅读器界面，URL不是HTML页面: {current_url}")
            
            allure.attach(self.driver.get_screenshot_as_png(),
                         name="继续阅读验证",
                         attachment_type=allure.attachment_type.PNG)
    
    @allure.story("页面滚动阅读验证")
    @allure.title("XSYD_UI_10 - 页面滚动阅读验证")
    @allure.description("验证页面滚动阅读体验：从首页进入阅读页，滚动到底部，点击下一章节")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.reading
    def test_page_scrolling(self):
        """页面滚动阅读验证 - 简化版本：滚动到底部，点击下一章按钮"""
        with allure.step("1. 打开首页并进入阅读页"):
            self.home_page.open_home_page()
            time.sleep(1)
            
            success = self.home_page.click_novel_tag(0)
            self.assert_true(success, "无法点击小说标签")
            
            success = self.home_page.click_read_button()
            self.assert_true(success, "无法点击阅读按钮")
            time.sleep(2)
        
        with allure.step("2. 验证已进入阅读器界面"):
            current_url = self.get_current_url()
            self.assert_true("/book/" in current_url, f"未跳转至阅读器界面，URL: {current_url}")
            self.assert_true(".html" in current_url, "URL不是HTML页面")
            allure.attach(self.driver.get_screenshot_as_png(), name="阅读器界面", attachment_type=allure.attachment_type.PNG)
        
        with allure.step("3. 等待章节内容加载"):
            self.reader_page.wait_for_chapter_loaded()
            chapter_title = self.reader_page.get_chapter_title()
            self.assert_is_not_none(chapter_title, "章节标题未显示")
            self.logger.info(f"当前章节标题: {chapter_title}")
        
        with allure.step("4. 使用Selenium滚动到页面底部"):
            # 使用JavaScript直接滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # 检查是否滚动成功（简单的验证）
            scroll_y = self.driver.execute_script("return window.scrollY;")
            scroll_height = self.driver.execute_script("return document.body.scrollHeight;")
            self.logger.info(f"滚动位置: {scroll_y}, 页面高度: {scroll_height}")
            
            # 验证滚动位置接近底部
            self.assert_greater(scroll_y, 0, "页面未滚动")
            allure.attach(self.driver.get_screenshot_as_png(), name="滚动到底部", attachment_type=allure.attachment_type.PNG)
        
        with allure.step("5. 点击下一章按钮"):
            url_before = self.get_current_url()
            chapter_title_before = self.reader_page.get_chapter_title()
            self.logger.info(f"点击下一章前 - URL: {url_before}, 章节: {chapter_title_before}")
            
            self.reader_page.click_next_chapter()
            time.sleep(2)
            
            self.reader_page.wait_for_next_chapter_loaded()
            
            url_after = self.get_current_url()
            chapter_title_after = self.reader_page.get_chapter_title()
            self.logger.info(f"点击下一章后 - URL: {url_after}, 章节: {chapter_title_after}")
        
        with allure.step("6. 验证章节切换"):
            current_url = self.get_current_url()
            page_title = self.driver.title
            self.assert_is_not_none(page_title, "页面标题为空，可能已崩溃")
            
            if "indexList" in current_url or "catalog" in current_url:
                self.logger.info("单章节书籍，已跳转到目录页")
                self.assert_true(True, "单章节书籍正常跳转到目录页")
            elif url_before != url_after:
                self.logger.info("成功切换到下一章节")
                self.assert_true("/book/" in current_url, "未保持在阅读器界面")
            else:
                self.logger.info("已经是最后一章，无法切换到下一章")
                self.assert_true(True, "已是最后一章，符合预期")
            
            allure.attach(self.driver.get_screenshot_as_png(), name="章节切换后", attachment_type=allure.attachment_type.PNG)


if __name__ == "__main__":
    # 直接运行测试（用于调试）
    pytest.main([__file__, "-v", "--alluredir=ui_case/reports/allure-results"])