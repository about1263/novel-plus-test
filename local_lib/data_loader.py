#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import yaml
from typing import Dict, List, Any


def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    加载YAML文件
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"YAML文件不存在: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    return data or {}


def load_test_cases(yaml_file: str) -> List[Dict[str, Any]]:
    """
    从YAML文件加载测试用例，返回pytest参数化所需的数据格式
    
    返回格式: [
        {
            'id': '用例ID',
            'title': '测试标题',
            'description': '测试描述',
            'request': {...},
            'expected': {...},
            'tags': [...]
        },
        ...
    ]
    """
    data = load_yaml_file(yaml_file)
    test_cases = data.get('test_cases', {})
    
    result = []
    for case_name, case_data in test_cases.items():
        # 确保每个用例都有名称字段
        case_data['name'] = case_name
        result.append(case_data)
    
    return result


def load_test_cases_for_parametrize(yaml_file: str) -> List[tuple]:
    """
    为pytest.mark.parametrize准备数据
    
    返回格式: [
        (用例名称, 用例数据),
        ...
    ]
    """
    test_cases = load_test_cases(yaml_file)
    return [(case['name'], case) for case in test_cases]


def get_test_data_path(module: str, filename: str) -> str:
    """
    获取测试数据文件路径
    
    Args:
        module: 模块名，如 'book', 'user'
        filename: 文件名，如 'book_rank.yaml'
    
    Returns:
        完整的文件路径
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'test_data', module, filename)


# 示例使用
if __name__ == '__main__':
    # 测试加载book_rank.yaml
    yaml_path = get_test_data_path('book', 'book_rank.yaml')
    print(f"YAML文件路径: {yaml_path}")
    
    try:
        cases = load_test_cases(yaml_path)
        print(f"加载到 {len(cases)} 个测试用例:")
        for case in cases:
            print(f"  - {case['id']}: {case['title']}")
    except Exception as e:
        print(f"加载失败: {e}")