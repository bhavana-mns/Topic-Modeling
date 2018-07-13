import urllib, sys
from bs4 import BeautifulSoup
import psycopg2
import re
from selenium import webdriver

articleid=0
for i in range(0,50):
	
	title="-"
	full_a="-"
	authorName="-"
	article_link="-"
	publish_time="-"
	media_link="-"
	site = "https://www.thequint.com/news/politics/"+str(i)
	hdr = {'User-Agent': 'Mozilla/5.0'}
	req = urllib.request.Request(site, headers=hdr)
	page = urllib.request.urlopen(req)
	i+=1
	soup = BeautifulSoup(page,"html.parser")
	#print (soup)

	res=soup.find("div",class_="container")
	temp=res.find("div",class_="row")

	data=[]
	type1=temp.find_all("div",class_="story-fluid-medium ctg-news col-medium undefined ")
	type2=temp.find_all("div",class_="story-card-small col-small ctg-news")
	type3=temp.find_all("div",class_="story-card-medium ctg-news col-medium undefined ")

	for i in range(0,len(type1)):
		data.append(type1[i])
	for i in range(0,len(type2)):
		data.append(type2[i])
	for i in range(0,len(type3)):
		data.append(type3[i])

	try:
		for r in data:
			#print r.a.get('href') # Article Link
			article_link = r.a.get('href')
			subsite=r.a.get('href')
			subsite="https://www.thequint.com"+subsite
			subreq=urllib.request.Request(subsite, headers=hdr)
			subpage=urllib.request.urlopen(subreq)
			content=BeautifulSoup(subpage,"html.parser")
			title = content.title.text
			print(title)

			regex=re.compile("story-article ctg-news*")
			art=content.findAll("article",{"class":regex})
			articleid+=1
			print(articleid)

			if(len(art)>0):
			
				regex=re.compile("story-article__hero__image*")
				temp=art[0].findAll("div",attrs={"class":regex})
				if(len(temp)>0):
					img= temp[0].findAll("img",attrs={"src":True})
					media_link = img[0]['src']
					#print(media_link)	
	

		
				text=art[0].findAll("div",class_="story-article__body container")
		
	
				regex=re.compile("story-article__body__left*")		
				details=text[0].findAll("div",{"class":regex})
		
				if(len(details)>0):
					details1=text[0].findAll("span",{"class":"story-article__body__left__top__byline__left--authors"})
					if(len(details1)>0):		
						authorName=details1[0].find("a").text
						print(authorName)
					#print(details[0])	

					publish_time=details[0].find("time").text
					print(publish_time)	

		
				non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
				full_article = ""

				#Article data
				for full_content in text[0].find_all("div",{"itemprop":"articleBody","class":"story-article__cards"}):  # full article	
					for texts in full_content.findAll("div",class_="story-card"):
						for para in texts.findAll("p"):
							full_article += para.text.encode('utf-8').decode('utf-8').translate(non_bmp_map)
							full_a = full_article
	
				#print(full_article)
				#print(title)
			#articleid=articleid.lower()
			#print(articleid)
			title=title.lower()
			#print(title)
			full_a=full_a.lower()
			authorName=authorName.lower()
			article_link=article_link.lower()
			publish_time=publish_time.lower()
			media_link=media_link	.lower()
			
	
			conn = None
			try:
				conn = psycopg2.connect(host="localhost",database="articles1",user="bhavana",password="pwd")
				cur = conn.cursor()
				print('Database Connection Open')
				cur.execute("""insert into untaggedarticles(ArticleID,ArticleTitle,FullArticle,Author,Article_Link,Date_Published) values(%s,%s,%s,%s,%s,%s)""", (articleid,title,full_a,authorName,article_link,publish_time))
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
	
				
	except Exception as e:
		print(e.message)


			
