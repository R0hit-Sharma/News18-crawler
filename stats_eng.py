import psycopg2
import psycopg2.extras
from datetime import datetime
from fetch_per import fetchUrls

# data format same as input data format in storedata
def connect():
    conn = psycopg2.connect("dbname=postgres user=debanjan_final password=Deb@12345 host=10.237.26.159 port=5432")
    return conn
    
def error_info(news_id):
    lines=""
    if news_id==1:
        with open('hindu_log.txt', 'r+') as f:
            lines=f.read()
            f.truncate(0)
    elif news_id==2:
        with open('toi_log.txt', 'r+') as f:
            lines=f.read()
            f.truncate(0)      
    elif news_id==4:
        with open('ie_log.txt', 'r+') as f:
            lines=f.read()
            f.truncate(0)
    elif news_id==5:
        with open('nie_log.txt', 'r+') as f:
            lines=f.read()
            f.truncate(0)
    elif news_id==8:
        with open('ht_log.txt', 'r+') as f:
            print("here2")
            lines=f.read()
            f.truncate(0)
    elif news_id==10:
        with open('news18_log.txt', 'r+') as f:
            lines=f.read()
            f.truncate(0)
    
    
    return lines
#give name of newspaper from id
def get_paper_name(news_id):
    conn = connect()
    cur = conn.cursor()	
    cur.execute("select name from sources where id = "+str(news_id))
    newspaper = cur.fetchone()
    cur.close()
    conn.close()
    return newspaper

#returns count of urls fetched on a date
def get_url_count(news_id,srch_date):
    conn = connect()
    cur = conn.cursor()
    qry = "select count(*) from news_articles where sources_xid ="+str(news_id)+" and published_date= '"+str(srch_date)+"'"
    print(qry)
    cur.execute(qry)
    #cur.execute("select count(*) from news_articles where id = %s and published_date=%s",(news_id,srch_date))
    url_count = cur.fetchone()
    cur.close()
    conn.close()
    return url_count

#returns articles fetched
def get_art_fetched(news_id,srch_date):
    conn = connect()
    cur = conn.cursor()
    qry = "select count(*) from news_articles where sources_xid ="+str(news_id)+" and published_date= '"+str(srch_date)+"' and mongo_id IS NOT NULL"
    print(qry)
    cur.execute(qry)
    #cur.execute("select count(*) from news_articles where id = %s and published_date=%s",(news_id,srch_date))
    art_count = cur.fetchone()
    cur.close()
    conn.close()
    return art_count


#save stats
def save_stat(news_id,start_time,stop_time,srch_date,srch_day):
    conn = connect()
    cur = conn.cursor()	
    newspaper = get_paper_name(news_id)
    url_count = get_url_count(news_id,srch_date)
    art_count = get_art_fetched(news_id,srch_date)
    error=error_info(news_id)
    print(str(error))
    print(art_count)
    cur.execute("INSERT INTO stats_eng(newspaper,newspaper_id,urls_count,articles_count,day,date,crawling_start_time,crawling_end_time,language,error_comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'English',%s)",
    (newspaper,news_id,url_count,art_count,str(srch_day),srch_date,start_time,stop_time,str(error)))
    conn.commit()
    cur.close()
    conn.close()
    
	
#gives date from timestamp
def get_date(time_stamp):
    datetime_object = datetime.strptime(time_stamp, '%Y-%m-%d %H:%M:%S.%f')
    srch_date = datetime_object.date()
    return srch_date
	
#give day from date
def get_day(srch_date):
    conn = connect()
    cur = conn.cursor()
    qry = "select extract(dow from date '"+str(srch_date)+"')"
    #cur.execute("select extract(dow from date %s)",str(srch_date))
    cur.execute(qry)
    ext_day = cur.fetchone()
    cur.close()
    conn.close()
    return ext_day[0]

#store stats of one day
def store_stat(start_time,stop_time):
    datetime_object = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f')
    srch_date = datetime_object.date()
    fetchUrls(srch_date)
    #get_date(start_time)
    print(srch_date)
    srch_day = get_day(start_time)
    for news_id in [10]:
    	save_stat(news_id,start_time,stop_time,srch_date,srch_day)
    	print(news_id)

days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
for mon in range (5,7):
    if mon == 4:
        startDate = 9
        endDate = days[mon-1]+1
    elif mon == 6:
        startDate = 1
        endDate = 11
    else:
        startDate = 1
        endDate = days[mon-1]+1
    for day in range (startDate, endDate):
        dateTime1 = '2020-'+str(mon)+'-'+str(day)+' 00:00:01.000000'
        dateTime2 = '2020-'+str(mon)+'-'+str(day)+' 23:59:59.000000'
        store_stat(dateTime1,dateTime2)

#save_stat(8,'2019-09-30 03:29:34.769201','2019-09-30 05:29:34.769201','2019-09-30','2')
#s=error_info(8)
#print(s)   	
#fetchUrls(get_date('2019-06-11 04:06:23.499869'))
#store_stat('2019-12-31 00:00:00.000000','2019-12-31 23:59:59.000000')
