#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
定时监控脚本 - 每小时执行一次API+UI测试，失败时邮件告警
"""
import argparse
import os
import re
import subprocess
import smtplib
import time
import sys
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header

from local_lib.config import read_write_config
from local_lib.script_log import log


class TestMonitor:
    def __init__(self, env="lane", interval=3600):
        self.env = env
        self.interval = interval
        self.mail_config = self._load_mail_config()

    def _load_mail_config(self):
        cfg = {
            'smtp_server': read_write_config.getValue('mail', 'smtp_server'),
            'smtp_port': int(read_write_config.getValue('mail', 'smtp_port')),
            'smtp_ssl': read_write_config.getValue('mail', 'smtp_ssl').lower() == 'true',
            'sender': read_write_config.getValue('mail', 'sender'),
            'password': read_write_config.getValue('mail', 'password'),
            'receiver': read_write_config.getValue('mail', 'receiver'),
        }
        return cfg

    def _run_cmd(self, cmd, timeout=600):
        log.info(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result

    def _run_api_tests(self):
        log.info("=" * 50)
        log.info("开始执行API测试")
        log.info("=" * 50)
        result = self._run_cmd(
            [sys.executable, "main.py", "--env", self.env, "--all_modules"],
            timeout=600
        )
        output = (result.stdout or "") + (result.stderr or "")
        failed = False
        failures = []
        for line in output.split("\n"):
            if "FAILED" in line:
                failed = True
                if "=" not in line:
                    failures.append(line.strip())
            if "模块" in line and "测试完成" in line and "失败" in line:
                failed = True
                failures.append(line.strip())
            if "测试完成:" in line and "/" in line and "个模块成功" in line:
                m = re.search(r"(\d+)/(\d+)", line)
                if m and int(m.group(1)) < int(m.group(2)):
                    failed = True
        return failed, failures, output

    def _run_ui_tests(self):
        log.info("=" * 50)
        log.info("开始执行UI测试")
        log.info("=" * 50)
        try:
            result = self._run_cmd(
                [sys.executable, "-m", "ui_case.run_tests", "--headless", "--env", self.env],
                timeout=120
            )
        except subprocess.TimeoutExpired:
            log.error("UI测试超时（超过120秒），跳过")
            return True, ["UI测试执行超时"], "UI测试执行超时"
        output = (result.stdout or "") + (result.stderr or "")
        failed = result.returncode != 0
        failures = []
        for line in (result.stdout or "").split("\n"):
            if "FAILED" in line or "failed" in line.lower():
                if "=" not in line:
                    failures.append(line.strip())
        return failed, failures, output

    def _send_alert(self, api_failed, ui_failed, api_failures, ui_failures,
                    api_output, ui_output, round_num):
        cfg = self.mail_config
        if cfg['password'] == '请填写QQ邮箱授权码':
            log.error("邮件未配置: 请先在 pro_config.ini 的 [mail] 中填写 QQ邮箱授权码")
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"[告警] novel-plus测试失败 - 第{round_num}轮 - {now}"

        body = f"""
<html>
<body style="font-family: Microsoft YaHei, sans-serif;">
<h2 style="color: #cc0000;">novel-plus 自动化测试告警</h2>
<p><b>时间:</b> {now}</p>
<p><b>轮次:</b> 第{round_num}轮</p>
<p><b>环境:</b> {self.env}</p>
<hr>
<h3 style="color: {'red' if api_failed else 'green'};">
  API测试: {'❌ 失败' if api_failed else '✅ 通过'}
</h3>
"""
        if api_failed and api_failures:
            body += "<h4>失败详情:</h4><ul>"
            for f in api_failures:
                body += f"<li>{f}</li>"
            body += "</ul>"

        body += f"""
<h3 style="color: {'red' if ui_failed else 'green'};">
  UI测试: {'❌ 失败' if ui_failed else '✅ 通过'}
