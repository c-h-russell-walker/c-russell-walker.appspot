import webapp2
from google.appengine.ext import db

# import files
import handler
import rot13
import utilities

class MainHandler(handler.Handler):
  def get(self):
    self.render("front.html");

# Display 10 most recents entires
class BlogHandler(handler.Handler):
  def get(self, id=""):
    if id:
      # retrieve post with passed in id cast as integer
      post = Post.get_by_id(int(id))
      if not post:
        self.error(404)
        return
      self.render("blog.html", post=post)
    else:
      # posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 10")
      # Google App Engine API - todo: add 10 limit
      posts = Post.all().order('-created')
      self.render("blog.html", posts=posts)

class Post(db.Model):
  subject = db.StringProperty(required = True)
  content = db.TextProperty(required = True)
  created = db.DateTimeProperty(auto_now_add = True)
  last_modified = db.DateTimeProperty(auto_now = True)

class PostHandler(handler.Handler):
  def get(self):
    self.render("post_form.html")
  def post(self):
    subject = utilities.escape_html(self.request.get("subject"))
    content = utilities.escape_html(self.request.get("content"))
    
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

class AsciiHandler(handler.Handler):
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

class SignupHandler(handler.Handler):
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
    user_username = utilities.escape_html(self.request.get('username'))
    user_password = utilities.escape_html(self.request.get('password'))
    user_verify = utilities.escape_html(self.request.get('verify'))
    user_email = utilities.escape_html(self.request.get('email'))
    
    username_error = ''
    password_error = ''
    password_match_error = ''
    email_error = ''
    
    username = utilities.valid_username(user_username)
    password = utilities.valid_password(user_password)
    verify = utilities.valid_password(user_verify)
    if len(user_email) > 0:
      email = utilities.valid_email(user_email)
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
                                ('/blog/post/([0-9]+)', BlogHandler),
                                ('/blog/newpost', PostHandler),
                                ('/rot13', rot13.rot13Handler),
                                ('/welcome', WelcomeHandler),
                                ('/signup', SignupHandler)],
                                debug=True)