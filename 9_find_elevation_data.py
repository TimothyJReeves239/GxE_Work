#!/usr/bin/env python
# coding: utf-8

# In[83]:


import requests
import selenium
from bs4 import BeautifulSoup
import time
from selenium import webdriver
import os
from selenium.webdriver.support.ui import Select
import pandas as pd
import glob


# In[84]:


url = "https://geonames.usgs.gov/apex/f?p=138:1:0::NO::P1_COUNTY,P1_COUNTY_ALONG:n,"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")


# In[99]:


state_abrev = {"ALABAMA":"AL","ALASKA":"AK","ARIZONA":"AZ","ARKANSAS":"AR","CALIFORNIA":"CA","COLORADO":"CO",
               "CONNECTICUT":"CT","DELAWARE":"DE","FLORIDA":"FL","GEORGIA":"GA","HAWAII":"HI","IDAHO":"ID",
               "ILLINOIS":"IL","INDIANA":"IN","IOWA":"IA","KANSAS":"KS","KENTUCKY":"KY","LOUISIANA":"LA",
               "MAINE":"ME","MARYLAND":"MD","MASSACHUSETTS":"MA","MICHIGAN":"MI","MINNESOTA":"MN",
               "MISSISSIPPI":"MS","MISSOURI":"MO","MONTANA":"MT","NEBRASKA":"NE","NEVADA":"NV",
               "NEW HAMPSHIRE":"NH","NEW JERSEY":"NJ","NEW MEXICO":"NM","NEW YORK":"NY","NORTH CAROLINA":"NC",
               "NORTH DAKOTA":"ND","OHIO":"OH","OKLAHOMA":"OK","OREGON":"OR","PENNSYLVANIA":"PA",
               "RHODE ISLAND":"RI","SOUTH CAROLINA":"SC","SOUTH DAKOTA":"SD","TENNESSEE":"TN","TEXAS":"TX",
               "UTAH":"UT","VERMONT":"VT","VIRGINIA":"VA","WASHINGTON":"WA","WEST VIRGINIA":"WV",
               "WISCONSIN":"WI","WYOMING":"WY"}


# In[91]:


State_List


# In[85]:


State_List = soup.find(id = "P1_STATE")


# In[90]:


for x in State_List: 
    x.get_text().replace("\n", ",").split(",")
#Get available state listings
reduce_state_list(State_List)
#Messy step that continues b/c of poor planning =/


# In[101]:


columns = [
"County",
"State",
"Latitude",
"Longitude",
"Ele(ft)",
"Map",
"BGN Date",
"Entry Date"]


# In[102]:


browser = webdriver.Chrome(executable_path=os.path.abspath("/Users/timreeves/Desktop/Python_Stuff/maize_yield_pred/chromedriver 2"))
#Path to Selenium Webdriver---needs to be changed for use
quicklist = ['Alabama', 'Louisiana']
#for state in State_List[2:3]:
for state in quicklist:
    #state = State_List[4]
    browser.get(url)
    browser.find_element_by_id('P1_FNAME').clear()
    browser.find_element_by_id("P1_FNAME").send_keys("county")
    time.sleep(3)
    #browser.find_element_by_id("P1_FNAME").send_keys("county")
    #Input Keyword "county" to Query
    select = Select(browser.find_element_by_id('P1_STATE'))
    select.select_by_visible_text(state)
    #Select states in iteration
    select2 = Select(browser.find_element_by_id("P1_CLASS"))
    select2.select_by_visible_text("Civil")
    #Input "Civil" to Query ---Unknown reason---@DataBase Documentation
    time.sleep(2)
    browser.find_element_by_xpath("//*[contains(text(), 'Send Query')]").click()
    time.sleep(9)
    try:
        browser.find_element_by_xpath("//*[contains(text(), 'View & Print all')]").click()
    except Exception as e:
        continue
    #Exception for states with no county data**
    #Get full list of county data
    time.sleep(1)
    for row in browser.find_elements_by_id("report_R1355627358520833459"):
        #Find Table
        cell = row.find_elements_by_tag_name("td")[1]
        cells = browser.find_elements_by_class_name("highlight-row")
        #Find Data from Table by Row
        ###print(cell.text)
        ###for t in range(len(cells)):
            ###print(cells[t].text)
    push_csv(join_cells(split_and_reduce(cells)))


