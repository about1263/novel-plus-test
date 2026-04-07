#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import threading
from configparser import RawConfigParser

from pro_config.project_config import project_config_path


class ReadWriteConfig:
    """
    专门读取配置文件的，.ini文件格式
    """

    def __init__(self, config_path=None):
        self.config_path = config_path
        if not config_path:
            self.config_path = project_config_path
        if not os.path.exists(os.path.dirname(self.config_path)):
            os.mkdir(os.path.dirname(self.config_path))
        self.config = RawConfigParser()
        # 添加线程锁，防止并发读写问题
        self.lock = threading.RLock()

    def getValue(self, section, key):
        """
        获取配置值
        """
        with self.lock:
            self.config.read(self.config_path, encoding='utf-8')
            try:
                return self.config.get(section, key)
            except Exception as e:
                print(f"获取配置失败: {e}")
                return None

    def setValue(self, section, key, value):
        """
        设置配置值
        """
        with self.lock:
            self.config.read(self.config_path, encoding='utf-8')
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, key, value)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)


# 全局配置实例
read_write_config = ReadWriteConfig()