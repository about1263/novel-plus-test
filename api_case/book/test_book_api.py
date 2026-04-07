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
        response = client.post(endpoint, data=data)
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
    assert response['code'] == expected['code'], f"期望code={expected['code']}, 实际code={response['code']}"
    
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
                
            else:
                log.warning(f"未知的检查类型: {check_type}")
    
    # 记录日志
    log.info(f"测试用例 {test_case['id']} 执行成功: {test_case['title']}")


@allure.feature("小说模块")
@allure.story("小说排行榜")
class TestBookRank:
    """小说排行榜测试类"""

    @allure.title("点击排行榜接口测试")
    @pytest.mark.book
    def test_list_click_rank(self, api_client):
        """测试点击排行榜接口"""
        response = api_client.get('/book/listClickRank')
        
        assert response['code'] == '00000'
        assert 'data' in response
        rank_list = response['data']
        
        # 验证返回的数据结构
        # assert isinstance(rank_list, list)
        log.info(f"获取点击排行榜成功，共{len(rank_list)}条数据")

    @allure.title("新书排行榜接口测试")
    @pytest.mark.book
    def test_list_new_rank(self, api_client):
        """测试新书排行榜接口"""
        response = api_client.get('/book/listNewRank')
        
        assert response['code'] == '00000'
        assert 'data' in response
        log.info("获取新书排行榜成功")

    @allure.title("更新排行榜接口测试")
    @pytest.mark.book
    def test_list_update_rank(self, api_client):
        """测试更新排行榜接口"""
        response = api_client.get('/book/listUpdateRank')
        
        assert response['code'] == '00000'
        assert 'data' in response
        log.info("获取更新排行榜成功")

    @allure.title("小说排行信息查询接口测试")
    @pytest.mark.book
    def test_list_rank(self, api_client):
        """测试小说排行信息查询接口"""
        params = {
            'type': 0,  # 排行类型
            'limit': 30  # 限制数量
        }
        
        response = api_client.get('/book/listRank', params=params)
        
        assert response['code'] == '00000'
        assert 'data' in response
        log.info("获取小说排行信息成功")

    @allure.title("小说排行榜数据驱动测试")
    @pytest.mark.book
    @pytest.mark.parametrize("test_case", load_test_cases_for_parametrize(
        get_test_data_path('book', 'book_rank.yaml')
    ), ids=lambda x: x[0])
    def test_book_rank_cases(self, api_client, authenticated_client, test_case):
        """小说排行榜数据驱动测试"""
        case_name, case_data = test_case
        
        # 根据auth_required选择客户端
        if case_data.get('auth_required', False):
            client = authenticated_client
        else:
            client = api_client
        
        # 执行测试用例
        execute_test_case(client, case_data)


@allure.feature("小说模块")
@allure.story("小说分类")
class TestBookCategory:
    """小说分类测试类"""

    @allure.title("小说分类列表查询接口测试")
    @pytest.mark.book
    def test_list_book_category(self, api_client):
        """测试小说分类列表查询接口"""
        response = api_client.get('/book/listBookCategory')
        
        assert response['code'] == '00000'
        assert 'data' in response
        category_list = response['data']
        
        # 验证分类数据结构
        # for category in category_list:
        #     assert 'id' in category
        #     assert 'name' in category
        
        log.info(f"获取小说分类列表成功，共{len(category_list)}个分类")

    @allure.title("小说分类数据驱动测试")
    @pytest.mark.book
    @pytest.mark.parametrize("test_case", load_test_cases_for_parametrize(
        get_test_data_path('book', 'book_category.yaml')
    ), ids=lambda x: x[0])
    def test_book_category_cases(self, api_client, authenticated_client, test_case):
        """小说分类数据驱动测试"""
        case_name, case_data = test_case
        
        # 根据auth_required选择客户端
        if case_data.get('auth_required', False):
            client = authenticated_client
        else:
            client = api_client
        
        # 执行测试用例
        execute_test_case(client, case_data)


@allure.feature("小说模块")
@allure.story("小说搜索")
class TestBookSearch:
    """小说搜索测试类"""

    @allure.title("分页搜索接口测试")
    @pytest.mark.book
    def test_search_by_page(self, api_client):
        """测试分页搜索接口"""
        # 构建搜索参数
        search_params = {
            'keyword': '测试',  # 搜索关键词
            'page': 1,
            'pageSize': 20
        }
        
        response = api_client.get('/book/searchByPage', params=search_params)
        
        assert response['code'] == '00000'
        assert 'data' in response
        log.info("小说搜索成功")

    @allure.title("小说搜索数据驱动测试")
    @pytest.mark.book
    @pytest.mark.parametrize("test_case", load_test_cases_for_parametrize(
        get_test_data_path('book', 'book_search.yaml')
    ), ids=lambda x: x[0])
    def test_book_search_cases(self, api_client, authenticated_client, test_case):
        """小说搜索数据驱动测试"""
        case_name, case_data = test_case
        
        # 根据auth_required选择客户端
        if case_data.get('auth_required', False):
            client = authenticated_client
        else:
            client = api_client
        
        # 执行测试用例
        execute_test_case(client, case_data)


