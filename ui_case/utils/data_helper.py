"""
测试数据管理类
生成和管理UI测试数据
"""
import json
import os
import random
import string
from datetime import datetime
from typing import Dict, List, Any, Optional


class DataHelper:
    """测试数据助手"""
    
    def __init__(self, data_file=None):
        """
        初始化数据助手
        
        Args:
            data_file: 测试数据文件路径，默认为 ui_case/configs/test_data.json
        """
        if data_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_file = os.path.join(base_dir, 'configs', 'test_data.json')
        
        self.data_file = data_file
        self.test_data = self._load_test_data()
    
    def _load_test_data(self) -> Dict[str, Any]:
        """加载测试数据"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 返回默认测试数据
            return {
                "users": {
                    "valid_user": {
                        "phone": "13800138000",
                        "password": "123456",
                        "nickname": "测试用户"
                    },
                    "invalid_users": [
                        {"phone": "1380013800", "password": "123456", "description": "手机号格式错误"},
                        {"phone": "", "password": "123456", "description": "手机号为空"},
                        {"phone": "13800138000", "password": "", "description": "密码为空"},
                        {"phone": "13800138000", "password": "wrongpass", "description": "密码错误"}
                    ]
                },
                "test_cases": {
                    "login": {
                        "normal_login": {
                            "phone": "13800138000",
                            "password": "123456",
                            "expected_result": "登录成功"
                        },
                        "wrong_password": {
                            "phone": "13800138000",
                            "password": "12345678",
                            "expected_result": "账号或密码错误"
                        },
                        "invalid_phone": {
                            "phone": "1380013800",
                            "password": "123456",
                            "expected_result": "手机号格式不正确"
                        },
                        "empty_phone": {
                            "phone": "",
                            "password": "123456",
                            "expected_result": "手机号/密码不能为空"
                        },
                        "empty_password": {
                            "phone": "13800138000",
                            "password": "",
                            "expected_result": "手机号/密码不能为空"
                        }
                    }
                }
            }
    
    def save_test_data(self):
        """保存测试数据到文件"""
        data_dir = os.path.dirname(self.data_file)
        os.makedirs(data_dir, exist_ok=True)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f, indent=4, ensure_ascii=False)
    
    # 用户数据方法
    def get_valid_user(self) -> Dict[str, str]:
        """获取有效用户数据"""
        return self.test_data.get("users", {}).get("valid_user", {})
    
    def get_invalid_users(self) -> List[Dict[str, str]]:
        """获取无效用户数据列表"""
        return self.test_data.get("users", {}).get("invalid_users", [])
    
    def get_user_by_type(self, user_type: str) -> Optional[Dict[str, str]]:
        """根据类型获取用户数据"""
        users = self.test_data.get("users", {})
        
        if user_type == "valid":
            return users.get("valid_user")
        elif user_type == "invalid_phone":
            for user in users.get("invalid_users", []):
                if user.get("description") == "手机号格式错误":
                    return user
        elif user_type == "empty_phone":
            for user in users.get("invalid_users", []):
                if user.get("description") == "手机号为空":
                    return user
        elif user_type == "empty_password":
            for user in users.get("invalid_users", []):
                if user.get("description") == "密码为空":
                    return user
        elif user_type == "wrong_password":
            for user in users.get("invalid_users", []):
                if user.get("description") == "密码错误":
                    return user
        
        return None
    
    # 测试用例数据方法
    def get_test_case(self, module: str, case_name: str) -> Optional[Dict[str, Any]]:
        """获取测试用例数据"""
        return self.test_data.get("test_cases", {}).get(module, {}).get(case_name)
    
    def get_login_test_cases(self) -> Dict[str, Dict[str, Any]]:
        """获取所有登录测试用例"""
        return self.test_data.get("test_cases", {}).get("login", {})
    
    # 数据生成方法
    @staticmethod
    def generate_phone_number() -> str:
        """生成随机手机号"""
        # 中国手机号前缀
        prefixes = ['138', '139', '150', '151', '152', '157', '158', '159', 
                   '130', '131', '132', '155', '156', '186', '187', '188']
        prefix = random.choice(prefixes)
        suffix = ''.join(random.choices(string.digits, k=8))
        return prefix + suffix
    
    @staticmethod
    def generate_password(length=8) -> str:
        """生成随机密码"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choices(chars, k=length))
    
    @staticmethod
    def generate_nickname() -> str:
        """生成随机昵称"""
        adjectives = ['勇敢的', '聪明的', '快乐的', '安静的', '热情的', '优雅的', '幽默的', '神秘的']
        nouns = ['小猫', '小狗', '老虎', '狮子', '熊猫', '狐狸', '兔子', '小鸟']
        return random.choice(adjectives) + random.choice(nouns)
    
    @staticmethod
    def generate_email() -> str:
        """生成随机邮箱"""
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', '163.com', 'qq.com']
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        domain = random.choice(domains)
        return f"{username}@{domain}"
    
    @staticmethod
    def generate_date(start_year=2020, end_year=2024) -> str:
        """生成随机日期"""
        year = random.randint(start_year, end_year)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # 避免2月29日等问题
        return f"{year}-{month:02d}-{day:02d}"
    
    @staticmethod
    def generate_text(min_words=5, max_words=20) -> str:
        """生成随机文本"""
        words = ['测试', '数据', '生成', '自动化', '框架', '页面', '对象', '模式', 
                '元素', '定位', '断言', '验证', '成功', '失败', '错误', '提示',
                '登录', '注册', '用户', '密码', '手机', '邮箱', '验证码', '提交']
        word_count = random.randint(min_words, max_words)
        selected_words = random.choices(words, k=word_count)
        return ''.join(selected_words)
    
    # 数据操作方法
    def add_user(self, user_type: str, user_data: Dict[str, str]):
        """添加用户数据"""
        if user_type == "valid":
            self.test_data.setdefault("users", {})["valid_user"] = user_data
        elif user_type == "invalid":
            self.test_data.setdefault("users", {}).setdefault("invalid_users", []).append(user_data)
    
    def add_test_case(self, module: str, case_name: str, case_data: Dict[str, Any]):
        """添加测试用例数据"""
        self.test_data.setdefault("test_cases", {}).setdefault(module, {})[case_name] = case_data
    
    def update_user(self, user_type: str, user_data: Dict[str, str]):
        """更新用户数据"""
        if user_type == "valid":
            if "users" in self.test_data and "valid_user" in self.test_data["users"]:
                self.test_data["users"]["valid_user"].update(user_data)
        elif user_type == "invalid":
            if "users" in self.test_data and "invalid_users" in self.test_data["users"]:
                for i, user in enumerate(self.test_data["users"]["invalid_users"]):
                    if user.get("description") == user_data.get("description"):
                        self.test_data["users"]["invalid_users"][i].update(user_data)
                        break
    
    def delete_user(self, user_type: str, identifier=None):
        """删除用户数据"""
        if user_type == "valid":
            if "users" in self.test_data and "valid_user" in self.test_data["users"]:
                del self.test_data["users"]["valid_user"]
        elif user_type == "invalid":
            if "users" in self.test_data and "invalid_users" in self.test_data["users"]:
                if identifier:
                    self.test_data["users"]["invalid_users"] = [
                        user for user in self.test_data["users"]["invalid_users"]
                        if user.get("description") != identifier
                    ]
                else:
                    self.test_data["users"]["invalid_users"] = []
    
    def export_to_json(self, file_path: str):
        """导出测试数据到JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f, indent=4, ensure_ascii=False)
    
    @classmethod
    def import_from_json(cls, file_path: str) -> 'DataHelper':
        """从JSON文件导入测试数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        data_helper = cls()
        data_helper.test_data = test_data
        return data_helper