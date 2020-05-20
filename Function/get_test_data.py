#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xlrd
from Util.GlobalVar import location_queue
from Util.CommonMethod import num2big
import datetime
import threading
from Util.Log import log_data
import time


class GetLocationData(threading.Thread):

    def __init__(self, name, filename):
        threading.Thread.__init__(self)
        self.name = name
        self.filename = filename
        self.rs = None
        self.table = None

    def run(self):
        log_data.debug(threading.current_thread().getName())
        self.rs = xlrd.open_workbook(self.filename)
        self.table = self.rs.sheets()[0]
        rows = self.table.nrows
        with open("num.txt", 'r') as f:
            num = f.read()
        if not num:
            num = 1
        else:
            num = int(num)
        for case in range(num, rows):
            # 获取字段长度列和字段值列
            data_row = self.table.row_values(case)
            # 获取excel行的数据
            status, latitude, longitude, speed, report_time, mileage = data_row
            if not status:
                status = "00000003"
                latitude = num2big(int(latitude * 1000000), 4)
                longitude = num2big(int(longitude * 1000000), 4)
            else:
                status = "00000001"
                latitude = num2big(0, 4)
                longitude = num2big(0, 4)

            speed = num2big(int(speed * 10), 2)

            if not report_time:
                report_time = datetime.datetime.now().strftime('%y%m%d%H%M%S')
            if not mileage:
                mileage = num2big(int(num), 4)
            location_queue.put((status, latitude, longitude, speed, report_time, mileage))
            with open("num.txt", 'w') as f:
                num = int(num) + 1
                f.write(str(num))
            time.sleep(10)


