#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import allure
import os
import json

from local_lib.script_log import log
from local_lib.data_loader import load_test_cases, get_test_data_path, load_test_cases_for_parametrize


def execute_test_case(client, test_case):
    """
    执行单个测试用例
    
    Args:
        client: API客户端（api_client或authenticated_client）
        test_case: 测试用例数据字典
    """
    request_data = test_case['request']
    expected = test_case['expected']
    
    method = request_data.get('method', 'GET').upper()
    endpoint = request_data['endpoint']
    params = request_data.get('params', {})
    data = request_data.get('data', {})
    
    # 处理路径参数
    path_params = request_data.get('path_params', {})
    if path_params:
        for key, value in path_params.items():
            placeholder = '{' + key + '}'
            endpoint = endpoint.replace(placeholder, str(value))
    
    # 执行请求
    if method == 'GET':
        response = client.get(endpoint, params=params)
        # 打印响应内容
        print(f"测试用例 {test_case['id']} 响应内容:")
        print(json.dumps(response, indent=2, ensure_ascii=False, default=str))
        print("-" * 80)
    elif method == 'POST':
        # 对于登录接口，使用form-data格式
        form_data = endpoint == '/user/login'
        response = client.post(endpoint, data=data, form_data=form_data)
        # 打印响应内容
        print(f"测试用例 {test_case['id']} 响应内容:")
        print(json.dumps(response, indent=2, ensure_ascii=False, default=str))
        print("-" * 80)
    elif method == 'DELETE':
        response = client.delete(endpoint)
        # 打印响应内容
        print(f"测试用例 {test_case['id']} 响应内容:")
        print(json.dumps(response, indent=2, ensure_ascii=False, default=str))
        print("-" * 80)
    else:
        raise ValueError(f"不支持的HTTP方法: {method}")
    
    # 验证响应
    expected_code = expected['code']
    if expected_code.startswith('!'):
        # 期望code不等于某个值
        not_code = expected_code[1:]
        assert response['code'] != not_code, f"期望code不等于{not_code}, 实际code={response['code']}"
    else:
        assert response['code'] == expected_code, f"期望code={expected_code}, 实际code={response['code']}"
    
    if expected.get('data_exists', False):
        assert 'data' in response, "响应中缺少data字段"
    
    # 执行额外的数据检查
    data_checks = expected.get('data_checks', [])
    if data_checks and 'data' in response:
        response_data = response['data']
        
        for check in data_checks:
            check_type = check.get('check_type')
            
            if check_type == 'list_not_empty':
                # 检查列表不为空
                assert isinstance(response_data, list), "响应数据不是列表"
                assert len(response_data) > 0, "响应数据列表为空"
                log.info(f"检查通过: {check.get('description', '列表不为空')}")
                
            elif check_type == 'keyword_in_results':
                # 检查结果中包含关键字
                keyword = check.get('keyword')
                field = check.get('field', 'bookName')
                assert keyword, "关键字检查缺少keyword参数"
                
                if isinstance(response_data, list):
                    found = False
                    for item in response_data:
                        if isinstance(item, dict) and field in item:
                            field_value = str(item[field])
                            if keyword in field_value:
                                found = True
                                break
                    assert found, f"未在{field}字段中找到关键字'{keyword}'"
                log.info(f"检查通过: {check.get('description', f'包含关键字{keyword}')}")
                
            elif check_type == 'field_equals':
                # 检查字段等于特定值
                field = check.get('field')
                expected_value = check.get('value')
                assert field, "字段检查缺少field参数"
                
                if isinstance(response_data, list):
                    for i, item in enumerate(response_data):
                        assert field in item, f"第{i+1}条结果缺少字段'{field}'"
                        actual_value = item[field]
                        assert actual_value == expected_value, (
                            f"第{i+1}条结果的字段'{field}'不匹配: "
                            f"期望={expected_value}, 实际={actual_value}"
                        )
                log.info(f"检查通过: {check.get('description', f'字段{field}等于{expected_value}')}")
                
            elif check_type == 'word_count_range':
                # 检查字数范围（假设wordCount字段以万字为单位）
                min_count = check.get('min')
                max_count = check.get('max')
                assert min_count is not None and max_count is not None, "字数范围检查缺少min/max参数"
                
                if isinstance(response_data, list):
                    for i, item in enumerate(response_data):
                        assert 'wordCount' in item, f"第{i+1}条结果缺少wordCount字段"
                        word_count = float(item['wordCount']) if item['wordCount'] else 0
                        assert min_count <= word_count <= max_count, (
                            f"第{i+1}条结果的字数{word_count}不在范围[{min_count}, {max_count}]内"
                        )
                log.info(f"检查通过: {check.get('description', f'字数在{min_count}-{max_count}万字之间')}")
                
            elif check_type == 'sorted_descending':
                # 检查按字段降序排序
                field = check.get('field')
                assert field, "排序检查缺少field参数"
                
                if isinstance(response_data, list) and len(response_data) > 1:
                    for i in range(len(response_data) - 1):
                        current = response_data[i]
                        next_item = response_data[i + 1]
                        
                        # 处理时间戳字符串的比较
                        current_val = current.get(field, '')
                        next_val = next_item.get(field, '')
                        
                        # 尝试转换为可比较的格式（如果是时间戳）
                        try:
                            if isinstance(current_val, str) and 'T' in current_val:
                                # 假设是ISO时间格式
                                from datetime import datetime
                                current_dt = datetime.fromisoformat(current_val.replace('Z', '+00:00'))
                                next_dt = datetime.fromisoformat(next_val.replace('Z', '+00:00'))
                                assert current_dt >= next_dt, (
                                    f"第{i+1}条和第{i+2}条结果不是降序排列: "
                                    f"{current_val} < {next_val}"
                                )
                            else:
                                # 普通值比较
                                assert current_val >= next_val, (
                                    f"第{i+1}条和第{i+2}条结果不是降序排列: "
                                    f"{current_val} < {next_val}"
                                )
                        except Exception as e:
                            log.warning(f"排序检查解析错误，跳过: {e}")
                            break
                log.info(f"检查通过: {check.get('description', f'按{field}降序排列')}")
                
            elif check_type == 'list_empty_or_minimal':
                # 检查列表为空或极少数目
                max_items = check.get('max_items', 0)
                assert isinstance(response_data, list), "响应数据不是列表"
                
                if len(response_data) > max_items:
                    log.warning(f"列表包含{len(response_data)}项，超过预期的{max_items}项")
                log.info(f"检查通过: {check.get('description', f'列表项数不超过{max_items}')}")
                
            elif check_type == 'response_message_contains':
                # 检查响应消息包含关键词
                keywords = check.get('keywords', [])
                assert keywords, "消息检查缺少keywords参数"
                
                msg = response.get('msg', '')
                found = False
                for keyword in keywords:
                    if keyword in msg:
                        found = True
                        break
                
                if not found:
                    log.warning(f"响应消息'{msg}'不包含关键词{keywords}")
                else:
                    log.info(f"检查通过: {check.get('description', '响应消息包含关键词')}")
                    
            elif check_type == 'response_message_not_contains':
                # 检查响应消息不包含关键词
                keywords = check.get('keywords', [])
                assert keywords, "消息检查缺少keywords参数"
                
                msg = response.get('msg', '')
                for keyword in keywords:
                    if keyword in msg:
                        log.warning(f"响应消息'{msg}'包含不应出现的关键词{keyword}")
                log.info(f"检查通过: {check.get('description', '响应消息不包含关键词')}")
                
            elif check_type == 'field_exists':
                # 检查字段是否存在
                field = check.get('field')
                assert field, "字段存在检查缺少field参数"
                
                if isinstance(response_data, dict):
                    assert field in response_data, f"响应数据中缺少字段'{field}'"
                elif isinstance(response_data, list) and len(response_data) > 0:
                    # 检查列表中的第一个元素
                    first_item = response_data[0]
                    if isinstance(first_item, dict):
                        assert field in first_item, f"响应数据列表中第一个元素缺少字段'{field}'"
                log.info(f"检查通过: {check.get('description', f'字段{field}存在')}")
                
            else:
                log.warning(f"未知的检查类型: {check_type}")
    
    # 记录日志
    log.info(f"测试用例 {test_case['id']} 执行成功: {test_case['title']}")


