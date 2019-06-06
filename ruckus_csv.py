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
zd_url = config['config']['zd_url']
devices_limit = config['config']['devices_limit']


# ZoneDirector Login
def zd_login():
    url_login = zd_url + "/user/user_login_guestpass.jsp"

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
    r = br.open(url_login)

    # login form
    br.select_form(nr=0)
    br.form['username'] = zd_username
    br.form['password'] = zd_password
    br.submit()

    return br


# Generate Guest Pass Token
def gen_token(br, url, username, expiration):
        # redirect to guest pass page
        br.open(url)
    
        br.select_form(nr=0)
        br.form['fullname'] = username
        br.form['duration'] = str(expiration)

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
        return soup.find(id="key").string


if __name__ == "__main__":
    # ZD connection/login
    br = zd_login()
    url_principal = br.geturl()
    br.open(url_principal)

    # guest data
    days = raw_input( "Expiration in days: ")

    with open('userlist.txt', 'r') as f:
        content = f.read().splitlines()

        for line in content:
            print "Username: %s" % line
            print "Token: %s\n" % gen_token(br, url_principal, line, days)
