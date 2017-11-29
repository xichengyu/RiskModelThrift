# coding=utf-8

# from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('../../RecommendationSystem/Requester')
sys.path.append('../../RecommendationSystem/Model')
import mysql
# from random import choice
import json
import traceback
import coldstart_rules
import time


class data_handler(object):
    def __init__(self, thrift_request, filtering_model):
        self.request = thrift_request
        self.model = filtering_model
        self.sql_queries = mysql.gen_queries(thrift_request)

    def get_data(self):
        data = {}
        channels = ["美食", "酒店", "电影", "丽人", "休闲娱乐", "algo_commercial_district", "购物"]
        try:
            request = mysql.request_mysql("10.0.8.2", "xchao", "SdB^1aS&cqTQvaXf")
            business_circle = request.requester(self.sql_queries[-1])[0][1]
            for i, query in enumerate(self.sql_queries):
                # print str(query)
                # start = time.time()
                if i == 0:
                    tmp = list(request.requester(query))
                    # print "$"*10, tmp

                    data[channels[i]] = list(request.requester('select * from xchao.algo_shop_information where channel'
                                                               '="美食" and avg_cost != "" and business_circle="%s" and '
                                                               'convert(avg_cost, signed) > 50 and convert(avg_cost, '
                                                               'signed)<=200' % business_circle)) if not tmp else tmp
                elif i == 1:
                    tmp = list(request.requester(query))
                    data[channels[i]] = list(request.requester('select * from xchao.algo_shop_information where channel'
                                                               '="酒店" and avg_cost != "" and business_circle="%s" and '
                                                               'convert(avg_cost, signed) > 300 and convert(avg_cost, '
                                                               'signed)<=750' % business_circle)) if not tmp else tmp
                else:
                    data[channels[i]] = list(request.requester(query))
                # print 'Query: %s' % query
                # print 'Cost: ', time.time() - start
            request.closer()
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        # print data["美食"]
        return data                 # in dict format, e.g. {"channel_1": mysql_data_1, "channel_2": mysql_data_2}

    def gen_plans(self):
        try:
            return self.model(self.request, self.get_data())
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            return {}
            # in dict format, e.g. [{"channel_1": [{"sid1": {"interval1": hour1}}], "channel_2": [{"sid2": {"interval2": hour2}}]},
            #                       {"channel_3": [{"sid3": {"interval3": hour3}}], "channel_4": [{"sid4": {"interval4": hour4}}]}]

    def gen_response(self):
        """
        sid, reason and ext of shop are changeable according to different filtering model
        """
        reason_dict = {"美食": "根据您的标签和喜好推荐，不知道是否合您的胃口呢？",
                       "休闲娱乐": "闲暇的午后/静谧的夜晚，一起来放松一下。",
                       "丽人": "和闺蜜出行，快来一起变得更美吧！",
                       "电影": "最近有诺兰的大片出没，快去看电影吧！",
                       "酒店": "出门在外，找个舒服的地方下榻休息一晚。",
                       }
        response = {
            "qid": self.request['queryId'],
            "plans": []
        }
        try:
            final_plans = self.gen_plans()
            '''
            for plan in final_plans:
                print '-' * 50
                for channel, shops in plan.items():
                    print channel, shops
            '''
            i = 0
            for final_plan in final_plans:
                plan = {
                    "plan_id": self.request['queryId']+ "_%d" % i,
                    "shops": []
                }
                # print "酒店" in final_plan
                for channel, shops in final_plan.items():
                    if channel == "酒店":                 # 酒店信息放在方案最后
                        for shop in shops:
                            json_hotel = {
                                "sid": shop.keys()[0],
                                "reason": reason_dict[channel],
                                "ext": get_ext_info(shop.keys()[0]),
                                "interval": json.loads(shop.values()[0].keys()[0])
                            }
                        continue
                    for shop in shops:
                        json_shop = {
                            "sid": shop.keys()[0],
                            "reason": afternoon_or_night(shop.values()[0].keys()[0]) if channel == "休闲娱乐" else reason_dict[channel],
                            "ext": get_ext_info(shop.keys()[0]),
                            "interval": json.loads(shop.values()[0].keys()[0])
                        }
                        plan['shops'].append(json_shop)
                plan['shops'] = sort_shop_by_interval(plan['shops'], self.request)
                if "酒店" in final_plan:
                    if len(plan['shops']) > 0:      # 方案中已有其他channel的商户
                        json_hotel["interval"] = [plan['shops'][-1]['interval'][1], ""]
                    else:
                        json_hotel["interval"][1] = ""
                    plan['shops'].append(json_hotel)
                response['plans'].append(plan)
                i += 1
        except:
            print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
            pass
        return json.dumps(response)


def afternoon_or_night(interval):
    starttime = json.loads(interval)[0]
    reason = "闲暇的午后，一起来放松一下。"
    try:
        if int(starttime.split(':')[0]) >= 18:
            reason = "静谧的夜晚，一起来放松一下。"
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return reason


