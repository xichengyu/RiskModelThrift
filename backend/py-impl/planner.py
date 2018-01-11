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


fieldnames = [x.strip() for x in open("./conf/fieldname.txt").readlines()]


class data_handler(object):
    def __init__(self, thrift_request, filtering_model):
        self.request = thrift_request
        self.model = filtering_model

    def get_data(self):
        X = []
        try:
            # X = joblib.load("./conf/X.nparray")
            X_dict = self.request["fieldData"]
            for fieldname in fieldnames:
                X.append(X_dict[fieldname])
        except:
            return KeyError
        return X

    def gen_score(self):
        data = self.get_data()
        if not data:
            return "request format error!"
        try:
            return self.model(data)
        except:
            print(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc())
            return "request format error!"

    def gen_response(self):
        response = {"score": self.gen_score(), "responseId": self.request["queryId"], "idnoHash":self.request["idnoHash"],
                    "applyDate":self.request["applyDate"]}
        return json.dumps(response)


if __name__ == '__main__':

    test_request = "{}"

    handle_data = data_handler(test_request, scorecard.main)
    score = handle_data.gen_score()

    print(len(score))
    print(max(score), min(score))








