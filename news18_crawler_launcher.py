import os
from scrapy.crawler import CrawlerProcess
from news18 import QuotesSpider
from scrapy.utils.project import get_project_settings
from datetime import datetime
from threading import Timer
import threading
import schedule
import time
import datetime


name = "news18"
path = "/home/dell/Envs3/ENV/bin/tutorial/tutorial/spiders"
process = CrawlerProcess(get_project_settings())
process.crawl(name)
	
def startCrawler():
	process.start()
	print ("News 18 Crawler ran at " +str(datetime.datetime.now()))
	#threading.Timer(120, startCrawler).start()


if __name__ == "__main__":
	startCrawler()
	schedule.every().day.at("11:00").do(startCrawler)
	#schedule.every(2).minutes.do(startCrawler)
	while True:
		schedule.run_pending()
		time.sleep(1) # wait one second
