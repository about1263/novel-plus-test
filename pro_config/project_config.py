"""
小说网站测试项目配置
"""
import os

# 项目根目录
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 动态配置文件
project_config_path = os.path.join(project_path, 'pro_config/pro_config.ini')

# 小说网站API配置
novel_api_urls = {
    'online': 'http://47.108.213.8',  # 生产环境
    'lane': 'http://47.108.213.8'     # 测试环境
}

# 测试用户配置
test_users = {
    'admin': {'username': 'admin', 'password': '123456'},
    'author': {'username': 'author001', 'password': '123456'},
    'reader': {'username': '18723968509', 'password': 'zxcvbnm.'},  # 读者测试账号（手机号登录）
    'mobile_reader': {'username': '18723968509', 'password': 'zxcvbnm.'},  # 别名
    'test_reader': {'username': 'reader001', 'password': '123456'}  # 备用测试账号
}

# 小说分类配置
book_categories = {
    'male': {'id': 1, 'name': '男频'},
    'female': {'id': 2, 'name': '女频'}
}

# 小说状态配置
book_status = {
    'serializing': 0,  # 连载中
    'completed': 1     # 已完结
}