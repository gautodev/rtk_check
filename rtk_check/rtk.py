#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : rtk.py
# Author        : bssthu
# Project       : rtk_checker
# Description   : 解析差分数据
# 

import os
import sys
import json
import time
import signal
from rtk_check import log
from rtk_check.client_thread import ClientThread
from rtk_check.checker import Checker


class Rtk:
    def __init__(self):
        self.checker = Checker()
        self.client = None
        self.is_interrupt = False

    def got_data_cb(self, data, rcv_count):
        """接收到差分数据的回调函数

        Args:
            data: 收到的数据包
            rcv_count: 收到的数据包的编号
        """
        self.checker.add_data(data)

    def exit_by_signal(self, signum, frame):
        self.is_interrupt = True

    def wait_for_keyboard(self):
        """quit when press q or press ctrl-c, or exception from other threads"""
        try:
            print("enter 'q' to quit")
            while input() != 'q':
                print("enter 'q' to quit. rcv count: %d" % self.client.rcv_count)
                if not self.client.running:
                    break
        except KeyboardInterrupt:
            pass
        except EOFError:
            # no input
            signal.signal(signal.SIGINT, self.exit_by_signal)
            while not self.is_interrupt:
                time.sleep(1)
                if not self.client.running:
                    break

    def main(self):
        # config
        config_file_name = os.path.join(sys.path[0], 'conf/config.json')
        try:
            with open(config_file_name) as config_fp:
                configs = json.load(config_fp)
        except:
            print('failed to load config from config.json.')
            return

        # log init
        log.initialize_logging(configs['enableLog'].lower() == 'true')
        log.info('main: start')

        # threads
        self.client = ClientThread(configs['serverIpAddress'], configs['serverPort'], self.got_data_cb)

        self.client.start()

        # wait
        self.wait_for_keyboard()

        # quit & clean up
        self.client.running = False
        self.client.join()
        log.info('main: bye')
