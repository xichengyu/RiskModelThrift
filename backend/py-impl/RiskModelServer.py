#!/usr/bin/env python
# coding=utf-8

import sys
# import socket
import json
sys.path.append('../gen-py')
sys.path.append('../../RiskModelSystem/Model')
import scorecard
import planner

from RiskModel import RiskModelThriftService
from RiskModel.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='[%Y-%m-%d %H:%M:%S]', filename='thrift.log', filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


class RiskModelHandler:
    def transmitRiskModelData(self, rmodel_request):
        start = time.time()*1000
        response = RiskModelResponse()
        request = json.loads(rmodel_request.json_data)
        logging.info(request)

        handle_data = planner.data_handler(request, scorecard.main)
        response.json_data = handle_data.gen_response()     # generate thrift response

        # response.json_data = rmodel_request.json_data

        logging.info(json.loads(response.json_data))
        logging.info("Thrift time cost(ms): %s", str(time.time()*1000 - start))

        return response


def BuildTserver(ip, port):
    handler = RiskModelHandler()
    processor = RiskModelThriftService.Processor(handler)
    transport = TSocket.TServerSocket(ip, port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    # server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
    server = TServer.TForkingServer(processor, transport, tfactory, pfactory)
    # logging.info("Starting python server with TThreadedServer...")
    logging.info("Starting python server with TForkingServer...")

    server.serve()


if __name__ == "__main__":

    cnf_file_path = "../conf/riskmodel.conf"

    thrift_server = "172.31.24.11:9090"
    # thrift_server = "0.0.0.0:9090"

    BuildTserver(thrift_server.split(":")[0], int(thrift_server.split(":")[1]))

