#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import concurrent.futures
import os
import re
import subprocess
import sys
import datetime
import shutil

from local_lib.config import read_write_config
from local_lib.script_log import log


class NovelTestRunner:
    """
    小说网站测试运行器
    """

    def __init__(self):
        import json
        self.case_marks = json.loads(read_write_config.getValue('projectConfig', 'case_mark'))

    def run(self, env, case_path, case_mark=None, **kwargs):
        """
        运行测试
        :param env: 环境
        :param case_path: 用例路径
        :param case_mark: 用例标记
        :param kwargs: 其他参数
        """
        path_list = [re.sub(pattern=r"(^\s*|\s*$)", repl="", string=i) for i in case_path.split(",") if i]
        
        # 设置环境变量
        os.environ['NOVEL_ENV'] = env
        
        # 清理旧的report目录
        if os.path.exists("report"):
            try:
                shutil.rmtree("report")
                log.info("已清理旧的report目录")
            except Exception as e:
                log.warning(f"清理report目录失败: {e}")
        
        # 构建pytest命令
        pytest_cmd = ["pytest", "-v", "--alluredir", "report"]
        
        # 添加用例标记
        if case_mark:
            pytest_cmd.extend(["-m", case_mark])
        
        # 添加用例路径
        for path in path_list:
            pytest_cmd.append(path)
        
        # 添加其他参数
        if kwargs.get('workers'):
            pytest_cmd.extend(["-n", str(kwargs['workers'])])
        
        log.info(f"执行命令: {' '.join(pytest_cmd)}")
        
        try:
            # 执行测试
            result = subprocess.run(pytest_cmd, capture_output=True, text=True)
            
            # 输出结果
            if result.stdout:
                log.info(f"测试输出:\n{result.stdout}")
            if result.stderr:
                log.error(f"测试错误:\n{result.stderr}")
            
            # 生成Allure HTML报告
            try:
                report_dir = "allure-reports/report"
                
                # 确保报告目录存在
                os.makedirs("allure-reports", exist_ok=True)
                
                # 生成HTML报告
                allure_cmd = ["allure", "generate", "report", "-o", report_dir]
                log.info(f"生成Allure报告: {' '.join(allure_cmd)}")
                allure_result = subprocess.run(allure_cmd, capture_output=True, text=True)
                
                if allure_result.returncode == 0:
                    log.info(f"Allure报告已生成: {report_dir}")
                    
                    # 创建latest符号链接（Windows上创建目录副本或使用junction）
                    latest_dir = "allure-reports/latest"
                    try:
                        # 删除旧的latest链接
                        if os.path.exists(latest_dir):
                            if os.path.islink(latest_dir):
                                os.unlink(latest_dir)
                            elif os.path.isdir(latest_dir):
                                shutil.rmtree(latest_dir)
                            else:
                                os.remove(latest_dir)
                        
                        # 在Windows上创建目录副本
                        if os.path.exists(report_dir):
                            shutil.copytree(report_dir, latest_dir, dirs_exist_ok=True)
                            log.info(f"最新报告副本已创建: {latest_dir}")
                    except Exception as link_error:
                        log.warning(f"创建latest链接失败: {link_error}")
                else:
                    log.warning(f"Allure报告生成失败: {allure_result.stderr}")
                    
            except Exception as e:
                log.warning(f"生成Allure报告时出错: {e}")
            
            return result.returncode == 0
            
        except Exception as e:
            log.error(f"执行测试失败: {e}")
            return False

    def run_all_modules(self, env, **kwargs):
        """
        运行所有模块的测试
        """
        modules = ['user', 'book', 'author', 'search', 'news', 'home', 'resource', 'ai']
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(modules)) as executor:
            futures = {}
            for module in modules:
                future = executor.submit(self.run, env, f"api_case/{module}", **kwargs)
                futures[future] = module
            
            # 等待所有任务完成
            results = {}
            for future in concurrent.futures.as_completed(futures):
                module = futures[future]
                try:
                    results[module] = future.result()
                    log.info(f"模块 {module} 测试完成: {'成功' if results[module] else '失败'}")
                except Exception as e:
                    results[module] = False
                    log.error(f"模块 {module} 测试异常: {e}")
            
            return results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='小说网站测试运行器')
    parser.add_argument('--env', required=True, choices=['online', 'lane'], 
                       help='测试环境: online(生产) 或 lane(测试)')
    parser.add_argument('--work_path', required=True, 
                       help='测试用例路径，多个路径用逗号分隔')
    parser.add_argument('--mark', help='测试用例标记')
    parser.add_argument('--workers', type=int, default=1, 
                       help='并发工作进程数，默认1')
    parser.add_argument('--all_modules', action='store_true',
                       help='运行所有模块测试')
    
    args = parser.parse_args()
    
    runner = NovelTestRunner()
    
    if args.all_modules:
        log.info(f"开始运行所有模块测试，环境: {args.env}")
        results = runner.run_all_modules(args.env, workers=args.workers)
        
        # 统计结果
        success_count = sum(1 for result in results.values() if result)
        total_count = len(results)
        
        log.info(f"测试完成: {success_count}/{total_count} 个模块成功")
        
    else:
        log.info(f"开始运行测试，环境: {args.env}, 路径: {args.work_path}")
        success = runner.run(args.env, args.work_path, args.mark, workers=args.workers)
        
        if success:
            log.info("测试执行成功")
        else:
            log.error("测试执行失败")
            sys.exit(1)


if __name__ == '__main__':
    main()