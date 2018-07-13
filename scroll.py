from selenium import webdriver
import urllib, sys
from bs4 import BeautifulSoup
import psycopg2
import re
import time

browser = webdriver.Firefox(executable_path='/home/hp/Downloads/geckodriver')
#driver.get('http://inventwithpython.com')

#browser = webdriver.Firefox()
site = "https://scroll.in/category/76/politics"
browser.get(site)

lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
match=False
while(match==False):
	lastCount = lenOfPage
	time.sleep(3)
	lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
	if lastCount==lenOfPage:
		match=True
source_data = browser.page_source
soup = BeautifulSoup(source_data,"html.parser")
hdr = {'User-Agent': 'Mozilla/5.0'}

res=soup.find_all("div",class_="row-stories column scroll-box scroll-box-3")
temp=[]
for i in range(0,len(res)):
	temp+=res[i].find_all("li",class_="row-story")
#print(len(temp))
for r in temp:

	articleid="-"
	title="-"
	full_a="-"
	authorName="-"
	article_link="-"
	publish_time="-"
	media_link="-"
	tags=[]

	#print r.a.get('href') # Article Link
	article_link = r.a.get('href')
	subsite=r.a.get('href')
	subreq=urllib.request.Request(subsite, headers=hdr)
	subpage=urllib.request.urlopen(subreq)
	content=BeautifulSoup(subpage,"html.parser")
	#print (content.title.text) # Article Title
	title = content.title.text
	print(title)

	art=content.findAll("article")
	articleid = art[0]['data-id']
	ArticleID=art[0]['data-id']
	print(articleid)

	text=art[0].findAll("div",class_="article-content-container")
	

	time=text[0].findAll("div",class_="article-time-container")
	time = time[0].findAll("time",class_="article-published-time")
	publish_time=time[0]['datetime']
	#print(publish_time)
	
	temp=art[0].findAll("picture",{"itemprop":"image"})
	if(len(temp)>0):
		img= temp[0].findAll("img",attrs={"src":True})
		media_link = img[0]['src']
		#print(media_link)
		
	non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
	full_article = ""
	author=""
	
	#Author Details (img and name)
	author_data=art[0].find_all("span",{"itemprop":"author"})
	authorName=author_data[0].find("a").text
	#print(authorName)
		
	#Tags
	tags=[]
	tag_data=text[0].find_all("ul",class_="article-tags-list")
	tag=tag_data[0].find_all("li")
	#print(len(tag))
	for i in range(0,len(tag)):
		for t in tag[i].find_all("a"):
			text1=t.text.replace('  ','')
			tags.append(text1.replace('\n',''))
	#print(tags)
	
	
	#Article data
	for full_content in text[0].find_all("div",class_="article-body"):  # full article	
		for para in full_content.findAll("p"):
			full_article += para.text.encode('utf-8').decode('utf-8').translate(non_bmp_map)
			full_a = full_article
	#print(full_article)
	#print(title)

	
	
	conn = None
	try:
		conn = psycopg2.connect(host="localhost",database="articles1",user="bhavana",password="pwd")
		cur = conn.cursor()
		print('Database Connection Open')
		cur.execute("""insert into taggedarticles(ArticleID,ArticleTitle,FullArticle,Author,Tags,Article_Link,Date_Published) values(%s,%s,%s,%s,%s,%s,%s)""",
                                            (articleid,title,full_a,authorName,tags,article_link,publish_time))
		conn.commit()

		cur.execute("""insert into Media(ArticleID,MediaLink) values(%s,%s)""",(articleid,media_link))
		cur.close()
		conn.commit()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	finally:
		if conn is not None:
			conn.close()
			print('Database connection closed.')

	print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
	






    
