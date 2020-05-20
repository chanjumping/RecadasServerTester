#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Util.CommonMethod import byte2str, num2big, calc_check_code, get_serial_no, big2num, str2hex, calc_length_su_ter
from Util.GlobalVar import send_queue, communication_id
from Util.Log import log_data, log_file
from Function.upload_attachment import UploadAttachment, event


parse_su_ter_command = {
    b'\x89\x00': lambda x: parse_query_status(x),
    b'\x81\x06': lambda x: parse_query_terminal_para(x),
    b'\x81\x03': lambda x: parse_set_terminal_para(x),
    b'\x81\x05': lambda x: parse_terminal_control(x),
    b'\x81\x07': lambda x: parse_query_terminal_property(),
    b'\x83\x00': lambda x: parse_tts(x),
    b'\x84\x00': lambda x: parse_phone_recall(x),
    b'\x92\x08': lambda x: parse_attachment_upload(x),
    b'\x80\x01': lambda x: parse_comm_reply(x),
    b'\x92\x12': lambda x: parse_upload_finish_reply(x),

}


# 解析8106参数ID对应的内容
para_id_name = {
    '00000001': '终端心跳发送间隔',
    '00000002': 'TCP超时时间',
    '00000003': 'TCP重传次数',
    '00000013': '主服务器地址',
    '00000017': '备份服务器地址',
    '00000018': 'TCP端口',
    '00000019': 'UDP端口',
    '00000055': '最高速度',
    '00000056': '超速持续时间',
    '00000057': '连续驾驶时间门限',
    '00000084': '车牌颜色',
    '0000F400': '告警灵敏度级别',
    '0000F401': '告警产生时间间隔',
    '0000F402': '告警上传平台时间间隔',
}

# 解析8106不同的参数ID类型有不同的解析方法
para_data_deal_method = {

    '00000001': lambda x: big2num(byte2str(x)),
    '00000002': lambda x: big2num(byte2str(x)),
    '00000003': lambda x: big2num(byte2str(x)),
    '00000013': lambda x: x.decode('gbk'),
    '00000017': lambda x: x.decode('gbk'),
    '00000018': lambda x: big2num(byte2str(x)),
    '00000019': lambda x: big2num(byte2str(x)),
    '00000055': lambda x: big2num(byte2str(x)),
    '00000056': lambda x: big2num(byte2str(x)),
    '00000057': lambda x: big2num(byte2str(x)),
    '00000084': lambda x: big2num(byte2str(x)),
}


# 回复0104应答参数查询时的内容
para_data_content = {

    '00000001': num2big(10, 4),
    '00000002': num2big(60, 4),
    '00000003': num2big(3, 4),
    '00000013': str2hex('119.23.49.157', 13),
    '00000017': str2hex('123.123.123.123', 15),
    '00000018': num2big(2083, 4),
    '00000019': num2big(0, 4),
    '00000055': num2big(60, 4),
    '00000056': num2big(10, 4),
    '00000057': num2big(14400, 4),
    '00000084': num2big(0, 4),
    # '0000F400': 'FFF0' * 4 + 'FFF1' * 3 + 'FFF2' * 2 + 'FF43' * 4 + 'FFF4' * 3 + '00' * 32,
    '0000F400': 'EFF0'*16 + '00'*32,
    '0000F401': '0000EFF0' * 24 + '00' * 32,
    '0000F402': '0000EFF0' * 24 + '00' * 32
}


# 通用应答
def comm_reply_su_ter(data, reply_result):
    device_id = data[4:10]
    msg_id = data[0:2]
    serial_no = data[10:12]
    result = reply_result
    msg_body = byte2str(serial_no) + byte2str(msg_id) + result
    body = '0001' + calc_length_su_ter(msg_body) + byte2str(device_id) + num2big(get_serial_no()) + msg_body
    data = '7E' + body + calc_check_code(body) + '7E'
    return data


