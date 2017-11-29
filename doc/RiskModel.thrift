// code:utf-8

/*
    Request (string value in JSON format):
    KEY                 DESCRIPTION             TYPE
    queryId             query id                string
    userId              user id                 int
    interestName        user interest tag       int
    relation            relation code           int
    count               number of people        int
    cdid                code of business circle int
    startTime           start time in hour      float
    endTime             end time in hour        float
    latitude                                    float
    longitude                                   float
    
    {
        "queryId": "123",(每次推荐的id(string))
        "userId": 12345,(用户id(Long))
        "interestName": "甜点,自助餐"(爱好标签(string))
        "currentLocation":"浙江省杭州市西斗门路3号",(用户当前位置(string))
        "residentCity":"浙江,杭州",(用户常驻城市(string)
        "consumeType":1,(消费类型(int) 1:土豪型(餐厅消费500左右,酒店消费800左右) 2:小康型(餐厅消费300左右,酒店消费500左右) 3:经济型(餐厅消费100左右,酒店消费200左右))
        "relation": 1,(人物关系(int) 0：情侣 1：家人 2：客户 3：朋友 4：闺蜜 5：兄弟)
        "count": 3,(人数(int)0：1人 1：2人 2：3-4人 3：5-10人 4：11人及以上)
        "cdid": "0571001",(商圈id(string))
        "startTime": "17:05",(开始时间(string))
        "endTime": "19:30",(结束时间(string))
        "latitude": 23.234,(纬度(float))
        "longitude": 123.123(经度(float))
    }
*/

struct RiskModelRequest
{
    1:optional string json_data,
}

/*
    Response (string value in JSON format):
    KEY         DESCRIPTION         TYPE
    qid         query id            string
    plans       list of plans       list<plan>
    
    plan:
    KEY         DESCRIPTION         TYPE
    plan_id     plan id             string
    shops       list of shops       list<shop>

    shop:
    KEY         DESCRIPTION                 TYPE
    sid         shop id                     int
    reason      reason for recommendation   string
    ext         list of ext information     list<ext> (一个店铺可能会有多个团购信息)

    example:
    {
        'qid': 'for test-123',  # (queryId, 由uid和时间戳组成)
        'plans':[
        {
            'plan_id':'12345-20161021-10001',   # (queryId＋计划序号)
            'shops':[
                {
                    'sid':'r123',
                    'reason':'喜欢勇日本料理的人也喜欢该餐厅',
                    'ext': [{"description": "仅售39元！价值45元的自助火锅，提供免费WiFi。",（团购描述信息（string））
                             "title": "[西溪]川娃泡菜馆&自助火锅",                       （团购标题（string））
                             "url": "http://t.dianping.com/deal/21860012",            （团购页面url（string））
                             "price": 39,                                             （团购价格（int））
                             "marketPrice": 45,                                       （团购原价（int））
                             "id": "EBB6BFB56E16FBD0A6F56C0A64685929",                （各团购信息id（string））
                             "expire": 1502121600,                                    （团购信息失效时间戳（int））
                             "sid": "6CC80BF447A3241E6385B8F2CEE82BD3",               （团购信息对应商铺id（string））
                             "sold": 11                                               （已经售出团购数目（int））
                            },
                            ],      ＃ 优惠信息
                    'interval': ['11:00', '13:00']
                },
                {
                    'sid':'m123',
                    'reason':'根据您喜欢的电影《美国队长3》推荐',
                    'ext':[],
                    'interval': ['11:00', '13:00']
                }
            ]
        },
        ]
    }
*/
struct RiskModelResponse
{
    1:optional string json_data,
}

service RiskModelThriftService {
    RiskModelResponse transmitRiskModelData(1:RiskModelRequest rmodel_request)
}
