#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Util.CommonMethod import rec_translate, byte2str, send_translate
from Util.GlobalVar import rec_queue, rec_queue_file
from Util.Log import log_data, log_file
import re


def produce(buf, remain):
    data = remain + buf
    st_list = [m.start() for m in re.finditer(b"\x7e", data)]
    current = -1
    for x in range(len(st_list)):
        if st_list[x] <= current:
            continue
        if not st_list[x] == st_list[-1]:
            if st_list[x]+1 == st_list[x+1]:
                log_data.info(data[st_list[x]:st_list[x] + 2])
                continue
        for y in range(x + 1, len(st_list)):
            data_piece = data[st_list[x]:st_list[y] + 1]
            if len(data_piece) > 2 and b'\x7e' not in data_piece[1:-1]:
                data_piece = rec_translate(data_piece)
                rec_queue.put(data_piece)
                current = st_list[y]
                break
            else:
                log_data.error("未能解析的7E数据" + byte2str(data_piece))
    remain = data[current + 1:]
    return remain


def send_queue_data(data):
    if data:
        if ' ' in data:
            data = ''.join(data.split(' '))
        data_bak = data
        if data.startswith('7E'):
            data = send_translate(bytes.fromhex(data))
        else:
            data = bytes.fromhex(data)
        send_data = data

        text_hex = ' '.join(data_bak[i:i + 2] for i in range(0, len(data_bak), 2))
        if len(text_hex) > 500:
            text_hex = text_hex[:500]
        log_data.debug('%s%s%s%s%s' % ("SEND DATA:   ", 'lens: ', str(int(len(data_bak) / 2)).ljust(5, ' '), '   data: || ', text_hex))
        return send_data


def produce_for_file(buf, remain):
    data = remain + buf
    st_list = [m.start() for m in re.finditer(b"\x7e", data)]
    current = -1
    for x in range(len(st_list)):
        if st_list[x] <= current:
            continue
        if not st_list[x] == st_list[-1]:
            if st_list[x]+1 == st_list[x+1]:
                log_data.info(data[st_list[x]:st_list[x] + 2])
                continue
        for y in range(x + 1, len(st_list)):
            data_piece = data[st_list[x]:st_list[y] + 1]
            if len(data_piece) > 2 and b'\x7e' not in data_piece[1:-1]:
                data_piece = rec_translate(data_piece)
                rec_queue_file.put(data_piece)
                current = st_list[y]
                break
            else:
                log_data.error("未能解析的7E数据" + byte2str(data_piece))
    remain = data[current + 1:]
    return remain


def send_queue_data_file(data):
    if data:
        if ' ' in data:
            data = ''.join(data.split(' '))
        data_bak = data
        if data.startswith('7E'):
            data = send_translate(bytes.fromhex(data))
        else:
            data = bytes.fromhex(data)
        send_data = data

        text_hex = ' '.join(data_bak[i:i + 2] for i in range(0, len(data_bak), 2))
        if len(text_hex) > 500:
            text_hex = text_hex[:500]
        log_file.debug('%s%s%s%s%s' % ("SEND DATA:   ", 'lens: ', str(int(len(data_bak) / 2)).ljust(5, ' '), '   data: || ', text_hex))
        return send_data
