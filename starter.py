import time
import os
import re
import glob
import spintax
import zipfile
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementNotVisibleException


def findclassnamebefore(name, inputdata):
    regex = re.findall(r'class=".{,50}"' + name, inputdata)
    print(regex)
    return '.' + (regex[0].split('\"')[1]).replace(' ', '.')


def findclassnameafter(name, inputdata):
    regex = re.findall(name + r'class=".{,50}"', inputdata)
    return '.' + (regex[0].split('\"'))[3].replace(' ', '.')




for path, subdirs, files in os.walk('./Articles/'):
    for name in files:
        print(os.path.join(path, name))
        with open(os.path.join(path, name), 'r', encoding='utf-8') as openedfile:
            article = spintax.spin(openedfile.read())
        openedfile.close()
        try:
            os.remove(os.path.join(path, name))
        except OSError:
            pass

        with open('counterfile.txt', 'r') as counterfile:
            counter = counterfile.read()
        counter = int(counter)

        print(type(counter))
        print(article)

        print(re.findall('(?<=#title#).*(?=#title#)', article))
        print(re.findall('(?<=#body#).*(?=#body#)', article))
        print(re.findall('(?<=#tags#).*(?=#tags#)', article))

    # with open('login.txt', 'r', encoding='UTF-8') as loginfile:
        # for counter in range(counter):
        #     loginfile.next()
        # for line in loginfile:
        #     loginline = line.split('\t')
        for index, line in enumerate(open('login.txt', 'r', encoding='UTF-8')):
            if index > counter:
                print(line)
                loginline = line.split('\t')
                proxylogin = loginline[3].split(':')[0]
                proxypass = loginline[3].split('@')[0].split(':')[1]
                proxyip = loginline[3].split('@')[1].split(':')[0]
                proxyport = loginline[3].split('@')[1].split(':')[1]
                print(proxylogin)
                print(proxypass)
                print(proxyip)
                print(proxyport)

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
                            host: """ + "\"" + proxyip + "\"" + """,
                            port: parseInt(""" + proxyport + """)
                          },
                          bypassList: ["foobar.com"]
                        }
                      };

                chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

                function callbackFn(details) {
                    return {
                        authCredentials: {
                            username: """ + "\"" + proxylogin + "\"" + """,
                            password: """ + "\"" + proxypass + "\"" + """
                        }
                    };
                }

                chrome.webRequest.onAuthRequired.addListener(
                            callbackFn,
                            {urls: ["<all_urls>"]},
                            ['blocking']
                );
                """
                pluginfile = 'proxy_auth_plugin.zip'

                with zipfile.ZipFile(pluginfile, 'w') as zp:
                    zp.writestr("manifest.json", manifest_json)
                    zp.writestr("background.js", background_js)

                co = Options()
                co.add_argument("--start-maximized")
                co.add_extension(pluginfile)

                driver = webdriver.Chrome('chromedriver.exe', chrome_options=co)
                driver.delete_all_cookies()
                driver.get('https://www.blogger.com/go/signin?hl=pl')
                time.sleep(2)
                element = driver.find_element_by_tag_name('input')
                element.clear()
                element.send_keys(loginline[0])
                time.sleep(1)
                element.send_keys(Keys.RETURN)
                time.sleep(10)
                element = driver.find_element_by_xpath \
                    ('/html/body/div/div/div[2]/div[2]/form/div[2]/div/div/div//div/div/div/div/div/input')
                element.send_keys(loginline[1])
                time.sleep(1)
                element.send_keys(Keys.RETURN)
                time.sleep(2)
                if 'zostało zmienione' not in driver.page_source:
                    if 'numer telefonu' in driver.page_source:
                        element = driver.find_element_by_xpath \
                            ('/html/body/div/div/div[2]/div[2]/form/div[2]/div/div/div/ul/li[3]')
                        element.click()
                        time.sleep(2)
                        element = driver.find_element_by_css_selector(findclassnameafter('type="tel" ', driver.page_source))
                        element.send_keys(loginline[2])
                        time.sleep(2)
                        element = driver.find_element_by_css_selector(findclassnamebefore('>Dalej', driver.page_source))
                        element.click()
                    driver.get('https://www.blogger.com/blogger.g?blogID=' + loginline[4] + '#editor/src=sidebar')
                    time.sleep(15)
                    if 'tabindex="0" aria-selected="true">Nowy post' in driver.page_source:
                        element = driver.find_element_by_css_selector(findclassnamebefore(' tabindex="0" aria-selected="false">HTML', driver.page_source))
                        element.click()
                    article=article.strip()
                    element = driver.find_element_by_css_selector(findclassnamebefore(' title=\"Tytuł', driver.page_source))
                    element.send_keys(re.findall('(?<=#title#).*(?=#title#)', article))
                    element = driver.find_element_by_css_selector('.htmlBox')
                    element.send_keys(re.findall('(?<=#body#).*(?=#body#)', article, re.DOTALL))
                    element = driver.find_element_by_css_selector(findclassnamebefore('></span> <span>Etykiety', driver.page_source))
                    element.click()
                    element = driver.find_element_by_css_selector(findclassnamebefore(' aria-label="Podaj listę', driver.page_source))
                    element.send_keys(re.findall('(?<=#tags#).*(?=#tags#)', article))
                    time.sleep(5)
                    element = driver.find_element_by_css_selector('.blogg-button.blogg-primary')
                    element.click()
                    time.sleep(10)
                    try :
                        element.click()
                    except ElementNotVisibleException:
                        pass
                    time.sleep(5)
                    with open('out.txt','a') as outfile:
                        outfile.write(line)
                driver.close()
                counter += 1
                with open('counterfile.txt', 'w') as counterfile:
                    counterfile.write(str(counter))


