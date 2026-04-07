#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import os
from faker import Faker

from local_lib.api_client import NovelAPIClient
from pro_config.project_config import test_users, novel_api_urls


# 创建Faker实例用于生成测试数据
fake = Faker('zh_CN')


def pytest_addoption(parser):
    """添加命令行选项"""
    parser.addoption("--env", action="store", default="lane", 
                    help="测试环境: online 或 lane")
    parser.addoption("--user-type", action="store", default="reader",
                    help="用户类型: admin, author, reader")


@pytest.fixture(scope="session")
def env(request):
    """测试环境fixture"""
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def api_client(env):
    """API客户端fixture"""
    client = NovelAPIClient(env)
    return client


@pytest.fixture(scope="function")
def authenticated_client(api_client, request):
    """已认证的API客户端fixture"""
    user_type = request.config.getoption("--user-type")
    user_info = test_users.get(user_type, test_users['reader'])
    
    # 登录获取token
    try:
        response = api_client.user_login(user_info['username'], user_info['password'])
        # 用户登录接口返回200表示成功，作者接口返回00000
        if response.get('code') in ['200', '00000']:
            # 检查响应中是否有token字段
            if 'data' in response and 'token' in response['data']:
                api_client.set_token(response['data']['token'])
            else:
                pytest.skip(f"登录响应中缺少token字段")
        else:
            pytest.skip(f"登录失败，返回code: {response.get('code')}")
    except Exception as e:
        pytest.skip(f"登录失败: {e}")
    
    yield api_client
    
    # 测试结束后清理token
    api_client.set_token(None)


@pytest.fixture(scope="function")
def test_user_data():
    """测试用户数据fixture"""
    return {
        'username': fake.user_name(),
        'password': 'Test123456',
        'phone': fake.phone_number(),
        'nickname': fake.name()
    }


@pytest.fixture(scope="function")
def test_book_data():
    """测试小说数据fixture"""
    return {
        'book_name': fake.catch_phrase(),
        'book_desc': fake.text(max_nb_chars=200),
        'category_id': 1,  # 男频
        'category_name': '玄幻',
        'work_direction': 0,  # 男频
        'is_vip': 0  # 免费
    }


@pytest.fixture(scope="function")
def test_chapter_data():
    """测试章节数据fixture"""
    return {
        'chapter_name': f'第{fake.random_int(1, 100)}章 {fake.word()}',
        'chapter_content': fake.text(max_nb_chars=1000),
        'is_vip': 0
    }


# 自定义标记
novel = pytest.mark.novel
user = pytest.mark.user
book = pytest.mark.book
author = pytest.mark.author
search = pytest.mark.search
news = pytest.mark.news
home = pytest.mark.home
resource = pytest.mark.resource
ai = pytest.mark.ai
cache = pytest.mark.cache
file = pytest.mark.file
friendLink = pytest.mark.friendLink
pay = pytest.mark.pay
common = pytest.mark.common
front = pytest.mark.front
admin = pytest.mark.admin


# 钩子函数
def pytest_collection_modifyitems(config, items):
    """修改收集的测试项"""
    # 可以根据环境或其他条件跳过某些测试
    env = config.getoption("--env")
    
    for item in items:
        # 为所有测试项添加novel标记
        item.add_marker(pytest.mark.novel)