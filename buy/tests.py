from django.test import TestCase
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from django.test import TestCase

class TestChangeamount():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_changeamount(self):
    self.driver.get("http://localhost:8000/")
    self.driver.set_window_size(1204, 803)
    self.driver.find_element(By.LINK_TEXT, "Buy Stocks").click()
    self.driver.find_element(By.ID, "search").click()
    self.driver.find_element(By.ID, "search").send_keys("NVDA")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    self.driver.find_element(By.ID, "search").send_keys("AMZN")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    self.driver.find_element(By.CSS_SELECTOR, ".center").click()
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) .amount").send_keys("2")
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) .amount").click()
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) .amount").send_keys("3")
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) .amount").click()
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) .amount").send_keys("2")
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) .amount").click()
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) .amount").send_keys("3")
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) .amount").click()
    element = self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) .amount")
    actions = ActionChains(self.driver)
    actions.double_click(element).perform()
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) .amount").send_keys("4")
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) .amount").click()

class TestAddtocart(TestCase):
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_addtocart(self):
    self.driver.get("http://localhost:8000/")
    self.driver.set_window_size(1014, 861)
    self.driver.find_element(By.LINK_TEXT, "Buy Stocks").click()
    self.driver.find_element(By.ID, "search").click()
    self.driver.find_element(By.ID, "search").send_keys("AMZN")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    self.driver.find_element(By.ID, "search").send_keys("NVDA")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    self.driver.find_element(By.CSS_SELECTOR, ".center").click()
  
class TestCheckout():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_checkout(self):
    self.driver.get("http://localhost:8000/")
    self.driver.set_window_size(1261, 863)
    self.driver.find_element(By.LINK_TEXT, "Buy Stocks").click()
    self.driver.find_element(By.ID, "search").click()
    self.driver.find_element(By.ID, "search").send_keys("SPOT")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    self.driver.find_element(By.ID, "search").send_keys("NVDA")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    self.driver.find_element(By.CSS_SELECTOR, ".center").click()
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) .amount").send_keys("2")
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) .amount").click()
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) .amount").send_keys("2")
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) .amount").click()
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) .amount").send_keys("3")
    self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) .amount").click()
    self.driver.find_element(By.ID, "checkout").click()

class TestDuplicateentry():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_duplicateentry(self):
    self.driver.get("http://localhost:8000/")
    self.driver.set_window_size(1079, 861)
    self.driver.find_element(By.LINK_TEXT, "Buy Stocks").click()
    self.driver.find_element(By.ID, "search").click()
    self.driver.find_element(By.ID, "search").send_keys("NVDA")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    self.driver.find_element(By.ID, "search").send_keys("NVDA")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    self.driver.find_element(By.ID, "search").send_keys("NVDA")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    self.driver.find_element(By.ID, "search").send_keys("SPOT")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    self.driver.find_element(By.ID, "search").send_keys("SPOT")
    self.driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
    self.driver.find_element(By.CSS_SELECTOR, ".center").click()
  
class TestNavigatebuy():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_navigatebuy(self):
    self.driver.get("http://localhost:8000/")
    self.driver.set_window_size(1269, 959)
    self.driver.find_element(By.LINK_TEXT, "Buy Stocks").click()
    self.driver.find_element(By.LINK_TEXT, "Home").click()
    self.driver.find_element(By.LINK_TEXT, "Sell Stocks").click()
    self.driver.find_element(By.LINK_TEXT, "Buy Stocks").click()
  
