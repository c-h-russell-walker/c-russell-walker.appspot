# Utilities & methods
# imports
import re
import cgi

# Regex for validation
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

# Validation functions
def valid_username(username):
  return USER_RE.match(username)
def valid_password(password):
  return PASSWORD_RE.match(password)
def valid_email(email):
  return EMAIL_RE.match(email)

# HTML Escape function
def escape_html(s):
  return cgi.escape(s, quote = True);