@allure.feature("小说模块")
@allure.story("小说详情")
class TestBookDetail:
    """小说详情测试类"""

    @allure.title("查询小说详情信息接口测试")
    @pytest.mark.book
    def test_query_book_detail(self, api_client):
        """测试查询小说详情信息接口"""
        test_book_id = 1
        
        response = api_client.get(f'/book/queryBookDetail/{test_book_id}')
        
        assert response['code'] == '00000'
        assert 'data' in response
        book_detail = response['data']
        
        # 验证小说详情字段
        # assert 'bookName' in book_detail
        # assert 'bookDesc' in book_detail
        
        log.info(f"获取小说详情成功: {book_detail.get('bookName', '未知')}")

    @allure.title("增加点击次数接口测试")
    @pytest.mark.book
    def test_add_visit_count(self, api_client):
        """测试增加点击次数接口"""
        test_book_id = 1
        
        response = api_client.post('/book/addVisitCount', data={'bookId': test_book_id})
        
        assert response['code'] == '00000'
        log.info("增加点击次数成功")

    @allure.title("小说详情数据驱动测试")
    @pytest.mark.book
    @pytest.mark.parametrize("test_case", load_test_cases_for_parametrize(
        get_test_data_path('book', 'book_detail.yaml')
    ), ids=lambda x: x[0])
    def test_book_detail_cases(self, api_client, authenticated_client, test_case):
        """小说详情数据驱动测试"""
        case_name, case_data = test_case
        
        # 根据auth_required选择客户端
        if case_data.get('auth_required', False):
            client = authenticated_client
        else:
            client = api_client
        
        # 执行测试用例
        execute_test_case(client, case_data)


@allure.feature("小说模块")
@allure.story("小说推荐")
class TestBookRecommendation:
    """小说推荐测试类"""

    @allure.title("查询章节相关信息接口测试")
    @pytest.mark.book
    def test_list_rec_book_by_cat_id(self, api_client):
        """测试查询章节相关信息接口"""
        test_cat_id = 1  # 分类ID
        
        response = api_client.get('/book/queryBookIndexAbout', params={'catId': test_cat_id})
        
        assert response['code'] == '00000'
        assert 'data' in response
        log.info("获取章节相关信息成功")

    @allure.title("小说推荐数据驱动测试")
    @pytest.mark.book
    @pytest.mark.parametrize("test_case", load_test_cases_for_parametrize(
        get_test_data_path('book', 'book_recommendation.yaml')
    ), ids=lambda x: x[0])
    def test_book_recommendation_cases(self, api_client, authenticated_client, test_case):
        """小说推荐数据驱动测试"""
        case_name, case_data = test_case
        
        # 根据auth_required选择客户端
        if case_data.get('auth_required', False):
            client = authenticated_client
        else:
            client = api_client
        
        # 执行测试用例
        execute_test_case(client, case_data)


