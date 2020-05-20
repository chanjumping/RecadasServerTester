#!/usr/bin/python
# -*- coding: utf-8 -*-
import queue


# 接收队列
rec_queue = queue.Queue()
# 发送队列
send_queue = queue.Queue()
# 位置信息队列
location_queue = queue.Queue()

communication_id = '000218510624'

# 文件链路接收队列
rec_queue_file = queue.Queue()
# 文件链路发送队列
send_queue_file = queue.Queue()

