import json
import logging
import os
import random
import time
from datetime import datetime as dt

import yaml
from fake_useragent import UserAgent
from retry import retry
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(f'main.{os.path.basename(__file__)}')
cfg = yaml.load(open('./config.yaml', 'r'), Loader=yaml.FullLoader)


@retry((TimeoutException), tries=7, delay=2, logger=logger)
def get(driver, url):
    def get_current_url():
        current_url = driver.current_url
        logger.info(' ' * 15 + f'current url: {current_url}')
        return current_url

    get_current_url()
    # get
    driver.get(url)
    time.sleep(4)
    get_current_url()


def get_browser_opt():
    """
    Get browser option from config
    """
    opt = Options()

    user_agent = UserAgent().Chrome
    language = cfg['browser']['lang']
    user_data_dir = cfg['browser']['user_data_dir']

    # argument
    opt.add_argument(f'user-agent={user_agent}')  # 随机UA
    opt.add_argument(f'lang={language}.UTF-8')  # 设置语言 JA_JP/KO_KR/zh_HK/zh_CN/en_US
    opt.add_argument("--disable-notifications")  # 禁止显示通知
    opt.add_argument('--disable-infobars')  # 隐藏"Chrome正在受到自动软件的控制"
    opt.add_argument('--disable-gpu')  # 禁用GPU
    opt.add_argument('--disable-dev-shm-usage')
    opt.add_argument(f"--user-data-dir={user_data_dir}")  # 设置会话数据保存目录
    opt.add_argument("--start-maximized")  # 浏览器最大化
    opt.set_capability('unhandledPromptBehavior', 'ignore')  # 处理ALERT
    # opt.add_extension(get_proxy())  # 增加ip proxy扩展

    # experimental option
    opt.add_experimental_option("prefs", {"enable_do_not_track": True})  # DO NOT TRACK
    opt.add_experimental_option('excludeSwitches', ['enable-automation'])  # 隐藏

    return opt


def imp_cookies(driver):
    """
    Import cookies from *.txt
    """
    # get cookies from file
    cookies_path = '%s/cookies.txt' % cfg['browser']['user_data_dir']
    if os.path.isfile(cookies_path):
        with open(cookies_path, "r") as f:
            cookies = json.load(f)
        # clean cookies
        for cookie in cookies:
            try:
                cookie['expirationDate'] = cookie.pop('expiry')
            except:
                pass
        # import cookies
        for cookie in cookies:
            driver.add_cookie(cookie)
        # log
        now = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f'imported cookies on {now}')
    else:
        logger.info('no exsisted cookies')


def exp_cookies(driver):
    """
    Export cookies to *.txt
    """
    # get cookies from browser
    cookies = driver.get_cookies()
    # export cookies
    cookies_path = '%s/cookies.txt' % cfg['browser']['user_data_dir']
    json.dump(cookies, open(cookies_path, "w"))
    # log
    now = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f'last cookies exported on {now} : {cookies[-1]}')


def init_browser():
    """
    Initialize browser
    """
    url = cfg['browser']['url']
    now = dt.now().strftime('%Y-%m-%d %H:%M:%S')

    #读入浏览器参数
    opt = get_browser_opt()

    #启动实例
    driver = webdriver.Chrome(options=opt, executable_path='./chromedriver.exe')
    driver.set_page_load_timeout(40)
    driver.implicitly_wait(10)  # seconds

    logger.info(f"going to {url} on {now}")
    get(driver, url)

    return driver


def close_browser():
    """
    Close browser
    """
    global driver
    driver.quit()
    logger.info(f"browser closed")
