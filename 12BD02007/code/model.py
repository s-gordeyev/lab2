import sqlite3
from datetime import date

class Post:
	def __init__(self):
		self.user = None
		self.postText = None
		self.date = None
		
	def __init__(self, user, postText, date):
		self.user = user
		self.postText = postText
		self.date = date
		
	def __str__(self):
		return self.user + " " + self.postText + " " + self.date
		
		
class ServiceLayer:
	def __init__(self):
		self.data = None
		self.conn = sqlite3.connect('posts.db')
			
	def getValueOfAttr(self, attrName, cnt=None):
		return getattr(self.data if cnt is None else self.data[cnt], attrName, '')

	def getDataLength(self):
		return len(self.data)
		
	def getPosts(self, params = None):
		listOfPosts = []
	
		cur = self.conn.cursor()

		#rs = cur.execute('''delete from posts''')
		#self.conn.commit()
		
		rs = cur.execute('''select username, post, date from posts order by date''')
		
		for row in rs:
			listOfPosts.append(Post(row[0], row[1], row[2]))
		
		self.data = listOfPosts

		
	def insertPost(self, params):
		if params is None:
			return
		
		cur = self.conn.cursor()
		today = date.today()
		todayStr = str(today.year) + "-" + str(today.month) + "-" + str(today.day)

		prm = [params[b'user'][0].decode('UTF-8'), params[b'textPost'][0].decode('UTF-8'), todayStr]

		rs = cur.execute('''insert into posts(username, post, date) values(?, ?, ?)''', prm)
		self.conn.commit()
		
	def __del__(self):
		self.conn.commit()
		self.conn.close()	
		