# 查询终端参数
def parse_query_terminal_para(data):
    msg_body = data[12:-1]
    serial_no = data[10:12]

    para_num = big2num(byte2str(msg_body[0:1]))
    para_body = msg_body[1:]
    para_id_list = []
    para_data_list = ''
    for n in range(para_num):
        para_id = byte2str(para_body[n*4:(n+1)*4])
        para_id_list.append(para_id)
        para_data = para_data_content.get(para_id)
        para_data_list = para_data_list + para_id + num2big(len(para_data)//2, 1) + para_data

    log_data.debug('—————— 查询终端参数 ——————')
    log_data.debug('参数总数 {}'.format(para_num))
    log_data.debug('参数列表 {}'.format(', '.join(para_id_list)))
    log_data.debug('—————— END ——————')

    msg_body = byte2str(serial_no) + num2big(para_num, 1) + para_data_list
    body = '0104' + calc_length_su_ter(msg_body) + communication_id + num2big(get_serial_no()) + msg_body
    data = '7E' + body + calc_check_code(body) + '7E'
    send_queue.put(data)


# 设置终端参数
def parse_set_terminal_para(data):

    reply_data = comm_reply_su_ter(data, '00')
    send_queue.put(reply_data)

    msg_body = data[12:-1]
    para_num = big2num(byte2str(msg_body[0:1]))
    para_body = msg_body[1:]
    start = 0
    log_data.debug('—————— 设置终端参数 ——————')
    for _ in range(para_num):
        para_id = byte2str(para_body[start:start+4])
        para_len = big2num(byte2str(para_body[start+4:start+5]))
        para_data = para_body[start+5:start+5+para_len]
        start = start+5+para_len
        if para_id == '0000F400':
            log_data.debug('## {} ##'.format(para_id_name.get(para_id)))
            log_data.debug('')
            for n in range(len(para_data)//2):
                log_data.debug('第 {} 个参数 {}'.format(n+1, (byte2str(para_data[n*2:(n + 1)*2]))))
        elif para_id == '0000F401':
            log_data.debug('## {} ##'.format(para_id_name.get(para_id)))
            log_data.debug('')
            for n in range(len(para_data)//4):
                log_data.debug('第 {} 个参数 {}'.format(n+1, (byte2str(para_data[n*4:(n + 1)*4]))))
        elif para_id == '0000F402':
            log_data.debug('## {} ##'.format(para_id_name.get(para_id)))
            log_data.debug('')
            for n in range(len(para_data)//4):
                log_data.debug('第 {} 个参数 {}'.format(n+1, (byte2str(para_data[n*4:(n + 1)*4]))))
        else:
            log_data.debug('{}  {}'.format(para_id_name.get(para_id), para_data_deal_method.get(para_id)(para_data)))
    log_data.debug('—————— END ——————')


# 终端控制
def parse_terminal_control(data):

    reply_data = comm_reply_su_ter(data, '00')
    send_queue.put(reply_data)

    msg_body = data[12:-1]
    command = big2num(byte2str(msg_body[:1]))
    log_data.debug('—————— 终端控制 ——————')
    log_data.debug('命令字 {}'.format(command))
    if command == 1 or command == 2:
        command_para = msg_body[1:]
        log_data.debug('命令参数 {}'.format(command_para.decode('gbk')))
    log_data.debug('—————— END ——————')


# 查询终端属性
def parse_query_terminal_property():

    log_data.debug('—————— 查询终端属性 ——————')

    terminal_type = '0000'
    maker_id = str2hex('recon', 5)
    terminal_model = str2hex('Reconova_P500', 20)
    terminal_id = str2hex('12_0107', 7)
    sim_iccid = str2hex('1351101122', 10)
    hw_len = 32
    hw = str2hex('This is HardWare.0107', hw_len)
    fw_len = 32
    fw = str2hex('This is FirmWare.', fw_len)
    gnss = '00'
    comm_pro = '00'

    msg_body = terminal_type + maker_id + terminal_model + terminal_id + sim_iccid + num2big(hw_len, 1) + hw + \
               num2big(fw_len, 1) + fw + gnss + comm_pro
    body = '0107' + calc_length_su_ter(msg_body) + communication_id + num2big(get_serial_no()) + msg_body
    data = '7E' + body + calc_check_code(body) + '7E'
    send_queue.put(data)


# 查询设备状态
def parse_query_status(data):
    msg_body = data[12:-1]
    msg_type = byte2str(msg_body[:1])
    log_data.debug('—————— 查询基本信息 ——————')
    msg_num = big2num(byte2str(msg_body[1:2]))
    peripheral_id = byte2str(msg_body[2:3])
    if msg_type == 'F8':

        log_data.debug('参数总数 {}'.format(msg_num))
        log_data.debug('== 查询信息 ==')

        company_name_len = 32
        company_name = str2hex('Reconova', company_name_len)
        product_model_len = 32
        product_model = str2hex('RN-CA-P500', product_model_len)
        hw_len = 32
        hw = str2hex('This is HardWare.0900', hw_len)
        sw_len = 32
        sw = str2hex('This is SoftWare.', sw_len)
        device_id_len = 32
        device_id = str2hex('123456_F8', device_id_len)
        client_code_len = 32
        client_code = str2hex('ABCDEFG', client_code_len)

        msg_info = num2big(company_name_len, 1) + company_name + num2big(product_model_len, 1) + product_model + \
                   num2big(hw_len, 1) + hw + num2big(sw_len, 1) + sw + num2big(device_id_len, 1) + device_id + \
                   num2big(client_code_len, 1) + client_code
        msg_body = msg_type + '01' + peripheral_id + num2big(len(msg_info) // 2, 1) + msg_info
        body = '0900' + calc_length_su_ter(msg_body) + communication_id + num2big(get_serial_no()) + msg_body
        data = '7E' + body + calc_check_code(body) + '7E'

        send_queue.put(data)

    elif msg_type == 'F9':

        log_data.debug('参数总数 {}'.format(msg_num))
        log_data.debug('== 查询硬件信息 ==')

        msg_info = '00000000'
        msg_body = msg_type + '01' + peripheral_id + num2big(len(msg_info) // 2, 1) + msg_info
        body = '0900' + calc_length_su_ter(msg_body) + communication_id + num2big(get_serial_no()) + msg_body
        data = '7E' + body + calc_check_code(body) + '7E'

        send_queue.put(data)

    elif msg_type == 'FA':

        log_data.debug('参数总数 {}'.format(msg_num))
        log_data.debug('== 查询软件信息 ==')

        terminal_sim_len = 11
        terminal_sim = str2hex('13811111111', terminal_sim_len)
        signal_level = '00'
        mcu_len = 14
        mcu = str2hex('RN-CA-P500-MCU', mcu_len)
        device_id_len = 32
        device_id = str2hex('123456_FA', device_id_len)
        communicate_id_len = 32
        communicate_id = str2hex('123456', communicate_id_len)

        msg_info = num2big(terminal_sim_len, 1) + terminal_sim + signal_level + num2big(mcu_len, 1) + mcu + \
                   num2big(device_id_len, 1) + device_id + num2big(communicate_id_len, 1) + communicate_id
        msg_body = msg_type + '01' + peripheral_id + num2big(len(msg_info) // 2, 1) + msg_info
        body = '0900' + calc_length_su_ter(msg_body) + communication_id + num2big(get_serial_no()) + msg_body
        data = '7E' + body + calc_check_code(body) + '7E'

        send_queue.put(data)

    log_data.debug('—————— END ——————')


# 文本信息
def parse_tts(data):

    reply_data = comm_reply_su_ter(data, '00')
    send_queue.put(reply_data)

    msg_body = data[12:-1]
    flag = msg_body[0:1]
    txt = msg_body[1:]
    flag_content = ''
    flag_int = big2num(byte2str(flag))
    if flag_int & 0b100000:
        flag_content += 'CAN故障码信息 '
    else:
        flag_content += '中心导航信息 '
    if flag_int & 0b1:
        flag_content += '紧急 '
    if flag_int & 0b100:
        flag_content += '终端显示器显示 '
    if flag_int & 0b1000:
        flag_content += '终端TTS播读 '
    if flag_int & 0b10000:
        flag_content += '广告屏显示 '
    log_data.debug('—————— 文本信息 ——————')
    log_data.debug('标志： {}'.format(flag_content))
    log_data.debug('文本信息： {}'.format(txt.decode('gbk')))
    log_data.debug('—————— END ——————')


# 电话回拨
def parse_phone_recall(data):

    reply_data = comm_reply_su_ter(data, '00')
    send_queue.put(reply_data)

    msg_body = data[12:-1]
    flag = msg_body[0:1]
    phone_number = msg_body[1:]
    if flag == b'\x00':
        flag_content = '普通通话'
    elif flag == b'\x01':
        flag_content = '监听'
    else:
        flag_content = '未知类型标志！！！'
    log_data.debug('—————— 电话回拨 ——————')
    log_data.debug('标志： {}'.format(flag_content))
    log_data.debug('文本信息： {}'.format(phone_number.decode('gbk')))
    log_data.debug('—————— END ——————')


# 附件上传
def parse_attachment_upload(data):

    reply_data = comm_reply_su_ter(data, '00')
    send_queue.put(reply_data)

    msg_body = data[12:-1]
    address_len = big2num(byte2str(msg_body[0:1]))
    address = msg_body[1:1+address_len].decode('gbk')
    port_tcp = big2num(byte2str(msg_body[1+address_len:3+address_len]))
    port_udp = big2num(byte2str(msg_body[3+address_len:5+address_len]))
    alarm_flag = byte2str(msg_body[5+address_len:21+address_len])
    alarm_no = byte2str(msg_body[21+address_len:53+address_len])
    log_data.debug('—————— 收到服务器地址 ——————')
    log_data.debug('服务器IP： {}'.format(address))
    log_data.debug('TCP端口： {}'.format(port_tcp))
    log_data.debug('UDP端口： {}'.format(port_udp))
    log_data.debug('报警标识： {}'.format(alarm_flag))
    log_data.debug('报警编号： {}'.format(alarm_no))
    log_data.debug('—————— END ——————')

    upload_attachment_thread = UploadAttachment('Upload Attachment Thread ... ', address, port_tcp, alarm_flag, alarm_no)
    upload_attachment_thread.start()


# 平台通用应答
def parse_comm_reply(data):
    msg_body = data[12:-1]
    serial_no = msg_body[0:2]
    msg_id = msg_body[2:4]
    result = msg_body[4:5]
    if msg_id == b'\x12\x10':
        event.set()
    elif msg_id == b'\x12\x11':
        event.set()


# 上传附件结束
def parse_upload_finish_reply(data):
    msg_body = data[12:-1]
    file_name_len = big2num(byte2str(msg_body[0:1]))
    file_name = msg_body[1:1+file_name_len].decode('gbk')
    file_type = byte2str(msg_body[1+file_name_len:2+file_name_len])
    result = byte2str(msg_body[2+file_name_len:3+file_name_len])
    retransmission_num = big2num(byte2str(msg_body[3+file_name_len:4+file_name_len]))
    log_file.debug('—————— 文件上传完成应答 ——————')
    log_file.debug('文件名称： {}'.format(file_name))
    log_file.debug('文件类型： {}'.format(file_type))
    log_file.debug('上传结果： {}'.format(result))
    log_file.debug('补传数量： {}'.format(retransmission_num))
    if not retransmission_num == 0:
        log_data.debug('补传内容： {}'.format(byte2str(msg_body[4 + file_name_len:])))
    log_file.debug('—————— END ——————')
    event.set()
