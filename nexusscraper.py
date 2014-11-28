#!/usr/bin/python3
#License: WTFPL <http://www.wtfpl.net/>
#Author: zertap

import http.cookiejar
import urllib.request
from bs4 import BeautifulSoup
from io import StringIO
import sqlite3
import re

class NexusScraper():
    opener       = None
    catid_parser = None
    
    def __init__(self, cookie_path):
        cookie_jar  = self.get_cookies(cookie_path)
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

        self.catid_parser = re.compile(r"(?<=src_cat=)(\d+)")

    def get_category(self, modid, game="skyrim"):
        url      = "http://www.nexusmods.com/%s/mods/%s/?" % (game, modid)
        req      = self.opener.open(url)
        response = req.read()
        soup     = BeautifulSoup(response)

        try:
            header_cat = str(soup.select(".header-cat")[0])
            cat_id = self.catid_parser.findall(header_cat)[0]

            return cat_id
            
        except IndexError:
            print("Failed to fetch category id for %s/%s (File may be hidden/deleted.)" % (modid, game))
            
        
    def get_cookies(self, ff_cookies):
        cj  = http.cookiejar.CookieJar()
        con = sqlite3.connect(ff_cookies)
        cur = con.cursor()
        cur.execute("SELECT host, path, isSecure, expiry, name, value FROM moz_cookies")
        for item in cur.fetchall():
            c = http.cookiejar.Cookie(0, item[4], item[5],
                None, False,
                item[0], item[0].startswith('.'), item[0].startswith('.'),
                item[1], False,
                item[2],
                item[3], item[3]=="",
                None, None, {})
            cj.set_cookie(c)
        return cj
