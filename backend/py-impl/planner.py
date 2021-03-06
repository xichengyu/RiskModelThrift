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
import os
from sklearn.externals import joblib
from pandas import DataFrame as df


fieldname_dict = {}
for file in os.listdir("./conf/fieldname"):
    if ".txt" in file:
        fieldname_dict[file.split(".")[0]] = [x.strip() for x in open("./conf/fieldname/%s" % file).readlines()]


class data_handler(object):
    def __init__(self, thrift_request, filtering_model):
        self.request = thrift_request
        self.model = filtering_model

    def get_data(self):
        try:
            X_dict = self.request["fieldData"]
            for fieldname in fieldname_dict[self.request["modelId"]]:
                X_dict[fieldname] = [X_dict[fieldname]]
        except:
            traceback.print_exc()
            return KeyError
        X = df(X_dict)[fieldname_dict[self.request["modelId"]]]
        X.replace("None", -1.0, inplace=True)
        X = X.astype(float)

        # print(X.dtypes)

        return X

    def gen_score(self):
        data = self.get_data()

        print(data)
        print(self.model)

        try:
            res = self.model(data)
            print(res)
            return res
        except:
            print(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc())
            return "request key error!"

    def gen_response(self):

        response = {"modelId": self.request["modelId"], "score": str(self.gen_score()[0]),
                    "responseId": self.request["queryId"], "idnoHash": self.request["idnoHash"],
                    "applyDate": self.request["applyDate"]}
        print(response)
        return json.dumps(response)


