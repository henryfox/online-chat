import webapp2
import os
import jinja2
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

class storehandler(Handler):
	def post(self):
    		post = self.request.get("post")
    		self.comment = Comment(content=post)
    		self.comment.put()
    		self.redirect("/user")

class delethandler(Handler):
	def get(self):
		db.delete(Comment.all(keys_only=True))
		self.redirect("/user")

class MainHandler(Handler):
	def get(self):
		name = self.request.get("name")
		self.response.headers.add_header('Set-Cookie', 'name=%s' % str(name))
		self.query = Comment.all()
		self.render("main.html", query = self.query)
		


	

class loginhandler(Handler):
	def get(self):
		self.render("login.html")
		
        

app = webapp2.WSGIApplication([
    ('/', loginhandler),
    ('/user', MainHandler),
    ('/store', storehandler),
    ('/delete', delethandler)
], debug=True)