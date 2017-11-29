ps aux | grep XchaoServer.py | awk '{print $2}'| xargs kill -9
nohup python3 XchaoServer.py > test.log &
