from urllib.request import urlopen, Request
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import warnings
from tqdm import tqdm
from selenium.webdriver.common.keys import Keys
import pandas as pd

warnings.filterwarnings(action='ignore')

baseUrl = "https://www.instagram.com/explore/tags/"
plusUrl = input('검색할 태그를 입력하세요 : ')
url = baseUrl + quote_plus(plusUrl)

driver = webdriver.Chrome(
    executable_path="./webdriver/chromedriver.exe"
)
driver.get(url)
time.sleep(3)

# 로그인 하기
login_section = '//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/span/a[1]/button'
driver.find_element_by_xpath(login_section).click()
time.sleep(2)


elem_login = driver.find_element_by_name("username")
elem_login.clear()
elem_login.send_keys('baaangsooo')

elem_login = driver.find_element_by_name('password')
elem_login.clear()
elem_login.send_keys('!yangsoon2@.')

time.sleep(1)

xpath = """//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/button"""
driver.find_element_by_xpath(xpath).click()

time.sleep(4)

"""태그 크롤링"""

SCROLL_PAUSE_TIME = 1.0
reallink = []

while True:
    pageString = driver.page_source
    bsObj = BeautifulSoup(pageString, 'lxml')

    for link1 in bsObj.find_all(name='div', attrs={"class":"Nnq7C weEfm"}):
        for i in range(3):
            title = link1.select('a')[i]
            real = title.attrs['href']
            reallink.append(real)

    last_height = driver.execute_script('return document.body.scrollHeight')
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")

    if new_height == last_height:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        else:
            last_height = new_height
            continue



## 해시태크 가져오기
num_of_data = len(reallink)

print('총 {0}개의 데이터를 수집합니다.'.format(num_of_data))
csvtext = []

for i in tqdm(range(num_of_data)):

    csvtext.append([])
    req = Request("https://www.instagram.com/p"+reallink[i], headers={'User-Agent': 'Mozila/5.0'})

    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, 'lxml', from_encoding='utf-8')
    soup1 = soup.find('meta', attrs={'property':"og:description"})

    reallink1 = soup1['content']
    reallink1 = reallink1[reallink1.find("@") + 1:reallink1.find(")")]
    reallink1 = reallink1[:20]

    if reallink1 == '':
        reallink1 = "Null"
    csvtext[i].append(reallink1)

    for reallink2 in soup.find_all('meta', attrs={'property':"instapp:hashtags"}):
        hashtags = reallink2['content'].rstrip(',')
        csvtext[i].append(hashtags)

    # csv로 저장

    data = pd.DataFrame(csvtext)
    data.to_csv('insta.txt', encoding='utf-8')

driver.close()
