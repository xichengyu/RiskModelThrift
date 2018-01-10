# coding=utf-8

# from __future__ import unicode_literals
import sys
sys.path.append('../../RiskModelSystem/Model')
# from random import choice
import json
import traceback
import scorecard
import time
from sklearn.externals import joblib


class data_handler(object):
    def __init__(self, thrift_request, filtering_model):
        self.request = thrift_request
        self.model = filtering_model

    def get_data(self):
        X = []
        try:
            X = joblib.load("./conf/X.nparray")
        except:
            pass
        return X

    def gen_score(self):
        try:
            return self.model(self.get_data())
        except:
            print(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc())
            return {}

    def gen_response(self):
        response = {}
        return json.dumps(response)


if __name__ == '__main__':

    test_request = "{}"

    handle_data = data_handler(test_request, scorecard.main)
    score = handle_data.gen_score()

    print(len(score))








