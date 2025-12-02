from django.test import TestCase
import pytest
import time, re
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class TestLogin():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.driver.implicitly_wait(10)
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_login(self):
    self.driver.get("http://localhost:8000/")
    self.driver.set_window_size(1133, 840)
    self.driver.find_element(By.LINK_TEXT, "Log In").click()
    self.driver.find_element(By.ID, "id_password").send_keys("r)uEP)}Wv$h_4ZY")
    self.driver.find_element(By.ID, "id_username").send_keys("clintplozay2@gmail.com")
    self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(6)").click()
    text = self.driver.find_element(By.CSS_SELECTOR, "section .muted").text
    print(text)
    assert text == 'Hi clintplozay2@gmail.com!', 'login unsuccessfull'

class TestChangeamount():
    def setup_method(self, method):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_changeamount(self):
        self.driver.get("http://localhost:8000/")
        self.driver.set_window_size(1133, 840)
        self.driver.find_element(By.LINK_TEXT, "Log In").click()
        self.driver.find_element(By.ID, "id_password").send_keys("r)uEP)}Wv$h_4ZY")
        self.driver.find_element(By.ID, "id_username").send_keys("clintplozay2@gmail.com")
        self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(6)").click()
        self.driver.find_element(By.LINK_TEXT, "Buy Stocks").click()
        self.driver.find_element(By.ID, "search").click()
        self.driver.find_element(By.ID, "search").send_keys("AMZN")
        self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
        self.driver.find_element(By.CSS_SELECTOR, ".center").click()

        self.driver.find_element(By.CSS_SELECTOR, "tr .amount").click()
        self.driver.find_element(By.CSS_SELECTOR, "tr .amount").send_keys(Keys.BACK_SPACE + '2')
        result = int(self.driver.find_element(By.CSS_SELECTOR, "tr .total").text)
        inpt = int(float(self.driver.find_element(By.CSS_SELECTOR, "tr .price").text) * 2)
        assert result == inpt, f'result:{result}'


        

