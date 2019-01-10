# -- coding:utf-8 --
import time

class Maoyan:

	detailurl = "http://m.maoyan.com/ajax/detailmovie?movieId=%s"
	listurl = "http://m.maoyan.com/ajax/movieOnInfoList?token="
	commenturl = "http://m.maoyan.com/mmdb/comments/movie/%d.json?offset=%d&startTime=%s"
	name = "maoyan"

	def __init__(self):
		self.network = Network()
		self.db = Db()
		self.movieids = []

	def getdb(self):
		'''获取数据库实例'''

		return self.db

	def getlist(self,page):
		'''获取猫眼电影首页列表'''

		res = self.network.getjson(Maoyan.listurl)
		if res != None and "movieIds" in res:
			self.movieids = res['movieIds']
			for movieid in self.movieids:
				self.getdetail(movieid)
				

	def getdetail(self,movieid):
		'''获取电影详情数据'''

		sourceid = Maoyan.name+ str(movieid)

		log = self.db.find("movies",{"source_id":sourceid})
		tableid = None
		if log == False:
			movie = self.network.getjson( Maoyan.detailurl % str(movieid) )
			if movie != None:
				movie = movie['detailMovie']
				res = self.db.insert('movies',{
					'en_name':movie['enm'],
					'ch_name':movie['nm'],
					'source_id':sourceid,
					'release_date':movie['rt'],
					'score':movie['sc'],
					'score_num':movie['snum'],
					'zone':movie['src'],
					'lang':movie['oriLang'],
					'cat':movie['cat'],
					'star': movie['star'] if 'star' in movie else '',
					'description': movie['dra'] if 'dra' in movie else '',
					'director':movie['dir'] if 'dir' in movie else '',
					'cover':movie['img'],
					'create_at':int(time.time())
				})
				releasedate = movie['rt']
				if res:
					tableid = res
		else:
			tableid = log['id']
			releasedate = str( log['release_date'])
		page = 1

		releasetime = int(time.mktime( time.strptime( releasedate,"%Y-%m-%d" ) ) )
		starttime = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(time.time()) )
		while True:
			starttime = self.getcomments(movieid,tableid,starttime)
			if releasetime > int(time.mktime( time.strptime( starttime,"%Y-%m-%d %H:%M:%S" ) ) ):
				break
				

		# 获取电影详情
		pass

	def getcomments(self,movieid,tableid,startTime):
		'''获取评论数据
		猫眼电影评论数据最多分页1000页
		需要在获取1000页数据之后更新offsettime重新从第一页数据开始获取
		'''

		page = 1
		# 获取评论
		pagesize = 30
		t =  str(startTime).replace(" ","%20")
		lasttime = startTime
		while True:
			startoffset = (page-1)*pagesize
			
			url = Maoyan.commenturl % (movieid, startoffset,t)
			res = self.network.getjson(url)
			if res != None:
				if 'cmts' not in res:
					break
				comments = res['cmts']
				for item in comments:
					lasttime = item['startTime']
					sourceid = Maoyan.name+str(item['id'])
					log = self.db.find('comments',{"movie_id":str(tableid),"source_id":sourceid})
					if log:
						continue

					buytick = 0
					if 'tagList' in item:
						for tag in item['tagList']['fixed']:
				
							if tag['name'] == '购票':
								buytick = 1
					self.db.insert('comments',{
						'avatar':item['avatarurl'] if 'avatarurl' in item else '',
						'userlevel':item['userLevel'] if 'userLevel' in item else 0,
						'city':item['cityName'] if 'cityName' in item else '',
						'approve':item['approve'] if 'approve' in item else 0,#点赞数
						'buytick':buytick,
						'source_id':sourceid,
						'movie_id':tableid,
						'content':item['content'],
						'score':item['score'],
						'nick':item['nick'],
						'gender':item['gender'] if 'gender' in item else 3,
						'time':int(time.mktime( time.strptime( item['startTime'],"%Y-%m-%d %H:%M:%S" ) ) ),
						'create_at':int(time.time())
					})
					
			page = page+1

		return lasttime
			

	def startcron(self):
		self.getlist(1)
		



