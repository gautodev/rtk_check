#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : checker.py
# Author        : bssthu
# Project       : rtk_checker
# Description   :
#

import threading
from rtk_check import log
from rtk_check.rtk_util import try_parse


class Checker(threading.Thread):
    """解析差分数据的线程"""

    def __init__(self):
        """构造函数"""
        super().__init__()
        self.data = []
        self.lock = threading.Lock()

    def parse_data(self):
        """解析数据

        Returns:
            是否有解析了的完整报文
        """

        # 拷贝
        data = None
        self.lock.acquire()
        try:
            data = self.data.copy()
        except Exception as e:
            log.error('checker error when copy data: %s' % e)
        self.lock.release()
        if data is None:
            return

        try:
            # 解析
            index, len_message, msg_type = try_parse(data)
            # 删除解析后的数据
            if len_message > 0:
                if index > 0:
                    log.info('unknown data size: %d' % index)
                    # print unknown data
                    #print([hex(x) for x in data[:index]])
                    #print(bytes(data[:index]).decode('utf-8', errors='ignore'))
                log.info('pkg size: %d, msg size: %d, msg type: %d' % (len_message, len_message-6, msg_type))
                #print([hex(x) for x in data[:index + len_message]])
                #print(bytes(data[:index + len_message]).decode('utf-8', errors='ignore'))
                self.remove_from_data(index + len_message)
                return True
        except Exception as e:
            log.error('checker error when parse msg: %s' % e)
        return False

    def add_data(self, data):
        """加入新收到的数据

        Args:
            data: 新收到的数据
        """
        self.lock.acquire()
        try:
            self.data.extend(data)
        except Exception as e:
            log.error('checker error when add: %s' % e)
        self.lock.release()
        # 收到后开始解析，直到解析不出报文
        while self.parse_data():
            continue

    def remove_from_data(self, len_to_remove):
        """从 data 开头移除数据

        Args:
            len_to_remove: 要删除的数据长度
        """
        self.lock.acquire()
        try:
            if (len_to_remove > 0) and (len_to_remove < len(self.data)):
                self.data = self.data[len_to_remove:]
            else:
                self.data = []
        except Exception as e:
            log.error('checker error when remove data: %s' % e)
        self.lock.release()
