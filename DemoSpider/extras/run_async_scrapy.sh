#!/bin/bash

TASK_NUM=${task_num:-1}

for i in $(seq 1 $TASK_NUM)
do
    echo "Starting Scrapy crawler instance #$i"
    scrapy crawl demo_s &
    sleep 3
done

wait