@allure.feature("用户模块")
@allure.story("用户登录")
class TestUserLogin:
    """用户登录测试类"""

    @allure.title("用户登录数据驱动测试")
    @pytest.mark.user
    @pytest.mark.parametrize("test_case", load_test_cases_for_parametrize(
        get_test_data_path('user', 'user_login.yaml')
    ), ids=lambda x: x[0])
    def test_user_login_cases(self, api_client, authenticated_client, test_case):
        """用户登录数据驱动测试"""
        case_name, case_data = test_case
        
        # 根据auth_required选择客户端
        if case_data.get('auth_required', False):
            client = authenticated_client
        else:
            client = api_client
        
        # 执行测试用例
        execute_test_case(client, case_data)


@allure.feature("用户模块")
@allure.story("用户令牌管理")
class TestUserToken:
    """用户令牌管理测试类"""

    @allure.title("用户令牌管理数据驱动测试")
    @pytest.mark.user
    @pytest.mark.parametrize("test_case", load_test_cases_for_parametrize(
        get_test_data_path('user', 'user_token.yaml')
    ), ids=lambda x: x[0])
    def test_user_token_cases(self, api_client, authenticated_client, test_case):
        """用户令牌管理数据驱动测试"""
        case_name, case_data = test_case
        
        # 根据auth_required选择客户端
        if case_data.get('auth_required', False):
            client = authenticated_client
        else:
            client = api_client
        
        # 执行测试用例
        execute_test_case(client, case_data)


