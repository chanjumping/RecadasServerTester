#! /usr/bin/env python
# coding=utf-8


# import logging
import logging.handlers
import os

log_data = logging.getLogger('log_data')
log_file = logging.getLogger('log_file')

if not os.path.exists('Logs'):
    os.makedirs('Logs')

log_data.setLevel(logging.DEBUG)
log_file.setLevel(logging.DEBUG)

if os.listdir('Logs'):
    m = max([int(x.split('.')[0][3:]) for x in os.listdir('Logs') if 'file' not in x])
else:
    m = 0

# 创建一个handler，用于写入日志文件
fh_data = logging.handlers.RotatingFileHandler(r'Logs/log{}.log'.format(m + 1), maxBytes=104857600, backupCount=50)
fh_data.setLevel(logging.DEBUG)
fh_file = logging.handlers.RotatingFileHandler(r'Logs/log_file{}.log'.format(m + 1), maxBytes=104857600, backupCount=50)
fh_file.setLevel(logging.DEBUG)

# 再创建一个handler，用于输出到控制台
ch_data = logging.StreamHandler()
ch_data.setLevel(logging.DEBUG)
ch_file = logging.StreamHandler()
ch_file.setLevel(logging.INFO)

# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh_data.setFormatter(formatter)
ch_data.setFormatter(formatter)
fh_file.setFormatter(formatter)
ch_file.setFormatter(formatter)

# 给logger添加handler
log_data.addHandler(fh_data)
log_data.addHandler(ch_data)
# log_event.addHandler(fh)
log_file.addHandler(ch_data)
log_file.addHandler(fh_file)
log_file.addHandler(ch_file)
