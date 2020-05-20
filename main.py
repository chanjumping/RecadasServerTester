#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SeverModel.client_socket import ClientSocket
from Function.get_test_data import GetLocationData
from Gui.gui_excel import root
from Util.GlobalVar import communication_id
from Function.upload_location import UploadLocation

read_excel_thread = GetLocationData('Read excel Thread start ... ', filename=r".\TestData\LocationData.xls")
read_excel_thread.start()

t = ClientSocket(conn_type=1, address='119.23.49.157', port=2083)
# t = ClientSocket(conn_type=1, address='172.16.100.164', port=8888)
t.start_work()

upload_location_thread = UploadLocation('【 Data Server 】 Upload Location Thread start ... ', communication_id)
upload_location_thread.start()
root.mainloop()
