import webapp2
import cgi
import os
import re
import jinja2
from jinja2 import Environment
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)
  
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_username(username):
  return USER_RE.match(username)
def valid_password(password):
  return PASSWORD_RE.match(password)
def valid_email(email):
  return EMAIL_RE.match(email)

def escape_html(s):
  return cgi.escape(s, quote = True);

class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
      self.response.out.write(*a, **kw)
  def render_str(self, template, **params):
      t = jinja_env.get_template(template)
      return t.render(params)
  def render(self, template, **kw):
      self.write(self.render_str(template, **kw))

class MainHandler(Handler):
  def get(self):
    self.render("front.html");

# Display 10 most recents entires
class BlogHandler(Handler):
  def get(self, id=""):
    posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 10")
    if id:
      # retrieve post with passed in id cast as integer
      post = Post.get_by_id(int(id))
      self.render("blog.html", post=post)
    else:
      self.render("blog.html", posts=posts)

class Post(db.Model):
  subject = db.StringProperty(required = True)
  content = db.TextProperty(required = True)
  created = db.DateTimeProperty(auto_now_add = True)

class PostHandler(Handler):
  def get(self):
    self.render("post_form.html")
  def post(self):
    subject = escape_html(self.request.get("subject"))
    content = escape_html(self.request.get("content"))
    
    if subject and content:
      p = Post(subject = subject, content = content)
      p.put()
      # redirect to permalink for entry
      post_id = str(p.key().id())
      self.redirect("/blog/post/" + post_id)
    else:
      error = "Please enter both subject and content."
      self.render("post_form.html", subject=subject, content=content, error=error)

class Art(db.Model):
  title = db.StringProperty(required = True)
  art = db.TextProperty(required = True)
  created = db.DateTimeProperty(auto_now_add = True)

class AsciiHandler(Handler):
  def render_front(self, title="", art="", error=""):
    arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
    self.render("ascii.html", title=title, art=art, error=error, arts=arts)
  def get(self):
    self.render_front()
  def post(self):
    title = self.request.get("title")
    art = self.request.get("art")
    
    if title and art:
      a = Art(title = title, art = art)
      a.put()
      self.redirect("/")
    else:
      error = "We need both a title and artwork."
      self.render_front(title, art, error)

class SignupHandler(Handler):
  def write_form(self,
                 username_error="",
                 password_error="",
                 password_match_error="",
                 email_error="",
                 username="",
                 email=""):
    self.render("signup_form.html", username_error = username_error,
                                    password_error = password_error,
                                    password_match_error = password_match_error,
                                    email_error = email_error,
                                    username = username,
                                    email = email)
   
  def get(self):
    self.write_form()
  
  def post(self):
    user_username = escape_html(self.request.get('username'))
    user_password = escape_html(self.request.get('password'))
    user_verify = escape_html(self.request.get('verify'))
    user_email = escape_html(self.request.get('email'))
    
    username_error = ''
    password_error = ''
    password_match_error = ''
    email_error = ''
    
    username = valid_username(user_username)
    password = valid_password(user_password)
    verify = valid_password(user_verify)
    if len(user_email) > 0:
      email = valid_email(user_email)
    else:
      email = True;
    
    error_flag = False;
    
    if not username:
      error_flag = True;
      username_error = 'That\'s not a valid username.'
    if not password:
      error_flag = True;
      password_error = 'That\'s not a valid password.'
    if not user_password == user_verify:
      error_flag = True;
      password_match_error = 'Your passwords didn\'t match.'
    if not email:
      error_flag = True;
      email_error = 'That\'s not a valid email.'
    
    if not error_flag:
      self.redirect("/welcome?username=%s" % user_username)
    else:
      self.write_form(username_error, password_error, password_match_error, email_error, user_username, user_email)

class rot13Handler(Handler):
  def write_form(self, rot13=""):
    self.render("rot13_form.html", rot13=rot13)
  
  def get(self):
    self.write_form()
  
  def post(self):
    user_rot13 = self.request.get('text')
    user_rot13 = escape_html(user_rot13)
    rot13 = user_rot13.encode("rot13")
    self.write_form(rot13)

class WelcomeHandler(webapp2.RequestHandler):
  def get(self):
    username = self.request.get('username')
    if valid_username(username):
      self.response.out.write("<h2>Welcome, " + username + "!</h2>")
    else:
      self.redirect('signup')

app = webapp2.WSGIApplication([('/', MainHandler),
                                ('/ascii', AsciiHandler),
                                ('/blog', BlogHandler),
                                ('/blog/post/([-\w]+)', BlogHandler),
                                ('/blog/newpost', PostHandler),
                                ('/rot13', rot13Handler),
                                ('/welcome', WelcomeHandler),
                                ('/signup', SignupHandler)],
                                debug=True)