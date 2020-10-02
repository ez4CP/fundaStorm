import bs4 as bs
from urllib.request import Request, urlopen
from collections import defaultdict
import pandas as pd
from selenium import webdriver
from firebase import firebase
import os

####### Note:- IN CASE, CODE IS UNABLE TO RETRIEVE SECTORS AND COMPANIES, USE THE COMMENTED CODE BELOW.


# def get_sectors():
#     delete_elements=['  Market Capitalisation', '  Net Sales', '  Net Profit','  Total Assets','  Quarterly Growth'
#     ,'  Excise', '  Other Income', '  Raw Materials', '  Power & Fuel', '  Employee Cost', '  PBDIT', '  Interest', '  Tax',
#      '  EPS', '  Investments', '  Sundry Debtors', '  Cash/Bank', '  Inventory', '  Debt', '  Contingent Liabilities', 
#      '  Price Earning Ratios', '  Cash P/E Ratios']


#     # req = Request('https://www.moneycontrol.com/stocks/marketinfo/marketcap/nse/index.html', headers={'User-Agent': 'Mozilla/5.0'})
#     req = Request('http://www.moneycontrol.com/stocks/sectors/aluminium.html', headers={'User-Agent': 'Mozilla/5.0'})
#     webpage = urlopen(req).read()
#     sc=bs.BeautifulSoup(webpage,'lxml')
#     dict_sectors=defaultdict()
    
#     for item in sc.findAll("div", {"class": "budgright_list expview-scroll MT10"}):
#         sub_items = item.findAll('li')
#         for sub_item in sub_items:
#             dict_sectors[sub_item.text] =  sub_item.find('a')['href']
#     print(dict_sectors)
#     for i in delete_elements:
#         dict_sectors.pop(i)
#     return dict_sectors

# def companies_by_sectors(sector_link):
#     req = Request(sector_link, headers={'User-Agent': 'Mozilla/5.0'})
#     dict_companies=defaultdict()
#     webpage = urlopen(req).read()
#     sc=bs.BeautifulSoup(webpage,'lxml')
#     flag = 0
#     for item in sc.findAll("div", {"class": "top_gain_table MT10"}):
#         for a in item.findAll("a"):
#             dict_companies[a.text]='http://www.moneycontrol.com'+a['href']
#             flag=1
#     if flag==0:
#         driver = webdriver.Chrome('D:/fundaStorm/fundaStorm/chromedriver_win32/chromedriver.exe')
#         driver.get(sector_link)
#         all_companies=driver.find_elements_by_xpath('//*[@id="topcomp"]/div/div')
#         for company in all_companies:
#             elems = company.find_elements_by_tag_name('a')
#             for elem in elems:
#                 text=elem.get_attribute('text')
#                 href = elem.get_attribute('href')
#                 dict_companies[text]=href
    
#     return dict_companies





def get_sectors():
    req = Request('https://www.moneycontrol.com/stocks/marketinfo/marketcap/nse/index.html', headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    sc=bs.BeautifulSoup(webpage,'lxml')
    dict_sectors=defaultdict()
    for item in sc.findAll("div", {"class": "lftmenu"}):
        sub_items = item.findAll('li')
        for sub_item in sub_items:
            dict_sectors[sub_item.text] =  "https://www.moneycontrol.com/"+sub_item.find('a')['href']
    dict_sectors.pop('Top 100')
    return dict_sectors

def companies_by_sectors(sector_link):
    req = Request(sector_link, headers={'User-Agent': 'Mozilla/5.0'})
    dict_companies=defaultdict()
    webpage = urlopen(req).read()
    sc=bs.BeautifulSoup(webpage,'lxml')
    for item in sc.findAll("a", {"class": "bl_12"}):
        dict_companies[item.text]="https://www.moneycontrol.com/"+item['href']
    dict_companies.pop(' Customize')
    dict_companies.pop("Slide Show")
    return dict_companies


def initiate_driver_link(company_link):
    driver = webdriver.Chrome('D:/fundaStorm/fundaStorm/chromedriver_win32/chromedriver.exe')
    driver.get(company_link)
    return driver

def get_income( company_link, choose, options):
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('headless')
    chrome_options.add_argument('window-size=1200x600')
    driver = webdriver.Chrome('D:/fundaStorm/fundaStorm/chromedriver_win32/chromedriver.exe',chrome_options=chrome_options)
    # driver = webdriver.Chrome('D:/fundaStorm/fundaStorm/chromedriver_win32/chromedriver.exe')
    driver.get(company_link)
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
    try:
        tbl_class=driver.find_elements_by_class_name('clearfix.MB20')
        # driver.implicitly_wait(45)
        for tbl in tbl_class:
            fin_tbl=tbl.find_element_by_xpath('//*[@id="IncomeStatement"]/div[2]/div/table').get_attribute('outerHTML')
        df  = pd.read_html(fin_tbl)  
        for i in df:
            i=i.to_dict()

    except:
        print("Company has stopped functioning")
    # cp=pd.read_html(x,attrs={'class': 'mctable1 thborder frtab'})
    # print(cp[0])
        i = defaultdict()
    
    options={'BalanceSheet' : '//*[@id="Consolidated_finance"]/div/div[1]/ul/li[2]/a' , 
             'CashFlows' : '//*[@id="Consolidated_finance"]/div/div[1]/ul/li[3]/a',
             'Ratios' : '//*[@id="Consolidated_finance"]/div/div[1]/ul/li[4]/a'}

    ratio=get_balance(driver,'Ratios',options, company_link)
    balance_sheet_data=get_balance(driver,'BalanceSheet',options, company_link)

    cash_flow=get_balance(driver,'CashFlows',options, company_link)
    driver.close()
    return i,ratio,balance_sheet_data,cash_flow
    
def get_balance(driver, choose , options,company_link):

    count=0
    while count< 10:
        try:
            driver.find_element_by_xpath(options[choose]).click()
        except:
            pass
        count+=1

    tbl_class=driver.find_elements_by_id(choose)
    
    # for tbl in tbl_class:
    #     fin_tbl=tbl.find_element_by_xpath('//*[@id="BalanceSheet"]/div[1]/div/table').get_attribute('outerHTML')

    for table in tbl_class:
        try:
            df  = pd.read_html(table.get_attribute('outerHTML')) 
            temp_df=pd.DataFrame()
            for d in df:
                temp_df = temp_df.append(d, ignore_index=True)
            rb_data=temp_df.to_dict()

        except:
            print("Company not found")
            rb_data=defaultdict()
    
    
    return rb_data

    
# if __name__ == "__main__":
#     options={'BalanceSheet' : '//*[@id="Consolidated_finance"]/div/div[1]/ul/li[2]/a' , 
#             'CashFlows' : '//*[@id="Consolidated_finance"]/div/div[1]/ul/li[3]/a',
#             'Ratios' : '//*[@id="Consolidated_finance"]/div/div[1]/ul/li[4]/a'}
#     dict_sectors=get_sectors()
#     print(dict_sectors)
#     for value in dict_sectors.keys():
#         print(value)
#         dict_companies =companies_by_sectors(dict_sectors[value])
#         print(dict_companies)
    
#         for i in dict_companies.values():
#             print(i)
#             get_income(i)