import urllib.request
import json
class Network:

	def __init__(self):
		self.headrs = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
		}
	def setheader(self,headrs):
		'''设置请求头'''

		self.headrs = headrs

	def get(self,url):
		'''get 方式获取数据'''
		html = urllib.request.urlopen( urllib.request.Request(method='GET',url=url,headers=self.headrs) )

		if html.getcode() == 200:
			return html.read()
		else:
			return None

	def getjson(self,url):
		'''get方式获取json数据'''
		res = self.get(url)
		if res != None:
			return json.loads(res,encoding='utf-8')
		return None








import MySQLdb

class Db:

	def __init__(self):
		self.db = MySQLdb.connect("localhost", "root", "", "maoyan", charset='utf8mb4' )


	def getdb(self):
		'''获取mysql连接对象'''

		return self.db


	def excute(self,cursor,sql):
		'''执行sql语句'''

		try:
			# 执行SQL语句
			res = cursor.execute(sql)
			if res !=False:
				return (res,cursor)
		except Exception as e:
			print(sql,e)


		return None

	def makeselectsql(self,table,wheremap,kw):
		'''执行select查询'''
		field = '*'
		sql = "SELECT %s from %s WHERE %s"

		wheres = []
		for k in wheremap.keys():
			item = wheremap[k]
			if isinstance(item, (list)):
				wheres.append(k+''+item[0]+"'"+item[1]+"'")
			else:
				wheres.append(k+"='"+item+"'")

		if kw != None:
			if 'field' in kw:
				field = kw['field']
			params = [field,table," AND ".join(wheres)]
			if 'order' in kw:
				sql = sql +' order by %s'
				params.append(kw['order'])
			if 'limit' in kw:
				sql = sql +' limit %s'
				params.append(kw['limit'])
		sql = sql % tuple(params)
		return self.excute(self.db.cursor(cursorclass = MySQLdb.cursors.DictCursor),sql)

	def select(self,table,wheremap,**kw):
		'''select 查询
			table 数据表
			wheremap dict 查询条件{"id":1,"status":['<',1]} 对应where id=1 and status<1
			kw 参数可以指定排字段 order='id desc'
		'''
		res = self.makeselectsql(table,wheremap,kw)
		if res != None:
			cursor = res[1]
			return cursor.fetchall()
		return False

	def find(self,table,wheremap,**kw):
		'''查询单个数据
			table 数据表
			wheremap dict 查询条件{"id":1,"status":['<',1]} 对应where id=1 and status<1
		'''

		kw['limit'] = '1';
		res = self.makeselectsql(table,wheremap,kw)
		if res != None:
			cursor = res[1]
			return cursor.fetchone()
		return False

	def count(self,table,wheremap,**kw):
		'''执行count查询
			table 数据表
			wheremap dict 查询条件{"id":1,"status":['<',1]} 对应where id=1 and status<1
		'''

		kw['field'] = 'count(*) as count'
		res = self.makeselectsql(table,wheremap,kw)
		if res != None:
			cursor = res[1]
			return cursor.rowcount()
		return False

	def insert(self,table,data):
		'''执行insert操作
			table 数据表
			data dict 需要插入的数据
		'''
		keys = []
		values = []
		valuesstrs = []
		for k in data.keys():
			keys.append(k)
			valuesstrs.append("'%s'")
			values.append(MySQLdb.escape_string( str(data[k]) ).decode('utf-8') )
		v = ",".join(valuesstrs) % tuple(values)

		sql = "INSERT INTO %s (%s) VALUES(%s)" % (table,",".join(keys), v )
		res = self.excute(self.db.cursor(cursorclass = MySQLdb.cursors.DictCursor),sql)
		if res != None:
			self.db.commit()
			return res[1].lastrowid
		self.db.rollback()
		return False



