# ROT13

import handler
import utilities

class rot13Handler(handler.Handler):
  def write_form(self, rot13=""):
    self.render("rot13_form.html", rot13=rot13)
  
  def get(self):
    self.write_form()
  
  def post(self):
    user_rot13 = self.request.get('text')
    user_rot13 = utilities.escape_html(user_rot13)
    rot13 = user_rot13.encode("rot13")
    self.write_form(rot13)