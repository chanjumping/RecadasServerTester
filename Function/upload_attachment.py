#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread, Event
from Util.GlobalVar import communication_id, send_queue_file
import os
from Util.CommonMethod import num2big, str2hex, calc_length_su_ter, calc_check_code, get_serial_no, byte2str
from Util.Log import log_file
from Gui.gui_excel import alarm_flag_alarm_type


event = Event()


class UploadAttachment(Thread):

    def __init__(self, name, address, port, alarm_flag, alarm_no):
        Thread.__init__(self)
        self.name = name
        self.setName(self.name)
        self.address = address
        self.port = port
        self.alarm_flag = alarm_flag
        self.alarm_no = alarm_no
        self.file_list = []
        self.file_path = r'.\Attachment'

    def run(self):
        from SeverModel.client_socket import ClientSocket
        # t = ClientSocket(device_id=communication_id, address='192.168.0.98', port=8000)
        t = ClientSocket(conn_type=2, address=self.address, port=self.port)
        t.start_work()
        self.alarm_file_info()
        event.wait()
        for file in self.file_list:
            self.file_info_upload(file)
            event.clear()
            event.wait()
            self.file_data_upload(file)
            event.clear()
            event.wait()
        t.close_conn()

    def alarm_file_info(self):
        device_id = str2hex(communication_id[-7:], 7)
        info_type = '00'
        attachment_num = '04'
        file_info_list = ''
        alarm_type = alarm_flag_alarm_type.get(self.alarm_flag)
        if alarm_type:
            alarm_flag_alarm_type.pop(self.alarm_flag)
        self.file_path = os.path.join(self.file_path, alarm_type)
        self.file_list = os.listdir(self.file_path)
        for file in self.file_list:
            name, file_type = file.split('.')
            name_list = name.split('_')
            name_list[1] = alarm_type[:2]
            name_list[2] = alarm_type
            name_list[-1] = bytes.fromhex(self.alarm_no).decode('gbk')
            new_file = '_'.join(name_list)
            new_file = new_file + '.' + file_type
            os.rename(os.path.join(self.file_path, file), os.path.join(self.file_path, new_file))
            index = self.file_list.index(file)
            self.file_list[index] = new_file
            file_name_len = len(new_file)
            file_name = str2hex(new_file, file_name_len)
            file_size = os.path.getsize(os.path.join(self.file_path, new_file))
            file_info_list += num2big(file_name_len, 1) + file_name + num2big(file_size, 4)

        msg_body = device_id + self.alarm_flag + self.alarm_no + info_type + attachment_num + file_info_list
        body = '1210' + calc_length_su_ter(msg_body) + communication_id + num2big(get_serial_no()) + msg_body
        data = '7E' + body + calc_check_code(body) + '7E'
        log_file.debug('—————— 报警附件信息 ——————')
        send_queue_file.put(data)

    def file_info_upload(self, file):
        file_name_len = len(file)
        file_name = str2hex(file, file_name_len)
        file_type = os.path.splitext(file)[-1]
        if file_type == '.jpg':
            file_type = '00'
        elif file_type == '.mp4':
            file_type = '02'
        file_size = os.path.getsize(os.path.join(self.file_path, file))

        msg_body = num2big(file_name_len, 1) + file_name + file_type + num2big(file_size, 4)
        body = '1211' + calc_length_su_ter(msg_body) + communication_id + num2big(get_serial_no()) + msg_body
        data = '7E' + body + calc_check_code(body) + '7E'
        log_file.debug('—————— 文件信息上传 {} ——————'.format(file))
        send_queue_file.put(data)

    def file_data_upload(self, file):
        file_size = os.path.getsize(os.path.join(self.file_path, file))
        piece = 65536
        n = file_size // piece
        r = file_size % piece
        with open(os.path.join(self.file_path, file), 'rb') as f:
            file_data = f.read()
        for x in range(n):
            offset = x * piece
            file_data_piece = file_data[offset:offset+piece]
            data = '30316364' + str2hex(file, 50) + num2big(offset, 4) + num2big(piece, 4) + byte2str(file_data_piece)
            log_file.debug('—————— 文件数据上传 {}   偏移量 {} 数据长度 {} ——————'.format(file, offset, piece))
            send_queue_file.put(data)
        offset = n * piece
        if r:
            piece = r
            file_data_piece = file_data[offset:offset + piece]

            data = '30316364' + str2hex(file, 50) + num2big(offset, 4) + num2big(piece, 4) + byte2str(file_data_piece)
            log_file.debug('—————— 文件数据上传 {}   偏移量 {} 数据长度 {} ——————'.format(file, offset, piece))
            send_queue_file.put(data)

        file_name_len = len(file)
        file_name = str2hex(file, file_name_len)
        file_type = os.path.splitext(file)[-1]
        if file_type == '.jpg':
            file_type = '00'
        elif file_type == '.mp4':
            file_type = '02'

        import time
        time.sleep(0.5)

        msg_body = num2big(file_name_len, 1) + file_name + file_type + num2big(file_size, 4)
        body = '1212' + calc_length_su_ter(msg_body) + communication_id + num2big(get_serial_no()) + msg_body
        data = '7E' + body + calc_check_code(body) + '7E'
        log_file.debug('—————— 文件上传完成 {} ——————'.format(file))
        send_queue_file.put(data)