def get_ext_info(sid):
    ext = []
    keys = ['sid', 'title', 'description', 'sold', 'expire', 'price', 'marketPrice', 'url', 'id']
    try:
        # request = mysql.request_mysql("121.40.158.249", "ttc", "rds6w957743lgxzkywz2o.mysql.rds.aliyuncs.com")
        request = mysql.request_mysql("10.0.8.2", "xchao", "SdB^1aS&cqTQvaXf")
        # start = time.time()
        data = request.requester('select * from xchao.algo_promotion_information where sid="%s"' % sid)
        for line in data:
            ext.append(dict(zip(keys, line)))
        # print 'Query: %s' % query
        # print 'Cost: ', time.time() - start
        request.closer()
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return ext


def get_hour(time_interval):
    time_hour = coldstart_rules.initialize_timelist(time_interval)
    if time_hour[0] < 5:
        time_hour[0] += 24
    return time_hour


def sort_shop_by_interval(shop, thrift_request):
    try:
        trip_hour = coldstart_rules.initialize_timelist([thrift_request["startTime"],thrift_request["endTime"]])
        if trip_hour[0] < trip_hour[1] <= 24:
            shop = sorted(shop, cmp=lambda x, y: cmp(coldstart_rules.initialize_timelist(x["interval"])[0],
                                                     coldstart_rules.initialize_timelist(y["interval"])[0]))
        else:
            shop = sorted(shop, cmp=lambda x, y: cmp(get_hour(x["interval"])[0], get_hour(y["interval"])[0]))
            pass
        pass
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return shop


def coldstart_model(thrift_request, responsed_data):
    plans = []
    plan_number = 3
    try:
        crules = coldstart_rules.rules(thrift_request, responsed_data)

        # 先行规则
        # time_1 = time.time()
        crules.PR002()
        # time_2 = time.time()
        # print 'PR002_cost: ', time_2 - time_1
        crules.PR003()
        # time_3 = time.time()
        # print 'PR003_cost: ', time_3 - time_2
        crules.PR004()
        # time_4 = time.time()
        # print 'PR004_cost: ', time_4 - time_3
        PR001_res = crules.PR001()
        # time_5 = time.time()
        # print 'PR001_cost: ', time_5 - time_4
        shoptrip_interval_hour_all = PR001_res[0]
        shop_classi_hour_all = PR001_res[1]

        # 推荐规则
        topN_shop_info = crules.get_topN_shop_info(shoptrip_interval_hour_all, shop_classi_hour_all)
        shoptrip_interval_hour_topN = topN_shop_info[0]
        shop_classi_hour_topN = topN_shop_info[1]
        # time_6 = time.time()
        # print 'RRs_cost: ', time_6 - time_5

        # 组合规则
        lunch_dinner_shops = [{}, {}]
        if "美食" in shoptrip_interval_hour_topN and "美食" in shop_classi_hour_topN:
            lunch_dinner_shops = crules.GR002(shoptrip_interval_hour_topN['美食'], shop_classi_hour_topN['美食'])  # 饭点约束 & 组合约束
        delete_food_flag = True  # 是否饭点约束
        # print lunch_dinner_shops
        if not lunch_dinner_shops[0] and not lunch_dinner_shops[1]:
            delete_food_flag = False

        # 生成N个活动方案，N由plan_number确定
        for i in range(plan_number):
            selected_channel = crules.GR001(delete_food_flag)
            new_plan = crules.get_recommended_shop_order(selected_channel, lunch_dinner_shops,
                                                    delete_food_flag, shoptrip_interval_hour_topN, shop_classi_hour_topN)
            if_append_flag = True
            for plan in plans:          # 过滤相同的方案
                if new_plan == plan:
                    if_append_flag = False
                    break
            if if_append_flag:
                plans.append(new_plan)
        # time_7 = time.time()
        # print 'GRs_cost: ', time_7 - time_6
    except:
        print time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), traceback.format_exc()
        pass
    return plans


if __name__ == '__main__':

    # time_1 = time.time()

    test_request = {"queryId": "123", "userId": 12345, "interestName": "特色地方菜,自助餐,甜点饮品,料理,烧烤,西餐,简餐,海鲜",
                    "relation": 0, "count": 2, "currentLocation": "浙江省杭州市西斗门路3号", "residentCity":"浙江,杭州",
                    "cdid": "0571001",
                    "startTime": "9:55", "endTime": "23:55", "latitude": 23.234, "longitude": 123.123, "consumeType": 2}

    queries = mysql.gen_queries(test_request)       # generate SQL queries

    handle_data = data_handler(test_request, coldstart_model)

    # print 'initial_time: ', time.time() - time_1

    # time_3 = time.time()

    response = handle_data.gen_response()

    # print 'recommend_time: ', time.time() - time_3

    # print json.loads(response)['plans'][0]['shops'][1]['ext']
    print json.loads(response)