import pandas as pd
from pyecharts import Bar
from pyecharts import Grid,Page,Style
from MyGeo import MyGeo as Geo
from pyecharts import Pie
from pyecharts import Radar
from wordcloud import WordCloud, STOPWORDS,ImageColorGenerator
import jieba
import urllib.request
import matplotlib.pyplot as plt
import os
import re

class ReportGeneral:
	defaultSize = (1200,480)
	def __init__(self,tableid,db):
		self.tableid = tableid
		self.db = db
		self.movie = self.db.find("movies",{"id":str(tableid)})
		self.df = pd.read_sql("select * from comments where movie_id=%d order by time desc" % ( tableid, ) ,self.db.getdb(),index_col="id")

	def loaddata(self):
		'''pandas 从数据库中载入评论数据'''
		has_copy = any(self.df.duplicated())
		data_duplicated = self.df.duplicated().value_counts()
		data = self.df.drop_duplicates(keep="first")  # 删掉重复值
		data = data.reset_index(drop=True)  # 重置索引
		data["time"] =  pd.to_datetime(data['time'],unit='s')
		return data


	def generatescore(self,data,page):
		'''根据评分数据生成评分人数柱状图，性别分布饼状图，分时评论图'''

		bar = Bar("评分",title_pos ="center",width=ReportGeneral.defaultSize[0])
		pie = Pie("用户性别",title_pos ="center",width=ReportGeneral.defaultSize[0])
		# 购票人数评价情况
		tmp = data[data['buytick']==1]
		grouped = tmp.groupby(by="score")["source_id"].size()
		grouped = grouped.sort_values(ascending=False)
		index = grouped.index
		values = grouped.values
		bar.add("购票用户评分",index,values,is_label_show=True,is_legend_show=True,mark_line=["min","max"],legend_pos="80%")

		grouped = tmp.groupby(by="gender")["score"].count().sort_index()

		index = ["男","女","未知"]
		values = grouped.values
		pie.add("用户性别",index,values,radius=[45,65],is_label_show=True,legend_pos="80%",legend_orient= "vertical",title_pos ="center")

		tmp = data[data['buytick']==0]
		grouped = tmp.groupby(by="score")["source_id"].size()
		grouped = grouped.sort_values(ascending=False)
		index = grouped.index
		values = grouped.values
		bar.add("未购票用户评分",index,values,is_label_show=True,is_legend_show=True,mark_line=["min","max"],title_pos ="center",legend_pos="80%")
		page.add(bar)
		page.add(pie)

		data["hour"] = data["time"].dt.hour
		data["date"] = data["time"].dt.date
		need_date = data[["date","hour"]]
		def get_hour_size(mdata):
			hour_data = mdata.groupby(by="hour")["hour"].size().reset_index(name="count")
			return hour_data
		mdata = need_date.groupby(by="date").apply(get_hour_size)

		data_reshape = mdata.pivot_table(index="date",columns="hour",values="count")

		bar = Bar("分时评论分析",width =ReportGeneral.defaultSize[0],height=ReportGeneral.defaultSize[1],title_pos ="center")
		data_reshape.fillna(0,inplace=True)

		for index,row in data_reshape.T.iterrows():
			v1 = list(row.values)
			bar.add(str(index)+"时",row.index,v1,is_legend_show=True,legend_pos="80%",legend_text_size=8)

		page.add(bar)
		return page


	def handle(self,cities):
		# 获取坐标文件中所有地名
		data = None
		with open('C:/Program Files/Python37/Lib/site-packages/pyecharts/datasets/city_coordinates.json',mode='r', encoding='utf-8') as f:
			data = json.loads(f.read())  # 将str转换为json

		newcitys = []
		# 循环判断处理
		data_new = data.copy()  # 拷贝所有地名数据
		for citydata in cities:  # 使用set去重
			# 处理不存在的地名
			if citydata[1] == 0:
				break

			for k in data_new.keys():
				if k == citydata[0]:
					newcitys.append(citydata)
					break
		return newcitys


	def generategeo(self,data,page):
		'''生成地域分布图'''
		tmp = data[~data["city"].isnull()]
		grouped = tmp.groupby(by="city")["source_id"].size()
		cities = []
		mx = max(grouped.values)
		for k in grouped.index:
			if k != "":
				cities.append( tuple([k,grouped[k]]))

		
		cities = self.handle(cities)

		style = Style(
			title_color='#404a59',
			title_pos='center',
			width=1200,
			height=600,
			background_color='#fff'
		)
		
		def formatter(params):
			return params.name + params.value[2]
	

		geo = Geo("粉丝分布","",**style.init_style)
		attr, value = geo.cast(cities)
		# attr, value = geo.cast(data)
		mx = max(value)
		geo.add('', attr, value, visual_range=[0, mx], visual_text_color="#404a59", symbol_size=15, is_visualmap=True,tooltip_formatter=formatter,legend_pos="35%")
		page.add(geo)
		return page


	def data_wordclound(self,comments):
		'''生成词云图片'''
		urllib.request.urlretrieve(self.movie['cover'],'./tmp.jpg')

		hai_coloring = plt.imread('./tmp.jpg')
		# 多虑没用的停止词
		stopwords = STOPWORDS.copy()
		stopwords.add(self.movie['ch_name'])
		newwords = []
		with open('./stopword.dic.txt','r',encoding='utf-8') as f:
			words = f.read()
			newwords = words.split('\n')
		for w in newwords:
			stopwords.add(w)

		bg_image = plt.imread('./tmp.jpg')
		wc = WordCloud(width=640, height=900, mask=bg_image,
					   stopwords=stopwords, font_path='C:/Windows/Fonts/simhei.ttf', )

		plt.figure( figsize=(6.4,9), facecolor='k')
		plt.imshow(wc.generate(comments))
		plt.axis("off")
		plt.tight_layout(pad=0)
		name = self.movie['source_id']+self.movie['en_name']+"_word.jpg"
		plt.savefig(name)


		
		
		return name

	def staticcomment(self,data):
		'''统计评论词'''

		with open('./stopword.dic.txt','r',encoding='utf-8') as f:
			words = f.read()
			newwords = words.split('\n')

		commentwordstes = []
		comments = ''
		cmts = data['content']
		for item in cmts:
			if item != '':
				item = re.sub("[\.\!\?\%。？\*#￥\$^\&\@\=\->/\t\n\\<\d]+"," ",item)
				words = jieba.cut(item.strip())
				filterwords = []
				for w in words:
					if w not in newwords:
						commentwordstes.append({"word":w,'count':1})
						filterwords.append(w)

				if len(filterwords)>0:
					comments += ' '.join(filterwords)
		return (comments,commentwordstes)

	def generatecommentschart(self,comment,page):
		'''生成评论最多的100个词语图表'''
		df1=pd.DataFrame(comment)
		grouped = df1.groupby(by="word")["count"].size()
		grouped = grouped.sort_values(ascending=False).head(100)
		index = grouped.index
		values = grouped.values
		bar = Bar("出现次数最多的评论词语（前100）",width =ReportGeneral.defaultSize[0],height=ReportGeneral.defaultSize[1],title_pos ="center")
		bar.add("评论词语", index, values, is_stack=True,legend_pos="80%",)
		page.add(bar)
		return page


	def generage(self):
		'''生成报告'''
		title = "%s 电影分析报告" % self.movie['ch_name']
		data = self.loaddata()
		page = Page(page_title=title)
		commentinfo = self.staticcomment(data)
		page = self.generatecommentschart(commentinfo[1],page)
		wordpath = self.data_wordclound(commentinfo[0])
		commentinfo = None
		page = self.generatescore(data,page)
		page =self.generategeo(data,page)
		
		
		temp = "./template.html"
		page.render(title+".html",template_name=temp,movie=self.movie,wowrdcloudurl=wordpath)



if __name__ == '__main__':
	maoyan = Maoyan()
	# maoyan.startcron() #爬数据

	rep = ReportGeneral(1,maoyan.getdb()) #生成报告
	rep.generage()