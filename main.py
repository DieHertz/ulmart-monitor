#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import lxml.html
import smtplib
import time

articles = set()
available = {}


def fetch_html(url):
    connection = urllib2.urlopen(url)
    html = connection.read()
    connection.close()
    return lxml.html.fromstring(html)


def send_email(url, available):
    """Sends email about availability of an item"""
    no = '' if available else 'no longer'
    sender = 'ulmart'
    recipients = ['diehertz@gmail.com']
    message = '\r\n'.join([
        'From: Andrey M. <diehertz@gmail.com>',
        'To: Andrey M. <diehertz@gmail.com>',
        'MIME-Version: 1.0',
        'Content-type: text/html; charset=utf-8',
        'Subject: Item %s available!' % no,
        '',
        '<a href="%s">Item</a> is %s available for purchase!' % (url, no)
    ])
    login = ''
    pwd = ''

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(login, pwd)
    smtp.sendmail(sender, recipients, message)
    smtp.quit()


def print_with_time(s):
    print time.strftime('%d %B %Y %H:%M:%S') + ': ' + s


def check_article(article):
    article_str = str(article)
    url = 'http://ulmart.ru/goods/' + article_str
    document = fetch_html(url)

    status = document.get_element_by_id('p-stat')
    status_text = status.iterchildren().next().text_content().strip()
    is_available = status_text == 'Есть в наличии'.decode('utf-8')

    print_with_time(article_str + ': ' + status_text)

    try:
        if is_available and not available[article]:
            send_email(url, True)
        elif not is_available and available[article]:
            send_email(url, False)
    except Exception, e:
        print_with_time(e.message)
    else:
        available[article] = is_available


def check_articles():
    for article in articles:
        try:
            check_article(article)
        except:
            pass


sleep_time_sec = 15


def fetch_articles():
    print_with_time('fetching articles')
    url = 'http://ulmart.ru/search?string=gtx+980&discount=true'
    document = fetch_html(url)

    product_list = document.get_element_by_id('catalogGoodsBlock').getchildren()[-1].find_class('b-product')
    for product in product_list:
        article = int(product.get('id').replace('prod', ''))
        if article not in articles:
            articles.add(article)
            available[article] = False

n = 0
while True:
    try:
        if not n % 20:
            fetch_articles()
        check_articles()
    except Exception, e:
        print_with_time(e.message)
    finally:
        time.sleep(sleep_time_sec)
        n += 1
