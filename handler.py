# Handler
import webapp2
import jinja_loader

class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
      self.response.out.write(*a, **kw)
  def render_str(self, template, **params):
      t = jinja_loader.jinja_env.get_template(template)
      return t.render(params)
  def render(self, template, **kw):
      self.write(self.render_str(template, **kw))