@allure.feature("用户模块")
@allure.story("用户书架管理")
class TestUserBookshelf:
    """用户书架管理测试类"""

    @allure.title("用户书架管理数据驱动测试")
    @pytest.mark.user
    @pytest.mark.parametrize("test_case", load_test_cases_for_parametrize(
        get_test_data_path('user', 'user_bookshelf.yaml')
    ), ids=lambda x: x[0])
    def test_user_bookshelf_cases(self, api_client, authenticated_client, test_case):
        """用户书架管理数据驱动测试"""
        case_name, case_data = test_case
        
        # 根据auth_required选择客户端
        if case_data.get('auth_required', False):
            client = authenticated_client
        else:
            client = api_client
        
        # 执行测试用例
        execute_test_case(client, case_data)


@allure.feature("用户模块")
@allure.story("用户阅读记录")
class TestUserReadHistory:
    """用户阅读记录测试类"""

    @allure.title("用户阅读记录数据驱动测试")
    @pytest.mark.user
    @pytest.mark.parametrize("test_case", load_test_cases_for_parametrize(
        get_test_data_path('user', 'user_read_history.yaml')
    ), ids=lambda x: x[0])
    def test_user_read_history_cases(self, api_client, authenticated_client, test_case):
        """用户阅读记录数据驱动测试"""
        case_name, case_data = test_case
        
        # 根据auth_required选择客户端
        if case_data.get('auth_required', False):
            client = authenticated_client
        else:
            client = api_client
        
        # 执行测试用例
        execute_test_case(client, case_data)


@allure.feature("用户模块")
@allure.story("用户反馈管理")
class TestUserFeedback:
    """用户反馈管理测试类"""

    @allure.title("用户反馈管理数据驱动测试")
    @pytest.mark.user
    @pytest.mark.parametrize("test_case", load_test_cases_for_parametrize(
        get_test_data_path('user', 'user_feedback.yaml')
    ), ids=lambda x: x[0])
    def test_user_feedback_cases(self, api_client, authenticated_client, test_case):
        """用户反馈管理数据驱动测试"""
        case_name, case_data = test_case
        
        # 根据auth_required选择客户端
        if case_data.get('auth_required', False):
            client = authenticated_client
        else:
            client = api_client
        
        # 执行测试用例
        execute_test_case(client, case_data)


@allure.feature("用户模块")
@allure.story("用户评论管理")
class TestUserComment:
    """用户评论管理测试类"""

    @allure.title("用户评论管理数据驱动测试")
    @pytest.mark.user
    @pytest.mark.parametrize("test_case", load_test_cases_for_parametrize(
        get_test_data_path('user', 'user_comment.yaml')
    ), ids=lambda x: x[0])
    def test_user_comment_cases(self, api_client, authenticated_client, test_case):
        """用户评论管理数据驱动测试"""
        case_name, case_data = test_case
        
        # 根据auth_required选择客户端
        if case_data.get('auth_required', False):
            client = authenticated_client
        else:
            client = api_client
        
        # 执行测试用例
        execute_test_case(client, case_data)


@allure.feature("用户模块")
@allure.story("章节购买")
class TestUserBuyChapter:
    """章节购买测试类"""

    @allure.title("章节购买数据驱动测试")
    @pytest.mark.user
    @pytest.mark.parametrize("test_case", load_test_cases_for_parametrize(
        get_test_data_path('user', 'user_buy_chapter.yaml')
    ), ids=lambda x: x[0])
    def test_user_buy_chapter_cases(self, api_client, authenticated_client, test_case):
        """章节购买数据驱动测试"""
        case_name, case_data = test_case
        
        # 如果用例标记为skip，则跳过
        if case_data.get('skip', False):
            pytest.skip("此测试需要虚拟支付环境，已跳过")
        
        # 根据auth_required选择客户端
        if case_data.get('auth_required', False):
            client = authenticated_client
        else:
            client = api_client
        
        # 执行测试用例
        execute_test_case(client, case_data)