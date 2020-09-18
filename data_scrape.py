import bs4 as bs
from urllib.request import Request, urlopen
from collections import defaultdict
import pandas as pd
from selenium import webdriver




def get_sectors(sector_name):
    req = Request('https://www.moneycontrol.com/stocks/marketinfo/marketcap/nse/index.html', headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    sc=bs.BeautifulSoup(webpage,'lxml')
    dict_sectors=defaultdict()
    for item in sc.findAll("div", {"class": "lftmenu"}):
        sub_items = item.findAll('li')
        for sub_item in sub_items:
            dict_sectors[sub_item.text] =  sub_item.find('a')['href']
    return dict_sectors[sector_name]

def companies_by_sectors(sector_link):
    req = Request("https://www.moneycontrol.com/"+sector_link, headers={'User-Agent': 'Mozilla/5.0'})
    dict_companies=defaultdict()
    webpage = urlopen(req).read()
    sc=bs.BeautifulSoup(webpage,'lxml')
    for item in sc.findAll("a", {"class": "bl_12"}):
        dict_companies[item.text]=item['href']
    dict_companies.pop(' Customize')
    dict_companies.pop("Slide Show")
    return dict_companies

def get_financials(dict_companies):
    driver = webdriver.Chrome('D:/fundaStorm/fundaStorm/chromedriver_win32/chromedriver.exe')
    x=driver.get('https://www.moneycontrol.com/india/stockpricequote/computers-software/tataconsultancyservices/TCS')
    time_period=driver.find_elements_by_class_name('cIncomeStmt')
    for time in time_period:
        count=0
        while count<10:
            try:
                time.find_element_by_xpath('//*[@id="IncomeStatement"]/div[1]/a[4]').click()
                break
            except:
                pass
            count+=1
    
    tbl_class=driver.find_elements_by_class_name('clearfix.MB20')
    driver.implicitly_wait(45)
    for tbl in tbl_class:
        fin_tbl=tbl.find_element_by_xpath('//*[@id="IncomeStatement"]/div[2]/div/table').get_attribute('outerHTML')
    df  = pd.read_html(fin_tbl)  
    print(df)
    # cp=pd.read_html(x,attrs={'class': 'mctable1 thborder frtab'})
    # print(cp[0])
    driver.close()
    


if __name__ == "__main__":
    dict_sectors=get_sectors("Airlines")
    dict_companies =companies_by_sectors(dict_sectors)
    get_financials(dict_companies)
