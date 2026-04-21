"""
UI测试运行器
用于运行UI自动化测试
"""
import sys
import os
import argparse
import subprocess
import shutil
from datetime import datetime

from ui_case.utils.config_manager import ConfigManager
from ui_case.utils.cleanup_manager import CleanupManager


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='运行Novel-Plus UI自动化测试')
    
    parser.add_argument('--browser', type=str, default='chrome',
                       choices=['chrome', 'edge'],
                       help='浏览器类型 (默认: chrome)')
    parser.add_argument('--headless', action='store_true',
                       help='启用无头模式')
    parser.add_argument('--env', type=str, default='lane',
                       choices=['lane', 'online'],
                       help='测试环境 (默认: lane)')
    parser.add_argument('--report', type=str, default='allure',
                       choices=['allure', 'html', 'none'],
                       help='报告类型 (默认: allure)')
    parser.add_argument('--test_path', type=str, default='ui_case/test_cases',
                       help='测试路径 (默认: ui_case/test_cases)')
    parser.add_argument('--test_module', type=str,
                       help='测试模块 (例如: test_login)')
    parser.add_argument('--test_case', type=str,
                       help='测试用例 (例如: test_normal_login)')
    parser.add_argument('--workers', type=int, default=1,
                       help='并发工作进程数 (默认: 1)')
    parser.add_argument('--all_modules', action='store_true',
                       help='运行所有模块测试')
    parser.add_argument('--clean', action='store_true',
                       help='清理旧报告')
    
    return parser.parse_args()


def run_tests(args):
    """运行测试"""
    # 初始化配置和清理管理器
    config_manager = ConfigManager()
    cleanup_manager = CleanupManager(config_manager)
    
    # 检查并执行自动清理
    if cleanup_manager.increment_and_check():
        print("执行自动清理...")
        cleanup_manager.cleanup_all()
    
    # 如果指定了--clean参数，执行按需清理
    if args.clean:
        print("执行按需清理...")
        cleanup_manager.cleanup_on_demand(screenshot_days=7, report_days=7)
    
    # 构建pytest命令
    cmd = ['pytest']
    
    # 添加测试路径
    if args.test_case and args.test_module:
        cmd.append(f'{args.test_path}/{args.test_module}.py::{args.test_case}')
    elif args.test_module:
        cmd.append(f'{args.test_path}/{args.test_module}.py')
    elif args.test_path:
        cmd.append(args.test_path)
    else:
        cmd.append('ui_case/test_cases')
    
    # 添加命令行参数
    cmd.extend(['-v', '--tb=short'])
    
    if args.headless:
        cmd.append('--headless')
    
    if args.browser:
        cmd.extend(['--browser', args.browser])
    
    if args.env:
        cmd.extend(['--env', args.env])
    
    if args.workers > 1:
        cmd.extend(['-n', str(args.workers)])
    
    # 报告配置
    if args.report == 'allure':
        # 获取项目根目录（ui_case的父目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        allure_results_dir = os.path.join(project_root, 'ui_case', 'reports', 'allure-results')
        allure_report_dir = os.path.join(project_root, 'ui_case', 'reports', 'allure-report')
        
        # 创建目录
        os.makedirs(allure_results_dir, exist_ok=True)
        os.makedirs(allure_report_dir, exist_ok=True)
        
        cmd.extend(['--alluredir', allure_results_dir])
        
        print(f"Allure结果目录: {allure_results_dir}")
        print(f"Allure报告目录: {allure_report_dir}")
    
    # 执行命令
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    # 生成报告
    if args.report == 'allure' and result.returncode == 0:
        print("生成Allure报告...")
        
        # 查找allure命令路径
        allure_path = shutil.which('allure')
        if allure_path is None:
            # 尝试查找allure.bat（Windows）
            allure_path = shutil.which('allure.bat')
        
        if allure_path is None:
            # 尝试使用已知路径
            known_paths = [
                'G:\\allure-2.34.0\\allure-2.34.0\\bin\\allure.bat',
                'C:\\Program Files\\allure\\bin\\allure.bat',
                '/usr/local/bin/allure',
                '/usr/bin/allure'
            ]
            for path in known_paths:
                if os.path.exists(path):
                    allure_path = path
                    break
        
        if allure_path is None:
            print("警告: 未找到allure命令，跳过报告生成")
            print("请安装allure命令行工具或将其添加到PATH环境变量")
        else:
            try:
                allure_cmd = [allure_path, 'generate', allure_results_dir, '-o', allure_report_dir, '--clean']
                print(f"执行Allure命令: {' '.join(allure_cmd)}")
                subprocess.run(allure_cmd, check=True)
                
                # 创建latest链接
                latest_dir = os.path.join(project_root, 'ui_case', 'reports', 'latest')
                try:
                    if os.path.islink(latest_dir):
                        os.unlink(latest_dir)
                    os.symlink(allure_report_dir, latest_dir)
                    print(f"创建latest符号链接: {latest_dir} -> {allure_report_dir}")
                except Exception as e:
                    print(f"警告: 创建latest符号链接失败: {e}")
                    print(f"最新报告目录: {allure_report_dir}")
                
                print(f"报告已生成: {allure_report_dir}")
                print(f"使用命令查看报告: allure open {latest_dir}")
            except FileNotFoundError:
                print(f"错误: allure命令不存在于路径: {allure_path}")
                print("请检查allure安装路径")
            except subprocess.CalledProcessError as e:
                print(f"生成Allure报告失败，退出码: {e.returncode}")
                print(f"错误输出: {e.stderr}")
            except Exception as e:
                print(f"生成Allure报告时发生异常: {e}")
    
    return result.returncode


def clean_reports(keep_days=7):
    """清理旧报告"""
    import shutil
    import time
    
    # 获取项目根目录（ui_case的父目录）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    report_dir = os.path.join(project_root, 'ui_case', 'reports')
    if not os.path.exists(report_dir):
        print(f"报告目录不存在: {report_dir}")
        return
    
    cutoff_time = time.time() - (keep_days * 24 * 60 * 60)
    
    for item in os.listdir(report_dir):
        item_path = os.path.join(report_dir, item)
        
        # 跳过latest链接和固定目录
        if item in ['latest', 'allure-report', 'allure-results']:
            continue
        
        try:
            if os.path.isdir(item_path) and item.startswith('allure-report-'):
                # 检查目录修改时间
                if os.path.getmtime(item_path) < cutoff_time:
                    shutil.rmtree(item_path)
                    print(f"删除旧报告目录: {item_path}")
            elif os.path.isfile(item_path) and item.endswith('.json'):
                # 检查文件修改时间
                if os.path.getmtime(item_path) < cutoff_time:
                    os.remove(item_path)
                    print(f"删除旧报告文件: {item_path}")
        except Exception as e:
            print(f"清理报告失败 {item_path}: {e}")


def main():
    """主函数"""
    args = parse_args()
    
    # 运行测试（清理逻辑已在run_tests中处理）
    return_code = run_tests(args)
    
    # 返回退出码
    sys.exit(return_code)


if __name__ == '__main__':
    main()