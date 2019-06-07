# -*- coding: utf-8 -*-

#01 とりあえず出来上がり
#02 半年分はOK 
#03 implement orderfilter but does not work, always error for connectivity, and csv encoding error

import sys
import os
import re
from robobrowser import RoboBrowser
from time import sleep 
import csv

AZ_E="xxxx@xxxx.xxxx"
AZ_P="xxxx"

ErrorFlag = True
Browser = None 
OrderFilters = None

re._pattern_type = re.Pattern

f = open('order_history.csv', 'a')
key = ['注文日', '合計', 'お届け先', 'item', 'item_url']
w = csv.writer(f, lineterminator='\n')
w.writerow(key)
# header = {k : k for k in key}
# w = csv.DictWriter(f, header)
# w.writerow(header)

def main():
  # global Browser
  global ErrorFlag
  global OrderFilters

  # Order Fiter List
  open_orderhistory()
  print("DEBUG:main():Browser-", Browser)
  if chk_orderhistory_error():
    print("INFO:main():Order History Loading error")
    ErrorFlag = True
    return
  else:
    ErrorFlag = False
  orderfiltersform = rtv_orderfilter()
  OrderFilters = orderfiltersform['orderFilter'].options   

  while True:
    orderfilter_str = OrderFilters.pop()
    # if orderfilter_str is blank then exit

    orderfiltersform['orderFilter'] = 'year-2008'
    # orderfiltersform['orderFilter'] = orderfilter_str
    Browser.submit_form(orderfiltersform, headers={'Referer':Browser.url, 'Accept-Language':'ja,en-US;q=0.7,en;q=0.3'})
    assert '注文履歴' in Browser.parsed.title.string
    sleep(1)

    # print("DEBUG:main():Result of orderhistory\n", browser.parsed.prettify())
    while True:
      print_order_history()
      break

      link_to_next = browser.get_link('次')
      # print("link single:", link_to_next)
      if not link_to_next:
        break
      print('Following link...', file=sys.stderr)
      browser.follow_link(link_to_next)

def open_orderhistory():
  global Browser
  Browser = None
  Browser = RoboBrowser(parser='html.parser',user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36') 
  print('Navigating....', file=sys.stderr)
  Browser.open('https://www.amazon.co.jp/gp/css/order-history')
  assert 'Amazonログイン' in Browser.parsed.title.string
  form = Browser.get_form(attrs={'name':'signIn'})
  form['email'] = AZ_E
  form['password']=AZ_P
  Browser.submit_form(form, headers={'Referer':Browser.url, 'Accept-Language':'ja,en-US;q=0.7,en;q=0.3'})
  # print("DEBUG:open_orderhistory():browser-", Browser.parsed.prettify()[0:100])
  assert '注文履歴' in Browser.parsed.title.string
  sleep(1)

def chk_orderhistory_error():
    links = Browser.get_links('次') # This is OK
    # links = browser.get_links(re.compile('.*次'))  # This is OK with RE
    # print("DEBUG:chk_orderhisotry_erro():links-", links)
    if not links:
      print("DEBUG:open_orderhistory():browser-", Browser.parsed.prettify())
      return True
    return  False

def rtv_orderfilter():
    form = Browser.get_form(attrs={'id':'timePeriodForm'})
    # print("DEBUG:rtv_orderfilter():form-", form)
    # print("DEBUG:rtv_orderfilter():form options-", form['orderFilter'].options)
    return form

def print_order_history():
  # global browser
  for line_item in Browser.select('.order'):
#   for line_item in browser.select('.order-info'):
    order_h = {}
    # for column in line_item.select("div.order-info div[class='a-columni'][class='a-row']"): # Does not work?
    for column in line_item.select("div.order-info div[class^='a-']"):
#      for column in line_item_o.select('.a-column'):
        # print("column:", column)
        label_e = column.select_one('.label')
        value_e = column.select_one('.value')
        if label_e and value_e: 
          label = label_e.get_text().strip()
          value = value_e.get_text().strip()
          order_h[label] = value
    for line_item_s in line_item.select('.shipment .a-row > a.a-link-normal' ):
        order = order_h.copy()
      # print('shipment', line_item_s)
      # for raw in line_item_s.select('.a-row a.a-link-normal'):
        # print('raw:', raw)
        label = line_item_s.text.strip()
        value = line_item_s.get('href').strip()
        order['item'] = label
        order['item_url'] = value.rstrip('\r')

        print(order) 
        w.writerow(list(order.values()))


if __name__ == '__main__':
  while True:
    main()
    if not ErrorFlag:
       break
    sleep(10)
