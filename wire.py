from selenium import webdriver
import urllib, sys
from bs4 import BeautifulSoup
import psycopg2
import re
import time
from selenium.webdriver.common.keys import Keys

browser = webdriver.Firefox(executable_path='/home/hp/Downloads/geckodriver')
site = "https://thewire.in/category/politics/all"
browser.get(site)

for i in range(1,30):
	#print("-----------------------------------")
	elem = browser.find_elements_by_class_name("card__footer")
	#print(elem[1])
	more=elem[1].find_element_by_link_text('more')
	more.click()
'''
no_of_pagedowns = 100

while no_of_pagedowns:
    elem.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.2)
    no_of_pagedowns-=1

'''
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

res=soup.find_all("div",class_="card__content-wrapper ")
#print(len(res))

temp=[]
for i in range(0,len(res)):
	temp+=res[i].find_all("div",class_="card horizontal card__header--rm-margin row-height ")

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
	subsite="https://thewire.in"+subsite
	subreq=urllib.request.Request(subsite, headers=hdr)
	subpage=urllib.request.urlopen(subreq)
	content=BeautifulSoup(subpage,"html.parser")
	#print (content.title.text) # Article Title
	title = content.title.text
	#print(title)

	
	art=content.findAll("section")
	#print(art[0])
	articleid = art[0]['data-id']
	ArticleID=art[0]['data-id']
	#print(articleid)
	#publish_time = art[0]['post-pubdate']
	#print art[0]['post-pubdate'] #Published date
	#tag_ins = art[0]['post-tags'].replace(',','~')
	#print art[0]['post-tags'].replace(',','~') # tags
	temp=art[0].findAll("div",class_="featured-image valign-wrapper wp-caption aligncenter")
	img= temp[0].findAll("img",class_="img-responsive",attrs={"src":True})
	media_link = img[0]['src']
	#print img[0]['src'] # Image url
	#authorName = str(art[0]['post-auth'])
    
	
	non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
	full_article = ""
	author=""
	#print(title)
	#Author Details (img and name)
	author_data=art[0].find_all("div",class_="author")

	authtemp=author_data[0].findAll("div",class_="author-avatar-placeholder")
	
	authimg=authtemp[0].findAll("img",class_="circle responsive-img author__image",attrs={"src":True})
	
	if(len(authimg)>0):
		auth_link=authimg[0]['src']
	authname=author_data[0].findAll("div",class_="author__name")
	auth=authname[0].find("a")
	author+=auth.text.encode('utf-8').decode('utf-8').translate(non_bmp_map)
	
	#Tags
	tag_data=art[0].find_all("span",class_="data-tag")
	tag=tag_data[0].find_all("a")
	tags=tag[0]['title']
	#print(tags)
	
	#Article data
	for full_content in art[0].find_all("div",class_="col s12 m10 postComplete__description"):  # full article yes		
		for para in full_content.findAll("p"):
			full_article += para.text.encode('utf-8').decode('utf-8').translate(non_bmp_map)
			full_a = full_article
			#print(full_article)
	#print(title)

	title=title.lower()
	#print(title)
	full_a=full_a.lower()
	authorName=authorName.lower()
	article_link=article_link.lower()
	publish_time=publish_time.lower()
	media_link=media_link.lower()
	#print(tags)

	#print(str(articleid) + "\t" + title + "\t" + full_a + "\t" + authorName + "\t" + "{}".format(tags) + "\t" + article_link + "\t" + publish_time + "\t" + media_link)
	

	
	conn = None
	try:
		conn = psycopg2.connect(host="localhost",database="articles1",user="bhavana",password="pwd")
		cur = conn.cursor()
		print('Database Connection Open')
		cur.execute("""insert into taggedarticles(ArticleID,ArticleTitle,FullArticle,Author,Tags,Article_Link) values(%s,%s,%s,%s,%s,%s)""",
                                            (articleid,title,full_a,author,tags,article_link))
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
	






    
