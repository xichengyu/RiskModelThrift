cp ../../../LLpay_RiskModel/ModelBuilder/OfflineBuilder/ScoreCard/conf/woe_score.nparray ./conf/
cp ../../../LLpay_RiskModel/ModelBuilder/OfflineBuilder/ScoreCard/conf/X_interval.nparray ./conf/
cp ../../../LLpay_RiskModel/ModelBuilder/OfflineBuilder/ScoreCard/conf/scale_location.coef ./conf/
ps aux | grep RiskModelServer.py | awk '{print $2}'| xargs kill -9
nohup python3.6 RiskModelServer.py > /dev/null 2>&1 &

