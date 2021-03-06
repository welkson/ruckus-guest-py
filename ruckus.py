# -*- coding: utf-8 -*-

import mechanize
import ssl
import configparser
from BeautifulSoup import BeautifulSoup

# config
config = configparser.ConfigParser()
config.read("config.cfg")
zd_username = config['config']['zd_username']
zd_password = config['config']['zd_password']
zd_url = config['config']['zd_url'] + '/user/user_login_guestpass.jsp'
devices_limit = config['config']['devices_limit']

# ignore self-signed certificates alerts
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

# browser
br = mechanize.Browser()
br.set_handle_robots(False)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

# Open some site, let's pick a random one, the first that pops in mind:
r = br.open(zd_url)

# login form
br.select_form(nr=0)
br.form['username'] = zd_username
br.form['password'] = zd_password
br.submit()

url_principal = br.geturl()
br.open(url_principal)

# guest data
user = raw_input("Name: ")
days = raw_input( "Expiration in days: ")

br.select_form(nr=0)
br.form['fullname'] = user
br.form['duration'] = str(days)

# LimitNumber = number of devices by token (shared)
br.form.new_control('text', 'limitnumber', {'value': devices_limit})
br.form.fixup()

# submit form
br.submit()

# read html from ZD
html = br.response().read()

# extract html in soup format
soup = BeautifulSoup(html)

# recovery token
print "Your token: " + soup.find(id="key").string