class TestAddtocart():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.driver.implicitly_wait(10)
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_addtocart(self):
    self.driver.get("http://localhost:8000/")
    self.driver.set_window_size(1133, 840)
    self.driver.find_element(By.LINK_TEXT, "Log In").click()
    self.driver.find_element(By.ID, "id_password").send_keys("r)uEP)}Wv$h_4ZY")
    self.driver.find_element(By.ID, "id_username").send_keys("clintplozay2@gmail.com")
    self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(6)").click()
    self.driver.find_element(By.LINK_TEXT, "Buy Stocks").click()
    self.driver.find_element(By.ID, "search").click()
    self.driver.find_element(By.ID, "search").send_keys("AMZN")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    self.driver.find_element(By.CSS_SELECTOR, ".center").click()
    el = self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) .ticker")
    assert el.text == 'AMZN', f'result:{el.text}, should be AMZN'
  '''
class TestCheckout():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.driver.implicitly_wait(10)
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_checkout(self):
    self.driver.get("http://localhost:8000/")
    self.driver.set_window_size(1133, 840)
    self.driver.find_element(By.LINK_TEXT, "Log In").click()
    self.driver.find_element(By.ID, "id_password").send_keys("r)uEP)}Wv$h_4ZY")
    self.driver.find_element(By.ID, "id_username").send_keys("clintplozay2@gmail.com")
    self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(6)").click()
    wallet = self.driver.find_element(By.CSS_SELECTOR, 'section .userPanel p:nth-child(2)').text
    assert wallet != None
    old_val = float(re.findall('[0-9]+[.]{0,1}[0-9]*',wallet)[0])
    self.driver.find_element(By.LINK_TEXT, "Buy Stocks").click()
    self.driver.find_element(By.ID, "search").click()
    self.driver.find_element(By.ID, "search").send_keys("SPOT")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    WebDriverWait(self.driver, 10).until(
        lambda driver: driver.find_element(By.ID, "search").get_attribute("value") == ""
    )
    self.driver.find_element(By.ID, "search").send_keys(Keys.BACK_SPACE * 4)
    self.driver.find_element(By.ID, "search").send_keys("NVDA")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    WebDriverWait(self.driver, 10).until(
        lambda driver: driver.find_element(By.ID, "search").get_attribute("value") == ""
    )
    #self.driver.find_element(By.ID, "search").send_keys(Keys.BACK_SPACE * 4)
    self.driver.find_element(By.CSS_SELECTOR, ".center").click()
    self.driver.find_element(By.ID, "checkout").click()
    time.sleep(10)
    wallet = self.driver.find_element(By.CSS_SELECTOR, 'section .userPanel p:nth-child(2)').text
    new_val = float(re.findall('[0-9]+[.]{0,1}[0-9]*',wallet)[0])
    total1 = self.driver.find_element(By.CSS_SELECTOR, "tbody tr:nth-child(1) .price").text
    total2 = self.driver.find_element(By.CSS_SELECTOR, "tbody tr:nth-child(2) .price").text
    expected = round(old_val - (total1 + total2),2)
    assert new_val == expected, f'{new_val} != {old_val - (total1 + total2)}'
'''
class TestDuplicateentry():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.driver.implicitly_wait(10)
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_duplicateentry(self):
    self.driver.get("http://localhost:8000/")
    self.driver.set_window_size(1133, 840)
    self.driver.find_element(By.LINK_TEXT, "Log In").click()
    self.driver.find_element(By.ID, "id_password").send_keys("r)uEP)}Wv$h_4ZY")
    self.driver.find_element(By.ID, "id_username").send_keys("clintplozay2@gmail.com")
    self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(6)").click()
    self.driver.find_element(By.LINK_TEXT, "Buy Stocks").click()
    self.driver.find_element(By.ID, "search").click()
    self.driver.find_element(By.ID, "search").send_keys("NVDA")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    WebDriverWait(self.driver, 10).until(
        lambda driver: driver.find_element(By.ID, "search").get_attribute("value") == ""
    )
    self.driver.find_element(By.ID, "search").send_keys("NVDA")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    WebDriverWait(self.driver, 10).until(
        lambda driver: driver.find_element(By.ID, "search").get_attribute("value") == ""
    )
    self.driver.find_element(By.ID, "search").send_keys("NVDA")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    WebDriverWait(self.driver, 10).until(
        lambda driver: driver.find_element(By.ID, "search").get_attribute("value") == ""
    )
    self.driver.find_element(By.ID, "search").send_keys("SPOT")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    WebDriverWait(self.driver, 10).until(
        lambda driver: driver.find_element(By.ID, "search").get_attribute("value") == ""
    )
    self.driver.find_element(By.ID, "search").send_keys("SPOT")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    WebDriverWait(self.driver, 10).until(
        lambda driver: driver.find_element(By.ID, "search").get_attribute("value") == ""
    )
    self.driver.find_element(By.CSS_SELECTOR, ".center").click()
    time.sleep(1)
    result = len(self.driver.find_elements(By.CSS_SELECTOR, "tbody tr"))
    assert result == 2

class TestNavigatebuy():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.driver.implicitly_wait(10)
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_navigatebuy(self):
    self.driver.get("http://localhost:8000/")
    self.driver.set_window_size(1133, 840)
    self.driver.find_element(By.LINK_TEXT, "Log In").click()
    self.driver.find_element(By.ID, "id_password").send_keys("r)uEP)}Wv$h_4ZY")
    self.driver.find_element(By.ID, "id_username").send_keys("clintplozay2@gmail.com")
    self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(6)").click()
    self.driver.find_element(By.LINK_TEXT, "Buy Stocks").click()
    self.driver.find_element(By.LINK_TEXT, "Home").click()
    self.driver.find_element(By.LINK_TEXT, "Sell Stocks").click()
    self.driver.find_element(By.LINK_TEXT, "Buy Stocks").click()
    assert self.driver.find_element(By.CSS_SELECTOR, "header h1").text == 'Buy Stocks'
  
