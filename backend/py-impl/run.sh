ps aux | grep RiskModelServer.py | awk '{print $2}'| xargs kill -9
nohup python3.6 RiskModelServer.py > test.log &
