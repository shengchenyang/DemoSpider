#!/usr/bin/bash
source /root/mytemp/DemoSpider/DemoSpider_venv/bin/activate
cd /root/mytemp/DemoSpider/DemoSpider && nohup python ./run.py &
deactivate
