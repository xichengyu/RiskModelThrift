// code:utf-8

/*
    Request (string value in JSON format):
    KEY                 DESCRIPTION             TYPE
    queryId             query id                string
    modelId             model id                string
    idnoHash            idno in hash format     string
    applyDate           apply data              string
    fieldData           data of fields          map or dict({})

    fieldData:
    KEY                 DESCRIPTION             TYPE
    fieldName         name of each filed        string


    {
        "queryId": "1515639695000",(uuid)
        "modelId": "LL0038",
        "idnoHash": "d8cb27acb114052c8274d9ee1af5bc40abf1ee94bdb885e0f1733f8fd7d287c2",(加密的用户idno(string))
        "applyDate": "2017-01-11 11:11:11", (用户申请时间，时间格式(string))
        "fieldData": {"fieldName1": 1.0,
                      "fieldName2": 2.0,
                      ...
                     }, (用户各指标详细数据，指标数据形式为float)
    }
*/

struct RiskModelRequest
{
    1:optional string json_data,
}

/*
    Response (string value in JSON format):
    KEY                 DESCRIPTION             TYPE
    responseId          response id             string
    modelId             model id                string
    idnoHash            idno in hash format     string
    applyDate           apply data              string
    score               score of user           float


    {
        "responseId": "1515639695000", (uuid)
        "modelId": "LL0038",
        "idnoHash": "d8cb27acb114052c8274d9ee1af5bc40abf1ee94bdb885e0f1733f8fd7d287c2", (加密的用户idno(string))
        "applyDate": "2017-01-11 11:11:11", (用户申请时间，时间格式(string))
        "score": 1.0, (用户各指标详细数据，支持多用户查询，list格式，指标数据形式为float)
    }
*/

struct RiskModelResponse
{
    1:optional string json_data,
}

service RiskModelThriftService {
    RiskModelResponse transmitRiskModelData(1:RiskModelRequest rmodel_request)
}
