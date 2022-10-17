import streamlit as st
import json
import plotly.express as px
import pandas as pd
import geopandas as gpd
import geojson
import numpy as np
#Description
#Open dataset
dataset = 'TILL6022_Emission_Dataset.csv'
df = pd.read_csv(dataset, delimiter=',', encoding='ISO-8859-1') #,parse_dates = ['date']
country_bb = pd.read_csv('country_bb.csv', delimiter=',', encoding='ISO-8859-1')
# country_bb.set_index('country', inplace=True)
#df.set_index('country', inplace=True)
#sf = df[df.date == '2019-01-01']
# vf = df[df.sector == 'Total']
df.date = pd.to_datetime(df.date)
df_filt = df.groupby(['country','sector']).resample('MS',on='date').sum()    #D for Day, MS for month, QS to quarter, Y for year
df_filt = df_filt.reset_index()
df_filt.date = np.datetime_as_string(df_filt.date, unit='D')

# Side bar code
sidebar = st.sidebar
sidebar.title('Carbon Emissions in Transport')
sidebar.write('Test 123')


#Drop down menus
given_time = st.selectbox('Select time period to visualise', ['Day','Month','Quartile','Year'])
if given_time == 'Day':
    date_filt = 'D'
elif given_time == 'Month':
    date_filt = 'MS'
elif given_time == 'Quartile':
    date_filt = 'QS'
elif given_time == 'Year':
    date_filt = 'Y'

given_sector = st.selectbox('Select sector to visualise', df.sector.unique())

default_country = int(np.where(df['country'].unique() == 'WORLD')[0])
given_country = st.selectbox('Select country to visualise', df.country.unique(), index = default_country)
if (given_country == 'WORLD' or given_country == 'ROW' or given_country == 'EU27 & UK'):
    latrange = [-90,90]
    lonrange = [-180,180]
elif given_country == 'US':
    given_country == 'United States'
    given_country_bb = country_bb[country_bb.country == given_country]
    latrange = [float(given_country_bb['latmin']),float(given_country_bb['latmax'])]
    lonrange = [float(given_country_bb['lonmin']),float(given_country_bb['lonmax'])]
else:
    given_country_bb = country_bb[country_bb.country == given_country]
    latrange = [float(given_country_bb['latmin']),float(given_country_bb['latmax'])]
    lonrange = [float(given_country_bb['lonmin']),float(given_country_bb['lonmax'])]


df_filt = df.groupby(['country','sector']).resample(date_filt,on='date').sum()    #D for Day, MS for month, QS to quarter, Y for year
df_filt = df_filt.reset_index()
df_filt.date = np.datetime_as_string(df_filt.date, unit='D')



fig = px.choropleth(df_filt[df_filt.sector =='Domestic Aviation'], 
                    # geojson= counties,
                    # featureidkey='ISO_A3',
                    locations= 'country',
                    locationmode= "country names",
                    color='co2',
                    #hover_name="country",
                    animation_frame= 'date'
                    #zoom=2,
)
fig.update_geos(lataxis_range=latrange, lonaxis_range=lonrange)  
fig.update_layout(
    title_text = "CO2 emmissions transport sector",
    geo = dict(
        showframe = False,
        showcoastlines = True,
        projection_type = "equirectangular",
    ),
    height=1000,
    width  = 1000
    

)

st.plotly_chart(fig)