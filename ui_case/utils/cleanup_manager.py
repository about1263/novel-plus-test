"""
清理管理器
负责清理UI测试生成的临时文件、截图、日志和报告
"""
import os
import json
import shutil
import logging
import glob
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path


class CleanupManager:
    """清理管理器"""
    
    def __init__(self, config_manager=None):
        """
        初始化清理管理器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        if config_manager:
            # 从配置获取清理设置
            self.cleanup_config = self._get_cleanup_config()
            self.test_config = config_manager.get_test_config()
            self.logging_config = config_manager.get_logging_config()
        else:
            # 默认配置
            self.cleanup_config = {
                'enabled': True,
                'interval': 5,
                'keep_screenshots': 10,
                'keep_report_days': 3,
                'log_max_size_mb': 10,
                'log_backup_count': 3
            }
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            self.test_config = {
                'screenshot_dir': os.path.join(project_root, 'ui_case', 'screenshots'),
                'report_dir': os.path.join(project_root, 'ui_case', 'reports')
            }
            self.logging_config = {
                'log_file': os.path.join(project_root, 'ui_case', 'logs', 'ui_test.log')
            }
        
        # 运行计数器文件路径
        self.counter_file = os.path.join(self._get_report_dir(), 'run_counter.json')
    
    def _get_cleanup_config(self) -> Dict[str, Any]:
        """获取清理配置"""
        try:
            # 尝试从配置文件获取清理配置
            if hasattr(self.config_manager, 'config') and self.config_manager.config.has_section('cleanup'):
                config = self.config_manager.config
                return {
                    'enabled': config.getboolean('cleanup', 'enabled', fallback=True),
                    'interval': config.getint('cleanup', 'interval', fallback=5),
                    'keep_screenshots': config.getint('cleanup', 'keep_screenshots', fallback=10),
                    'keep_report_days': config.getint('cleanup', 'keep_report_days', fallback=3),
                    'log_max_size_mb': config.getint('cleanup', 'log_max_size_mb', fallback=10),
                    'log_backup_count': config.getint('cleanup', 'log_backup_count', fallback=3)
                }
        except Exception as e:
            self.logger.warning(f"获取清理配置失败: {e}")
        
        # 默认配置
        return {
            'enabled': True,
            'interval': 5,
            'keep_screenshots': 10,
            'keep_report_days': 3,
            'log_max_size_mb': 10,
            'log_backup_count': 3
        }
    
    def _get_screenshot_dir(self) -> str:
        """获取截图目录"""
        screenshot_dir = self.test_config.get('screenshot_dir', 'ui_case/screenshots')
        if not os.path.isabs(screenshot_dir):
            # 如果是相对路径，转换为绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            screenshot_dir = os.path.join(project_root, screenshot_dir)
        os.makedirs(screenshot_dir, exist_ok=True)
        return screenshot_dir
    
    def _get_report_dir(self) -> str:
        """获取报告目录"""
        report_dir = self.test_config.get('report_dir', 'ui_case/reports')
        if not os.path.isabs(report_dir):
            # 如果是相对路径，转换为绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            report_dir = os.path.join(project_root, report_dir)
        os.makedirs(report_dir, exist_ok=True)
        return report_dir
    
    def _get_log_file(self) -> str:
        """获取日志文件路径"""
        log_file = self.logging_config.get('log_file', 'ui_case/logs/ui_test.log')
        if not os.path.isabs(log_file):
            # 如果是相对路径，转换为绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            log_file = os.path.join(project_root, log_file)
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        return log_file
    
    def _load_counter(self) -> int:
        """加载运行计数器"""
        try:
            if os.path.exists(self.counter_file):
                with open(self.counter_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('run_count', 0)
        except Exception as e:
            self.logger.warning(f"加载运行计数器失败: {e}")
        return 0
    
    def _save_counter(self, count: int):
        """保存运行计数器"""
        try:
            data = {'run_count': count, 'last_run': datetime.now().isoformat()}
            with open(self.counter_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存运行计数器失败: {e}")
    
    def increment_and_check(self) -> bool:
        """
        增加运行次数并检查是否达到清理阈值
        
        Returns:
            bool: 是否需要执行清理
        """
        if not self.cleanup_config['enabled']:
            return False
        
        run_count = self._load_counter()
        run_count += 1
        
        self.logger.info(f"运行计数器: {run_count}/{self.cleanup_config['interval']}")
        
        # 检查是否达到清理间隔
        if run_count >= self.cleanup_config['interval']:
            self.logger.info(f"达到清理阈值({self.cleanup_config['interval']}次)，执行清理...")
            self._save_counter(0)
            return True
        else:
            self._save_counter(run_count)
            return False
    
    def cleanup_all(self):
        """执行所有清理操作"""
        if not self.cleanup_config['enabled']:
            self.logger.info("清理功能已禁用")
            return
        
        self.logger.info("开始执行清理操作...")
        
        try:
            # 1. 清理截图
            screenshots_cleaned = self.cleanup_screenshots(
                keep_last=self.cleanup_config['keep_screenshots']
            )
            
            # 2. 清理日志
            logs_cleaned = self.cleanup_logs()
            
            # 3. 清理旧报告
            reports_cleaned = self.cleanup_old_reports(
                keep_days=self.cleanup_config['keep_report_days']
            )
            
            # 4. 清理临时文件
            temp_files_cleaned = self.cleanup_temp_files()
            
            self.logger.info(f"清理完成: 截图={screenshots_cleaned}, 日志={logs_cleaned}, "
                           f"报告={reports_cleaned}, 临时文件={temp_files_cleaned}")
            
        except Exception as e:
            self.logger.error(f"清理操作失败: {e}")
    
    def cleanup_screenshots(self, keep_last: int = 10) -> int:
        """
        清理截图文件，保留最近N个
        
        Args:
            keep_last: 保留最近多少个截图文件
            
        Returns:
            int: 删除的文件数量
        """
        screenshot_dir = self._get_screenshot_dir()
        if not os.path.exists(screenshot_dir):
            self.logger.info(f"截图目录不存在: {screenshot_dir}")
            return 0
        
        # 获取所有截图文件
        screenshot_pattern = os.path.join(screenshot_dir, "*.png")
        screenshot_files = glob.glob(screenshot_pattern)
        
        if len(screenshot_files) <= keep_last:
            self.logger.info(f"截图文件数量({len(screenshot_files)})未超过保留限制({keep_last})")
            return 0
        
        # 按修改时间排序（最新的在前面）
        screenshot_files.sort(key=os.path.getmtime, reverse=True)
        
        # 需要删除的文件
        files_to_delete = screenshot_files[keep_last:]
        
        # 删除文件
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                self.logger.debug(f"删除截图文件: {file_path}")
                deleted_count += 1
            except Exception as e:
                self.logger.warning(f"删除截图文件失败 {file_path}: {e}")
        
        self.logger.info(f"清理截图: 保留{keep_last}个，删除{deleted_count}个，原始{len(screenshot_files)}个")
        return deleted_count
    
    def cleanup_logs(self) -> int:
        """
        清理日志文件
        
        Returns:
            int: 处理的日志文件数量
        """
        log_file = self._get_log_file()
        log_dir = os.path.dirname(log_file)
        
        if not os.path.exists(log_dir):
            self.logger.info(f"日志目录不存在: {log_dir}")
            return 0
        
        # 检查日志文件大小
        processed_count = 0
        if os.path.exists(log_file):
            file_size_mb = os.path.getsize(log_file) / (1024 * 1024)
            max_size_mb = self.cleanup_config['log_max_size_mb']
            
            if file_size_mb > max_size_mb:
                self.logger.info(f"日志文件过大({file_size_mb:.2f}MB > {max_size_mb}MB)，执行轮转...")
                
                # 执行日志轮转
                backup_count = self.cleanup_config['log_backup_count']
                
                # 删除最旧的备份
                for i in range(backup_count, 0, -1):
                    backup_file = f"{log_file}.{i}"
                    if os.path.exists(backup_file):
                        if i >= backup_count:
                            os.remove(backup_file)
                            self.logger.debug(f"删除日志备份: {backup_file}")
                        else:
                            new_backup = f"{log_file}.{i+1}"
                            os.rename(backup_file, new_backup)
                            self.logger.debug(f"重命名日志备份: {backup_file} -> {new_backup}")
                
                # 重命名当前日志文件
                if os.path.exists(log_file):
                    os.rename(log_file, f"{log_file}.1")
                    self.logger.debug(f"重命名当前日志: {log_file} -> {log_file}.1")
                    processed_count = 1
        
        # 清理旧的日志备份（超过备份数量的）
        backup_pattern = f"{log_file}.*"
        backup_files = glob.glob(backup_pattern)
        backup_files.sort()
        
        backup_count = self.cleanup_config['log_backup_count']
        if len(backup_files) > backup_count:
            files_to_delete = backup_files[backup_count:]
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    self.logger.debug(f"删除旧的日志备份: {file_path}")
                    processed_count += 1
                except Exception as e:
                    self.logger.warning(f"删除日志备份失败 {file_path}: {e}")
        
        return processed_count
    
    def cleanup_old_reports(self, keep_days: int = 3) -> int:
        """
        清理旧报告
        
        Args:
            keep_days: 保留多少天内的报告
            
        Returns:
            int: 删除的报告数量
        """
        report_dir = self._get_report_dir()
        if not os.path.exists(report_dir):
            self.logger.info(f"报告目录不存在: {report_dir}")
            return 0
        
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        deleted_count = 0
        
        for item in os.listdir(report_dir):
            item_path = os.path.join(report_dir, item)
            
            # 跳过latest链接和固定目录
            if item in ['latest', 'allure-report', 'allure-results', 'run_counter.json']:
                continue
            
            try:
                if os.path.isdir(item_path) and item.startswith('allure-report-'):
                    # 检查目录修改时间
                    if os.path.getmtime(item_path) < cutoff_time:
                        shutil.rmtree(item_path)
                        self.logger.info(f"删除旧报告目录: {item_path}")
                        deleted_count += 1
                elif os.path.isfile(item_path) and item.endswith('.json'):
                    # 检查文件修改时间
                    if os.path.getmtime(item_path) < cutoff_time:
                        os.remove(item_path)
                        self.logger.info(f"删除旧报告文件: {item_path}")
                        deleted_count += 1
            except Exception as e:
                self.logger.error(f"清理报告失败 {item_path}: {e}")
        
        return deleted_count
    
    def cleanup_temp_files(self) -> int:
        """
        清理临时文件
        
        Returns:
            int: 删除的临时文件数量
        """
        # 清理__pycache__目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        deleted_count = 0
        
        # 查找并删除__pycache__目录
        for root, dirs, files in os.walk(project_root):
            if '__pycache__' in dirs:
                pycache_dir = os.path.join(root, '__pycache__')
                try:
                    shutil.rmtree(pycache_dir)
                    self.logger.debug(f"删除__pycache__目录: {pycache_dir}")
                    deleted_count += 1
                except Exception as e:
                    self.logger.warning(f"删除__pycache__目录失败 {pycache_dir}: {e}")
        
        return deleted_count
    
    def cleanup_on_demand(self, screenshot_days: int = 7, report_days: int = 7):
        """
        按需清理，可指定保留天数
        
        Args:
            screenshot_days: 截图保留天数
            report_days: 报告保留天数
        """
        self.logger.info(f"执行按需清理: 截图保留{screenshot_days}天, 报告保留{report_days}天")
        
        # 清理旧截图（按天数）
        self._cleanup_old_screenshots_by_days(screenshot_days)
        
        # 清理旧报告
        self.cleanup_old_reports(report_days)
        
        # 清理临时文件
        self.cleanup_temp_files()
    
    def _cleanup_old_screenshots_by_days(self, keep_days: int):
        """按天数清理旧截图"""
        screenshot_dir = self._get_screenshot_dir()
        if not os.path.exists(screenshot_dir):
            return
        
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        deleted_count = 0
        
        screenshot_pattern = os.path.join(screenshot_dir, "*.png")
        for screenshot_file in glob.glob(screenshot_pattern):
            try:
                if os.path.getmtime(screenshot_file) < cutoff_time:
                    os.remove(screenshot_file)
                    self.logger.debug(f"删除旧截图: {screenshot_file}")
                    deleted_count += 1
            except Exception as e:
                self.logger.warning(f"删除截图失败 {screenshot_file}: {e}")
        
        if deleted_count > 0:
            self.logger.info(f"按天数清理截图: 删除{deleted_count}个{keep_days}天前的截图")