if __name__ == '__main__':
    # test_request = {"queryId": "123", "idnoHash": "12345", "applyDate": "2017-01-11 11:11:11", "fieldData": {"1": 52.0, "2": 0.26934999999999998, "3": 0.71509999999999996, "4": 462.0, "5": 55.0, "6": 53.0, "7": 0.46100000000000002, "8": 59.0, "9": 211.03, "10": 0.46999999999999997, "11": 2.0, "12": 51.0, "13": 86.234999999999999, "14": 2675.0, "15": 0.24560000000000001, "16": 0.23599999999999999, "17": 0.75360000000000005, "18": 0.52190000000000003, "19": 0.14999999999999999, "20": 0.25440000000000002, "21": 0.89380000000000004, "22": 0.0, "23": 0.0, "24": 92.247900000000001, "25": 0.045999999999999999, "26": 0.0, "27": 93.463999999999999, "28": 0.0, "29": 10.0, "30": 5.0039999999999996, "31": 57.182000000000002, "32": 60.552999999999997, "33": 59.0, "34": 55.0, "35": 52.0, "36": 47.0, "37": 39.194000000000003, "38": 82.891999999999996, "39": 60.552999999999997, "40": 25.003, "41": 0.22700000000000001, "42": 0.69030000000000002, "43": 0.082699999999999996, "44": 0.33329999999999999, "45": 0.16669999999999999, "46": 0.16669999999999999, "47": 0.33329999999999999, "48": 0.10000000000000001, "49": 0.30559999999999998, "50": 0.083299999999999999, "51": 0.1111, "52": 0.083299999999999999, "53": 0.076899999999999996, "54": 0.125, "55": 0.1111, "56": 0.1111, "57": 0.77780000000000005, "58": 0.1429, "59": 0.1429, "60": 0.1429, "61": 0.28570000000000001, "62": 0.28570000000000001, "63": 0.10000000000000001, "64": 0.20000000000000001, "65": 0.20000000000000001, "66": 0.33329999999999999, "67": 0.20000000000000001, "68": 0.20000000000000001, "69": 0.20000000000000001, "70": 0.20000000000000001, "71": 0.2414, "72": 0.034500000000000003, "73": 0.2069, "74": 0.29920000000000002, "75": 0.17050000000000001, "76": 0.27579999999999999, "77": 0.1933, "78": 0.0613}}

    # test_request = {"modelId": "LL0041", "idnoHash": "1ba967b1e0ccfa1cd94f6b0c1a6dfd7df42a255d44ad93c36686b5c8c514d3ee", "fieldData": {"SUM_NORMAL_SL_CNT_60D": None, "MAX_JL_SL_CNT_1D_90D": None, "SIGN_FIRST_DAYS_FQ": 35, "SUM_N2000Y_SL_CNT_1D_60D": None, "SUM_YX2000Y_SL_CNT_1D_90D": None, "SUM_XH2000Y_SL_CNT_7D": None, "MIN_JL_SL_CNT_1D_60D": None, "MIN_JL_SL_CNT_7D": None, "SUM_YX_SL_CNT_1D_30D": None, "PAY_SUMAMT_90D_FQ": 2200, "RATIO_OVER_SL_1D_90D360D": None, "RATIO_O7DO_SL_CNT_1D_180D": None, "PAYCNTAMTXD_NEDIV10_30D": 0, "RATIO_YXXH_SL_CNT_1D_360D": None, "PAYOVDMINXD_LT500_XUDAI_60D": None, "PAYCNTAMT_180D_FQ": 4, "MAX_JL_SL_CNT_180D": None, "PAYOVD_AVGXD_LT500_XUDAI_90D": -1, "PAYOVDAMTXD_LT500_XUDAI_7D": None, "PAYOVDMAXXD_LT500_XUDAI_90D": None, "SIGN_LAST_DAYS_FQ": 35, "PAY_LAST_DAYSXD": 18, "RATIO_O7DA_SL_CNT_1D_30D": None, "SUM_NORMAL_SL_TRD_CNT_1D_180D": None, "PASSCNTAMT_90DXD": 1, "RATIO_OVER_SL_1D_30D360D": None, "PAY_SUMAMT_180D_FQ": 2200, "SUM_NORMAL_SL_TRD_CNT_1D_60D": None, "PASSCNTAMT_180DXD": 1, "SEX": 1, "PASSMAXAMTXD": 1000, "SUM_O4D7D_SL_CNT_1D_90D": None, "PAYOVDCNTXD_LT500_XUDAI_90D": 0, "RATIO_O7DO_SL_CNT_1D_90D": None, "PAY_SUMAMT_90DXD": 3555.48, "PASS_SUMAMTXD": 1000, "PAYCNTAMTXD_NEDIV1": 1, "PAYCNTAMTXD_LT500_XUDAI": 0, "ID_NO_HASH": "1ba967b1e0ccfa1cd94f6b0c1a6dfd7df42a255d44ad93c36686b5c8c514d3ee", "PAYOVDAMTXD_LT500_XUDAI_90D": None, "PAY_SUMAMT_180DXD": 3555.48, "PASS_SUMAMT_90DXD": 1000, "SUM_XH_SL_CNT_HIST": None, "P2PMAX_AMT": 665, "SUM_O8D29D_SL_CNT_1D_30D": None, "RATIO_OVER_SL_1D_7D360D": None, "AVG_JL_SL_CNT_30D": None, "SIGNCNTTRD_180D_FQ": 1, "SIGNCNTTRD_FQ": 1, "SIGNCNTTRD_90DXD": 4, "SIGNCNTTRD_180DXD": 5, "PAYCNTAMT_90DXD": 4, "PAYCNTAMTXD_LT500_XUDAI_90D": 0, "PAYCNTAMTXD_NEDIV100_90D": 3, "PASS_LAST_DAYSXD": 53, "PAYOVD_AVGXD_LT500_XUDAI": -1, "PAYCNTAMTXD_NEDIV100": 3, "PASSMINAMTXD": 1000, "MAX_JL_SL_CNT_60D": None, "PAYCNTAMTXD": 4, "MAX_JL_SL_CNT_1D_180D": None, "AVG_JL_SL_CNT_180D": None, "MAX_JL_SL_CNT_1D_30D": None, "SUM_YX_SL_CNT_1D_180D": None, "PAYCNTAMTXD_NEDIV10": 1, "SUM_YX2000Y_SL_CNT_HIST": None, "PAYOVDAMTXD_LT500_XUDAI": None, "PAYCNTAMTXD_NEDIV1_60D": 1, "SUM_YX_SL_TRD_CNT_HIST": None, "MAX_JL_SL_CNT_7D": None, "SIGNCNTTRD_7DXD": 0, "SUM_XH2000Y_SL_CNT_HIST": None, "SUM_XH_SL_TRD_CNT_1D_90D": None, "SUM_NORMAL_SL_CNT_7D": None, "PAY_SUMAMT_30D_FQ": 2200, "PAYMAXAMTXD": 1415.48, "AVG_JL_SL_CNT_60D": None, "PAYCNTAMTXD_NEDIV10_90D": 1, "PAYOVDCNTXD_LT500_XUDAI_7D": 0, "AVG_JL_SL_CNT_1D_180D": None, "PAY_LAST_DAYS_FQ": 11, "PAYCNTAMT_180DXD": 4, "RATIO_YXXH_SL_CNT_1D_30D": None, "SUM_XH_SL_CNT_1D_180D": None, "SUM_NORMAL_SL_TRD_CNT_60D": None, "PAY_LAST_DAYSXD_LT200": 35, "SUM_O4D7D_SL_CNT_1D_30D": None, "SIGN_LAST_DAYSXD": 18, "SUM_OVER_SL_CNT_1D_90D": None, "RATIO_YXXH_SL_CNT_7D": None, "PASS_SUMAMT_180DXD": 1000, "SUM_XH_SL_TRD_CNT_1D_180D": None, "PAYCNTAMTXD_GT500_NXUDAI_90D": 0, "AGE": 31, "P2P_SUM_AMT": 1440, "SUM_NORMAL_SL_CNT_30D": None, "PASS_FIRST_DAYSXD": 53, "SUM_XH2000Y_SL_CNT_1D_360D": None, "RATIO_OVER_SL_CNT_30D": None, "PASS_SUMAMT_30DXD": None, "RATIO_YXXH_SL_CNT_1D_180D": None, "PAYTRDMIN_AMT": 20, "SUM_N2000Y_SL_CNT_30D": None, "AVG_JL_SL_CNT_1D_30D": None, "PAYOVDMAXXD_LT500_XUDAI_60D": None, "SUM_O8D29D_SL_CNT_1D_90D": None, "SUM_N2000Y_SL_CNT_HIST": None, "SUM_OVER_SL_TRD_CNT_1D_30D": None, "SUM_NORMAL_SL_TRD_CNT_1D_90D": None, "SIGN_FIRST_DAYSXD": 141, "RATIO_O7DO_SL_CNT_1D_60D": None, "PAYOVDCNTXD_LT500_XUDAI_60D": 0, "SUM_XH_SL_CNT_7D": None, "SUM_NORMAL_SL_TRD_CNT_7D": None, "PASS_SUMAMT_7DXD": None, "AVG_JL_SL_CNT_90D": None, "MAX_JL_SL_CNT_30D": None, "AVG_JL_SL_CNT_HIST": None, "PAYCNTAMT_SUDA_90D": 0, "PAYMAXAMT_FQ": 1000, "PAYCNTAMTXD_NEDIV100_60D": 3, "PAYMINAMTXD": 20, "PAY_SUMAMTXD": 3555.47998046875, "PAYCNTAMTXD_LT500_XUDAI_60D": 0, "RATIO_OVER_SL_1D_60D360D": None, "SUM_NORMAL_SL_CNT_1D_30D": None, "PAYCNTAMT_YUNTU": 0, "SIGNCNTTRDXD": 5, "PASSCNTAMTXD": 1, "RATIO_YXXH_SL_CNT_1D_90D": None, "SUM_N2000Y_SL_CNT_1D_90D": None, "PAYCNTAMT_YUNTU_60D": 0, "SUM_O2000Y_SL_CNT_1D_60D": None, "SUM_XH_SL_TRD_CNT_180D": None, "SUM_N2000Y_SL_CNT_7D": None, "PAY_SUMAMT_7DXD": None, "SUM_YX2000Y_SL_CNT_1D_60D": None, "SUM_NORMAL_SL_CNT_1D_360D": None, "PASSCNTAMT_30DXD": 0, "AVG_JL_SL_CNT_7D": None, "P2PMIN_AMT": 336.1, "SUM_NORMAL_SL_CNT_HIST": None, "SIGNCNTTRD_90D_FQ": 1, "AVG_JL_SL_CNT_1D_360D": None, "PAYCNTTRD_30DXD": 1, "PAYCNTAMTXD_BT200_NEDIV100_60D": 2, "SUM_XH_SL_CNT_1D_360D": None, "SUM_XH_SL_CNT_1D_30D": None, "PAYCNTAMT_SUDA": 0, "PAYOVDMINXD_LT500_XUDAI": None, "SUM_NORMAL_SL_TRD_CNT_1D_360D": None, "AVG_JL_SL_CNT_1D_90D": None, "SIGNCNTTRD_30DXD": 1, "SUM_O4D7D_SL_CNT_1D_60D": None, "RATIO_OVER_SL_CNT_7D": None, "SUM_NORMAL_SL_TRD_CNT_1D_30D": None, "SUM_XH_SL_CNT_180D": None, "SUM_O2000Y_SL_CNT_7D": None, "PAYOVDCNTXD_LT500_XUDAI": 0, "SUM_O2000Y_SL_CNT_1D_30D": None, "RATIO_O7DA_SL_CNT_7D": None, "P2PCNT_AMT": 3, "SUM_XH_SL_TRD_CNT_7D": None, "PAYOVDAMTXD_LT500_XUDAI_60D": None, "PAYTRDMAXCNT_60D": 1, "SUM_XH_SL_TRD_CNT_1D_360D": None, "PAY_SUMAMT_30DXD": 1000, "PAYCNTAMTXD_BT200_NEDIV100_90D": 2, "PAY_LAST_DAYSXD_NEDIV1": 38, "RATIO_OVER_SL_CNT_60D": None, "PAYOVD_AVGXD_LT500_XUDAI_7D": -1, "SUM_NORMAL_SL_CNT_1D_90D": None, "PAYMINAMT_FQ": 100, "PAYOVDMAXXD_LT500_XUDAI_30D": None, "RATIO_O7DO_SL_CNT_1D_30D": None, "AVG_JL_SL_CNT_1D_60D": None, "SUM_XH2000Y_SL_CNT_1D_180D": None, "SUM_O8D29D_SL_CNT_1D_60D": None, "MAX_JL_SL_CNT_90D": None, "PAYCNTAMT_FQ": 4, "MAX_JL_SL_CNT_1D_360D": None, "SUM_XH_SL_CNT_1D_90D": None, "AVG_JL_SL_CNT_360D": None, "PAY_FIRST_DAYSXD": 41, "PAYOVD_AVGXD_LT500_XUDAI_60D": -1, "PAYCNTTRDXD": 4, "SUM_N2000Y_SL_CNT_1D_30D": None, "PAYCNTAMTXD_BT200_NEDIV100": 2, "PASSCNTAMT_7DXD": 0, "SUM_O4D7D_SL_CNT_7D": None, "PAYOVDMAXXD_LT500_XUDAI": None, "PAY_SUMAMT_FQ": 2200, "PAYCNTAMT_30DXD": 1, "PAYCNTAMTXD_NEDIV10_60D": 1, "SUM_YX_SL_CNT_1D_60D": None, "PAY_FIRST_DAYS_FQ": 11, "PAYCNTAMTXD_NEDIV100_30D": 0, "PAYOVDMINXD_LT500_XUDAI_90D": None, "DT_APPLY": "2018-01-10 12:00:44", "PAYCNTAMT_SUDA_60D": 0, "PASSCNTTRD_7DXD": 0, "PASS_LAST_DAYS_FQ": None, "RATIO_YXXH_SL_CNT_1D_60D": None, "MAX_JL_SL_CNT_HIST": None}, "applyDate": "2018-01-11 17:54:59", "queryId": "f89e5a80-69b8-44af-8a0d-f9bf79448a5c"}
    # handle_data = data_handler(test_request, scorecard.main)

    # test_request = json.loads(open("request.txt").readlines()[0].strip()) 
    # handle_data = data_handler(test_request, joblib.load("../../RiskModelSystem/Model/stacked_16.pkl").predict)

    test_request = json.loads(open("request_LL0043.txt").readlines()[0].strip())
    print(test_request)
    handle_data = data_handler(test_request, joblib.load("../../RiskModelSystem/Model/yuecai_xgb_0304.m").predict)

    response = handle_data.gen_response()
    print(response)

