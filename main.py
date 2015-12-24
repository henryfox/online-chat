import webapp2
import os
import jinja2
import urllib2
import json
import logging
from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape  = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Comment(db.Model):
	content = db.StringProperty(multiline=True)
	number = db.IntegerProperty()

class errorhandler(Handler):
	def get(self):
		self.render("error.html")

class storehandler(Handler):
	def post(self):
		self.query = Comment.all()
		self.name = self.request.cookies.get('name')  
    		self.post = str(self.request.get("post"))

		if self.post.replace(" ", "") == "":
    			self.redirect("/error")
		if self.post.replace(" ", ""):
    			word = {"words": []}
    			i = 0
	    		j = json.loads(urllib2.urlopen("http://www.wdyl.com/profanity?q=%s" % self.post.replace(" ", "+")).read())
	    		if j["response"] == "true":
	    			for x in self.post.split(" "):
	    				i += 1
	    				p = urllib2.urlopen("http://www.wdyl.com/profanity?q=%s" % str(x))
	    				j2 = json.loads(p.read())
	    				if j2["response"] == "true":
	    					word["words"].append({"swear": "true", "index": i - 1})
	    				else:
	    					word["words"].append({"swear": "false", "index": i - 1})
	   			for x in word["words"]:
	   				if x["swear"] == "true":
	   					start = int(x["index"])
	   					end = int(len(self.post.split(" ")[start]))
	   					self.post = self.post.split(" ")
	   					lenth = end - start
	   					self.post[start] = "*" * lenth
	   				
	   				self.post = " ".join(self.post)

    			self.comment = Comment(content= self.name + ": " + self.post)
    			self.comment.put()
    			self.redirect("/user")

class delethandler(Handler):
	def get(self):
		db.delete(Comment.all(keys_only=True))
		self.redirect("/user")

class makecooki(webapp2.RequestHandler):
	def get(self):
		name = self.request.get("name")
		self.response.headers.add_header('Set-Cookie', 'name=%s' % str(name))
		self.redirect("/user")


class MainHandler(Handler):
	def get(self):
		self.query = Comment.all()
		self.render("main.html", query=self.query)
		


	

class loginhandler(Handler):
	def get(self):
		self.render("login.html")
		
        

app = webapp2.WSGIApplication([
    ('/', loginhandler),
    ('/cookie', makecooki),
    ('/user', MainHandler),
    ('/store', storehandler),
    ('/delete', delethandler),
     ('/error', errorhandler)
], debug=True)
