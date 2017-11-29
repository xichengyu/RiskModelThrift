# coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import MySQLdb
import traceback


def gen_queries(thrift_request):
    cost_level = {
        1: {"food_cost": 200000,     # 200
            "hotel_cost": 750000},   # 750
        2: {"food_cost": 200,
            "hotel_cost": 750},
        3: {"food_cost": 50,
            "hotel_cost": 300},
        4: {"food_cost": 0,
            "hotel_cost": 0},
    }
    try:
        request = request_mysql("10.0.8.2", "xchao", "SdB^1aS&cqTQvaXf")
        # request = request_mysql("192.168.1.11", "zjtachao", "123456")
        bc_data = request.requester('select * from xchao.algo_commercial_district where cdid = "%s"' % thrift_request["cdid"])
        business_circle = bc_data[0][1]
        # print business_circle
        request.closer()
        queries = [
            'select * from xchao.algo_shop_information where channel="美食" and avg_cost != "" and business_circle="%s"' % business_circle,
            'select * from xchao.algo_shop_information where channel="酒店" and avg_cost != "" and business_circle="%s"' % business_circle,
            'select * from xchao.algo_shop_information where channel="电影" and avg_cost != ""',
            'select * from xchao.algo_shop_information where channel="丽人" and classi in ("美发", "美容/SPA", "美甲美睫")'
                                                                        ' and avg_cost != ""',
            'select * from xchao.algo_shop_information where channel="休闲娱乐" and classi not in '
                                    '("VR", "中医养生", "轰趴馆", "美容/SPA", "私房菜", "咖啡厅", "私人影院") and avg_cost != ""',
            # 'select * from xchao.algo_shop_information where channel="购物"',
            'select * from xchao.algo_commercial_district where cdid = "%s"' % thrift_request["cdid"]
        ]


        food_cost = cost_level[thrift_request["consumeType"]]["food_cost"]
        hotel_cost = cost_level[thrift_request["consumeType"]]["hotel_cost"]

        queries[0] += ' and convert(avg_cost, signed) > %d and convert(avg_cost, signed) <= %d' % \
                      (cost_level[thrift_request["consumeType"]+1]["food_cost"], food_cost)
        queries[1] += ' and convert(avg_cost, signed) > %d and convert(avg_cost, signed) <= %d' % \
                      (cost_level[thrift_request["consumeType"]+1]["hotel_cost"], hotel_cost)
        '''
        if food_cost <= 200:
            queries[0] += ' and convert(avg_cost, signed) >= %d and convert(avg_cost, signed) <= %d' % (food_cost-50, food_cost+50)
        else:
            queries[0] += ' and convert(avg_cost, signed) >= %d and convert(avg_cost, signed) <= %d' % (0.7*food_cost, 1.3*food_cost)

        if hotel_cost <= 200:
            queries[1] += ' and convert(avg_cost, signed) >= %d and convert(avg_cost, signed) <= %d' % (hotel_cost-50, hotel_cost+50)
        else:
            queries[1] += ' and convert(avg_cost, signed) >= %d and convert(avg_cost, signed) <= %d' % (0.7*hotel_cost, 1.3*hotel_cost)
        '''

    except:
        raise ValueError

    return queries
    # return ['select * from xchao.algo_shop_information']


class request_mysql(object):
    def __init__(self, host, user, password, charset="utf8", port=3306):
        self.db = MySQLdb.connect(host=host, port=port, user=user, passwd=password, charset=charset)
        self.cs = self.db.cursor()

    def requester(self, query):
            try:
                self.cs.execute(query)
                res = self.cs.fetchall()
                return res
            except:
                traceback.print_exc()
                pass

    def closer(self):
        self.cs.close()
        self.db.close()


if __name__ == '__main__':


    test_request = {"queryId": "123", "userId": 12345, "interestName": "特色地方菜,自助餐,甜点饮品,料理,烧烤,西餐,简餐,海鲜",
                    "relation": 3, "count": 2, "currentLocation": "浙江省杭州市西斗门路3号", "residentCity":"浙江,台州", "cdid": "0571052",
                    "startTime": "9:55", "endTime": "23:55", "latitude": 23.234, "longitude": 123.123, "consumeType": 1}

    query = gen_queries(test_request)

    print query
'''
    request = request_mysql("10.0.8.2", "xchao", "SdB^1aS&cqTQvaXf")
    data = request.requester('select * from xchao.algo_shop_information where name="冬去春来平壤阿里郎朝鲜餐厅"')
    request.closer()
    print data
'''