# -*- coding: utf-8 -*-


import sys
import os
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep 
import csv
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

AZ_E="xxx@xxx.xxx"
AZ_P="xxx"

ErrorFlag = True
Browser = None 
OrderFilters = None

 # re._pattern_type = re.Pattern

f = open('order_history.csv', 'a')
key = ['注文日', '合計', 'お届け先', 'item', 'item_url']
w = csv.writer(f, lineterminator='\n')
w.writerow(key)

def main():
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
  OrderFilters = rtv_orderfilter()

  while True:
    orderfilter_str = OrderFilters.pop()
    # if orderfilter_str is blank then exit

    # orderfiltersform['orderFilter'] = orderfilter_str
    select = Select(Browser.find_element_by_name('orderFilter'))
    select.select_by_value(orderfilter_str)
    assert '注文履歴' in Browser.page_source
    sleep(1)

    # print("DEBUG:main():Result of orderhistory\n", browser.parsed.prettify())
    while True:
      print_order_history()
      # break # For debugging, only 1page per year.

      try:
        link_to_next = Browser.find_element_by_css_selector('#ordersContainer > div.a-row > div > ul > li.a-last > a') # This is OK
        # link_to_next = browser.get_link('次')
        # print("link single:", link_to_next)
      except NoSuchElementException:
        break
      print('INFO:main():Following link...', link_to_next.get_attribute("href"), file=sys.stderr)
      link_to_next.click()

def open_orderhistory():
  global Browser
  Browser = None
  Browser = webdriver.Chrome(".\chromedriver")
  print('Navigating....', file=sys.stderr)
  Browser.get('https://www.amazon.co.jp/gp/css/order-history')
  assert 'Amazonログイン' in Browser.title
  form = Browser.find_element_by_name('signIn')
  form_email = Browser.find_element_by_name('email')
  form_pass = Browser.find_element_by_name('password')
  form_email.send_keys(AZ_E)
  form_pass.send_keys(AZ_P)
  form_email.submit()
  # Browser.submit_form(form, headers={'Referer':Browser.url, 'Accept-Language':'ja,en-US;q=0.7,en;q=0.3'})
  # print("DEBUG:open_orderhistory():browser-", Browser.parsed.prettify()[0:100])
  assert '注文履歴' in Browser.page_source
  # Browser.save_screenshot('search_result.png')
  sleep(1)

def chk_orderhistory_error():
    links = Browser.find_elements_by_css_selector('#ordersContainer > div.a-row > div > ul > li.a-last > a') # This is OK
    # links = Browser.find_elements_by_link_text('次へ') # This is OK
    # print("DEBUG:chk_orderhisotry_erro():links-", links)
    if not links:
      print("DEBUG:open_orderhistory_error():browser-", Browser.parsed.prettify())
      return True
    return  False

def rtv_orderfilter():
    select = Browser.find_element_by_name('orderFilter')
    optionvalues = select.find_elements_by_tag_name('option')
    # print("DEBUG:rtv_orderfilter():Option Values-", optionvalues)
    optionlist = []
    for option in optionvalues:
      if option.get_attribute("value").startswith("year"):
        optionlist.append(option.get_attribute("value"))
    # print("DEBUG:rtv_orderfilter():optionlist-", optionlist)
    return optionlist

def print_order_history():
  for line_item in Browser.find_elements_by_class_name('order'):
    order_h = {}
    for column in line_item.find_elements_by_css_selector("div.order-info div.a-column"):
        # print("DEBUG:print_order_history():column-", column)
        try:
          label_e = column.find_element_by_css_selector('.label')
          # label_e = column.find_element_by_class_name('label')
          value_e = column.find_element_by_css_selector('.value')
          # value_e = column.find_element_by_class_name('value')
        except NoSuchElementException:
          continue
        if label_e and value_e: 
          label = label_e.text
          #label = label_e.text().strip()
          value = value_e.text
          #value = value_e.text().strip()
          order_h[label] = value
    for line_item_s in line_item.find_elements_by_css_selector('.shipment .a-row > a.a-link-normal' ):
        order = order_h.copy()
        # print('DEBUG:print_order_history():shipment-', line_item_s)
        label = line_item_s.text.encode('cp932', 'ignore').decode('cp932').strip()
        value = line_item_s.get_attribute('href').encode('cp932', 'ignore').decode('cp932').strip()
        order['item'] = label
        order['item_url'] = value
        # order['item_url'] = value.rstrip('\r')

        print("INFO:print_order_history():order-", order) 
        w.writerow(list(order.values()))


if __name__ == '__main__':
  while True:
    main()
    if not ErrorFlag:
       break
    sleep(10)
    Browser.close()