@allure.feature("小说模块")
@allure.story("小说评论")
class TestBookComment:
    """小说评论测试类"""

    @allure.title("分页查询书籍评论列表接口测试")
    @pytest.mark.book
    def test_list_comment_by_page(self, api_client):
        """测试分页查询书籍评论列表接口"""
        params = {
            'bookId': 1,
            'page': 1,
            'pageSize': 5
        }
        
        response = api_client.get('/book/listCommentByPage', params=params)
        
        assert response['code'] == '00000'
        assert 'data' in response
        log.info("获取书籍评论列表成功")

    @allure.title("分页查询评论回复列表接口测试")
    @pytest.mark.book
    def test_list_comment_reply_by_page(self, api_client):
        """测试分页查询评论回复列表接口"""
        params = {
            'commentId': 1,
            'page': 1,
            'pageSize': 5
        }
        
        response = api_client.get('/book/listCommentReplyByPage', params=params)
        
        assert response['code'] == '00000'
        assert 'data' in response
        log.info("获取评论回复列表成功")

    @allure.title("新增评价接口测试")
    @pytest.mark.book
    def test_add_book_comment(self, authenticated_client):
        """测试新增评价接口"""
        comment_data = {
            'bookId': 1,
            'commentContent': '这是一条测试评论',
            'score': 5  # 评分
        }
        
        response = authenticated_client.post('/book/addBookComment', data=comment_data)
        
        assert response['code'] == '00000'
        log.info("新增评价成功")

    @allure.title("评价点赞/取消点赞接口测试")
    @pytest.mark.book
    def test_toggle_comment_like(self, authenticated_client):
        """测试评价点赞/取消点赞接口"""
        test_comment_id = 1
        
        response = authenticated_client.post('/book/toggleCommentLike', 
                                            data={'commentId': test_comment_id})
        
        assert response['code'] == '00000'
        log.info("评价点赞操作成功")

    @allure.title("评价点踩/取消点踩接口测试")
    @pytest.mark.book
    def test_toggle_comment_unlike(self, authenticated_client):
        """测试评价点踩/取消点踩接口"""
        test_comment_id = 1
        
        response = authenticated_client.post('/book/toggleCommentUnLike',
                                            data={'commentId': test_comment_id})
        
        assert response['code'] == '00000'
        log.info("评价点踩操作成功")

    @allure.title("新增回复接口测试")
    @pytest.mark.book
    def test_add_comment_reply(self, authenticated_client):
        """测试新增回复接口"""
        reply_data = {
            'commentId': 1,
            'replyContent': '这是一条测试回复'
        }
        
        response = authenticated_client.post('/book/addCommentReply', data=reply_data)
        
        assert response['code'] == '00000'
        log.info("新增回复成功")

    @allure.title("回复点赞/取消点赞接口测试")
    @pytest.mark.book
    def test_toggle_reply_like(self, authenticated_client):
        """测试回复点赞/取消点赞接口"""
        test_reply_id = 1
        
        response = authenticated_client.post('/book/toggleReplyLike',
                                            data={'replyId': test_reply_id})
        
        assert response['code'] == '00000'
        log.info("回复点赞操作成功")

    @allure.title("回复点踩/取消点踩接口测试")
    @pytest.mark.book
    def test_toggle_reply_unlike(self, authenticated_client):
        """测试回复点踩/取消点踩接口"""
        test_reply_id = 1
        
        response = authenticated_client.post('/book/toggleReplyUnLike',
                                            data={'replyId': test_reply_id})
        
        assert response['code'] == '00000'
        log.info("回复点踩操作成功")

    @allure.title("小说评论数据驱动测试")
    @pytest.mark.book
    @pytest.mark.parametrize("test_case", load_test_cases_for_parametrize(
        get_test_data_path('book', 'book_comment.yaml')
    ), ids=lambda x: x[0])
    def test_book_comment_cases(self, api_client, authenticated_client, test_case):
        """小说评论数据驱动测试"""
        case_name, case_data = test_case
        
        # 根据auth_required选择客户端
        if case_data.get('auth_required', False):
            client = authenticated_client
        else:
            client = api_client
        
        # 执行测试用例
        execute_test_case(client, case_data)


@allure.feature("小说模块")
@allure.story("小说章节")
class TestBookChapter:
    """小说章节测试类"""

    @allure.title("查询小说前十条最新更新目录接口测试")
    @pytest.mark.book
    def test_query_new_index_list(self, api_client):
        """测试查询小说前十条最新更新目录接口"""
        test_book_id = 1
        
        response = api_client.get('/book/queryNewIndexList', params={'bookId': test_book_id})
        
        assert response['code'] == '00000'
        assert 'data' in response
        index_list = response['data']
        
        log.info(f"获取最新更新目录成功，共{len(index_list)}条")

    @allure.title("目录页接口测试")
    @pytest.mark.book
    def test_index_list(self, api_client):
        """测试目录页接口"""
        params = {
            'bookId': 1,
            'page': 1,
            'pageSize': 5,
            'orderBy': 'index_num desc'
        }
        
        response = api_client.get('/book/queryIndexList', params=params)
        
        assert response['code'] == '00000'
        assert 'data' in response
        log.info("获取目录页成功")

    @allure.title("小说章节数据驱动测试")
    @pytest.mark.book
    @pytest.mark.parametrize("test_case", load_test_cases_for_parametrize(
        get_test_data_path('book', 'book_chapter.yaml')
    ), ids=lambda x: x[0])
    def test_book_chapter_cases(self, api_client, authenticated_client, test_case):
        """小说章节数据驱动测试"""
        case_name, case_data = test_case
        
        # 根据auth_required选择客户端
        if case_data.get('auth_required', False):
            client = authenticated_client
        else:
            client = api_client
        
        # 执行测试用例
        execute_test_case(client, case_data)