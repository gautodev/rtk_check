#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : rtk_util.py
# Author        : bssthu
# Project       : rtk_checker
# Description   :
#

from rtk_check import log


def try_parse(data):
    """从头开始，逐字节尝试解析
    Returns:
        index: 尝试到的位置
        len_message: 报文总长度，-1表示没有完整报文
    """
    for i in range(0, len(data) - 1):
        len_message = try_parse_from_begin(data[i:])
        if len_message > 0 and i + len_message <= len(data):
            return i, len_message
    return len(data), -1


def try_parse_from_begin(data):
    # 检查引导字和保留字
    if data[0] != 0xd3 or data[1] & 0b11111100 != 0x0:
        return -1

    # 报文长度
    len_rtcm = (data[1] & 0b11) * 0x100 + data[2]
    len_full_message = len_rtcm + 3 + 3     # 加上引导字、保留字、校验
    if len_rtcm <= 0 or len_full_message > len(data):
        return -1

    # 校验
    message = data[0:3+len_rtcm]
    crc_from_message = int.from_bytes(data[3+len_rtcm:3+len_rtcm+3], 'big')
    message_binary = ''.join(['{0:08b}'.format(x) for x in message])
    crc = int(get_crc(message_binary), 2)   # 计算 CRC
    if crc != crc_from_message:
        log.warning('crc check failed.')
        return -1
    return len_full_message


def get_crc(msg, div='1100001100100110011111011', code='0'*24):
    """Cyclic Redundancy Check

    https://gist.github.com/evansneath/4650991

    Args:
        msg: 需要校验的信息
        div: 生成多项式
        code: 需要校验的信息

    Returns:
        CRC码，默认使用 CRC-24Q 方法
    """
    # Append the code to the message. If no code is given, default to '000'
    msg += code

    # Convert msg and div into list form for easier handling
    msg = list(msg)
    div = list(div)

    # Loop over every message bit (minus the appended code)
    for i in range(len(msg)-len(code)):
        # If that message bit is 1, perform modulo 2 multiplication
        if msg[i] == '1':
            for j in range(len(div)):
                # Perform modulo 2 multiplication on each index of the divisor
                msg[i+j] = str((int(msg[i+j])+int(div[j]))%2)

    # Output the last error-checking code portion of the message generated
    return ''.join(msg[-len(code):])
