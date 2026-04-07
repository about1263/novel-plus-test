"""
UI测试运行器
用于运行UI自动化测试
"""
import sys
import os
import argparse
import subprocess
from datetime import datetime


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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        allure_results_dir = f'ui_case/reports/allure-results'
        allure_report_dir = f'ui_case/reports/allure-report-{timestamp}'
        
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
        allure_cmd = ['allure', 'generate', allure_results_dir, '-o', allure_report_dir, '--clean']
        subprocess.run(allure_cmd)
        
        # 创建latest链接
        latest_dir = 'ui_case/reports/latest'
        if os.path.islink(latest_dir):
            os.unlink(latest_dir)
        os.symlink(allure_report_dir, latest_dir)
        
        print(f"报告已生成: {allure_report_dir}")
        print(f"使用命令查看报告: allure open {latest_dir}")
    
    return result.returncode


def clean_reports(keep_days=7):
    """清理旧报告"""
    import shutil
    import time
    
    report_dir = 'ui_case/reports'
    if not os.path.exists(report_dir):
        print(f"报告目录不存在: {report_dir}")
        return
    
    cutoff_time = time.time() - (keep_days * 24 * 60 * 60)
    
    for item in os.listdir(report_dir):
        item_path = os.path.join(report_dir, item)
        
        # 跳过latest链接
        if item == 'latest':
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
    
    # 清理旧报告
    if args.clean:
        print("清理旧报告...")
        clean_reports()
    
    # 运行测试
    return_code = run_tests(args)
    
    # 返回退出码
    sys.exit(return_code)


if __name__ == '__main__':
    main()