import socket
import time
from datetime import datetime as dt

import requests
import urllib3
import yaml
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from utils import PyMySQL, logger, browser,utility

logger = logger.init_logger('./log/selenium_%s.log' % dt.now().strftime('%Y-%m-%d'))
cfg = yaml.load(open('config.yaml', 'r'), Loader=yaml.FullLoader)
db = [*cfg['MySQL'].values()]  # unpack dict to get dict value


def randHeader():
    '''随机生成User-Agent'''
    head_connection = ['Keep-Alive', 'close']
    head_accept = ['text/html, application/xhtml+xml, */*']
    head_accept_language = ['zh-CN,fr-FR;q=0.5', 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3']
    ua = {
        'Connection': head_connection[0],
        'Accept': head_accept[0],
        'Accept-Language': head_accept_language[1],
        'User-Agent': UserAgent().Chrome
    }
    return ua


def getURL(url, tries_num=3, sleep_time=7, time_out=3, max_retry=5):
    '''
        实现网络中断后自动重连，同时为了兼容各种网站不同的反爬策略，通过sleep时间和timeout动态调整来测试合适的网络连接参数；
        通过isproxy 来控制是否使用代理，以支持一些在内网办公的同学
        :param url:
        :param tries_num:  重试次数
        :param sleep_time: 休眠时间
        :param time_out: 连接超时参数
        :param max_retry: 最大重试次数，递归时使用
        :return: response9
        '''
    sleep_time_p = sleep_time
    time_out_p = time_out
    tries_num_p = tries_num
    isproxy = 0  # 如需要使用代理，改为1，并设置代理IP参数 proxy
    proxy = {"http": "http://110.37.84.147:8080", "https": "http://110.37.84.147:8080"}  # 这里需要替换成可用的代理IP

    try:
        if isproxy == 1:
            res = requests.get(url, headers=randHeader(), timeout=time_out, proxies=proxy)
        else:
            res = requests.get(url, headers=randHeader(), timeout=time_out)
        return res
    except (socket.timeout or urllib3.exceptions.ReadTimeoutError or requests.exceptions.ReadTimeout)as e:
        # 设置重试次数，最大timeout 时间和 最长休眠时间
        sleep_time_p = sleep_time_p + 3
        time_out_p = time_out_p + 3
        tries_num_p = tries_num_p - 1
        if tries_num_p > 0:
            time.sleep(sleep_time_p)
            logger.exception(f'%s - %d tries connection.' % (url, max_retry - tries_num_p))
            return getURL(url, tries_num_p, sleep_time_p, time_out_p, max_retry)
        else:
            logger.exception(f'%s - error after %d tries connection.' % (url, max_retry - tries_num_p))
            return 1


# def get_table_content(driver, xpath):
#     # 按行查询表格的数据，取出的数据是一整行，按空格分隔每一列的数据
#     table_tr_list = driver.find_element(By.XPATH, xpath).find_elements(By.TAG_NAME, "tr")
#     table_list = []  # 存放table数据
#     for tr in table_tr_list:  # 遍历每一个tr
#         # 将每一个tr的数据根据td查询出来，返回结果为list对象
#         table_td_list = tr.find_elements(By.TAG_NAME, "td")
#         row_list = []
#         # print(table_td_list)
#         for td in table_td_list:  # 遍历每一个td
#             row_list.append(td)  # 取出表格的数据，并放入行列表里
#         table_list.append(row_list)
#     return table_list


def getInfo(driver):

    for city in ['深圳','广州','上海','东京']:
        # 重新前往url
        url = cfg['browser']['url']
        driver.get(url)

        # 查找输入框 # todo 自己改
        input = driver.find_elements_by_xpath("//input[contains(@class,'searchbox')]")

        # 查找搜索键 # todo 自己改
        btn = driver.find_elements_by_xpath("//input[contains(@class,'searchboxSubmit')]")

        if len(input) >= 1 and len(btn) >= 1:
            input[0].send_keys(f'{city}今天的天气') # 输入内容 # todo 自己改
            utility.scroll_to(driver, btn[0])  # 定位搜索键
            ActionChains(driver).move_to_element(btn[0]).click().perform() # 点击搜索键

        # 停一下，网页跳转加载
        time.sleep(5)

        result = driver.find_elements_by_xpath("//li[contains(@class,'algo')]") # 结果列表 # todo 自己改
        if len(result) >= 1:
            for res in result:
                title = result[0].find_elements_by_xpath(".//h2/a[contains(@target,'blank')]") # 结果标题 # todo 自己改
                # 信息
                logger.info(title[0].get_attribute("href")) # 当前元素的 hyper link
                logger.info(title[0].text) # 当前元素的 text


def main():
    # # 连接数据库, 你应该不需要
    # global mySQL
    # mySQL = PyMySQL.PyMySQL()
    # mySQL._init_(*db) # *db 是数据库参数，在config.yaml

    # 初始化浏览器，使用 config.yaml 中的参数
    driver = browser.init_browser()

    # 读入cookies
    browser.imp_cookies(driver)

    # 主函数
    getInfo(driver)

    # 导出cookies
    browser.exp_cookies(driver)

    # # close DB connection
    # mySQL.dispose()

    # 关闭浏览器实例
    driver.quit()


if __name__ == "__main__":
    main()
