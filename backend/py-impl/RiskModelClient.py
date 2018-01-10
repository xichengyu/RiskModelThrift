#!/usr/bin/env python
# coding=utf-8

import sys
sys.path.append('../gen-py')
from RiskModel import RiskModelThriftService
from RiskModel.ttypes import *
from RiskModel.constants import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

try:

# Make socket
    transport = TSocket.TSocket('172.31.24.11', 9090)
    # transport = TSocket.TSocket('127.0.0.1', 9090)


# Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)

# Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

# Create a client to use the protocol encoder
    client = RiskModelThriftService.Client(protocol)

# Connect!
    transport.open()

    request = RiskModelRequest()

    request.json_data = '{"queryId": "123", "userId": 12345, "interestName": "特色地方菜,自助餐,甜点饮品,料理,烧烤,西餐,简餐,海鲜", ' \
                        '"relation": 4,"count": 2, "currentLocation": "浙江省杭州市西斗门路3号", "residentCity":"浙江,台州", "cdid": "0571001",' \
                        '"startTime": "9:00", "endTime": "21:00", "latitude": 23.234, "longitude": 123.123, "consumeType": 3}'

    response = client.transmitRiskModelData(request)
    print(response)

    transport.close()

except Thrift.TException:
    pass
