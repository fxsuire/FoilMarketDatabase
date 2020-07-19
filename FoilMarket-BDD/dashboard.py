import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import json
import pymongo
from bson.son import SON
import streamlit as st
import numpy as np

# connection to the database
client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client.Foil_Market

# we want to read all the data from the collection "Foil_Database"
# and have it in a dataframe

collection = db["Foil_Database"]

query = {}

cursor = collection.find(query)

#Displays the title of our application
st.title('Foil Market database (filtered)')

Read_Full_Data = pd.DataFrame(list(cursor))

#Sidebar title
st.sidebar.title("Filter")

# Filters UI
subset_data = Read_Full_Data
brand_name_input = st.sidebar.multiselect(
'Foil brands to display',
Read_Full_Data.groupby('Brand_Marque').count().reset_index()['Brand_Marque'].tolist())
# by country name
if len(brand_name_input) > 0:
    Filtered_Read_mg_df_Foil_Market = Read_Full_Data[Read_Full_Data['Brand_Marque'].isin(brand_name_input)]
else : 
    Filtered_Read_mg_df_Foil_Market = Read_Full_Data

# Displays the full set of data
st.write("Full foil database")
st.write(Filtered_Read_mg_df_Foil_Market)


# We want a more elaborate query with a count
# front wing in an hydrofoil is one of the main criteria to choose an appropriate foil
# we want to know how many front wings we have for each brand

collection = db["Foil_Database"]

pipeline = [
    {
        u"$match": {
            u"Component-Type_Type-Composant": u"Front Wing - Aile avant"
        }
    }, 
    {
        u"$group": {
            u"_id": {
                u"Brand_Marque": u"$Brand_Marque"
            },
            u"COUNT(*)": {
                u"$sum": 1
            }
        }
    }, 
    {
        u"$project": {
            u"Brand_Marque": u"$_id.Brand_Marque",
            u"COUNT(*)": u"$COUNT(*)",
            u"_id": 0
        }
    }, 
    {
        u"$sort": SON([ (u"COUNT(*)", 1) ])
    }
]

cursor = collection.aggregate(
    pipeline, 
    allowDiskUse = True
)

# Expand the cursor and construct the DataFrame
Read_mg_df_Front_Wing_Range =  pd.DataFrame(list(cursor))

#We rename the count column in something more uder friendly
Read_mg_df_Front_Wing_Range = Read_mg_df_Front_Wing_Range.rename(columns={"COUNT(*)": "Front_Wing_Number_in_Range"})

st.title('Dataset stats (no filter)')

# Displays the full set of data
st.write("Which brand has the largest frontwing range?")
st.write(Read_mg_df_Front_Wing_Range)


#Displays histogram of front wing range
fig = px.bar(Read_mg_df_Front_Wing_Range, x='Front_Wing_Number_in_Range', y='Brand_Marque')
st.plotly_chart(fig)
    
