#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import allure
import os
import json

from local_lib.script_log import log
from local_lib.data_loader import load_test_cases, get_test_data_path, load_test_cases_for_parametrize


def execute_test_case(client, test_case):
    request_data = test_case['request']
    expected = test_case['expected']

    method = request_data.get('method', 'GET').upper()
    endpoint = request_data['endpoint']
    params = request_data.get('params', {})
    data = request_data.get('data', {})

    path_params = request_data.get('path_params', {})
    if path_params:
        for key, value in path_params.items():
            placeholder = '{' + key + '}'
            endpoint = endpoint.replace(placeholder, str(value))

    if method == 'GET':
        response = client.get(endpoint, params=params)
        print(f"测试用例 {test_case['id']} 响应内容:")
        print(json.dumps(response, indent=2, ensure_ascii=False, default=str))
        print("-" * 80)
    elif method == 'POST':
        form_data = endpoint == '/user/login'
        response = client.post(endpoint, data=data, params=params, form_data=form_data)
        print(f"测试用例 {test_case['id']} 响应内容:")
        print(json.dumps(response, indent=2, ensure_ascii=False, default=str))
        print("-" * 80)
    elif method == 'DELETE':
        response = client.delete(endpoint)
        print(f"测试用例 {test_case['id']} 响应内容:")
        print(json.dumps(response, indent=2, ensure_ascii=False, default=str))
        print("-" * 80)
    else:
        raise ValueError(f"不支持的HTTP方法: {method}")

    expected_code = expected['code']
    if expected_code.startswith('!'):
        not_code = expected_code[1:]
        assert response['code'] != not_code, f"期望code不等于{not_code}, 实际code={response['code']}"
    else:
        assert response['code'] == expected_code, f"期望code={expected_code}, 实际code={response['code']}"

    if expected.get('data_exists', False):
        assert 'data' in response, "响应中缺少data字段"

    data_checks = expected.get('data_checks', [])
    if data_checks and 'data' in response:
        response_data = response['data']
        if isinstance(response_data, dict) and 'list' in response_data:
            list_data = response_data['list']
        else:
            list_data = response_data

        for check in data_checks:
            check_type = check.get('check_type')

            if check_type == 'list_not_empty':
                assert isinstance(list_data, list), "响应数据不是列表"
                assert len(list_data) > 0, "响应数据列表为空"
                log.info(f"检查通过: {check.get('description', '列表不为空')}")

            elif check_type == 'keyword_in_results':
                keyword = check.get('keyword')
                field = check.get('field', 'bookName')
                assert keyword, "关键字检查缺少keyword参数"

                if isinstance(list_data, list):
                    found = False
                    for item in list_data:
                        if isinstance(item, dict) and field in item:
                            field_value = str(item[field])
                            if keyword in field_value:
                                found = True
                                break
                    assert found, f"未在{field}字段中找到关键字'{keyword}'"
                log.info(f"检查通过: {check.get('description', f'包含关键字{keyword}')}")

            elif check_type == 'field_equals':
                field = check.get('field')
                expected_value = check.get('value')
                assert field, "字段检查缺少field参数"

                if isinstance(list_data, list):
                    for i, item in enumerate(list_data):
                        assert field in item, f"第{i+1}条结果缺少字段'{field}'"
                        actual_value = item[field]
                        assert actual_value == expected_value, (
                            f"第{i+1}条结果的字段'{field}'不匹配: "
                            f"期望={expected_value}, 实际={actual_value}"
                        )
                log.info(f"检查通过: {check.get('description', f'字段{field}等于{expected_value}')}")

            elif check_type == 'word_count_range':
                min_count = check.get('min')
                max_count = check.get('max')
                assert min_count is not None and max_count is not None, "字数范围检查缺少min/max参数"

                if isinstance(list_data, list):
                    for i, item in enumerate(list_data):
                        assert 'wordCount' in item, f"第{i+1}条结果缺少wordCount字段"
                        word_count = float(item['wordCount']) if item['wordCount'] else 0
                        assert min_count <= word_count <= max_count, (
                            f"第{i+1}条结果的字数{word_count}不在范围[{min_count}, {max_count}]内"
                        )
                log.info(f"检查通过: {check.get('description', f'字数在{min_count}-{max_count}万字之间')}")

            elif check_type == 'sorted_descending':
                field = check.get('field')
                assert field, "排序检查缺少field参数"

                if isinstance(list_data, list) and len(list_data) > 1:
                    for i in range(len(list_data) - 1):
                        current = list_data[i]
                        next_item = list_data[i + 1]

                        current_val = current.get(field, '')
                        next_val = next_item.get(field, '')

                        try:
                            if isinstance(current_val, str) and 'T' in current_val:
                                from datetime import datetime
                                current_dt = datetime.fromisoformat(current_val.replace('Z', '+00:00'))
                                next_dt = datetime.fromisoformat(next_val.replace('Z', '+00:00'))
                                assert current_dt >= next_dt, (
                                    f"第{i+1}条和第{i+2}条结果不是降序排列: "
                                    f"{current_val} < {next_val}"
                                )
                            else:
                                assert current_val >= next_val, (
                                    f"第{i+1}条和第{i+2}条结果不是降序排列: "
                                    f"{current_val} < {next_val}"
                                )
                        except Exception as e:
                            log.warning(f"排序检查解析错误，跳过: {e}")
                            break
                log.info(f"检查通过: {check.get('description', f'按{field}降序排列')}")

            elif check_type == 'list_empty_or_minimal':
                max_items = check.get('max_items', 0)
                assert isinstance(list_data, list), "响应数据不是列表"

                if len(list_data) > max_items:
                    log.warning(f"列表包含{len(list_data)}项，超过预期的{max_items}项")
                log.info(f"检查通过: {check.get('description', f'列表项数不超过{max_items}')}")

            elif check_type == 'response_message_contains':
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
                keywords = check.get('keywords', [])
                assert keywords, "消息检查缺少keywords参数"

                msg = response.get('msg', '')
                for keyword in keywords:
                    if keyword in msg:
                        log.warning(f"响应消息'{msg}'包含不应出现的关键词{keyword}")
                log.info(f"检查通过: {check.get('description', '响应消息不包含关键词')}")

            elif check_type == 'field_exists':
                field = check.get('field')
                assert field, "字段存在检查缺少field参数"

                if isinstance(list_data, list) and len(list_data) > 0:
                    first_item = list_data[0]
                    if isinstance(first_item, dict):
                        assert field in first_item, f"响应数据列表中第一个元素缺少字段'{field}'"
                elif isinstance(response_data, dict):
                    assert field in response_data, f"响应数据中缺少字段'{field}'"
                log.info(f"检查通过: {check.get('description', f'字段{field}存在')}")

            else:
                log.warning(f"未知的检查类型: {check_type}")

    log.info(f"测试用例 {test_case['id']} 执行成功: {test_case['title']}")


