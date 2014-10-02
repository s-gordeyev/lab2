import http.server
import socketserver
import re
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs

from model import *

HOST_NAME = 'localhost'
PORT_NUMBER = 9000

class Controller:
	def __init__(self):
		self.sl = ServiceLayer()
		self.fileName = None
		self.action = None
		self.param  = None
		self.textExt = ['.html', '.htm', '.foot', '.head']

	def getMethodByAction(self, action):
		try:
			return {'index':'getPosts', 'insertPost':'insertPost'}[action]
		except:
			return action
		
	def buildPage(self, fileName, action=None, param=None):
		if len([i for i in self.textExt if i == fileName[fileName.rfind('.'):]]) == 0:
			return self.readBFile(fileName)
	
		self.fileName = fileName
		self.action = action
		self.param  = param
	
		act = action
		if act is None:
			at = fileName.rfind('/')
			if at == -1: at = 0
			act = fileName[at:]
			
			at = fileName.rfind('.')
			if at == -1: at = 0
			act = act[:at]
			
			
		methodName = self.getMethodByAction(act)
		method = getattr(self.sl, methodName, None)
		if method is not None:
			method(param)
	
		text = self.readFile(self.fileName)
		text = self.replaceKeyWords(text)
		return bytes(text, 'UTF-8')
			
			
	def replaceKeyWords(self, text):
		text = self.replaceIteration(text)
	
		atA = text.find('<@')
		atB = -1

		while atA != -1:
			atB = text.find('@>', atA)
			hk = self.execute(text[atA+2:atB])
			hk = self.replaceKeyWords(hk)
			text = text[:atA] + hk + text[atB+2:]
			atA = text.find('<@')

		return text
		
	def replaceIteration(self, text):
		p = re.compile('(<@\s*replicate\s*@>)(.*)(<@\s*replicate[ ]\s*@>)', re.DOTALL)
		
		m = p.search(text)
		
		while m is not None:
			at = m.span(2)
			atWhole = m.span()
			p2 = re.compile('(<@\s*\w+\s*)(\w+)(\s*@>)')
			cmd = text[at[0]:at[1]]
			
			hkC = ''
			
			for i in range(self.sl.getDataLength()):
				hk = cmd
				m2 = p2.search(hk)
				
				while m2 is not None:
					at2 = m2.span(2)
					atWhole2 = m2.span()

					hk = hk[:atWhole2[0]] + self.sl.getValueOfAttr(hk[at2[0]:at2[1]], i) + hk[atWhole2[1]:]
					m2 = p2.search(hk)
				hkC += hk
					
			text = text[:atWhole[0]] + hkC + text[atWhole[1]:]
			m = p.search(text)
					
		return text

	def execute(self, command):
		atA = command.find('include')
		if atA > -1:
			path = command[atA+7:].strip()
			ans = self.readFile(path)
			return ans
			
		atA = command.find('put')
		if atA > -1:
			attr = command[atA+3:].strip()
			return self.sl.getValueOfAttr(attr)

		return ''

	def readFile(self, fileName):
		try:
			file = open(fileName, 'r')
			lines = file.readlines()

			fileText = ''
			for line in lines:
				fileText += line

			at = fileText.find('<')
			at = 0 if at == -1 else at
			fileText = fileText[at:]			
			
			return fileText
		except:
			return ''
		
	def readBFile(self, fileName):
		try:
			with open(fileName, mode='rb') as file:
				fileContent = file.read()
			return fileContent
		except FileNotFoundError as fnf:
			print('Exception:', fnf)
			return b''
		


class Handler(http.server.BaseHTTPRequestHandler):
	cntrl = Controller()
	
	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

	def getFileName(self):
		fileName = None

		if self.path.strip() == '/':
			fileName = 'index.html'
		else:
			fileName = self.path[1:]

		return fileName
		
	def do_GET(self):
		fileName = self.getFileName()
			
		page = self.cntrl.buildPage(fileName)
		
		self.do_HEAD()
		self.wfile.write(page)

	def parse_POST(self):
		ctype, pdict = parse_header(self.headers['content-type'])
		if ctype == 'multipart/form-data':
			postvars = parse_multipart(self.rfile, pdict)
		elif ctype == 'application/x-www-form-urlencoded':
			length = int(self.headers['content-length'])
			postvars = parse_qs(
					self.rfile.read(length), 
					keep_blank_values=1)
		else:
			postvars = {}
		return postvars
		
		
	def do_POST(self):
		postvars = self.parse_POST()

		fileName = self.getFileName()
		page = self.cntrl.buildPage(fileName, None,postvars)
		
		self.do_HEAD()
		self.wfile.write(page)
		

if __name__ == '__main__':
	httpd = http.server.HTTPServer((HOST_NAME, PORT_NUMBER), Handler)
	try:
		print("Server Starting - %s:%s" % (HOST_NAME, PORT_NUMBER))
		httpd.serve_forever()
	except KeyboardInterrupt:
		httpd.server_close()
	print("Server Stopped - %s:%s" % (HOST_NAME, PORT_NUMBER))