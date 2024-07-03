# Define your debug file here
from scrapy import cmdline

# 将 xxx 替换为需要运行的 spider 名
cmdline.execute(["scrapy", "crawl", "xxx"])
