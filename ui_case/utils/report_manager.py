"""
测试报告管理类
生成和管理UI测试报告
"""
import os
import json
import shutil
import subprocess
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

import allure
import pytest


class ReportManager:
    """报告管理器"""
    
    def __init__(self, config_manager=None):
        """
        初始化报告管理器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        if config_manager:
            self.report_config = config_manager.get_report_config()
            self.test_config = config_manager.get_test_config()
        else:
            self.report_config = {
                'report_type': 'allure',
                'report_title': 'Novel-Plus UI自动化测试报告',
                'report_theme': 'default',
                'history_trend': True,
                'attach_screenshot': True,
                'attach_log': True
            }
            self.test_config = {
                'report_dir': 'ui_case/reports'
            }
    
    def setup_allure(self, report_dir=None):
        """设置Allure报告"""
        if report_dir is None:
            report_dir = self.test_config.get('report_dir', 'ui_case/reports')
        
        # 创建报告目录
        os.makedirs(report_dir, exist_ok=True)
        
        # 设置Allure环境变量
        os.environ['ALLURE_RESULTS'] = os.path.join(report_dir, 'allure-results')
        
        # 创建Allure结果目录
        allure_results_dir = os.environ['ALLURE_RESULTS']
        os.makedirs(allure_results_dir, exist_ok=True)
        
        self.logger.info(f"Allure结果目录: {allure_results_dir}")
        return allure_results_dir
    
    def generate_allure_report(self, results_dir=None, report_dir=None, clean=True):
        """生成Allure报告"""
        if results_dir is None:
            results_dir = os.path.join(self.test_config.get('report_dir', 'ui_case/reports'), 'allure-results')
        
        if report_dir is None:
            report_dir = os.path.join(self.test_config.get('report_dir', 'ui_case/reports'), 'allure-report')
        
        if not os.path.exists(results_dir):
            self.logger.warning(f"Allure结果目录不存在: {results_dir}")
            return None
        
        # 创建报告目录
        os.makedirs(report_dir, exist_ok=True)
        
        # 生成报告
        try:
            cmd = ['allure', 'generate', results_dir, '-o', report_dir, '--clean']
            if self.report_config.get('history_trend', True):
                cmd.append('--history-trend')
            
            self.logger.info(f"生成Allure报告: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"Allure报告生成成功: {report_dir}")
                
                # 创建latest链接
                latest_dir = os.path.join(os.path.dirname(report_dir), 'latest')
                if os.path.islink(latest_dir):
                    os.unlink(latest_dir)
                os.symlink(report_dir, latest_dir)
                
                return report_dir
            else:
                self.logger.error(f"Allure报告生成失败: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"生成Allure报告异常: {e}")
            return None
    
    def open_allure_report(self, report_dir=None):
        """打开Allure报告"""
        if report_dir is None:
            report_dir = os.path.join(self.test_config.get('report_dir', 'ui_case/reports'), 'latest')
        
        if not os.path.exists(report_dir):
            self.logger.warning(f"报告目录不存在: {report_dir}")
            return False
        
        try:
            cmd = ['allure', 'open', report_dir]
            self.logger.info(f"打开Allure报告: {' '.join(cmd)}")
            subprocess.Popen(cmd)
            return True
        except Exception as e:
            self.logger.error(f"打开Allure报告异常: {e}")
            return False
    
    def generate_html_report(self, test_results, report_file=None):
        """生成HTML报告"""
        if report_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(self.test_config.get('report_dir', 'ui_case/reports'), 
                                      f'ui_test_report_{timestamp}.html')
        
        # 创建报告目录
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        # 简单的HTML报告模板
        html_template = '''
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .stat {{ display: inline-block; margin-right: 30px; font-size: 18px; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                .skipped {{ color: orange; }}
                .test-case {{ border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; border-radius: 3px; }}
                .test-name {{ font-weight: bold; }}
                .test-status {{ float: right; }}
                .passed-bg {{ background-color: #d4edda; }}
                .failed-bg {{ background-color: #f8d7da; }}
                .skipped-bg {{ background-color: #fff3cd; }}
                .timestamp {{ color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <div class="summary">
                <h2>测试概览</h2>
                <div class="stat">总用例数: <span>{total}</span></div>
                <div class="stat passed">通过: <span>{passed}</span></div>
                <div class="stat failed">失败: <span>{failed}</span></div>
                <div class="stat skipped">跳过: <span>{skipped}</span></div>
                <div class="stat">通过率: <span>{pass_rate}%</span></div>
                <div class="timestamp">生成时间: {timestamp}</div>
            </div>
            <h2>测试详情</h2>
            {test_cases}
        </body>
        </html>
        '''
        
        # 统计结果
        total = len(test_results)
        passed = sum(1 for r in test_results if r.get('status') == 'passed')
        failed = sum(1 for r in test_results if r.get('status') == 'failed')
        skipped = sum(1 for r in test_results if r.get('status') == 'skipped')
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        # 生成测试用例HTML
        test_cases_html = ''
        for result in test_results:
            status = result.get('status', 'unknown')
            status_class = f'{status}-bg'
            
            test_case_html = f'''
            <div class="test-case {status_class}">
                <div class="test-name">{result.get('name', '未知用例')}</div>
                <div class="test-status {status}">{status.upper()}</div>
                <div>描述: {result.get('description', '无描述')}</div>
                <div>执行时间: {result.get('duration', 0):.2f}秒</div>
                {self._generate_error_html(result.get('error'))}
            </div>
            '''
            test_cases_html += test_case_html
        
        # 填充模板
        html_content = html_template.format(
            title=self.report_config.get('report_title', 'UI自动化测试报告'),
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            pass_rate=f"{pass_rate:.1f}",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            test_cases=test_cases_html
        )
        
        # 写入文件
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML报告已生成: {report_file}")
        return report_file
    
    def _generate_error_html(self, error_info):
        """生成错误信息HTML"""
        if not error_info:
            return ''
        
        return f'''
        <div style="margin-top: 10px; padding: 10px; background-color: #ffe6e6; border-radius: 3px;">
            <strong>错误信息:</strong><br>
            <pre style="white-space: pre-wrap; font-size: 12px;">{error_info}</pre>
        </div>
        '''
    
    def save_test_results(self, results, results_file=None):
        """保存测试结果到JSON文件"""
        if results_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = os.path.join(self.test_config.get('report_dir', 'ui_case/reports'), 
                                       f'test_results_{timestamp}.json')
        
        # 创建目录
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        # 保存结果
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        self.logger.info(f"测试结果已保存: {results_file}")
        return results_file
    
    def attach_screenshot_to_allure(self, screenshot_path, name=None):
        """附加截图到Allure报告"""
        if not os.path.exists(screenshot_path):
            self.logger.warning(f"截图文件不存在: {screenshot_path}")
            return False
        
        try:
            if name is None:
                name = os.path.basename(screenshot_path)
            
            allure.attach.file(screenshot_path, name=name, 
                              attachment_type=allure.attachment_type.PNG)
            return True
        except Exception as e:
            self.logger.error(f"附加截图到Allure失败: {e}")
            return False
    
    def attach_log_to_allure(self, log_file, name=None):
        """附加日志到Allure报告"""
        if not os.path.exists(log_file):
            self.logger.warning(f"日志文件不存在: {log_file}")
            return False
        
        try:
            if name is None:
                name = os.path.basename(log_file)
            
            allure.attach.file(log_file, name=name, 
                              attachment_type=allure.attachment_type.TEXT)
            return True
        except Exception as e:
            self.logger.error(f"附加日志到Allure失败: {e}")
            return False
    
    def create_environment_file(self, env_data=None, env_file=None):
        """创建Allure环境文件"""
        if env_file is None:
            env_file = os.path.join(self.test_config.get('report_dir', 'ui_case/reports'), 
                                   'allure-results', 'environment.properties')
        
        # 创建目录
        os.makedirs(os.path.dirname(env_file), exist_ok=True)
        
        # 默认环境数据
        if env_data is None:
            env_data = {
                '测试环境': 'UI自动化测试环境',
                '浏览器': self.report_config.get('browser', 'Chrome'),
                '测试框架': 'pytest + selenium',
                'Python版本': f'{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}',
                '操作系统': os.name,
                '生成时间': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # 写入环境文件
        with open(env_file, 'w', encoding='utf-8') as f:
            for key, value in env_data.items():
                f.write(f'{key}={value}\n')
        
        self.logger.info(f"Allure环境文件已创建: {env_file}")
        return env_file
    
    def cleanup_old_reports(self, keep_days=7):
        """清理旧报告"""
        report_dir = self.test_config.get('report_dir', 'ui_case/reports')
        
        if not os.path.exists(report_dir):
            return
        
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        
        for item in os.listdir(report_dir):
            item_path = os.path.join(report_dir, item)
            
            # 跳过latest链接
            if item == 'latest':
                continue
            
            try:
                if os.path.isdir(item_path):
                    # 检查目录修改时间
                    if os.path.getmtime(item_path) < cutoff_time:
                        shutil.rmtree(item_path)
                        self.logger.info(f"删除旧报告目录: {item_path}")
                elif os.path.isfile(item_path) and item.endswith('.json'):
                    # 检查文件修改时间
                    if os.path.getmtime(item_path) < cutoff_time:
                        os.remove(item_path)
                        self.logger.info(f"删除旧报告文件: {item_path}")
            except Exception as e:
                self.logger.error(f"清理报告失败 {item_path}: {e}")