from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
import os
import zipfile
from datetime import datetime, timedelta

PROXY_USER = '09865371lol0BRfo'
PROXY_PASS = 'wIKBuvTgmo'
PROXY_HOST = '161.77.168.140'
PROXY_PORT = '59100'

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


def get_chromedriver(use_proxy=False, user_agent=None):
    path = os.path.dirname(os.path.abspath(__file__))
    chrome_options = webdriver.ChromeOptions()
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)
    if user_agent:
        chrome_options.add_argument('--user-agent=%s' % user_agent)
    driver = webdriver.Chrome(
        options=chrome_options)
    return driver


def scrape_ebay_info(url):

    try:
        with get_chromedriver(use_proxy=True) as driver:
            driver.get(url)
            product_characteristics = list()

            wait = WebDriverWait(driver, 10)

            price_element = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.x-price-primary span.ux-textspans"))
            )
            product_characteristics.append(price_element.text.split('/')[0])

            try:
                shipping_price = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, 'ux-labels-values--shipping'))
                )

                sum_of_shipping = shipping_price.find_element(
                    By.CLASS_NAME, 'ux-textspans--BOLD')
                product_characteristics.append(sum_of_shipping.text)
            except Exception as e:
                print(f"Error with finding: {e}")
                product_characteristics.append("Not mentioned")

            try:
                availability_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, 'd-quantity__availability')))
                count_availability_element = availability_element.find_element(
                    By.CLASS_NAME, 'ux-textspans')
                product_characteristics.append(count_availability_element.text)
            except Exception as e:
                print(f"Error with finding: {e}")
                product_characteristics.append("1 available")

            try:
                deliverd_dates = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, 'ux-labels-values--deliverto'))
                )

                deliverd_date = deliverd_dates.find_elements(
                    By.CLASS_NAME, 'ux-textspans--BOLD')
                if len(deliverd_date) > 1:
                    date_text = deliverd_date[1].text

                target_date = datetime.strptime(date_text, '%a, %b %d')
                target_date = target_date.replace(year=2024)
                current_date = datetime.now()
                difference = target_date - current_date

                product_characteristics.append(f"{difference.days} days")
            except Exception as e:
                print(f"Error with finding: {e}")
                product_characteristics.append("Not mentioned")

            return product_characteristics

    except Exception as e:
        print(f"Error scraping eBay images: {e}")
        return ['Error' for _ in range(4)]