# In[96]:


def split_and_reduce(cells):
    for z in range(len(cells)):
            cells[z] = cells[z].text.split(" ")
            #For each row of data, covert single string of all cells to list of strings
            cells[z] = cells[z][((cells[z].index("Civil"))+1):]
    return cells
            #Remove Columns up to "Class"---unimportant columns


# In[95]:


def join_cells(cells):
    for v in cells:
        if len(v) > 8:
            try:
                int(v[4]) != True
            except ValueError:   
                v[0:v.index(state_abrev[state.upper()])] = [" ".join(v[0:v.index(state_abrev[state.upper()])])]
                #Messy way of concatenating columns based on abrev. column
                if len(v) > 8:
                    v[5:-2] = [" ".join(v[5:-2])]
            else:
                v[5:-2] = [" ".join(v[5:-2])]
    return cells
#Concatenates county names regardless of length/# of strings


# In[94]:


def push_csv(cells):
    pd.DataFrame(cells, columns = columns).to_csv("../data/General/Elevation_Data/" + state + ".csv")
#Make DF & push to CSV


# In[87]:


def reduce_state_list(State_List):  
    for x in State_List:
        if x.upper() not in state_abrev:
            State_List.remove(x)
    State_List.remove('Federated States of Micronesia')
    State_List.remove("Republic of Palau")


# In[18]:


def concatenate_data(path_name):
    all_files = glob.glob(path_name + "/*.csv")

    li = []

    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)

    frame = pd.concat(li, axis=0, ignore_index=True)
    frame = frame.drop(columns = "Unnamed: 0")
    return frame


# In[107]:


concatenate_data("/Users/timreeves/Desktop/Python_Stuff/maize_yield_pred/data/General/Elevation_Data").to_csv("/Users/timreeves/Desktop/Python_Stuff/maize_yield_pred/data/General/Elevation_Data/combined_data.csv")


# In[115]:


combined_data = pd.read_csv("/Users/timreeves/Desktop/Python_Stuff/maize_yield_pred/data/General/Elevation_Data/combined_data.csv")
county_list = pd.read_csv("/Users/timreeves/Desktop/Python_Stuff/maize_yield_pred/data/General/County_lat_long_mod.csv")


# In[116]:


combined_data["statecounty"] = (combined_data['State'] + ' ' + combined_data['County'])


# In[117]:


county_list = county_list.rename(columns=county_list.iloc[0]).drop(county_list.index[0])


# In[118]:


county_list["statecounty"] = (county_list['State'] + ' ' + county_list['County'])


# In[119]:


combined_not_county = []
county_not_combined = []

for x in combined_data['statecounty'].unique():
    if x not in county_list['statecounty'].unique():
        combined_not_county.append(x)
print(len(combined_not_county))
print(combined_not_county)
for x in county_list['statecounty'].unique():
    if x not in combined_data['statecounty'].unique():
        county_not_combined.append(x)
print(len(county_not_combined))
print(county_not_combined)


# In[33]:


compared_data = pd.merge(combined_data, county_list,  how='outer', left_on=['County','State'], right_on = ['County','State'])


# In[82]:


mergedStuff = pd.merge(combined_data, county_list, on=['statecounty'], how='inner')
mergedStuff


# In[54]:


mergedStuff.to_csv("/Users/timreeves/Desktop/Python_Stuff/maize_yield_pred/data/General/Elevation_Data/merged.csv")


# In[46]:


combined_data['County'].isin(county_list['County']).value_counts()


# In[48]:


mergedStuff = pd.read_csv("/Users/timreeves/Desktop/Python_Stuff/maize_yield_pred/data/General/Elevation_Data/merged.csv")


# In[52]:


mergedStuff = mergedStuff.drop(["Unnamed: 0", "Unnamed: 0.1"], axis = 1)


# In[53]:


mergedStuff


# In[ ]:




