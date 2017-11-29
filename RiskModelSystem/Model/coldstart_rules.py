# coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from random import choice
import traceback
import random
import re
import json
import time


def test(thrift_request, data):
    plans = []
    try:
        for i in range(3):
            filtered_data = {}
            for k, v in data.items():
                filtered_data[k] = choice(v)
            plans.append(filtered_data)
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return plans
    # output in list[dict] format, e.g. [{"channel_1": "sid1", "channel_2": "sid2"}, {"channel_1": "sid3", "channel_2": "sid4"}]


classi_dict = {
    "火锅": ["火锅"],
    "特色地方菜": ["杭帮", "江浙菜", "川菜", "湘菜", "粤菜", "台湾菜", "东南亚菜", "创意菜", "东北菜", "其他"],
    "自助餐": ["自助餐"],
    "甜点饮品": ["咖啡厅", "面包甜点", "茶馆", "酒吧"],
    "料理": ["日本料理", "韩国料理"],
    "烧烤": ["烧烤"],
    "西餐": ["西餐"],
    "简餐": ["小吃快餐", "面馆"],
    "海鲜": ["海鲜"]
}

rela_atmos_dict = {
    0: ["情侣约会"],
    1: ["家庭聚会"],
    2: ["商务宴请"],
    3: ["朋友聚餐", "随便吃吃", "休闲小憩"],
    4: ["朋友聚餐", "随便吃吃", "休闲小憩"],
    5: ["朋友聚餐", "随便吃吃", "休闲小憩"]
}

tag_channel_dict = {
    "酒店住宿类": "酒店", "美容类": "丽人", "休闲娱乐类": "休闲娱乐", "影音类": "电影",
    "火锅": "美食", "特色地方菜": "美食", "自助餐": "美食", "甜点饮品": "美食",
    "料理": "美食", "烧烤": "美食", "西餐": "美食", "简餐": "美食", "海鲜": "美食"
}

chinese_num_dict = {
    "一": "1",
    "二": "2",
    "两": "2",
    "三": "3",
    "四": "4",
    "五": "5",
    "六": "6",
    "七": "7",
    "八": "8",
    "九": "9",
    "十": "10",
    "十一": "11",
    "十二": "12",
}

classi_hour_dict = {
    "小吃快餐": 1, "面馆": 1, "咖啡厅": 1, "面包甜点": 1, "茶馆": 1, "自助餐": 2, "西餐": 2,
    "火锅": 1.5, "杭帮": 1.5, "江浙菜": 1.5, "川菜": 1.5, "湘菜": 1.5, "粤菜": 1.5, "台湾菜": 1.5, "东南亚菜": 1.5, "创意菜": 1.5,
    "东北菜": 1.5, "其他": 1.5, "日本料理": 1.5, "韩国料理": 1.5, "烧烤": 1.5, "海鲜": 1.5,
    "电影院": 2.5,
    "茶馆": 1, "足疗按摩": 2, "酒吧":3, "网吧网咖":3, "密室":3, "桌球馆":3, "游乐游艺":3, "桌面游戏":4, "KTV":4, "棋牌室":4, "洗浴":4,
    "美甲美睫":1, "美容":2, "SPA":2, "美发":3
}

channel_weight_dict = {
    "美食": 1,
    "酒店": 1,
    "电影": 1,
    "休闲娱乐": 1,
    "丽人": 1,
}


def get_shopscore(shop_score):
    # print shop_score
    score_dic = {}
    try:
        shop_score = shop_score.replace('：', ':')
        # print shop_score
        score_list = shop_score.split(",")
        for score in score_list:
            tmp = score.split(":")
            # print tmp
            score_dic[tmp[0]] = float(tmp[1]) if tmp[1] != '' else 0
    except:
        # print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), ("\033[0m"), traceback.format_exc()     #输出结果应该为空
        pass
    return score_dic


def weighted_choice(channels, weights):
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            res = channels[i]
            channels.pop(i)
            weights.pop(i)
            return res, channels, weights


def repeatable_weighted_choice(cnt, channels, weights):
    res = []
    try:
        for i in range(cnt):
            tmp = weighted_choice(channels, weights)
            res.append(tmp[0])
            channels = tmp[1]
            weights = tmp[2]
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return res


def normalize_openning_hour(openning_hour):
    res = ''
    try:
        for char in unicode(openning_hour):
            if char in ['：', '.', ';', '；']:
                res += ':'
            elif char == ' ':
                res += ''
            elif char in ['－', '—', '_']:
                res += '-'
            else:
                res += char
        res = res.replace('::', ':')
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return res.encode("utf8")


def normalize_hour_system(hour_list):
    try:
        first_hour = int(hour_list[0].split(':')[0])
        first_min = hour_list[0].split(':')[1] if len(hour_list[0].split(':')) == 2 else '00'
        second_hour = int(hour_list[1].split(':')[0])
        second_min = hour_list[1].split(':')[1] if len(hour_list[1].split(':')) == 2 else '00'
        # print first_hour, first_min, second_hour, second_min
        if 0 < first_hour <= 6 and 0 < second_hour <= 6:
            hour_list[0] = str(first_hour + 12) + ':' + first_min
        elif 6 < second_hour <= 12:
            hour_list[1] = str(second_hour + 12) + ':' + second_min
            if first_hour < 5:
                hour_list[0] = str(first_hour + 12) + ':' + first_min
        if second_hour == 0 and second_min == '00':
            hour_list[1] = '24:00'
        if first_hour == 24:
            hour_list[0] = '00:00'
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return hour_list


def get_pure_hour_min(pure_time):
    pure_hour = ''
    pure_min = ''
    try:
        tmp = pure_time.split(':')
        pure_hour = tmp[0]
        pure_min = tmp[1] if len(tmp) == 2 else '00'
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return pure_hour, pure_min


def get_max_time(time_a, time_b):
    Max = time_a
    try:
        tmp_a = get_pure_hour_min(time_a)
        tmp_b = get_pure_hour_min(time_b)
        if int(tmp_a[0]) < int(tmp_b[0]):
            Max = time_b
        elif int(tmp_a[0]) == int(tmp_b[0]):
            if int(tmp_a[1]) < int(tmp_b[1]):
                Max = time_b
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return Max


def get_min_time(time_a, time_b):
    Min = time_a
    try:
        tmp_a = get_pure_hour_min(time_a)
        tmp_b = get_pure_hour_min(time_b)
        if int(tmp_a[0]) > int(tmp_b[0]):
            Min = time_b
        elif int(tmp_a[0]) == int(tmp_b[0]):
            if int(tmp_a[1]) > int(tmp_b[1]):
                Min = time_b
        else:
            if int(tmp_a[0]) < 6 and int(tmp_b[0]) > 20:
                Min = time_b
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return Min


def initialize_timelist(time_list):
    starthour = -1
    endhour = -1
    try:
        tmp_a = get_pure_hour_min(time_list[0])
        tmp_b = get_pure_hour_min(time_list[1])
        starthour = float(tmp_a[0])+float(tmp_a[1])/60 if tmp_a[1] != '' else float(tmp_a[0])
        endhour = float(tmp_b[0])+float(tmp_b[1])/60 if tmp_b[1] != '' else float(tmp_b[0])
        if starthour > endhour:
            endhour += 24
    except:
        # print tmp_a, tmp_b
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return [starthour, endhour]


def get_covered_time(time_list_a, time_list_b):
    res = []
    try:
        hour_list_a = initialize_timelist(time_list_a)
        hour_list_b = initialize_timelist(time_list_b)
        if hour_list_a[1] <= hour_list_b[0] or hour_list_b[1] <= hour_list_a[0]:
            pass
        else:
            res.append(time_list_b[0] if hour_list_a[0] < hour_list_b[0] else time_list_a[0])
            res.append(time_list_b[1] if hour_list_a[1] > hour_list_b[1] else time_list_a[1])
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    # print 'get_covered_time: ', time_list_a, time_list_b, res
    return res


def get_uncovered_hour(selected_interval_int, interval_int, classi_hour, activity_interval=0.167):
    res = []
    try:
        if selected_interval_int[0] >= interval_int[1] and selected_interval_int[1] - selected_interval_int[0] - activity_interval >= classi_hour:
            res.append([selected_interval_int[0] + activity_interval, selected_interval_int[1]])
        elif selected_interval_int[1] <= interval_int[0] and selected_interval_int[1] - selected_interval_int[0] - activity_interval >= classi_hour:
            res.append([selected_interval_int[0], selected_interval_int[1] - activity_interval])
        elif interval_int[0] <= selected_interval_int[0] and selected_interval_int[1] <= interval_int[1]:
            pass
        elif interval_int[0] >= selected_interval_int[0] and interval_int[1] <= selected_interval_int[1]:
            if interval_int[0]-activity_interval - selected_interval_int[0] >= classi_hour:
                res.append([selected_interval_int[0], interval_int[0]-activity_interval])
            if selected_interval_int[1] - interval_int[1]-activity_interval >= classi_hour:
                res.append([interval_int[1]+activity_interval, selected_interval_int[1]])
        elif interval_int[0] < selected_interval_int[0] < interval_int[1] < selected_interval_int[1]:
            if selected_interval_int[1] - interval_int[1] - activity_interval >= classi_hour:
                res.append([interval_int[1] + activity_interval, selected_interval_int[1]])
        elif selected_interval_int[0] < interval_int[0] < selected_interval_int[1] < interval_int[1]:
            if interval_int[0] - selected_interval_int[0]-activity_interval >= classi_hour:
                res.append([selected_interval_int[0], interval_int[0] - activity_interval])
        else:
            pass
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return res


def if_recommend_hotel(time_a, time_b, time_c):
    recommend_hotel = True
    try:
        tmp_a = get_pure_hour_min(time_a)
        tmp_b = get_pure_hour_min(time_b)
        tmp_c = get_pure_hour_min(time_c)
        starthour = int(tmp_a[0])+float(tmp_a[1])/60
        endhour = int(tmp_b[0])+float(tmp_b[1])/60
        line = int(tmp_c[0])+float(tmp_c[1])/60
        if starthour < endhour <= line:
            recommend_hotel = False
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return recommend_hotel



def screen_illegal_time(time_list):
    res = []
    try:
        for i, v in enumerate(time_list):
            if v.find(':') == -1 and v.find('-') == -1 and int(v) > 24:
                continue
            res.append(v)
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return res


def normalize_time_list(time_list, default, source=None):
    res = []
    time_list_length = len(time_list)
    try:
        if time_list_length < 1:
            res.append(default)
            # print res, source
        elif time_list_length == 1:
            # print time_list, source
            tmp = re.findall(r'[0-9]{1,2}:?[0-9]{,2}', time_list[0])
            tmp = screen_illegal_time(tmp)
            if len(tmp) < 2:
                # print tmp, time_list, source
                tmp = default
            else:
                tmp = normalize_hour_system(tmp)
            res.append(tmp)
            # print res, source
        elif time_list_length >= 2:
            tmp = []
            for i, v in enumerate(time_list):
                tmp += screen_illegal_time(re.findall(r'[0-9]{1,2}:?[0-9]{,2}', v))
                if len(tmp) == 2:
                    if int(tmp[0].split(':')[0]) == 24:
                        tmp[0] = '00:00'
                    if int(tmp[1].split(':')[0]) == 0:
                        tmp[1] = '24:00'
                    res.append(tmp)
                    tmp = []
            if len(res) == 1:
                res[0] = normalize_hour_system(res[0])
            elif len(res) == 2:
                first_first = int(res[0][0].split(':')[0])
                first_second = int(res[0][1].split(':')[0])
                second_first = int(res[1][0].split(':')[0])
                second_second = int(res[1][1].split(':')[0])

                if abs(first_first-second_first) <= 2 or abs(first_second-second_second) <= 2:
                    tmp = [[]]
                    tmp[0].append(get_max_time(res[0][0], res[1][0]))
                    tmp[0].append(get_min_time(res[0][1], res[1][1]))
                    # print res, tmp, source
                    res = tmp
                elif first_first < first_second <= second_first < second_second:
                    pass
                else:
                    if int(get_pure_hour_min(res[1][0])[0]) > 12 and int(get_pure_hour_min(res[1][1])[0]) > 12:
                        tmp_1 = get_pure_hour_min(res[0][1])
                        if int(tmp_1[0]) < 12:
                            res[0][1] = str(int(tmp_1[0])+12) + ':' + tmp_1[1]
            else:
                # print res, source
                pass
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    if not res:
        res.append(default)
    return res


def set_default_openning_hour(channel):
    default_openning_hour = []
    try:
        if channel == "酒店":
            default_openning_hour = ["00:00", "24:00"]
        elif channel == "丽人":
            default_openning_hour = ["10:00", "21:00"]
        elif channel == "美食":
            default_openning_hour = ["9:00", "22:00"]
        elif channel == "休闲娱乐":
            default_openning_hour = ["9:30", "23:00"]
        elif channel == "电影":
            default_openning_hour = ["10:00", "22:00"]
        else:
            pass
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return default_openning_hour


def openning_hour_extractor(openning_hour, default=None):   # 获取标准化的店铺营业时间，例：["11:00", "2:00"], 24小时制
    if default is None or not default:
        default = ["9:00", "22:00"]
    res = []
    global chinese_num_dict
    try:
        tmp = normalize_openning_hour(openning_hour)
        if tmp.find("全天") != -1 or tmp.find("24小时") != -1 or tmp == '每天':
            res = ['00:00', '24:00']
        else:
            res = re.findall(r'(?:早上|上午|中午|下午|晚上|凌晨)[0-9]{1,2}:[0-9]{,2}-+(?:早上|上午|中午|下午|晚上|凌晨)[0-9]{1,2}:[0-9]{,2}', tmp)
            if len(res) > 0:
                tmp = []
                for i, v in enumerate(res):
                    tmp += re.findall(r'(?:早上|上午|中午|下午|晚上|凌晨)[0-9]{1,2}:[0-9]{,2}', res[i])
                for i, v in enumerate(tmp):
                    if v.find('下午') != -1 or v.find('晚上') != -1:
                        pure_time = ''.join(re.findall(r'[0-9]{1,2}:[0-9]{,2}', v))
                        pure = get_pure_hour_min(pure_time)
                        pure_hour = int(pure[0])
                        pure_min = pure[1]
                        tmp[i] = str(pure_hour+12) + ':' + pure_min if pure_hour <= 12 else pure_time
                    else:
                        tmp[i] = ''.join(re.findall(r'[0-9]{1,2}:[0-9]{,2}', v))
                res = tmp
                # print res, openning_hour
            if not res:
                res = re.findall(r'[0-9]{1,2}:?[0-9]{,2}-+[0-9]{1,2}:?[0-9]{,2}', tmp)
            if not res:
                res = re.findall(r'[0-9]{1,2}:[0-9]{,2}|(?:早上|上午|中午|下午|晚上|凌晨)?[0-9]{1,2}点|(?:早上|上午|中午|'
                                 r'下午|晚上|凌晨)?(?:十一|十二|十|一|二|三|四|五|六|七|八|九|两)点|营业结束|[0-9]{4}', tmp)
                if len(res) > 0:
                    for i, v in enumerate(res):
                        loc = v.find('点')
                        if loc > -1:
                            num = res[i][:loc]
                            pure_time = ''.join(re.findall(r'[0-9]{1,2}|(?:十一|十二|十|一|二|三|四|五|六|七|八|九|两)', num))
                            pure_hour = chinese_num_dict[pure_time] if pure_time in chinese_num_dict else pure_time
                            if num.find('下午') != -1:
                                res[i] = str(int(pure_hour)+12) + ':00' if int(pure_hour) <= 12 else pure_hour + ':00'
                            elif num.find('晚上') != -1:
                                res[i] = str(int(pure_hour)+12) + ':00' if 5 <= int(pure_hour) <= 12 else pure_hour + ':00'
                            else:
                                res[i] = pure_hour + ':00'
                        elif res[i] == '营业结束':
                            res[i] = '24:00'
                        elif res[i].find(':') == -1:
                            res[i] = res[i][:1] + ':' + res[i][2:]
        # if openning_hour.find('点') != -1:
            # print res, openning_hour
        res = normalize_time_list(res, default, tmp)
        # print res, openning_hour
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return res


def get_covered_interval(openning_hour, trip_time):       # trip_time = [starttime, endtime]
    res = []
    try:
        for shop_interval in openning_hour:
            for trip_interval in trip_time:
                tmp = get_covered_time(shop_interval, trip_interval)
                if len(tmp) > 0:
                    res.append(tmp)
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return res


def delete_some(channel_data, classi_in_list):
    tmp = []
    try:
        for shop in channel_data:
            if shop[7] not in classi_in_list:
                tmp.append(shop)
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return tmp


def save_some(channel_data, classi_in_list):
    tmp = []
    try:
        for shop in channel_data:
            if shop[7] in classi_in_list:
                tmp.append(shop)
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return tmp


def get_covered_interval_hour_dict(covered_interval):
    dic = {}
    try:
        for item in covered_interval:
            tmp = initialize_timelist(item)
            dic[json.dumps(item)] = tmp[1] - tmp[0]
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return dic


def get_top_N(dic, n):
    dic = sorted(dic.iteritems(), key=lambda d: d[1], reverse=True)
    if len(dic) <= n:
        return dic
    else:
        return dic[:n]


def float_to_time(float_num):
    time = ''
    try:
        tmp = int(float_num * 60 + 0.5)
        hour = (tmp/60)%24
        miniute = tmp%60
        time += '00:' if hour == 0 else str(hour) + ":"
        time += '00' if miniute == 0 else str(miniute)
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return time


