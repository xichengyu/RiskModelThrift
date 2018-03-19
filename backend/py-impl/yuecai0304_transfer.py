# coding=utf-8
import pandas as pd
import traceback


def data_transfer(data):
    data1 = pd.DataFrame()
    try:
        data1['v1'] = data['SUM_VS_IM_TRD_CNT']+data['SUM_VS_SL_TRD_CNT']
        data1['v2'] = data['SUM_VS_IM_TRD_CNT']
        data1['v3'] = data['SUM_VS_SL_TRD_CNT']
        data1['v4(30)'] = data['SUM_VS_SL_CNT']+data['SUM_VS_IM_CNT']
        data1['v5(90)'] = min(data['MAX_VS_SL_DATE_DAYS'].item(), data['MAX_VS_IM_DATE_DAYS'].item())
        data1['v6(180)'] = data['SUM_VS_SL_CNT_30']+data['SUM_VS_IM_CNT_30']
        data1['v7'] = data['SUM_VS_SL_CNT_90']+data['SUM_VS_SL_CNT_90']
        data1['v8'] = data['SUM_VS_SL_CNT_180']+data['SUM_VS_IM_CNT_180']

        data1['w1'] = max(data['SUM_VC_SL_CNT'].item(), data['SUM_VP_SL_CNT'].item())
        data1['w2'] = data['SUM_VP_SL_CNT']
        data1['w3'] = max(data['SUM_VP_IM_TRD_CNT'].item(), data['SUM_VC_IM_TRD_CNT'].item())
        data1['w4(w2+w3)'] = max(data['SUM_VP_SL_TRD_CNT'].item(), data['SUM_VC_SL_TRD_CNT'].item())
        data1['w5(30)'] = data1['w3']+data1['w4(w2+w3)']
        data1['w6(90)'] = max(data['SUM_VC_SL_CNT_30D'].item(), data['SUM_VP_SL_CNT_30D'].item())
        data1['w7(180)'] = max(data['SUM_VC_SL_CNT_90D'].item(), data['SUM_VP_SL_CNT_90D'].item())
        data1['w8'] = max(data['SUM_VC_SL_CNT_180D'].item(), data['SUM_VP_SL_CNT_180D'].item())
        data1['w9'] = data['SUM_VWH_SLIM_CNT_HIST']
        data1['w10'] = data['SUM_FWH_SLIM_CNT_HIST']
        data1['w11'] = data['SUM_VWH_SLIM_CNT_1D30D']
        data1['w12'] = data['SUM_FWH_SLIM_CNT_1D30D']

        # 防止除数为0从而引起数据异常，故加上0.001
        data1['w13'] = max(data['MAX_VC_SL_DATE_DAYS'].item(), data['MAX_VP_SL_DATE_DAYS'].item())
        data1['w14'] = min(data['MIN_VC_SL_DATE_DAYS'].item(), data['MIN_VP_SL_DATE_DAYS'].item())
        data1['w15'] = max(data['MAX_VC_SL_AMT_360D'].item(), data['MAX_VP_SL_AMT_360D'].item())
        data1['w16'] = max(data['SUM_VC_SL_AMT'].item()/(data['SUM_VC_SL_CNT'].item() + 0.001),
                           data['SUM_VP_SL_AMT'].item()/(data['SUM_VP_SL_CNT'].item() + 0.001))
        data1['w17'] = max(data['MAX_VC_IM_AMT_360D'].item(), data['MAX_VP_IM_AMT_360D'].item())
        data1['w18'] = max(data['SUM_VC_IM_AMT'].item() / (data['SUM_VC_IM_CNT'].item() + 0.001),
                           data['SUM_VP_IM_AMT'].item() / (data['SUM_VP_IM_CNT'].item() + 0.001))
        return data1
    except:
        traceback.print_exc()
        return "data field missed!!"
