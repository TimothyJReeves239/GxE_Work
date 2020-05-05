import requests
import lxml.html as lh
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import os
from selenium.webdriver.support.ui import Select
import numpy as np

#Getting Url & Driver for Visulization
url="https://websoilsurvey.sc.egov.usda.gov/App/WebSoilSurvey.aspx"
driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"))

#implicit waits to allow loading of new tab/county category
driver.get(url)
driver.implicitly_wait(10)
driver.find_element_by_id('Download_Soils_Data').click()
driver.implicitly_wait(10)
driver.find_element_by_id('Download_Soils_Data_for..._Soil_Survey_Area_.40.SSURGO.41._title').click()

d = {}
#states taken from Jacob's weather list
states = ["ALABAMA","ALASKA","ARIZONA","ARKANSAS","CALIFORNIA","COLORADO",
               "CONNECTICUT","DELAWARE","FLORIDA","GEORGIA","HAWAII","IDAHO",
               "ILLINOIS","INDIANA","IOWA","KANSAS","KENTUCKY","LOUISIANA",
               "MAINE","MARYLAND","MASSACHUSETTS","MICHIGAN","MINNESOTA",
               "MISSISSIPPI","MISSOURI","MONTANA","NEBRASKA","NEVADA",
               "NEW HAMPSHIRE","NEW JERSEY","NEW MEXICO","NEW YORK","NORTH CAROLINA",
               "NORTH DAKOTA","OHIO","OKLAHOMA","OREGON","PENNSYLVANIA",
               "RHODE ISLAND","SOUTH CAROLINA","SOUTH DAKOTA","TENNESSEE","TEXAS",
               "UTAH","VERMONT","VIRGINIA","WASHINGTON","WEST VIRGINIA",
               "WISCONSIN","WYOMING"]
#Iteration over dropdown menu "state"
for x in states:
    select = Select(driver.find_element_by_name('state'))
    select.select_by_visible_text(x)

    time.sleep(1)

    Urls = driver.find_elements_by_partial_link_text("wss_SSA")
    new_pop = []
#All for checking; real version would end with a .click() on "wss_SSA"
    for y in Urls:
        y = y.text
        new_pop.append(y)
    d.update({x : new_pop})
df = pd.DataFrame({ key:pd.Series(value) for key, value in d.items() })
print(df)



"""posts = driver.find_elements_by_class_name("last")
for post in posts:
    print(post.text)"""




#Old code attempts failed because Url was non-specific


#pass the HTML to Beautifulsoup.
#main_table = table.findAll(class_='data')
#main_table = soup.find(id = 'Soil_Survey_Area_.40.SSURGO.41._Download_Links_ancestor')
#get the HTML of the table called site Table where all the links are displayed
#main_table = soup.find("div",attrs={id:'soilsurveyareacontainerid'})
#Now we go into main_table and get every a element in it which has a class "title" 
#links = main_table.find_all("a",class_="href")


