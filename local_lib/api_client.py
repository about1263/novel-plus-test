#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pro_config.project_config import novel_api_urls
from local_lib.config import read_write_config


class NovelAPIClient:
    """
    小说网站API客户端
    """

    def __init__(self, env='lane'):
        self.env = env
        self.base_url = novel_api_urls.get(env, novel_api_urls['lane'])
        self.timeout = int(read_write_config.getValue('novelConfig', 'timeout') or 30)
        self.token = None
        
        # 创建会话并配置重试策略
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def set_token(self, token):
        """设置认证token"""
        self.token = token

    def _get_headers(self):
        """获取请求头"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'NovelTestClient/1.0'
        }
        if self.token:
            # 尝试不同的token格式
            headers['Authorization'] = self.token  # 直接使用token
            # headers['Authorization'] = f'Token {self.token}'  # 备选方案
            # headers['token'] = self.token  # 备选方案
        return headers

    def request(self, method, endpoint, data=None, params=None, files=None, form_data=False):
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        # 如果是文件上传或form-data，需要调整Content-Type
        if files or form_data:
            headers.pop('Content-Type', None)
        
        try:
            if files:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    files=files,
                    params=params,
                    timeout=self.timeout
                )
            elif form_data:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    params=params,
                    timeout=self.timeout
                )
            else:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                    timeout=self.timeout
                )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            raise

    def get(self, endpoint, params=None):
        """GET请求"""
        return self.request('GET', endpoint, params=params)

    def post(self, endpoint, data=None, files=None, form_data=False, params=None):
        """POST请求"""
        return self.request('POST', endpoint, data=data, files=files, form_data=form_data, params=params)

    def put(self, endpoint, data=None):
        """PUT请求"""
        return self.request('PUT', endpoint, data=data)

    def delete(self, endpoint):
        """DELETE请求"""
        return self.request('DELETE', endpoint)

    # 用户相关API
    def user_login(self, username, password):
        """用户登录"""
        data = {
            "username": username,
            "password": password
        }
        return self.post('/user/login', data, form_data=True)

    def user_register(self, username, password, phone, verify_code, session_id):
        """用户注册"""
        data = {
            "username": phone,
            "password": password,
            "velCode": verify_code,
            "sessionId": session_id
        }
        return self.post('/user/register', data)

    def get_user_info(self):
        """获取用户信息"""
        return self.get('/user')

    def refresh_token(self):
        """刷新token"""
        return self.post('/user/refreshToken')

    def query_is_in_shelf(self, book_id):
        """查询小说是否已加入书架"""
        return self.get('/user/queryIsInShelf', params={'bookId': book_id})

    def add_to_book_shelf(self, book_id, pre_content_id):
        """加入书架"""
        data = {
            'bookId': book_id,
            'preContentId': pre_content_id
        }
        return self.post('/user/addToBookShelf', data=data)

    def remove_from_book_shelf(self, book_id):
        """移出书架"""
        return self.delete(f'/user/removeFromBookShelf/{book_id}')

    def list_book_shelf_by_page(self, page=1, page_size=10):
        """分页查询书架"""
        params = {
            'page': page,
            'pageSize': page_size
        }
        return self.get('/user/listBookShelfByPage', params=params)

    def list_read_history_by_page(self, page=1, page_size=10):
        """分页查询阅读记录"""
        params = {
            'page': page,
            'pageSize': page_size
        }
        return self.get('/user/listReadHistoryByPage', params=params)

    def add_read_history(self, book_id, pre_content_id):
        """添加阅读记录"""
        data = {
            'bookId': book_id,
            'preContentId': pre_content_id
        }
        return self.post('/user/addReadHistory', data=data)

    def add_feedback(self, content):
        """添加反馈"""
        data = {'content': content}
        return self.post('/user/addFeedBack', data=data)

    def list_user_feedback_by_page(self, page=1, page_size=5):
        """分页查询我的反馈列表"""
        params = {
            'page': page,
            'pageSize': page_size
        }
        return self.get('/user/listUserFeedBackByPage', params=params)

    def user_info(self):
        """查询个人信息（与get_user_info可能重复，保留兼容性）"""
        return self.get('/user/userInfo')

    def update_password(self, old_password, new_password1, new_password2):
        """更新密码"""
        data = {
            'oldPassword': old_password,
            'newPassword1': new_password1,
            'newPassword2': new_password2
        }
        return self.post('/user/updatePassword', data=data)

    def list_comment_by_page(self, page=1, page_size=5):
        """分页查询用户书评"""
        params = {
            'page': page,
            'pageSize': page_size
        }
        return self.get('/user/listCommentByPage', params=params)

    def buy_book_index(self, buy_record):
        """购买小说章节"""
        return self.post('/user/buyBookIndex', data=buy_record)

    # 小说相关API
    def search_books(self, keyword=None, **params):
        """搜索小说"""
        return self.get('/api/front/search/books', params)

    def get_book_info(self, book_id):
        """获取小说信息"""
        return self.get(f'/api/front/book/{book_id}')

    def get_book_chapters(self, book_id):
        """获取小说章节列表"""
        return self.get('/api/front/book/chapter/list', {'bookId': book_id})

    # 作者相关API
    def author_register(self, pen_name, phone, chat_account, email, work_direction):
        """作者注册"""
        data = {
            "penName": pen_name,
            "telPhone": phone,
            "chatAccount": chat_account,
            "email": email,
            "workDirection": work_direction
        }
        return self.post('/api/author/register', data)

    def publish_book(self, book_data):
        """发布小说"""
        return self.post('/api/author/book', book_data)

    # AI相关API
    def ai_polish(self, text):
        """AI润色"""
        return self.post('/api/author/ai/polish', params={'text': text})

    def ai_expand(self, text, ratio):
        """AI扩写"""
        return self.post('/api/author/ai/expand', params={'text': text, 'ratio': ratio})

    def ai_continue(self, text, length):
        """AI续写"""
        return self.post('/api/author/ai/continue', params={'text': text, 'length': length})

    def ai_condense(self, text, ratio):
        """AI缩写"""
        return self.post('/api/author/ai/condense', params={'text': text, 'ratio': ratio})

    # 用户评论相关API
    def update_comment(self, comment_id, content):
        """修改评论"""
        return self.put(f'/api/front/user/comment/{comment_id}', params={'content': content})

    def delete_comment(self, comment_id):
        """删除评论"""
        return self.delete(f'/api/front/user/comment/{comment_id}')

    def get_bookshelf_status(self, book_id):
        """查询书架状态"""
        return self.get('/api/front/user/bookshelf_status', params={'bookId': book_id})

    def delete_feedback(self, feedback_id):
        """删除用户反馈"""
        return self.delete(f'/api/front/user/feedback/{feedback_id}')

    # 小说阅读相关API
    def get_pre_chapter_id(self, chapter_id):
        """获取上一章节ID"""
        return self.get(f'/api/front/book/pre_chapter_id/{chapter_id}')

    def get_next_chapter_id(self, chapter_id):
        """获取下一章节ID"""
        return self.get(f'/api/front/book/next_chapter_id/{chapter_id}')

    def get_last_chapter_about(self, book_id):
        """获取小说最新章节相关信息"""
        return self.get('/api/front/book/last_chapter/about', params={'bookId': book_id})

    def get_book_content_about(self, chapter_id):
        """获取小说内容相关信息"""
        return self.get(f'/api/front/book/content/{chapter_id}')

    def get_newest_comments(self, book_id):
        """获取小说最新评论"""
        return self.get('/api/front/book/comment/newest_list', params={'bookId': book_id})

    def add_visit_count(self, book_id):
        """增加小说点击量"""
        return self.post('/api/front/book/visit', params={'bookId': book_id})

    # 作者章节管理API
    def get_book_chapter(self, chapter_id):
        """获取小说章节内容"""
        return self.get(f'/api/author/book/chapter/{chapter_id}')

    def update_book_chapter(self, chapter_id, chapter_data):
        """更新小说章节"""
        return self.put(f'/api/author/book/chapter/{chapter_id}', data=chapter_data)

    def delete_book_chapter(self, chapter_id):
        """删除小说章节"""
        return self.delete(f'/api/author/book/chapter/{chapter_id}')

    def publish_book_chapter(self, book_id, chapter_data):
        """发布小说章节"""
        return self.post(f'/api/author/book/chapter/{book_id}', data=chapter_data)

    def get_book_chapters_list(self, book_id, page_num=1, page_size=10):
        """获取小说章节列表（作者端）"""
        params = {
            'bookId': book_id,
            'pageNum': page_num,
            'pageSize': page_size
        }
        return self.get(f'/api/author/book/chapters/{book_id}', params=params)

    # 资源相关API
    def upload_image(self, file_path):
        """上传图片"""
        # 注意：这里需要处理文件上传，简化实现
        with open(file_path, 'rb') as f:
            files = {'file': f}
            return self.post('/api/front/resource/image', files=files)


# 全局API客户端实例
novel_api = NovelAPIClient()