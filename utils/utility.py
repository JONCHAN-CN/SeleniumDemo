import random
import os
import logging
import yaml
import pandas as pd
from datetime import datetime as dt
import datetime
import pytz
import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException)

SELENIUM_EXCEPTIONS = (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException)

logger = logging.getLogger(f'main.{str(os.path.basename(sys.argv[0])).strip(".py")}')


def click_button(driver, el):
    """
    Click a button using Javascript
    """
    driver.execute_script("arguments[0].click();", el)


def wait_xpath(driver, expr):
    """
    Takes an XPath expression, and waits at most 20 seconds until it exists
    """
    wait = WebDriverWait(driver, 20)
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, expr)))
    except SELENIUM_EXCEPTIONS:
        return


def scroll_to(driver, el):
    """
    Scroll an element into view, using JS
    """
    try:
        driver.execute_script("arguments[0].scrollIntoView();", el)
    except SELENIUM_EXCEPTIONS:
        return


def scroll_into_middle(driver, el):
    scrollElementIntoMiddle = "var viewPortHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0); var elementTop = arguments[0].getBoundingClientRect().top; window.scrollBy(0, elementTop-(viewPortHeight/2));"
    try:
        driver.execute_script(scrollElementIntoMiddle, el)
    except SELENIUM_EXCEPTIONS:
        return


def random_valid_btn(element_list, cnt=0):
    """
    Select random and valid button element
    """
    li = []
    for i in range(len(element_list)):
        if hasattr(element_list[i], "size"):
            if element_list[i].size['height'] > 0:
                li.append(i)
    if len(li) > 0:
        return random.choice(li)
    else:
        return ""


def first_valid_btn(element_list):
    """
    Select first and valid button element
    """
    for i in range(len(element_list)):
        if hasattr(element_list[i], "size"):
            if element_list[i].size['height'] > 0:
                return i
    return ""


def get_acct(acct_file_path, sep='----'):
    """
    Get account name from cookies file
    """
    try:
        acct = acct_file_path.split(sep)[0]
        passwd = acct_file_path.split(sep)[1][:-4]
        # passwd = acct_file_path.split(sep)[1].strip('.txt')

    except:
        acct, passwd = get_acct(acct_file_path, sep='---')
    return acct, passwd