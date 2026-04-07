"""
配置管理类
读取和管理UI测试配置
"""
import os
import configparser
import json
from typing import Any, Dict, Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file=None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，默认为 ui_case/configs/ui_config.ini
        """
        if config_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_file = os.path.join(base_dir, 'configs', 'ui_config.ini')
        
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        
        # 确保配置文件存在
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")
        
        self.config.read(self.config_file, encoding='utf-8')
    
    def get_browser_config(self) -> Dict[str, Any]:
        """获取浏览器配置"""
        return {
            'browser_type': self.config.get('browser', 'browser_type', fallback='chrome'),
            'headless': self.config.getboolean('browser', 'headless', fallback=False),
            'window_size': self.config.get('browser', 'window_size', fallback='1920,1080'),
            'implicit_wait': self.config.getint('browser', 'implicit_wait', fallback=10),
            'page_load_timeout': self.config.getint('browser', 'page_load_timeout', fallback=30),
            'driver_path': self.config.get('browser', 'driver_path', fallback=''),
            'download_dir': self.config.get('browser', 'download_dir', fallback=''),
            'chrome_version': self.config.get('browser', 'chrome_version', fallback=''),
            'edge_version': self.config.get('browser', 'edge_version', fallback='')
        }
    
    def get_environment_config(self) -> Dict[str, str]:
        """获取环境配置"""
        return {
            'base_url': self.config.get('environment', 'base_url', fallback='http://localhost:8080'),
            'login_path': self.config.get('environment', 'login_path', fallback='/user/login.html'),
            'home_path': self.config.get('environment', 'home_path', fallback='/index.html')
        }
    
    def get_test_config(self) -> Dict[str, Any]:
        """获取测试配置"""
        return {
            'test_username': self.config.get('test', 'test_username', fallback='13800138000'),
            'test_password': self.config.get('test', 'test_password', fallback='123456'),
            'wrong_password': self.config.get('test', 'wrong_password', fallback='12345678'),
            'invalid_phone': self.config.get('test', 'invalid_phone', fallback='1380013800'),
            'screenshot_dir': self.config.get('test', 'screenshot_dir', fallback='ui_case/screenshots'),
            'report_dir': self.config.get('test', 'report_dir', fallback='ui_case/reports'),
            'screenshot_on_failure': self.config.getboolean('test', 'screenshot_on_failure', fallback=True),
            'save_html_on_failure': self.config.getboolean('test', 'save_html_on_failure', fallback=False)
        }
    
    def get_timeout_config(self) -> Dict[str, int]:
        """获取超时配置"""
        return {
            'element_timeout': self.config.getint('timeout', 'element_timeout', fallback=10),
            'page_navigation_timeout': self.config.getint('timeout', 'page_navigation_timeout', fallback=20),
            'script_timeout': self.config.getint('timeout', 'script_timeout', fallback=10),
            'alert_timeout': self.config.getint('timeout', 'alert_timeout', fallback=5)
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return {
            'log_level': self.config.get('logging', 'log_level', fallback='INFO'),
            'log_file': self.config.get('logging', 'log_file', fallback='ui_case/logs/ui_test.log'),
            'console_output': self.config.getboolean('logging', 'console_output', fallback=True),
            'log_format': self.config.get('logging', 'log_format', 
                                         fallback='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        }
    
    def get_report_config(self) -> Dict[str, Any]:
        """获取报告配置"""
        return {
            'report_type': self.config.get('report', 'report_type', fallback='allure'),
            'report_title': self.config.get('report', 'report_title', 
                                           fallback='Novel-Plus UI自动化测试报告'),
            'report_theme': self.config.get('report', 'report_theme', fallback='default'),
            'history_trend': self.config.getboolean('report', 'history_trend', fallback=True),
            'attach_screenshot': self.config.getboolean('report', 'attach_screenshot', fallback=True),
            'attach_log': self.config.getboolean('report', 'attach_log', fallback=True)
        }
    
    def get_full_url(self, path: str = '') -> str:
        """获取完整URL"""
        env_config = self.get_environment_config()
        base_url = env_config['base_url']
        
        if path.startswith('http://') or path.startswith('https://'):
            return path
        
        if path.startswith('/'):
            return f"{base_url}{path}"
        
        return f"{base_url}/{path}"
    
    def get_login_url(self) -> str:
        """获取登录页面URL"""
        return self.get_full_url(self.get_environment_config()['login_path'])
    
    def get_home_url(self) -> str:
        """获取首页URL"""
        return self.get_full_url(self.get_environment_config()['home_path'])
    
    def get_screenshot_dir(self) -> str:
        """获取截图目录"""
        screenshot_dir = self.get_test_config()['screenshot_dir']
        os.makedirs(screenshot_dir, exist_ok=True)
        return screenshot_dir
    
    def get_report_dir(self) -> str:
        """获取报告目录"""
        report_dir = self.get_test_config()['report_dir']
        os.makedirs(report_dir, exist_ok=True)
        return report_dir
    
    def get_log_file(self) -> str:
        """获取日志文件路径"""
        log_file = self.get_logging_config()['log_file']
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        return log_file
    
    def update_config(self, section: str, key: str, value: Any):
        """更新配置项"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        self.config.set(section, key, str(value))
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def save_to_json(self, json_file: str):
        """将配置保存为JSON文件"""
        config_dict = {}
        
        for section in self.config.sections():
            config_dict[section] = dict(self.config.items(section))
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)
    
    @classmethod
    def load_from_json(cls, json_file: str) -> 'ConfigManager':
        """从JSON文件加载配置"""
        with open(json_file, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        
        # 创建临时INI文件
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False)
        
        config = configparser.ConfigParser()
        for section, items in config_dict.items():
            config.add_section(section)
            for key, value in items.items():
                config.set(section, key, str(value))
        
        with open(temp_file.name, 'w', encoding='utf-8') as f:
            config.write(f)
        
        return cls(temp_file.name)