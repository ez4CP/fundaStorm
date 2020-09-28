import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import data_scrape
import pandas as pd

def initialize_app():
    cred= credentials.Certificate('./fundastorm-cp7799-firebase-adminsdk-gmtkd-6b53d806cf.json')
    firebase_admin.initialize_app(cred)
    return firestore.client()

def add_company_link(db, sector_name, company_name, companies_by_sector):

#This adds link of the companies of all the sectors to the database

    data = {
    u'company_link': companies_by_sector[company_name]
}
    doc_ref = db.collection(u'Bourses').document(u'National Stock Exchange').collection(sector_name.replace("/"," or ")).document(company_name)
    doc_ref.set(data)

def add_data(db,sector_name, company_name, companies_by_sector, attribute, data_table):
    navigate = db.collection(u'Bourses').document(u'National Stock Exchange').collection(sector_name.replace("/"," or ")).document(company_name).collection(attribute).document(u'Annually')
    data= {
        u'Annual' : data_table
    }
    navigate.set(data)

def dictKeys_to_string(any_dictionary):
    for key in any_dictionary.keys():
        new_dict={}
        for k,val in any_dictionary[key].items():
            new_dict[str(k)]=val
        any_dictionary[key]=new_dict
    return any_dictionary

if __name__ == "__main__":
    db = initialize_app()
    count=0
    sectors= data_scrape.get_sectors()
    for sector in sectors.keys():
        companies_by_sector=data_scrape.companies_by_sectors(sectors[sector])
        for company in companies_by_sector.keys():
            print("{} {}".format(sector,company))
            add_company_link(db, sector, company, companies_by_sector)
            income_statement = data_scrape.get_income(companies_by_sector[company])
            if len(income_statement)>0 or income_statement:
                income_statement = dictKeys_to_string(income_statement)
                add_data(db, sector, company, companies_by_sector, 'Income Statement', income_statement)
        
        
    
