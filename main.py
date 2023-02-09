#!/usr/bin/python
"""
Скрипт для парсинга поисковой выдачи Google (1-й страницы)
может работать через vpn, tor.
Записывает html код страницы выдачи Google и json файл содержащий ссылки, заголовки и описания.
"""
import json
import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.support.ui import WebDriverWait

"""
SHOW: enable displaying Firefox driver
settings for proxying traffic:
    PROXY: enable proxy
    PROXY_TYPE: set type of proxy: 'tor', 'proxy' or 'proxy_pac
    PROXY_HTTP: set address of proxy
    PROXY_PORT: set port of proxy
    PROXY_PAC: set address or path of proxy.pac file
"""
SHOW: bool = True
PROXY: bool = True
PROXY_TYPE: str = 'tor'
PROXY_HTTP: str = '127.0.0.1'
PROXY_PORT: int = 9050
PROXY_PAC: str = ''


def init_driver():
    """
    Initial web driver (firefox),
    :return: driver: selenium.webdriver.Firefox with settings.
    """
    options = webdriver.FirefoxOptions()
    if not SHOW:
        options.arguments.append("-headless")  # disable visibility of window
    if PROXY:
        if PROXY_TYPE == "tor":
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.socks", PROXY_HTTP)
            options.set_preference("network.proxy.socks_port", PROXY_PORT)
            options.set_preference("network.proxy.socks_remote_dns", False)
        elif PROXY_TYPE == "proxy":
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.http", PROXY_HTTP)
            options.set_preference("network.proxy.http_port", PROXY_PORT)
            options.set_preference("network.proxy.ssl", PROXY_HTTP)
            options.set_preference("network.proxy.ssl_port", PROXY_PORT)
        elif PROXY_TYPE == "proxy_pac":
            options.set_preference("network.proxy.type", 2)
            options.set_preference("network.proxy.autoconfig_url", PROXY_PAC)
    # set firefox options
    driver = webdriver.Firefox(options=options)
    # set wait of page load
    driver.wait = WebDriverWait(driver, 5)
    return driver


def get_page_by_searched_text(driver, search: str):
    """
    Get google page with results of inputted text and print result into a source.html file
    :param driver: firefox webdriver
    :param search: text line for enter in input element.
    """
    driver.get('https://www.google.com')
    # uncomment 2 lines above if Google show page with setting up settings
    # send = driver.find_elements(by='tag name', value='button')
    # send[2].click()
    # find input element
    input_element = driver.find_element(by='tag name', value='input')
    # type to input element inputted text
    input_element.send_keys(search)
    # type enter
    input_element.send_keys(Keys.RETURN)

    # waiting for a page loaded
    time.sleep(10)

    # print result into source.html file
    with open('source.html', 'w', encoding='utf-8') as file:
        file.write(driver.page_source)


def parse_page() -> list[dict]:
    """
    Parse HTML file with bs4
    :return: links: dict with a link, small text and text description.
    """
    # read source.html.
    with open('source.html', 'r', encoding='utf-8') as file:
        source = file.read()
    soup = BeautifulSoup(source, 'lxml')
    # get div with the id=search
    search = soup.find('div', id='search')
    # find all sites searched in google
    elements = search.find_all('div', class_='kvH3mc BToiNc UK95Uc')
    links = []
    # get links, small text and description in elements
    for element in elements:
        link = element.find('a').get('href')
        text = element.find('a').find('h3').text
        description = element.find('div', class_='Z26q7c UK95Uc').text
        links.append({'link': link, 'text': text, 'description': description})
    return links


def main(search: str):
    """
    Call all functions for get links from Google searched page.
    :param search: String for enter Google.
    """
    driver = init_driver()

    get_page_by_searched_text(driver, search)
    links = parse_page()
    # print links to json file
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(links, file, indent=4, ensure_ascii=False)

    # close webdriver
    driver.quit()
    # remove log file from geckodriver(firefox).
    os.remove("geckodriver.log")


if __name__ == "__main__":
    main(input("type text for search in Google:\n"))
