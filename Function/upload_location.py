#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Util.GlobalVar import location_queue, send_queue
from Util.CommonMethod import calc_length_su_ter, calc_check_code, get_serial_no, num2big
from Util.Log import log_data
import threading
import time


class UploadLocation(threading.Thread):
    def __init__(self, name, device_id):
        threading.Thread.__init__(self)
        self.name = name
        self.setName(self.name)
        self.device_id = device_id

    def run(self):
        log_data.debug(threading.current_thread().getName())
        while True:
            while not location_queue.empty():
                location_data = location_queue.get_nowait()
                status, latitude, longitude, speed, report_time, mileage = location_data
                alarm_flag = '00000000'
                height = '0000'
                direction = '0000'
                # status = '00000003'
                # latitude = '0157CB96'
                # longitude = '06CA9628'
                # speed = num2big(880, 2)
                # report_time = '200206221122'
                msg_body = alarm_flag + status + latitude + longitude + height + speed + direction + report_time + '0104' +  mileage
                body = '0200' + calc_length_su_ter(msg_body) + self.device_id + num2big(get_serial_no()) + msg_body
                data = '7E' + body + calc_check_code(body) + '7E'
                send_queue.put(data)
                msg_body = ''
                body = '0002' + calc_length_su_ter(msg_body) + self.device_id + num2big(get_serial_no()) + msg_body
                data = '7E' + body + calc_check_code(body) + '7E'
                send_queue.put(data)
                time.sleep(0.1)