class rules(object):

    """
    Field Index of Shop:

    0:sid, 1:surl, 2:name, 3:city, 4:address, 5:business_circle, 6:channel, 7:classi, 8:telephone, 9:openning_hours,
    10:shop_score, 11:shop_star, 12:comment_keyword, 13:comment_num, 14:avg_cost, 15:lat, 16:lon, 17:pid, 18:purl,
    19:atmosphere, 20:createtime, 21:lastmodtime

    Field Index of Business_Circle:

    0:cdid, 1:name, 2:city, 3:area, 4:latitude, 5:longitude
    """

    def __init__(self, thrift_request, responsed_data):
        self.request = thrift_request
        self.data = responsed_data
        self.business_circle = self.data.pop("algo_commercial_district")

    # 先行规则
    def PR001(self):     # 出行时间 & 商圈过滤
        shoptrip_interval_hour = {}
        shop_classi_hour = {}
        try:
            user_location = ''
            try:
                user_location = self.business_circle[0][1]
            except:
                print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
                pass
            for channel in self.data.keys():    # 所有频道
                tmp = []
                for shop in self.data[channel]:     # 各个频道中的每家商户
                    if shop[5] != user_location:    # 商圈过滤
                        continue
                    # else:
                        # print user_location, shop[5]
                        # pass
                    shoptrip_covered_interval = get_covered_interval(openning_hour_extractor(shop[9], set_default_openning_hour(channel)), [[self.request['startTime'], self.request['endTime']]])
                    if not shoptrip_covered_interval:
                        continue
                    if channel not in ['酒店']:  # 酒店无规定活动时长
                        classi = shop[7].split('/')
                        classi_hour = -1        # 获取商户规定活动时长
                        for item in classi:
                            if item.encode('utf8') in classi_hour_dict:
                                classi_hour = classi_hour_dict[item.encode('utf8')]
                                break
                        shoptrip_covered_interval_hour_dict = get_covered_interval_hour_dict(shoptrip_covered_interval)
                        if classi_hour > 0:
                            shop_classi_hour[shop[0]] = classi_hour
                            key_time_lists = shoptrip_covered_interval_hour_dict.keys()
                            for key in key_time_lists:
                                if shoptrip_covered_interval_hour_dict[key] < classi_hour:
                                    shoptrip_covered_interval_hour_dict.pop(key)
                        else:
                            continue
                    else:
                        shoptrip_covered_interval_hour_dict = get_covered_interval_hour_dict(shoptrip_covered_interval)
                        shop_classi_hour[shop[0]] = 0
                    if not shoptrip_covered_interval_hour_dict:     # 删除营业时间不在出行时间内的店铺
                        continue
                    else:
                        shoptrip_interval_hour[shop[0]] = shoptrip_covered_interval_hour_dict
                        tmp.append(shop)
                self.data[channel] = tmp
            # for k, v in self.data.items():
                # print k, len(v)
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return shoptrip_interval_hour, shop_classi_hour

    def PR002(self):    # 活动时长
        starttime = get_pure_hour_min(self.request['startTime'])
        starthour = int(starttime[0])+float(starttime[1])/60
        endtime = get_pure_hour_min(self.request['endTime'])
        endhour = int(endtime[0])+float(endtime[1])/60
        interval = endhour-starthour if starthour <= endhour else 24-(starthour-endhour)
        try:
            if interval < 3:            # 在原始数据上做删除操作
                self.data["休闲娱乐"] = delete_some(self.data["休闲娱乐"], ["桌面游戏", "KTV", "棋牌室", "洗浴"])
                self.data["丽人"] = delete_some(self.data["丽人"], ["美发"])
            if interval < 2:
                tmp = []
                for shop in self.data["美食"]:
                    is_western = False
                    classi = shop[7].split("/")
                    for item in classi:
                        if item in ["西餐", "自助餐"]:
                            is_western = True
                            break
                    if not is_western:
                        tmp.append(shop)
                self.data["美食"] = tmp
                self.data.pop("电影")
                self.data["休闲娱乐"] = delete_some(self.data["休闲娱乐"], ["足疗按摩", "酒吧", "网吧网咖", "密室", "桌球馆", "游乐游艺"])
                self.data["丽人"] = delete_some(self.data["丽人"], ["美容/SPA"])
            if interval < 1:
                self.data.pop("休闲娱乐")
                self.data["丽人"] = delete_some(self.data["丽人"], ["美甲美睫"])
                tmp = []
                for shop in self.data["美食"]:
                    classi = shop[7].split("/")
                    for item in classi:
                        if item in ["咖啡厅", "面包甜点", "茶馆", "酒吧", "小吃快餐", "面馆"]:   #甜点饮品&简餐
                            tmp.append(shop)
                            break
                self.data["美食"] = tmp
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return self.data

    def PR003(self):    # 标签    0：情侣 1：家人 2：客户 3：朋友 4：闺蜜 5：兄弟 6:自己
        try:
            if "购物" in self.data:
                self.data.pop("购物")     # 冷启动不推荐购物
            if self.request["relation"] != 4:
                self.data.pop("丽人")
            if self.request["relation"] != 5:
                self.data["休闲娱乐"] = delete_some(self.data["休闲娱乐"], ["网吧网咖", "桌球馆"])
            if self.request["relation"] == 2:
                self.data.pop("电影")
            if self.request["count"] < 3:     # 0：1人 1：2人 2：3-4人 3：5-10人 4：11人及以上
                self.data["休闲娱乐"] = delete_some(self.data["休闲娱乐"], ["桌面游戏"])
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return self.data

    def PR004(self):    # 酒店规则
        try:
            residentcity = self.request['residentCity'].split(',')
            currentcity = self.request['currentLocation']
            is_resident = False if currentcity.find(residentcity[1]) == -1 else True
            if (not is_resident or self.request["relation"] == 0) and if_recommend_hotel(self.request['startTime'],
                                                                                         self.request['endTime'], '21:00'):
                pass
            else:
                self.data.pop('酒店')
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return self.data

    # 推荐规则
    def RR001(self):    # 美食类基础评分
        food_dic = {}
        A = unicode('口味'); B = unicode('环境'); C = unicode('服务')
        try:
            for shop in self.data["美食"]:
                try:
                    score = get_shopscore(shop[10])
                    if len(score) == 3:
                        if self.request["relation"] == 0:
                            food_dic[shop[0]] = 0.3*score[A] + 0.5*score[B] + 0.2*score[C]
                        elif self.request["relation"] == 1:
                            food_dic[shop[0]] = 0.5*score[A] + 0.3*score[B] + 0.2*score[C]
                        elif self.request["relation"] == 2:
                            food_dic[shop[0]] = 0.3*score[A] + 0.4*score[B] + 0.3*score[C]
                        else:
                            food_dic[shop[0]] = 0.4*score[A] + 0.3*score[B] + 0.3*score[C]
                    else:
                        food_dic[shop[0]] = 0
                    food_dic[shop[0]] = self.RR002(food_dic[shop[0]], shop)
                    food_dic[shop[0]] = self.RR003(food_dic[shop[0]], shop)
                except:
                    # print score
                    food_dic[shop[0]] = 0
                    print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
                    pass
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return get_top_N(food_dic, 10)

    def RR002(self, food_score, shop):    # 美食类正反馈
        global classi_dict
        global rela_atmos_dict
        try:
            if shop[-3] in rela_atmos_dict[self.request["relation"]]:
                food_score += 0.3*food_score
            classi = shop[7].split("/")
            for item in classi:
                for tag in self.request["interestName"].split(","):
                    if item in classi_dict[tag.encode('utf8')]:
                        food_score += 0.3*food_score
                        break
            if shop[13] != "" and int(shop[13]) > 1000:
                food_score += 0.2*food_score
            if shop[11] == "五星商户" or shop[11] == "准五星商户":
                food_score += 0.2*food_score
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return food_score

    def RR003(self, food_score, shop):    # 美食类负反馈
        global classi_dict
        try:
            classi = shop[7].split("/")
            for item in classi:
                if (self.request["relation"] == 2 and item in classi_dict["简餐"]) or \
                        (self.request["relation"] == 1 and
                        (item in classi_dict["西餐"] or item in classi_dict["料理"])):
                    # print '2A'*10
                    food_score -= 0.3 * food_score
                    break
            for item in classi:
                if self.request["count"] >= 3 and (item in classi_dict["西餐"] or item in classi_dict["料理"]):
                    # print '2B'*10
                    food_score -= 0.3 * food_score
                    break
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return food_score

    def RR004(self):    # 影音类基础评分
        movie_dic = {}
        try:
            for shop in self.data["电影"]:
                try:
                    score = get_shopscore(shop[10])
                    # print '-'*10, score
                    movie_dic[shop[0]] = sum(score.values())/3
                    # movie_dic[shop[0]] = self.RR006(movie_dic[shop[0]], shop)
                    # movie_dic[shop[0]] = self.RR007(movie_dic[shop[0]], shop)
                except:
                    pass
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return get_top_N(movie_dic, 5)

    def RR005(self):    # 休闲娱乐类基础评分
        leisure_dic = {}
        try:
            for shop in self.data["休闲娱乐"]:
                try:
                    score = get_shopscore(shop[10])
                    # print '-'*10, score
                    leisure_dic[shop[0]] = sum(score.values())/3
                    leisure_dic[shop[0]] = self.RR006(leisure_dic[shop[0]], shop)
                    leisure_dic[shop[0]] = self.RR007(leisure_dic[shop[0]], shop)
                except:
                    pass
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return get_top_N(leisure_dic, 10)

    def RR006(self, leisure_score, shop):    # 休闲娱乐类正反馈
        try:
            if self.request["relation"] == 2 and shop[7] in ["茶馆", "KTV", "足疗按摩", "洗浴"]:
                leisure_score += 0.3 * leisure_score
            if self.request["relation"] == 1 and shop[7] in ["茶馆", "棋牌室"]:
                leisure_score += 0.3 * leisure_score
            if shop[13] != "" and int(shop[13]) > 1000:
                leisure_score += 0.2*leisure_score
            if shop[11] == "五星商户" or shop[11] == "准五星商户":
                leisure_score += 0.2*leisure_score
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return leisure_score

    def RR007(self, leisure_score, shop):    # 休闲娱乐类负反馈
        try:
            if self.request["relation"] == 2 and shop[7] in ["密室", "游乐游艺", "桌面游戏", "棋牌室"]:
                leisure_score -= 0.3 * leisure_score
            if self.request["relation"] == 1 and shop[7] in ["酒吧", "密室", "桌球馆", "桌面游戏"]:
                leisure_score -= 0.3 * leisure_score
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return leisure_score

    def RR008(self):    # 美容类基础评分
        beauty_dic = {}
        try:
            for shop in self.data["丽人"]:
                try:
                    score = get_shopscore(shop[10])
                    beauty_dic[shop[0]] = sum(score.values())/3
                    beauty_dic[shop[0]] = self.RR009(beauty_dic[shop[0]], shop)
                except:
                    pass
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return get_top_N(beauty_dic, 10)

    def RR009(self, beauty_score, shop):    # 美容类正反馈
        try:
            if shop[13] != "" and int(shop[13]) > 1000:
                beauty_score += 0.2*beauty_score
            if shop[11] == "五星商户" or shop[11] == "准五星商户":
                beauty_score += 0.2*beauty_score
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return beauty_score

    def RR010(self):    # 酒店住宿类基础评分
        hotel_dic = {}
        try:
            for shop in self.data["酒店"]:
                try:
                    score = get_shopscore(shop[10])
                    hotel_dic[shop[0]] = sum(score.values())/3
                    hotel_dic[shop[0]] = self.RR011(hotel_dic[shop[0]], shop)
                    hotel_dic[shop[0]] = self.RR012(hotel_dic[shop[0]], shop)
                except:
                    pass
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return get_top_N(hotel_dic, 10)

    def RR011(self, hotel_score, shop):    # 酒店住宿类正反馈
        try:
            if self.request["relation"] == 0 and shop[7] in ["情侣酒店", "主题酒店"]:
                hotel_score += 0.3*hotel_score
            if self.request["relation"] == 2 and shop[7] in ["商务酒店"]:
                hotel_score += 0.3*hotel_score
            if shop[5] in ["西湖北线/黄龙", "龙井/虎跑", "高新文教区", "古墩路沿线", "小和山", "西溪", "灵隐", "转塘", "三墩镇",
                           "城西银泰"] and shop[7] in ["度假酒店"]:
                hotel_score += 0.3*hotel_score
            if shop[13] != "" and int(shop[13]) > 1000:
                hotel_score += 0.2*hotel_score
            if shop[11] == "五星商户" or shop[11] == "准五星商户":
                hotel_score += 0.2*hotel_score
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return hotel_score

    def RR012(self, hotel_score, shop):    # 酒店住宿类负反馈
        try:
            if (self.request["relation"] == 2 and shop[7] in ["情侣酒店", "主题酒店", "青年旅舍", "客栈旅舍", "民宿"]) or \
                (self.request["relation"] == 1 and shop[7] in ["情侣酒店", "主题酒店", "青年旅舍", "客栈旅舍"]) or \
                    (self.request["relation"] >= 3 and shop[7] in ["情侣酒店"]):
                hotel_score -= 0.3*hotel_score
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return hotel_score

    def get_topN_shop_info(self, shoptrip_interval_hour_all, shop_classi_hour_all):     # 获取每个频道(channel)排名前N位的商户信息
        shoptrip_interval_hour_topN = {}
        shop_classi_hour_topN = {}
        try:
            food_score_topN = self.RR001()  # 0: 美食
            movie_score_topN = self.RR004()  # 1: 电影
            leisure_score_topN = self.RR005()  # 2: 休闲娱乐
            beauty_score_topN = self.RR008()  # 3: 丽人
            hotel_score_topN = self.RR010()  # 4: 酒店

            if len(food_score_topN) > 0:
                shoptrip_interval_hour_topN['美食'] = {}
                shop_classi_hour_topN["美食"] = {}
                for key in food_score_topN:
                    try:
                        shoptrip_interval_hour_topN["美食"][key[0]] = shoptrip_interval_hour_all[key[0]]
                        shop_classi_hour_topN["美食"][key[0]] = shop_classi_hour_all[key[0]]
                    except:
                        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
                        continue
            if len(movie_score_topN) > 0:
                shoptrip_interval_hour_topN['电影'] = {}
                shop_classi_hour_topN['电影'] = {}
                for key in movie_score_topN:
                    try:
                        shoptrip_interval_hour_topN['电影'][key[0]] = shoptrip_interval_hour_all[key[0]]
                        shop_classi_hour_topN['电影'][key[0]] = shop_classi_hour_all[key[0]]
                    except:
                        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
                        continue
            if len(leisure_score_topN) > 0:
                shoptrip_interval_hour_topN['休闲娱乐'] = {}
                shop_classi_hour_topN['休闲娱乐'] = {}
                for key in leisure_score_topN:
                    try:
                        shoptrip_interval_hour_topN['休闲娱乐'][key[0]] = shoptrip_interval_hour_all[key[0]]
                        shop_classi_hour_topN['休闲娱乐'][key[0]] = shop_classi_hour_all[key[0]]
                    except:
                        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
                        continue
            if len(beauty_score_topN) > 0:
                shoptrip_interval_hour_topN['丽人'] = {}
                shop_classi_hour_topN['丽人'] = {}
                for key in beauty_score_topN:
                    try:
                        shoptrip_interval_hour_topN['丽人'][key[0]] = shoptrip_interval_hour_all[key[0]]
                        shop_classi_hour_topN['丽人'][key[0]] = shop_classi_hour_all[key[0]]
                    except:
                        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
                        continue
            if len(hotel_score_topN) > 0:
                shoptrip_interval_hour_topN['酒店'] = {}
                shop_classi_hour_topN['酒店'] = {}
                for key in hotel_score_topN:
                    try:
                        shoptrip_interval_hour_topN['酒店'][key[0]] = shoptrip_interval_hour_all[key[0]]
                        shop_classi_hour_topN['酒店'][key[0]] = shop_classi_hour_all[key[0]]
                    except:
                        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
                        continue
            '''
            keys = shoptrip_interval_hour_topN.keys()
            for key in keys:
                if not shoptrip_interval_hour_topN[key]:
                    shoptrip_interval_hour_topN.pop(key)
            keys = shop_classi_hour_topN.keys()
            for key in keys:
                if not shop_classi_hour_topN[key]:
                    shop_classi_hour_topN.pop(key)
            '''
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return shoptrip_interval_hour_topN, shop_classi_hour_topN

    # 组合规则
    def GR001(self, delete_food_flag):    # 组合方式
        global channel_weight_dict
        channel_weight = channel_weight_dict.copy()
        try:
            keys = channel_weight.keys()
            for key in keys:
                if key not in self.data or len(self.data[key]) == 0:
                    channel_weight.pop(key)
            if delete_food_flag:                    # 是否删除"美食"
                channel_weight.pop("美食")
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        channels = channel_weight.keys()
        weights = channel_weight.values()
        # cnt = random.randint(1, len(channel_weight))
        cnt = len(channel_weight)
        selected_channel = repeatable_weighted_choice(cnt, channels, weights)
        return selected_channel

    def GR002(self, shoptrip_food_interval_hour_dict_topN, shop_food_classi_hour_topN):        # 饭点约束 & 组合约束
        # print shoptrip_food_interval_hour_dict_topN
        grub_time = [['11:00', '13:00'], ['17:00', '19:00']]
        trip_time = [[self.request['startTime'], self.request['endTime']]]
        lunch_dinner_shops = []
        try:
            for single_grub_time in grub_time:
                grubtrip_interval_hour = get_covered_interval([single_grub_time], trip_time)
                shoptripgrub_interval_hour_dict_topN = {}
                try:
                    for sid, interval_hour_dict in shoptrip_food_interval_hour_dict_topN.items():
                        shoptripgrub_interval_hour_dict_topN[sid] = {}
                        interval = interval_hour_dict.keys()
                        for item in interval:
                            tmp = get_covered_interval_hour_dict(get_covered_interval([json.loads(item)], grubtrip_interval_hour))
                            for k, v in tmp.items():
                                # print sid, k, v, shop_food_classi_hour_topN[sid]
                                if v >= shop_food_classi_hour_topN[sid]:        # 覆盖营业时长需不小于规定活动时长
                                    shoptripgrub_interval_hour_dict_topN[sid][k] = v
                        if not shoptripgrub_interval_hour_dict_topN[sid]:
                            shoptripgrub_interval_hour_dict_topN.pop(sid)
                except:
                    print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
                    pass
                lunch_dinner_shops.append(shoptripgrub_interval_hour_dict_topN)
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        # print lunch_dinner_shops
        return lunch_dinner_shops

    def GR003(self, shoptrip_interval_hour_topN):        # 电影组合约束
        cinema_movie_dict = {}
        try:
            sid = random.choice(shoptrip_interval_hour_topN.keys())
            cinema_movie_dict = {sid: shoptrip_interval_hour_topN[sid]}
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return cinema_movie_dict

    # 各频道从topN中随机选择一家商户
    def GR004(self, selected_channel, lunch_dinner_shops, is_grub_time, shoptrip_interval_hour_topN):  # 间隔约束 & 时长约束
        recommended_shops = {}
        try:
            try:
                if is_grub_time:        # 如果在饭点有满足条件的美食商户，则推荐，并且在其他时间段不再推荐美食
                    recommended_shops["美食"] = []
                    for i, item in enumerate(lunch_dinner_shops):     # [{}, {}]
                        if not item:
                            continue
                        else:
                            sid = random.choice(item.keys())
                            recommended_shops["美食"].append({sid: item[sid]})
                            if i == 0 and sid in lunch_dinner_shops[1]:         # screen same shop in one plan
                                lunch_dinner_shops[1].pop(sid)
            except:
                print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
                pass
            for channel in selected_channel:
                try:
                    if channel in ['电影']:
                        continue            # "电影"的推荐在最后
                    else:
                        recommended_shops[channel] = []
                        tmp = shoptrip_interval_hour_topN[channel].keys()
                        sid = random.choice(tmp)
                        recommended_shops[channel].append({sid: shoptrip_interval_hour_topN[channel][sid]})
                except:
                    print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
                    pass
            if '电影' in selected_channel:
                recommended_shops["电影"] = []
                recommended_shops["电影"].append(self.GR003(shoptrip_interval_hour_topN["电影"]))
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return recommended_shops

    # 安排单个店铺的活动时间
    def arrange_order_single(self, recommended_shop_order, selected_channel, recommended_shops, shop_classi_hour_topN):
        classi_hour = shop_classi_hour_topN[selected_channel][recommended_shops[selected_channel][0].keys()[0]]
        # print selected_channel
        # print 'classi_hour: ', classi_hour
        selected_uncovered_interval_int = []
        try:
            for selected_sid, selected_interval_hour in recommended_shops[selected_channel][0].items():     #初始化选中频道的安排时间
                for selected_interval, selected_hour in selected_interval_hour.items():
                    selected_uncovered_interval_int.append(initialize_timelist(json.loads(selected_interval)))
            # print '-----', selected_uncovered_interval_int
            tmp = []
            for channel, shops in recommended_shop_order.items():       # 与方案中已有的店铺交叉比对，剔除交叉的时间段
                # print '='*10, channel
                for shop in shops:
                    # print shop
                    for sid, interval_hour in shop.items():
                        for interval, hour in interval_hour.items():
                            # print '>'*10
                            for selected_interval_int in selected_uncovered_interval_int:
                                if not selected_interval_int:
                                    continue
                                tmp += get_uncovered_hour(selected_interval_int, initialize_timelist(json.loads(interval)), classi_hour)
                            selected_uncovered_interval_int = tmp[:]        # 不断迭代选中频道店铺的安排时间
                            # print '-----', selected_uncovered_interval_int
                            tmp = []
            if not selected_uncovered_interval_int:     # 在可行的时间段内随机安排活动时间
                pass
            else:
                random_selected_interval_int = random.choice(selected_uncovered_interval_int)
                # print random_selected_interval_int
                recommended_shop_order[selected_channel] = [{recommended_shops[selected_channel][0].keys()[0]:
                {json.dumps([float_to_time(random_selected_interval_int[0]), float_to_time(random_selected_interval_int[0] + classi_hour)]): classi_hour}}]
                # print recommended_shop_order
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return recommended_shop_order

    # 获取最终的行程安排
    def get_recommended_shop_order(self, selected_channel, lunch_dinner_shops, delete_food_flag, shoptrip_interval_hour_topN, shop_classi_hour_topN):
        global tag_channel_dict
        global channel_weight_dict
        recommended_shop_order = {}
        channel_weight = channel_weight_dict.copy()
        recommended_channel_weights = []
        try:
            # 获取受推荐的店铺信息
            recommended_shops = self.GR004(selected_channel, lunch_dinner_shops, delete_food_flag, shoptrip_interval_hour_topN)
            recommended_channels = recommended_shops.keys()
            # print "*"*10, recommended_shops
            if delete_food_flag:
                recommended_shop_order["美食"] = recommended_shops["美食"]
                recommended_channels.remove("美食")
            # 标签权重
            for tag in self.request["interestName"].split(","):
                if tag in tag_channel_dict:
                    channel_weight[tag_channel_dict[tag]] = 1.3
            for channel in recommended_channels:
                if channel in channel_weight:
                    recommended_channel_weights.append(channel_weight[channel])
            # 安排各店铺的活动时间
            hotel_flag = False
            while len(recommended_channels) > 0:
                weighted_selected_channel = weighted_choice(recommended_channels, recommended_channel_weights)[0]
                if weighted_selected_channel == "酒店":        # 酒店排在方案的最后，不和其他商户做时间上的交叉比对
                    hotel_flag = True
                    continue
                # print weighted_selected_channel
                recommended_shop_order = self.arrange_order_single(recommended_shop_order, weighted_selected_channel, recommended_shops, shop_classi_hour_topN)
                # print recommended_channels
            if hotel_flag:
                recommended_shop_order["酒店"] = recommended_shops["酒店"]
            '''
            for channel, shops in recommended_shop_order.items():
                print channel
                for shop in shops:
                    for sid, interval in shop.items():
                        print sid, interval
                        print 'least_cost: ', shop_classi_hour_topN[channel][sid]
            '''
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return recommended_shop_order


if __name__ == '__main__':

    if 0:
        import MySQLdb
        db = MySQLdb.connect("192.168.1.11", "zjtachao", "123456")
        cs = db.cursor()
        cs.execute('select openning_hours from xchao.algo_shop_information')
        h = cs.fetchall()
        for time in h:
            tmp = openning_hour_extractor(time[0])
            if len(tmp) < 2:
                print 'origin_data: ', tmp, ['10:00', '21:00']
                print '*'*10, get_covered_interval(tmp, ['10:00', '21:00']), '\n'
                pass
    else:
        # print openning_hour_extractor('0:00-2:00周一至周日')
        print get_covered_interval_hour_dict([['17:00', '18:30'], ['17:00', '18:30'], ['11:00', '1:30']])
