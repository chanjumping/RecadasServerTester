#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import *
from Util.CommonMethod import num2big, calc_check_code, calc_length_su_ter
from Util.GlobalVar import send_queue, communication_id
import xlrd
from Util.CommonMethod import read_value, data2hex, get_serial_no


alarm_flag_alarm_type = {}


def send_dsm_alarm():
    case = r'.\TestData\驾驶异常.xls'
    rs = xlrd.open_workbook(case)
    table = rs.sheets()[0]
    data_len = table.col_values(1)
    data_content = table.col_values(2)

    deal_data = list(map(read_value, data_content))
    data = list(map(data2hex, deal_data, data_len))

    alarm_flag, status, latitude, longitude, height, speed, direction, report_time, alarm_id, alarm_flag_status, \
    alarm_type, alarm_level, fatigue_level, retain, alarm_speed, alarm_height, alarm_latitude, alarm_longitude, \
    alarm_report_time, car_status, device_id, alarm_report_time2, serial, attachment_num, last_retain = data

    basic_info = alarm_flag + status + latitude + longitude + height + speed + direction + report_time
    alarm_flag_no = device_id + alarm_report_time2 + serial + attachment_num + last_retain

    alarm_flag_alarm_type[alarm_flag_no] = '65' + alarm_type

    alarm_info = alarm_id + alarm_flag_status + alarm_type + alarm_level + fatigue_level + retain + alarm_speed + \
                 alarm_height + alarm_latitude + alarm_longitude + alarm_report_time + car_status + alarm_flag_no
    attach_info = '65' + num2big(int(len(alarm_info) / 2), 1) + alarm_info
    msg_body = basic_info + attach_info
    body = '0200' + calc_length_su_ter(msg_body) + communication_id + num2big(get_serial_no()) + msg_body
    data = '7E' + body + calc_check_code(body) + '7E'
    # print(data)
    send_queue.put(data)


def send_adas_alarm():
    case = r'.\TestData\前向预警.xls'
    rs = xlrd.open_workbook(case)
    table = rs.sheets()[0]
    data_len = table.col_values(1)
    data_content = table.col_values(2)

    deal_data = list(map(read_value, data_content))
    data = list(map(data2hex, deal_data, data_len))
    alarm_flag, status, latitude, longitude, height, speed, direction, report_time, alarm_id, alarm_flag_status, \
    alarm_type, alarm_level, front_car_speed, front_car_distance, departure_type, road_identify_type, \
    road_identify_data, alarm_speed, alarm_height, alarm_latitude, alarm_longitude, alarm_report_time, car_status, \
    device_id, alarm_report_time2, serial, attachment_num, last_retain = data

    basic_info = alarm_flag + status + latitude + longitude + height + speed + direction + report_time
    alarm_flag_no = device_id + alarm_report_time2 + serial + attachment_num + last_retain

    alarm_flag_alarm_type[alarm_flag_no] = '64' + alarm_type

    alarm_info = alarm_id + alarm_flag_status + alarm_type + alarm_level + front_car_speed + \
                 front_car_distance + departure_type + road_identify_type + road_identify_data + alarm_speed + \
                 alarm_height + alarm_latitude + alarm_longitude + alarm_report_time + car_status + alarm_flag_no
    attach_info = '64' + num2big(int(len(alarm_info) / 2), 1) + alarm_info
    msg_body = basic_info + attach_info
    body = '0200' + calc_length_su_ter(msg_body) + communication_id + num2big(get_serial_no()) + msg_body
    data = '7E' + body + calc_check_code(body) + '7E'
    # print(data)
    send_queue.put(data)


def send_bsd_alarm():
    case = r'.\TestData\盲区监测.xls'
    rs = xlrd.open_workbook(case)
    table = rs.sheets()[0]
    data_len = table.col_values(1)
    data_content = table.col_values(2)

    deal_data = list(map(read_value, data_content))
    data = list(map(data2hex, deal_data, data_len))
    alarm_flag, status, latitude, longitude, height, speed, direction, report_time, alarm_id, alarm_flag_status, \
    alarm_type, alarm_speed, alarm_height, alarm_latitude, alarm_longitude, alarm_report_time, car_status, device_id, \
    alarm_report_time, serial, attachment_num, last_retain = data

    basic_info = alarm_flag + status + latitude + longitude + height + speed + direction + report_time
    alarm_info = alarm_id + alarm_flag_status + alarm_type + alarm_speed + \
                 alarm_height + alarm_latitude + alarm_longitude + alarm_report_time + car_status + device_id + \
                 alarm_report_time + serial + attachment_num + last_retain
    attach_info = '67' + num2big(int(len(alarm_info) / 2), 1) + alarm_info
    msg_body = basic_info + attach_info
    body = '0200' + calc_length_su_ter(msg_body) + communication_id + num2big(get_serial_no()) + msg_body
    data = '7E' + body + calc_check_code(body) + '7E'
    # print(data)
    send_queue.put(data)


def send_tps_alarm():
    case = r'.\TestData\胎压监测.xls'
    rs = xlrd.open_workbook(case)
    table = rs.sheets()[0]
    data_len = table.col_values(1)
    data_content = table.col_values(2)

    deal_data = list(map(read_value, data_content))
    data = list(map(data2hex, deal_data, data_len))
    alarm_flag, status, latitude, longitude, height, speed, direction, report_time, alarm_id, alarm_flag_status, \
    alarm_speed, alarm_height, alarm_latitude, alarm_longitude, alarm_report_time, car_status, device_id, alarm_report_time, \
    serial, attachment_num, last_retain, event_num, tps_location, alarm_type, tps, tps_t, battery = data

    basic_info = alarm_flag + status + latitude + longitude + height + speed + direction + report_time
    alarm_info = alarm_id + alarm_flag_status + alarm_speed + alarm_height + alarm_latitude + alarm_longitude + \
                 alarm_report_time + car_status + device_id + alarm_report_time + serial + attachment_num + last_retain \
                 + event_num + tps_location + alarm_type + tps + tps_t + battery
    attach_info = '66' + num2big(int(len(alarm_info) / 2), 1) + alarm_info
    msg_body = basic_info + attach_info
    body = '0200' + calc_length_su_ter(msg_body) + communication_id + num2big(get_serial_no()) + msg_body
    data = '7E' + body + calc_check_code(body) + '7E'
    # print(data)
    send_queue.put(data)


root = Tk()

but = Button(root, text="前向预警告警", command=send_adas_alarm, width=15, bd=5)
but.grid(row=1, column=0, ipadx=20, ipady=5, padx=10, pady=10, sticky=W)

but = Button(root, text="驾驶异常告警", command=send_dsm_alarm, width=15, bd=5)
but.grid(row=1, column=1, ipadx=20, ipady=5, padx=10, pady=10, sticky=W)

but = Button(root, text="盲区监测告警", command=send_bsd_alarm, width=15, bd=5)
but.grid(row=2, column=0, ipadx=20, ipady=5, padx=10, pady=10, sticky=W)

but = Button(root, text="胎压监测告警", command=send_tps_alarm, width=15, bd=5)
but.grid(row=2, column=1, ipadx=20, ipady=5, padx=10, pady=10, sticky=W)


if __name__ == '__main__':
    root.mainloop()
