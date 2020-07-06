# coding: utf-8
import scrapy
from datetime import datetime
from datetime import timedelta
from storage import storedata
from newsitem import NewsItem
import refine_date

class QuotesSpider(scrapy.Spider):
    name = "news18"
    
    categories = {
            'india/' : 'NATIONAL_NEWS',
            'politics/' : 'NATIONAL_NEWS',
            'opinion/' : 'OPINION'
        }
        
    

    def start_requests(self):
        base_url = 'https://www.news18.com/'
        
        for category in self.categories:
            #print(base_url+category)
            if(category != 'opinion/'):
                yield scrapy.Request(url=base_url+category, callback=self.parse, meta = {'category' : category})
            else:
                yield scrapy.Request(url=base_url+category, callback=self.parse_opinion, meta = {'category' : category})
        

    def parse(self, response):
        
        #level 1 data... the main news topic --> div.section-blog-left-img
        lev1data = response.css('div.section-blog-left-img')
        lev1link = lev1data.css('a::attr(href)').extract()
        #Use .encode('ascii', 'ignore') to convert title to ascii to remove non-ascii characters
        lev1title = lev1data.css('img::attr(title)').extract()
        yield scrapy.Request(str(lev1link), callback=self.parse_date, meta={'link' : lev1link, 'title' : lev1title, 'category' : response.meta.get('category')})
        
       
        
        #level 2 data... highlighted news --> div.section-blog-left-img-list
        lev2data = response.css('div.section-blog-left-img-list')
        lev2list_link = lev2data.css('a::attr(href)').extract()
        lev2list_title = lev2data.css('li ::text').extract()
        if (len(lev2list_title) != len(lev2list_link)):
            print("\n\nNumber of level 2 links are not matching number of level 2 titles\n\n")
        else:
            for loop_count in range (len(lev2list_link)):
                yield scrapy.Request(str(lev2list_link[loop_count]), callback=self.parse_date, meta={'link' : lev2list_link[loop_count], 'title' : lev2list_title[loop_count], 'category' : response.meta.get('category')})
        
        
        #level 3 data... other news --> div.blog-list-blog
        lev3data = response.css('div.blog-list-blog')
        lev3list_link = lev3data.css('p a::attr(href)').extract()
        lev3list_title = lev3data.css('img::attr(title)').extract()
        if (len(lev3list_title) != len(lev3list_link)):
            print("\n\nNumber of level 3 links are not matching number of level 3 titles\n\n")
        else:
            for loop_count in range (len(lev3list_link)):
                yield scrapy.Request(str(lev3list_link[loop_count]), callback=self.parse_date, meta={'link' : lev3list_link[loop_count], 'title' : lev3list_title[loop_count], 'category' : response.meta.get('category')})

        
        #Create an html page with response.body to check if response was normal/ not normal
        with open('response.html', 'w') as the_file:
            the_file.write(response.body)
        the_file.close()

        
    def parse_opinion(self, response):
        
        #level 1 data... the main opinion --> div.lbox
        lev1data = response.css('div.lbox')
        lev1link = lev1data.css('a::attr(href)').extract()
        #Used .encode('ascii', 'ignore') to convert title to ascii to remove non-ascii characters
        lev1title = lev1data.css('img::attr(title)').extract()
        #since date is not available readily, follow the link to get date
        yield scrapy.Request(str(lev1link), callback=self.parse_date, meta={'link' : lev1link, 'title' : lev1title, 'category' : response.meta.get('category')})
        
       
        
        #level 2 data... highlighted opinion --> ul.rbox
        lev2data = response.css('ul.rbox')
        lev2list_link = lev2data.css('a::attr(href)').extract()
        lev2list_title = lev2data.css('li ::text').extract()
        if (len(lev2list_title) != len(lev2list_link)):
            print("\n\nNumber of level 2 links are not matching number of level 2 titles\n\n")
        else:
            for loop_count in range (0,len(lev2list_link),3):#increment loop_count by 3 as there is redundant data
                item = NewsItem()
                print(lev2list_link[loop_count])#article link
                item['link'] = lev2list_link[loop_count]
                print(lev2list_title[loop_count+1])#article title
                item['title'] = lev2list_title[loop_count+1]
                print(lev2list_title[loop_count+2])#article date
                item['date'] = refine_date.refine_date(lev2list_title[loop_count+2])
                print(self.categories.get(response.meta.get('category')))
                item['category'] = self.categories.get(response.meta.get('category'))
                self.store(item)
                print("\n\n")
        
        
        #level 3 data... other opinions --> li.bbnone:nth-child('+str(index)+')
        index = 1
        lev3data = response.css('li.bbnone:nth-child('+str(index)+')')
        while len(lev3data) != 0:#checks if the lev3data is empty
            lev3list_link = lev3data.css('a::attr(href)')[0].extract()#link of the opinion
            lev3list_title = lev3data.css('img::attr(title)').extract()#title of the opinion
            lev3list_date = lev3data.css('div:nth-child(2) > h3:nth-child(3)::text').get()#date of the title
            item = NewsItem()
            print(lev3list_link)
            item['link'] = lev3list_link
            print(lev3list_title)
            item['title'] = lev3list_title
            print(lev3list_date)
            item['date'] = refine_date.refine_date(lev3list_date)
            print(self.categories.get(response.meta.get('category')))
            item['category'] = self.categories.get(response.meta.get('category'))
            print("\n\n")
            self.store(item)
            index = index+1
            lev3data = response.css('li.bbnone:nth-child('+str(index)+')')

        #level 4 data... extra opinions --> ul.opinion-listing:nth-child(5) > li:nth-child(1)
        index = 1
        lev4data = response.css('ul.opinion-listing:nth-child(5) > li:nth-child('+str(index)+')')
        while len(lev4data) != 0:#checks if the lev4data is empty
            lev4list_link = lev4data.css('a::attr(href)')[0].extract()#link of the opinion
            lev4list_title = lev4data.css('img::attr(title)').extract()#title of the opinion
            lev4list_date = lev4data.css('div:nth-child(2) > h3:nth-child(3)::text').extract()#date of the title
            item = NewsItem()
            print(lev4list_link)
            item['link'] = lev4list_link
            print(lev4list_title)
            item['title'] = lev4list_title
            print(lev4list_date)
            item['date'] = refine_date.refine_date(lev4list_date)
            print(self.categories.get(response.meta.get('category')))
            item['category'] = self.categories.get(response.meta.get('category'))
            print("\n\n")
            self.store(item)
            index = index+1
            lev4data = response.css('ul.opinion-listing:nth-child(5) > li:nth-child('+str(index)+')')

    def parse_date(self, response):
		try:
			date_time = response.css('div.clearfix:nth-child(5) > div:nth-child(1) > span:nth-child(2) ::text')[1].extract()
			item = NewsItem()
			print("\n\n")
			item['link'] = response.meta.get('link')
			print(item['link'])
			item['title'] = response.meta.get('title')
			print(item['title'])
			item['date'] = refine_date.refine_date(date_time)
			print(item['date'])
			item['category'] = self.categories.get(response.meta.get('category'))
			print(item['category'])
			
			print("\n\n")
			self.store(item)            
		except:
			print('Not news I guess....')
        
    def store(self, item):
        meta = {
               'sourceName':'News18',
               'language':'English',
               'country':'India',
               'category':item['category'],
               'articleTitle':item['title'],
               'articleUrl':item['link'],
               'publishedDate':item['date'],
               'publishedTime':None
               }
        print('Storing: '+meta['articleUrl']+' ',meta['publishedDate'])
        storedata.storeMeta(meta)
