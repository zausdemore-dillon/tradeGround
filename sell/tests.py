from django.test import TestCase
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
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

        share_cell = self.driver.find_element(By.CLASS_NAME, 'holding-quantity')
        before = float(share_cell.text)

        self.driver.find_element(By.NAME, "quantity").send_keys("1")
        self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) .btn-sell").click()

        shares_cell_after = self.driver.find_element(By.CLASS_NAME, 'holding-quantity')
        after = float(shares_cell_after.text)
        assert (before - after) == 1, f"Expected '{before - 1}' in holdings quantity, but got '{before}'"

class TestSellPageLoginRequired():
    def setup_method(self, method):
        self.driver = webdriver.Firefox()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_sell_page_requires_login(self):
        self.driver.get("http://ec2-3-144-195-238.us-east-2.compute.amazonaws.com/sell/")
        # Wait for login form (id_username) to appear
        username = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "id_username"))
        )

        assert username.is_displayed()
        assert "login" in self.driver.current_url, f"Expected Login Page redirect"

class TestSellMoreSharesThanOwned():
    def setup_method(self, method):
        self.driver = webdriver.Firefox()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_sellMoreSharesThanOwned(self):
        self.driver.get("http://ec2-3-144-195-238.us-east-2.compute.amazonaws.com/")
        self.driver.set_window_size(1202, 920)
        self.driver.find_element(By.LINK_TEXT, "Log In").click()
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("testuser1")
        self.driver.find_element(By.CSS_SELECTOR, ".form").click()
        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("test_pass321")
        self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(6)").click()
        self.driver.find_element(By.LINK_TEXT, "Sell Stocks").click()

        share_cell = WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "holding-quantity"))
        )
        before = float(share_cell.text)

        self.driver.find_element(By.NAME, "quantity").click()
        self.driver.find_element(By.NAME, "quantity").send_keys("9999")
        self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) .btn-sell").click()

        share_cell_after = self.driver.find_element(By.CLASS_NAME, "holding-quantity")
        after = float(share_cell_after.text)
        assert after == before, f"Expected {before}, got {after}"

class TestSellAllShares():
    def setup_method(self, method):
        self.driver = webdriver.Firefox()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_sellAllShares(self):
        self.driver.get("http://ec2-3-144-195-238.us-east-2.compute.amazonaws.com/")
        self.driver.set_window_size(1202, 920)
        self.driver.find_element(By.LINK_TEXT, "Log In").click()
        self.driver.find_element(By.ID, "id_username").send_keys("testuser1")
        self.driver.find_element(By.ID, "id_username").send_keys(Keys.ENTER)
        self.driver.find_element(By.CSS_SELECTOR, ".form").click()
        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("test_pass321")
        self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(7)").click()
        self.driver.find_element(By.LINK_TEXT, "Sell Stocks").click()
        self.driver.execute_script("window.scrollTo(0,36)")

        share_cell = WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "holding-quantity"))
        )

        first_row = WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )

        ticker_text = first_row.find_element(By.TAG_NAME, "strong").text.strip()

        self.driver.find_element(By.NAME, "quantity").click()
        self.driver.find_element(By.NAME, "quantity").send_keys(share_cell.text)
        self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) .btn-sell").click()

        success_alert = WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success"))
        )
        assert "sold" in success_alert.text.lower() or "success" in success_alert.text.lower()

        rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        tickers = [r.find_element(By.TAG_NAME, "strong").text.strip() for r in rows]

        assert ticker_text not in tickers, "Expected {ticker_text} row to be deleted from user holdings"

class TestSellNegativeShares():
    def setup_method(self, method):
        self.driver = webdriver.Firefox()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_sellNegativeShares(self):
        self.driver.get("http://ec2-3-144-195-238.us-east-2.compute.amazonaws.com/")
        self.driver.set_window_size(1202, 920)
        self.driver.find_element(By.LINK_TEXT, "Log In").click()
        self.driver.find_element(By.ID, "id_username").send_keys("testuser1")
        self.driver.find_element(By.CSS_SELECTOR, ".center").click()
        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("test_pass321")
        self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(6)").click()
        self.driver.find_element(By.LINK_TEXT, "Sell Stocks").click()

        share_cell = WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "holding-quantity"))
        )
        before = float(share_cell.text)

        self.driver.find_element(By.NAME, "quantity").click()
        self.driver.find_element(By.NAME, "quantity").send_keys("-1")
        self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) .btn-sell").click()

        share_cell_after = WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "holding-quantity"))
        )
        after = float(share_cell_after.text)

        assert before == after, f"Expected share quantity to be {before}, but got {after}"