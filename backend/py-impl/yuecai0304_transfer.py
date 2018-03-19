# coding=utf-8
import pandas as pd
import traceback


def data_transfer(data):
    try:
        data['v1'] = data['SUM_VS_IM_TRD_CNT']+data['SUM_VS_SL_TRD_CNT']
        data['v2'] = data['SUM_VS_IM_TRD_CNT']
        data['v3'] = data['SUM_VS_SL_TRD_CNT']
        data['v4(30)'] = data['SUM_VS_SL_CNT']+data['SUM_VS_IM_CNT']
        data['v5(90)'] = min(data['MAX_VS_SL_DATE_DAYS'], data['MAX_VS_IM_DATE_DAYS'])
        data['v6(180)'] = data['SUM_VS_SL_CNT_30']+data['SUM_VS_IM_CNT_30']
        data['v7'] = data['SUM_VS_SL_CNT_90']+data['SUM_VS_SL_CNT_90']
        data['v8'] = data['SUM_VS_SL_CNT_180']+data['SUM_VS_IM_CNT_180']

        data['w1'] = max(data['SUM_VC_SL_CNT'], data['SUM_VP_SL_CNT'])
        data['w2'] = data['SUM_VP_SL_CNT']
        data['w3'] = max(data['SUM_VP_IM_TRD_CNT'], data['SUM_VC_IM_TRD_CNT'])
        data['w4(w2+w3)'] = max(data['SUM_VP_SL_TRD_CNT'], data['SUM_VC_SL_TRD_CNT'])
        data['w5(30)'] = data['w3']+data['w4(w2+w3)']
        data['w6(90)'] = max(data['SUM_VC_SL_CNT_30D'], data['SUM_VP_SL_CNT_30D'])
        data['w7(180)'] = max(data['SUM_VC_SL_CNT_90D'], data['SUM_VP_SL_CNT_90D'])
        data['w8'] = max(data['SUM_VC_SL_CNT_180D'], data['SUM_VP_SL_CNT_180D'])
        data['w9'] = data['SUM_VWH_SLIM_CNT_HIST']
        data['w10'] = data['SUM_FWH_SLIM_CNT_HIST']
        data['w11'] = data['SUM_VWH_SLIM_CNT_1D30D']
        data['w12'] = data['SUM_FWH_SLIM_CNT_1D30D']

        # 防止除数为0从而引起数据异常，故加上0.001
        data['w13'] = max(data['MAX_VC_SL_DATE_DAYS'], data['MAX_VP_SL_DATE_DAYS'])
        data['w14'] = min(data['MIN_VC_SL_DATE_DAYS'], data['MIN_VP_SL_DATE_DAYS'])
        data['w15'] = max(data['MAX_VC_SL_AMT_360D'], data['MAX_VP_SL_AMT_360D'])
        data['w16'] = max(data['SUM_VC_SL_AMT']/(data['SUM_VC_SL_CNT'] + 0.001),
                           data['SUM_VP_SL_AMT']/(data['SUM_VP_SL_CNT'] + 0.001))
        data['w17'] = max(data['MAX_VC_IM_AMT_360D'], data['MAX_VP_IM_AMT_360D'])
        data['w18'] = max(data['SUM_VC_IM_AMT'] / (data['SUM_VC_IM_CNT'] + 0.001),
                           data['SUM_VP_IM_AMT'] / (data['SUM_VP_IM_CNT'] + 0.001))
        return data
    except:
        traceback.print_exc()
        return "data field missed!!"
