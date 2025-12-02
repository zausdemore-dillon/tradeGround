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

class TestSellShare():
    def setup_method(self, method):
        self.driver = webdriver.Firefox()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_testSellShare(self):
        self.driver.get("http://ec2-3-144-195-238.us-east-2.compute.amazonaws.com/")
        self.driver.set_window_size(1202, 920)
        self.driver.find_element(By.LINK_TEXT, "Log In").click()
        self.driver.find_element(By.ID, "id_username").send_keys("testuser1")
        self.driver.find_element(By.CSS_SELECTOR, ".form").click()
        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("test_pass321")
        self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(6)").click()
        self.driver.find_element(By.LINK_TEXT, "Sell Stocks").click()
        self.driver.find_element(By.NAME, "quantity").click()

        share_cell = self.driver.find_element(By.ID, 'holding-quantity')
        before = int(share_cell.text)
        
        self.driver.find_element(By.NAME, "quantity").send_keys("1")
        self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) .btn-sell").click()

        shares_cell_after = self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) td:nth-child(2)")
        after = int(shares_cell_after.text)


        assert after == before - 1, f"Expected '{before - 1}' in holdings quantity, but got '{before}'"
