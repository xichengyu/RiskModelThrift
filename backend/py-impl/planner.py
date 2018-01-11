# coding=utf-8

# from __future__ import unicode_literals
import sys
sys.path.append('../../RiskModelSystem/Model')
# from random import choice
import json
import traceback
import scorecard
import time
import numpy as np


fieldnames = [x.strip() for x in open("./conf/fieldname.txt").readlines()]


class data_handler(object):
    def __init__(self, thrift_request, filtering_model):
        self.request = thrift_request
        self.model = filtering_model

    def get_data(self):
        X = np.array([[]])
        try:
            # X = joblib.load("./conf/X.nparray")
            X_dict = self.request["fieldData"]
            for fieldname in fieldnames:
                X = np.column_stack((X, np.array(X_dict[fieldname])))
        except:
            traceback.print_exc()
            # return KeyError
        return np.array(X)

    def gen_score(self):
        data = self.get_data()

        print(data)
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

    test_request = {"queryId": "123", "idnoHash": "12345", "applyDate": "2017-01-11 11:11:11", "fieldData": {"1": 52.0, "2": 0.26934999999999998, "3": 0.71509999999999996, "4": 462.0, "5": 55.0, "6": 53.0, "7": 0.46100000000000002, "8": 59.0, "9": 211.03, "10": 0.46999999999999997, "11": 2.0, "12": 51.0, "13": 86.234999999999999, "14": 2675.0, "15": 0.24560000000000001, "16": 0.23599999999999999, "17": 0.75360000000000005, "18": 0.52190000000000003, "19": 0.14999999999999999, "20": 0.25440000000000002, "21": 0.89380000000000004, "22": 0.0, "23": 0.0, "24": 92.247900000000001, "25": 0.045999999999999999, "26": 0.0, "27": 93.463999999999999, "28": 0.0, "29": 10.0, "30": 5.0039999999999996, "31": 57.182000000000002, "32": 60.552999999999997, "33": 59.0, "34": 55.0, "35": 52.0, "36": 47.0, "37": 39.194000000000003, "38": 82.891999999999996, "39": 60.552999999999997, "40": 25.003, "41": 0.22700000000000001, "42": 0.69030000000000002, "43": 0.082699999999999996, "44": 0.33329999999999999, "45": 0.16669999999999999, "46": 0.16669999999999999, "47": 0.33329999999999999, "48": 0.10000000000000001, "49": 0.30559999999999998, "50": 0.083299999999999999, "51": 0.1111, "52": 0.083299999999999999, "53": 0.076899999999999996, "54": 0.125, "55": 0.1111, "56": 0.1111, "57": 0.77780000000000005, "58": 0.1429, "59": 0.1429, "60": 0.1429, "61": 0.28570000000000001, "62": 0.28570000000000001, "63": 0.10000000000000001, "64": 0.20000000000000001, "65": 0.20000000000000001, "66": 0.33329999999999999, "67": 0.20000000000000001, "68": 0.20000000000000001, "69": 0.20000000000000001, "70": 0.20000000000000001, "71": 0.2414, "72": 0.034500000000000003, "73": 0.2069, "74": 0.29920000000000002, "75": 0.17050000000000001, "76": 0.27579999999999999, "77": 0.1933, "78": 0.0613}}

    handle_data = data_handler(test_request, scorecard.main)

    response = handle_data.gen_response()
    print(response)