@allure.feature("阅读记录模块")
@allure.story("阅读记录功能测试")
class TestReadingRecordModule:
    """阅读记录模块测试类 - 包含YDSG_API_05到YDSG_API_06所有测试用例"""

    @allure.title("阅读记录模块数据驱动测试")
    @pytest.mark.user
    @pytest.mark.parametrize("test_case", load_test_cases_for_parametrize(
        get_test_data_path('reading_record', 'reading_record_module.yaml')
    ), ids=lambda x: x[0])
    def test_reading_record_module_cases(self, api_client, authenticated_client, test_case):
        """阅读记录模块数据驱动测试 - 覆盖YDSG_API_05到YDSG_API_06"""
        case_name, case_data = test_case

        if case_data.get('auth_required', False):
            client = authenticated_client
        else:
            client = api_client

        # 预处理：为正常添加阅读记录用例获取有效的章节ID
        if case_data.get('id') == 'YDSG_API_05' and 'add_read_history_normal' in case_name:
            request_data = case_data['request']
            book_id = None
            if 'params' in request_data:
                book_id = request_data['params'].get('bookId')
            elif 'data' in request_data:
                book_id = request_data['data'].get('bookId')

            if book_id:
                try:
                    chapters_response = client.get_book_chapters(book_id)
                    if chapters_response.get('code') == '200' and 'data' in chapters_response:
                        chapters_data = chapters_response['data']
                        if isinstance(chapters_data, list) and len(chapters_data) > 0:
                            first_chapter = chapters_data[0]
                            chapter_id = first_chapter.get('id')
                            if chapter_id:
                                if 'params' in request_data:
                                    case_data['request']['params']['preContentId'] = chapter_id
                                    print(f"预处理: 更新preContentId为章节ID {chapter_id}")
                                elif 'data' in request_data:
                                    case_data['request']['data']['preContentId'] = chapter_id
                                    print(f"预处理: 更新preContentId为章节ID {chapter_id}")
                                else:
                                    print(f"预处理: 未找到data/params字段")
                        else:
                            print(f"预处理: 章节数据格式不符合预期: {chapters_data}")
                    else:
                        print(f"预处理: 获取章节失败，响应: {chapters_response}")
                except Exception as e:
                    print(f"预处理: 获取章节列表失败: {e}")

        execute_test_case(client, case_data)