# coding=utf-8

# from __future__ import unicode_literals
import sys
sys.path.append('../../RiskModelSystem/Model')
# from random import choice
import json
import traceback
import scorecard
import time


class data_handler(object):
    def __init__(self, thrift_request, filtering_model):
        self.request = thrift_request
        self.model = filtering_model

    def get_data(self):
        pass

    def gen_plans(self):
        try:
            return self.model(self.request, self.get_data())
        except:
            print(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc())
            return {}

    def gen_response(self):
        response = {}
        return json.dumps(response)


if __name__ == '__main__':

    # time_1 = time.time()

    # handle_data = data_handler(test_request, scorecard)

    # print 'initial_time: ', time.time() - time_1

    # time_3 = time.time()

    # response = handle_data.gen_response()

    # print 'recommend_time: ', time.time() - time_3

    # print json.loads(response)['plans'][0]['shops'][1]['ext']
    # print(json.loads(response))

    scorecard.main()







