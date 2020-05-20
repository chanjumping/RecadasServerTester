#!/usr/bin/env python
# -*- coding: utf-8 -*-


import socket
from ParseModel import parse_data, parse_su_ter
from Util.GlobalVar import rec_queue, send_queue, send_queue_file, rec_queue_file
from Util.CommonMethod import byte2str
import threading
import queue
from Util.Log import log_data, log_file
import time


class ClientSocket(object):

    def __init__(self, conn_type, address, port):
        self.connection = None
        self.remain = b''
        self.address = address
        self.port = port
        self.conn_type = conn_type

    def start_work(self):

        ip_bind = (self.address, self.port)
        self.connection = socket.socket()
        self.connection.connect(ip_bind)
        log_data.debug('=' * 100)

        if self.conn_type == 1:
            log_data.debug('【 Data Server 】 {} {} Connected ...'.format(self.connection.getpeername(), self.connection.getsockname()))

            th1 = threading.Thread(target=self.recv_data, args=())
            th1.start()
            th2 = threading.Thread(target=self.parse_data, args=())
            th2.start()
            th3 = threading.Thread(target=self.send_data, args=())
            th3.start()
        elif self.conn_type == 2:
            log_file.debug('【 File Server 】 {} {} Connected ...'.format(self.connection.getpeername(), self.connection.getsockname()))

            th1 = threading.Thread(target=self.recv_data_file, args=())
            th1.start()
            th2 = threading.Thread(target=self.parse_data_file, args=())
            th2.start()
            th3 = threading.Thread(target=self.send_data_file, args=())
            th3.start()

        # th1.join()
        # th2.join()
        # th3.join()

    def recv_data(self):
        log_data.debug("【 Data Server 】 Recv Thread start...")
        while not getattr(self.connection, '_closed', False):
            buf = b''
            try:
                if self.remain:
                    self.remain = parse_data.produce(buf, self.remain)
                buf = self.connection.recv(1024)
            except socket.timeout:
                time.sleep(0.1)
                log_data.debug('【 Data Server 】 [Recv Thread] Receiving data timeout，connection is interrupted.')
                break
            except OSError:
                time.sleep(0.1)
                log_data.debug('【 Data Server 】 [Recv Thread] OSError，connection is interrupted.')
                break
            except ConnectionResetError:
                time.sleep(0.1)
                log_data.debug('【 Data Server 】 [Recv Thread] ConnectionResetError，connection is interrupted.')
                break
            except ConnectionAbortedError:
                time.sleep(0.1)
                log_data.debug('【 Data Server 】 [Recv Thread] ConnectionAbortedError，connection is interrupted.')
                break
            except Exception as e:
                log_data.error('[Recv Thread] Unknown Error.')
                log_data.error(e)
                break

            if not buf:
                time.sleep(0.3)
                log_data.debug('【 Data Server 】 [Recv Thread] Receive empty data，connection is interrupted.')
                break
            self.remain = parse_data.produce(buf, self.remain)
            time.sleep(0.1)

    def recv_data_file(self):
        log_file.debug("【 File Server 】 Recv Thread start...")
        while not getattr(self.connection, '_closed', False):
            buf = b''
            try:
                if self.remain:
                    self.remain = parse_data.produce_for_file(buf, self.remain)
                buf = self.connection.recv(1024)
            except socket.timeout:
                time.sleep(0.1)
                log_file.debug('【 File Server 】 [Recv Thread] Receiving data timeout，connection is interrupted.')
                break
            except OSError:
                time.sleep(0.1)
                log_file.debug('【 File Server 】 [Recv Thread] OSError，connection is interrupted.')
                break
            except ConnectionResetError:
                time.sleep(0.1)
                log_data.debug('【 Data Server 】 [Recv Thread] ConnectionResetError，connection is interrupted.')
                break
            except ConnectionAbortedError:
                time.sleep(0.1)
                log_data.debug('【 Data Server 】 [Recv Thread] ConnectionAbortedError，connection is interrupted.')
                break
            except Exception as e:
                log_data.error('[Recv Thread] Unknown Error.')
                log_data.error(e)
                break

            if not buf:
                time.sleep(0.1)
                log_file.debug('【 File Server 】 [Recv Thread] Receive empty data，connection is interrupted.')
                break
            self.remain = parse_data.produce_for_file(buf, self.remain)
            time.sleep(0.1)

    def parse_data(self):
        log_data.debug("【 Data Server 】 Parse Thread start...")
        while not getattr(self.connection, '_closed', False):
            try:
                data = rec_queue.get_nowait()
            except queue.Empty:
                data = None
            if data:
                data_rec = data
                text = byte2str(data)
                text_hex = ' '.join(text[i:i + 2] for i in range(0, len(text), 2))
                if len(text_hex) > 500:
                    text_hex = text_hex[:500]
                log_data.debug(
                    '%s%s%s%s%s' % ("RECV DATA:   ", 'lens: ', str(len(data_rec)).ljust(5, ' '), '   data: || ', text_hex))

                # 进入解析过程
                command = data[1:3]
                func = parse_su_ter.parse_su_ter_command.get(command)
                if func:
                    func(data[1:-1])
            time.sleep(0.1)

    def parse_data_file(self):
        log_file.debug("【 File Server 】 Parse Thread start...")
        while not getattr(self.connection, '_closed', False):
            try:
                data = rec_queue_file.get_nowait()
            except queue.Empty:
                data = None
            if data:
                data_rec = data
                text = byte2str(data)
                text_hex = ' '.join(text[i:i + 2] for i in range(0, len(text), 2))
                if len(text_hex) > 500:
                    text_hex = text_hex[:500]
                log_file.debug(
                    '%s%s%s%s%s' % ("RECV DATA:   ", 'lens: ', str(len(data_rec)).ljust(5, ' '), '   data: || ', text_hex))

                # 进入解析过程
                command = data[1:3]
                func = parse_su_ter.parse_su_ter_command.get(command)
                if func:
                    func(data[1:-1])
            time.sleep(0.1)

    def send_data(self):
        log_data.debug("【 Data Server 】 Send Thread start...")
        while not getattr(self.connection, '_closed', False):
            try:
                data = send_queue.get_nowait()
            except queue.Empty:
                data = None
            text = parse_data.send_queue_data(data)
            if text:
                try:
                    self.connection.sendall(text)
                except socket.timeout:
                    time.sleep(0.1)
                    log_file.debug('【 Data Server 】 [Send Thread] Receiving data timeout，connection is interrupted.')
                    break
                except OSError:
                    time.sleep(0.1)
                    log_file.debug('【 Data Server 】 [Send Thread] OSError，connection is interrupted.')
                    break
                except ConnectionResetError:
                    time.sleep(0.1)
                    log_data.debug('【 Data Server 】 [Send Thread] ConnectionResetError，connection is interrupted.')
                    break
                except ConnectionAbortedError:
                    time.sleep(0.1)
                    log_data.debug('【 Data Server 】 [Send Thread] ConnectionAbortedError，connection is interrupted.')
                    break
                except Exception as e:
                    log_data.error('[Send Thread] Unknown Error.')
                    log_data.error(e)
                    break
            time.sleep(0.1)

    def send_data_file(self):
        log_file.debug("【 File Server 】 Send Thread start...")
        while not getattr(self.connection, '_closed', False):
            try:
                data = send_queue_file.get_nowait()
            except queue.Empty:
                data = None
            text = parse_data.send_queue_data_file(data)
            if text:
                try:
                    self.connection.sendall(text)
                except socket.timeout:
                    time.sleep(0.1)
                    log_file.debug('【 File Server 】 [Send Thread] Receiving data timeout，connection is interrupted.')
                    break
                except OSError:
                    time.sleep(0.1)
                    log_file.debug('【 File Server 】 [Send Thread] OSError，connection is interrupted.')
                    break
                except ConnectionResetError:
                    time.sleep(0.1)
                    log_file.debug('【 File Server 】 [Send Thread] ConnectionResetError，connection is interrupted.')
                    break
                except ConnectionAbortedError:
                    time.sleep(0.1)
                    log_file.debug('【 File Server 】 [Send Thread] ConnectionAbortedError，connection is interrupted.')
                    break
                except Exception as e:
                    log_file.error('[Send Thread] Unknown Error.')
                    log_file.error(e)
                    break
            time.sleep(0.1)

    def close_conn(self):

        if self.conn_type == 1:
            log_data.debug('【 Data Server 】 {} {} Disconnected ...'.format(self.connection.getpeername(), self.connection.getsockname()))
        elif self.conn_type == 2:
            log_file.debug('【 File Server 】 {} {} Disconnected ...'.format(self.connection.getpeername(), self.connection.getsockname()))
        self.connection.close()
        time.sleep(0.5)
        log_data.debug('=' * 100)