</h3>
"""
        if ui_failed and ui_failures:
            body += "<h4>失败详情:</h4><ul>"
            for f in ui_failures:
                body += f"<li>{f}</li>"
            body += "</ul>"

        body += f"<hr><pre style=\"font-size:12px;color:#666;\">API完整输出:\n{api_output[-2000:]}\n\nUI完整输出:\n{ui_output[-2000:]}</pre>"
        body += "</body></html>"

        try:
            msg = MIMEText(body, 'html', 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = cfg['sender']
            msg['To'] = cfg['receiver']

            if cfg['smtp_ssl']:
                server = smtplib.SMTP_SSL(cfg['smtp_server'], cfg['smtp_port'])
            else:
                server = smtplib.SMTP(cfg['smtp_server'], cfg['smtp_port'])
                server.starttls()

            server.login(cfg['sender'], cfg['password'])
            server.sendmail(cfg['sender'], [cfg['receiver']], msg.as_string())
            server.quit()
            log.info(f"告警邮件已发送至 {cfg['receiver']}")
        except Exception as e:
            log.error(f"发送邮件失败: {e}")

    def run_once(self, round_num, api_only=False):
        log.info(f"\n{'#' * 60}")
        log.info(f"第 {round_num} 轮测试开始 - {datetime.now()}")
        log.info(f"{'#' * 60}")

        api_failed, api_failures, api_output = self._run_api_tests()
        if api_only:
            ui_failed, ui_failures, ui_output = False, [], ""
        else:
            ui_failed, ui_failures, ui_output = self._run_ui_tests()

        if api_failed or ui_failed:
            log.warning("检测到测试失败，发送邮件告警...")
            self._send_alert(api_failed, ui_failed, api_failures, ui_failures,
                             api_output, ui_output, round_num)
        else:
            log.info("本轮所有测试通过，无需告警")

        log.info(f"第 {round_num} 轮测试结束 - {datetime.now()}\n")

    def start(self, api_only=False):
        round_num = 0
        if not self.mail_config or self.mail_config.get('password') == '请填写QQ邮箱授权码':
            log.warning("邮件未配置，仅执行测试不发送告警")
            log.warning("请在 pro_config.ini 的 [mail] 中填写 password（QQ邮箱授权码）")

        while True:
            round_num += 1
            try:
                self.run_once(round_num, api_only=api_only)
            except KeyboardInterrupt:
                log.info("收到中断信号，监控脚本退出")
                break
            except Exception as e:
                log.error(f"执行异常: {e}")

            log.info(f"等待 {self.interval} 秒后进入下一轮...")
            time.sleep(self.interval)


def main():
    parser = argparse.ArgumentParser(description='novel-plus 定时测试监控脚本')
    parser.add_argument('--env', default='lane', choices=['lane', 'online'],
                       help='测试环境 (默认: lane)')
    parser.add_argument('--interval', type=int, default=3600,
                       help='监控间隔（秒，默认3600=1小时）')
    parser.add_argument('--once', action='store_true',
                       help='仅执行一次，不循环')
    parser.add_argument('--api-only', action='store_true',
                       help='仅执行API测试，跳过UI测试')
    args = parser.parse_args()

    monitor = TestMonitor(env=args.env, interval=args.interval)

    if args.once:
        monitor.run_once(1, api_only=args.api_only)
    else:
        monitor.start(api_only=args.api_only)


if __name__ == '__main__':
    main()

# 使用示例:
#   启动定时循环监控（每小时执行一次）:       python monitor.py
#   演示：执行一次API测试并发送邮件告警:      python monitor.py --once --api-only
#   演示：执行一次完整测试（API+UI）:         python monitor.py --once
#   指定生产环境:                              python monitor.py --env online
#   自定义间隔为30分钟:                        python monitor.py --interval 1800
#   仅API测试且指定15分钟间隔:                python monitor.py --api-only --interval 900