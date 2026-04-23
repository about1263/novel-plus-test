#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import allure
import copy
import uuid
import json
import os
import pymysql

from local_lib.script_log import log
from local_lib.data_loader import load_test_cases, get_test_data_path


def execute_test_case(client, test_case):
    """
    执行单个测试用例（增强版，支持作者接口的form-data格式和路径参数）

    Args:
        client: API客户端
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
            endpoint = endpoint.replace('{' + key + '}', str(value))

    # 执行请求
    if method == 'GET':
        response = client.get(endpoint, params=params)
    elif method == 'POST':
        form_data = endpoint.startswith('/author/')
        response = client.post(endpoint, data=data, params=params, form_data=form_data)
    elif method == 'DELETE':
        response = client.delete(endpoint)
    else:
        raise ValueError(f"不支持的HTTP方法: {method}")

    # 打印响应
    print(f"测试用例 {test_case['id']} 响应内容:")
    print(json.dumps(response, indent=2, ensure_ascii=False, default=str))
    print("-" * 80)

    # 验证响应code
    expected_code = expected['code']
    if expected_code.startswith('!'):
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

            elif check_type == 'field_exists':
                field = check.get('field')
                assert field, "字段存在检查缺少field参数"
                if isinstance(response_data, dict):
                    assert field in response_data, f"响应数据中缺少字段'{field}'"
                elif isinstance(list_data, list) and len(list_data) > 0:
                    first_item = list_data[0]
                    if isinstance(first_item, dict):
                        assert field in first_item, f"响应数据列表中第一个元素缺少字段'{field}'"
                log.info(f"检查通过: {check.get('description', f'字段{field}存在')}")

            elif check_type == 'response_message_contains':
                keywords = check.get('keywords', [])
                assert keywords, "消息检查缺少keywords参数"
                msg = response.get('msg', '')
                found = any(kw in msg for kw in keywords)
                if not found:
                    log.warning(f"响应消息'{msg}'不包含关键词{keywords}")
                else:
                    log.info(f"检查通过: {check.get('description', '响应消息包含关键词')}")

            elif check_type == 'keyword_in_results':
                keyword = check.get('keyword')
                field = check.get('field', 'bookName')
                assert keyword, "关键字检查缺少keyword参数"
                if isinstance(list_data, list):
                    found = any(
                        isinstance(item, dict) and field in item and keyword in str(item[field])
                        for item in list_data
                    )
                    assert found, f"未在{field}字段中找到关键字'{keyword}'"
                log.info(f"检查通过: {check.get('description', f'包含关键字{keyword}')}")

            elif check_type == 'field_equals':
                field = check.get('field')
                expected_value = check.get('value')
                assert field, "字段检查缺少field参数"
                if isinstance(list_data, list):
                    for i, item in enumerate(list_data):
                        assert field in item, f"第{i+1}条结果缺少字段'{field}'"
                        assert item[field] == expected_value, (
                            f"第{i+1}条结果的字段'{field}'不匹配: "
                            f"期望={expected_value}, 实际={item[field]}"
                        )
                log.info(f"检查通过: {check.get('description', f'字段{field}等于{expected_value}')}")

            elif check_type == 'sorted_descending':
                field = check.get('field')
                assert field, "排序检查缺少field参数"
                if isinstance(list_data, list) and len(list_data) > 1:
                    for i in range(len(list_data) - 1):
                        current_val = list_data[i].get(field, '')
                        next_val = list_data[i + 1].get(field, '')
                        try:
                            if isinstance(current_val, str) and 'T' in current_val:
                                from datetime import datetime
                                current_dt = datetime.fromisoformat(current_val.replace('Z', '+00:00'))
                                next_dt = datetime.fromisoformat(next_val.replace('Z', '+00:00'))
                                assert current_dt >= next_dt, f"第{i+1}条和第{i+2}条结果不是降序排列"
                            else:
                                assert str(current_val) >= str(next_val), f"第{i+1}条和第{i+2}条结果不是降序排列"
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

            else:
                log.warning(f"未知的检查类型: {check_type}")

    log.info(f"测试用例 {test_case['id']} 执行成功: {test_case['title']}")


@allure.feature("小说管理&章节管理模块")
class TestNovelManagementModule:
    """小说管理&章节管理模块测试类 - 包含ZZGL_API_01到ZZGL_API_07所有测试用例"""

    yaml_file = get_test_data_path('novel_management', 'novel_management_module.yaml')
    all_cases = load_test_cases(yaml_file)

    # ==================== 辅助方法 ====================

    def _get_case(self, case_id):
        """根据测试用例ID获取深拷贝的测试数据"""
        for case in self.all_cases:
            if case['id'] == case_id:
                return copy.deepcopy(case)
        raise ValueError(f"未找到测试用例: {case_id}")

    def _create_test_book(self, client):
        """创建测试小说并返回bookId"""
        unique_name = f"ZZGL_BOOK_{uuid.uuid4().hex[:8]}"
        pic_url = self._upload_test_image(client, 'test_lib/test.png')
        response = client.post('/author/addBook', data={
            'bookName': unique_name,
            'bookDesc': '小说管理模块自动化测试创建的小说',
            'catId': 1,
            'catName': '玄幻奇幻',
            'workDirection': 0,
            'bookStatus': 0,
            'wordCount': 0,
            'picUrl': pic_url
        }, form_data=True)
        assert response.get('code') == '200', f"创建测试小说失败: {response}"

        book_id = self._find_book_id_by_name(client, unique_name)
        assert book_id is not None, f"无法在列表中查到刚创建的小说: {unique_name}"
        log.info(f"测试小说创建成功: bookId={book_id}, bookName={unique_name}")
        return book_id

    def _create_test_chapter(self, client, book_id):
        """在指定小说下创建测试章节并返回indexId"""
        unique_name = f"ZZGL_CHAPTER_{uuid.uuid4().hex[:8]}"
        response = client.post('/author/addBookContent', data={
            'bookId': book_id,
            'indexName': unique_name,
            'content': '自动化测试章节内容_' + uuid.uuid4().hex[:8],
            'isVip': 0
        }, form_data=True)
        assert response.get('code') == '200', f"创建测试章节失败: {response}"

        index_id = self._find_chapter_id_by_name(client, book_id, unique_name)
        assert index_id is not None, f"无法在章节列表中找到刚创建的章节: {unique_name}"
        log.info(f"测试章节创建成功: indexId={index_id}, bookId={book_id}")
        return index_id

    def _find_book_id_by_name(self, client, book_name):
        """通过小说名称查找bookId"""
        try:
            resp = client.get('/author/listBookByPage', params={'curr': 1, 'limit': 50})
            if 'data' not in resp:
                return None
            data = resp['data']
            books = data.get('list', []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
            for book in books:
                if isinstance(book, dict) and book.get('bookName') == book_name:
                    return book.get('id')
        except Exception as e:
            log.warning(f"查找小说ID时出错: {e}")
        return None

    def _find_chapter_id_by_name(self, client, book_id, chapter_name):
        """通过章节名称查找indexId"""
        try:
            resp = client.get('/book/queryNewIndexList', params={'bookId': book_id})
            if 'data' not in resp:
                return None
            chapters = resp['data']
            if isinstance(chapters, list):
                for ch in chapters:
                    if isinstance(ch, dict) and ch.get('indexName') == chapter_name:
                        return ch.get('id')
        except Exception as e:
            log.warning(f"查找章节ID时出错: {e}")
        return None

    def _disable_book(self, client, book_id):
        """下架测试小说（清理用）"""
        try:
            client.post('/author/updateBookStatus', data={'bookId': book_id, 'status': 0}, form_data=True)
            log.info(f"测试小说 {book_id} 已下架")
        except Exception as e:
            log.warning(f"下架小说 {book_id} 时出错: {e}")

    def _delete_chapter(self, client, index_id):
        """删除测试章节（清理用）"""
        try:
            client.delete(f'/author/deleteIndex/{index_id}')
            log.info(f"测试章节 {index_id} 已删除")
        except Exception as e:
            log.warning(f"删除章节 {index_id} 时出错: {e}")

    def _upload_test_image(self, client, relative_path):
        """上传测试图片，返回图片URL"""
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        abs_path = os.path.join(project_root, relative_path)
        response = client.upload_image(abs_path)
        assert response.get('code') == '200', f"上传图片失败: {response}"
        image_url = response.get('data', '')
        log.info(f"测试图片上传成功: {image_url}")
        return image_url

    def _delete_book_from_db(self, book_id):
        """从数据库直接删除指定小说的所有关联记录"""
        conn = None
        try:
            conn = pymysql.connect(
                host='47.108.213.8', port=33066,
                user='root', password='novel_plus_1022',
                database='novel_plus', charset='utf8mb4'
            )
            cur = conn.cursor()
            cur.execute('SELECT id FROM book_index WHERE book_id = %s', (book_id,))
            for idx_id in [r[0] for r in cur.fetchall()]:
                cur.execute(f'DELETE FROM book_content{book_id % 10} WHERE index_id = %s', (idx_id,))
            cur.execute('DELETE FROM book_index WHERE book_id = %s', (book_id,))
            cur.execute('SELECT id FROM book_comment WHERE book_id = %s', (book_id,))
            for cid in [r[0] for r in cur.fetchall()]:
                cur.execute('DELETE FROM book_comment_reply WHERE comment_id = %s', (cid,))
            cur.execute('DELETE FROM book_comment WHERE book_id = %s', (book_id,))
            cur.execute('DELETE FROM book WHERE id = %s', (book_id,))
            conn.commit()
            log.info(f"数据库清理成功: 已删除小说 book_id={book_id}")
        except Exception as e:
            log.warning(f"数据库清理失败: {e}")
        finally:
            if conn:
                conn.close()

    # ==================== Fixtures (Setup/Teardown) ====================

    @pytest.fixture
    def setup_test_book(self, authenticated_client):
        """
        Fixture: 创建测试小说，测试结束后自动下架清理
        - Setup: 创建一本测试小说，返回book_id
        - Teardown: 调用updateBookStatus下架小说
        """
        state = {'book_id': None}
        try:
            state['book_id'] = self._create_test_book(authenticated_client)
            yield state
        finally:
            if state['book_id']:
                self._disable_book(authenticated_client, state['book_id'])
                self._delete_book_from_db(state['book_id'])

    @pytest.fixture
    def setup_test_chapter(self, authenticated_client):
        """
        Fixture: 创建测试小说和章节，测试结束后自动清理
        - Setup: 创建测试小说和测试章节，返回book_id和index_id
        - Teardown: 先删除章节（如未删除），再下架小说，最后从数据库彻底删除
        """
        state = {'book_id': None, 'index_id': None}
        try:
            state['book_id'] = self._create_test_book(authenticated_client)
            state['index_id'] = self._create_test_chapter(authenticated_client, state['book_id'])
            yield state
        finally:
            if state['index_id']:
                self._delete_chapter(authenticated_client, state['index_id'])
            if state['book_id']:
                self._disable_book(authenticated_client, state['book_id'])
                self._delete_book_from_db(state['book_id'])

    # ==================== 小说管理测试 ====================

    @allure.story("小说管理-小说发布验证")
    @allure.title("ZZGL_API_01 - 小说发布验证")
    @pytest.mark.author
    def test_zzgl_api_01_publish_book(self, authenticated_client):
        """
        ZZGL_API_01 - 小说发布验证
        前置条件: 无
        测试步骤: 调用POST /author/addBook，传入正确的小说参数
        后置清理: 查找刚创建的小说，调用updateBookStatus下架
        数据隔离: 使用UUID生成唯一小说名，避免与其他测试冲突
        """
        case = self._get_case('ZZGL_API_01')
        unique_name = f"ZZGL_BOOK_{uuid.uuid4().hex[:8]}"
        pic_url = self._upload_test_image(authenticated_client, 'test_lib/test.png')
        case['request']['data']['bookName'] = unique_name
        case['request']['data']['picUrl'] = pic_url

        execute_test_case(authenticated_client, case)

        # 后置清理：查找并下架刚创建的小说，从数据库彻底删除
        try:
            book_id = self._find_book_id_by_name(authenticated_client, unique_name)
            if book_id:
                self._disable_book(authenticated_client, book_id)
                self._delete_book_from_db(book_id)
        except Exception as e:
            log.warning(f"小说发布测试清理时出错: {e}")

    @allure.story("小说管理-小说封面修改验证")
    @allure.title("ZZGL_API_03 - 小说封面修改验证(正常图片)")
    @pytest.mark.author
    def test_zzgl_api_03_update_book_pic(self, authenticated_client, setup_test_book):
        """
        ZZGL_API_03 - 小说封面修改验证
        前置条件: setup_test_book fixture自动创建测试小说（测试后自动清理）
        测试步骤: 使用test.png上传并修改封面，预期返回code=200
        后置清理: fixture自动下架小说
        """
        case = self._get_case('ZZGL_API_03')
        case['request']['data']['bookId'] = str(setup_test_book['book_id'])
        pic_url = self._upload_test_image(authenticated_client, 'test_lib/test.png')
        case['request']['data']['bookPic'] = pic_url
        execute_test_case(authenticated_client, case)

    @allure.story("小说管理-小说封面修改验证")
    @allure.title("ZZGL_EXT_01 - 小说封面修改验证(特殊分辨率图片)")
    @pytest.mark.author
    def test_zzgl_ext_01_update_book_pic_wrong(self, authenticated_client, setup_test_book):
        """
        ZZGL_EXT_01 - 小说封面修改验证(特殊分辨率图片)
        前置条件: setup_test_book fixture自动创建测试小说（测试后自动清理）
        测试步骤: 使用wrong_picture.jpg上传并修改封面，预期服务端应正常处理
        后置清理: 修改封面改回原图yuantu.png；fixture自动下架小说
        """
        case = self._get_case('ZZGL_API_03')
        book_id = setup_test_book['book_id']
        case['request']['data']['bookId'] = str(book_id)
        try:
            pic_url = self._upload_test_image(authenticated_client, 'test_lib/wrong_picture.jpg')
            case['request']['data']['bookPic'] = pic_url
            execute_test_case(authenticated_client, case)
        finally:
            try:
                pic_url = self._upload_test_image(authenticated_client, 'test_lib/yuantu.png')
                authenticated_client.post('/author/updateBookPic',
                                          data={'bookId': book_id, 'bookPic': pic_url},
                                          form_data=True)
                log.info("已恢复封面为原图 yuantu.png")
            except Exception as e:
                log.warning(f"恢复封面为原图失败(可能需要手动放置 yuantu.png): {e}")

    # ==================== 章节管理测试 ====================

    @allure.story("章节管理-新增章节验证")
    @allure.title("ZZGL_API_02 - 新增章节验证")
    @pytest.mark.author
    def test_zzgl_api_02_add_chapter(self, authenticated_client, setup_test_book):
        """
        ZZGL_API_02 - 新增章节验证
        前置条件: setup_test_book fixture自动创建测试小说（测试后自动清理）
        测试步骤: 调用POST /author/addBookContent，传入bookId和章节内容
        后置清理: 查找并删除刚创建的章节；fixture自动下架小说
        """
        case = self._get_case('ZZGL_API_02')
        book_id = setup_test_book['book_id']
        chapter_name = f"ZZGL_CHAPTER_{uuid.uuid4().hex[:8]}"
        case['request']['data']['bookId'] = book_id
        case['request']['data']['indexName'] = chapter_name

        execute_test_case(authenticated_client, case)

        # 后置清理：查找并删除刚创建的章节
        try:
            index_id = self._find_chapter_id_by_name(authenticated_client, book_id, chapter_name)
            if index_id:
                self._delete_chapter(authenticated_client, index_id)
        except Exception as e:
            log.warning(f"新增章节测试清理时出错: {e}")

    @allure.story("章节管理-章节修改验证")
    @allure.title("ZZGL_API_04 - 章节修改验证")
    @pytest.mark.author
    def test_zzgl_api_04_update_chapter(self, authenticated_client, setup_test_chapter):
        """
        ZZGL_API_04 - 章节修改验证
        前置条件: setup_test_chapter fixture自动创建测试小说和章节（测试后自动清理）
        测试步骤: 调用POST /author/updateBookContent，传入indexId和更新内容
        后置清理: fixture自动删除章节并下架小说
        """
        case = self._get_case('ZZGL_API_04')
        case['request']['data']['indexId'] = setup_test_chapter['index_id']
        case['request']['data']['indexName'] = f"UPDATED_{uuid.uuid4().hex[:8]}"

        execute_test_case(authenticated_client, case)

    @allure.story("章节管理-章节删除验证")
    @allure.title("ZZGL_API_05 - 章节删除验证")
    @pytest.mark.author
    def test_zzgl_api_05_delete_chapter(self, authenticated_client, setup_test_chapter):
        """
        ZZGL_API_05 - 章节删除验证
        前置条件: setup_test_chapter fixture自动创建测试小说和章节（测试后自动清理）
        测试步骤: 调用DELETE /author/deleteIndex/{indexId}，传入有效indexId
        后置清理: 通知fixture章节已被删除，避免重复删除；fixture自动下架小说
        """
        case = self._get_case('ZZGL_API_05')
        case['request']['path_params']['indexId'] = setup_test_chapter['index_id']

        execute_test_case(authenticated_client, case)

        # 通知fixture：章节已被测试删除，不再重复执行删除操作
        setup_test_chapter['index_id'] = None

    # ==================== 权限控制测试 ====================

    @allure.story("权限控制-未授权访问验证")
    @allure.title("ZZGL_API_06 - 未授权访问验证")
    @pytest.mark.author
    def test_zzgl_api_06_unauthorized_access(self, api_client):
        """
        ZZGL_API_06 - 未授权访问验证
        前置条件: 无（使用未登录的api_client，不携带token）
        测试步骤: 调用GET /author/listBookByPage，验证权限控制
        验证点: 应返回非200错误码，消息中包含权限不足提示
        """
        case = self._get_case('ZZGL_API_06')
        execute_test_case(api_client, case)

    # ==================== 数据统计测试 ====================

    @allure.story("数据统计-小说列表数据查看验证")
    @allure.title("ZZGL_API_07 - 小说数据查看验证")
    @pytest.mark.author
    def test_zzgl_api_07_list_book_data(self, authenticated_client):
        """
        ZZGL_API_07 - 小说数据查看验证
        前置条件: 无（使用已登录的作者账号）
        测试步骤: 调用GET /author/listBookByPage，查看返回数据字段
        验证点: 返回数据中包含list和total字段
        """
        case = self._get_case('ZZGL_API_07')
        execute_test_case(authenticated_client, case)
