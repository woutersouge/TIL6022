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
df = pd.read_csv(dataset, delimiter=',', encoding='ISO-8859-1')
df.date = pd.to_datetime(df.date)

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
# """
# This application is a simple example of dashboarding for visualising data.  
# You can find the streamlit cheatsheet here: https://share.streamlit.io/daniellewisdl/streamlit-cheat-sheet/app.py  
# """
# )

# #Data
# df = px.data.gapminder()
# years = df.year.unique()

# given_year = st.selectbox('Select year to visualise', years)
# st.write('You selected year ' + str(given_year))

# if given_year is not None:
#     df_new = df.query('year=='+str(given_year))
#     df_new = df_new.groupby('continent').sum()
#     if df_new is not None:
#         fig = px.bar(df_new, x=df_new.index, y="pop", color=df_new.index, range_y=[0,4000000000])
#         st.plotly_chart(fig)    


df_filt = df.groupby(['country','sector']).resample(date_filt,on='date').sum()    #D for Day, MS for month, QS to quarter, Y for year
df_filt = df_filt.reset_index()
df_filt.date = np.datetime_as_string(df_filt.date, unit='D')

with open("B:\Documenten\TU_Delft\Master\Module_1\Python\Assignment\TIL6022\countries.geojson") as f:
    counties = geojson.load(f)
gdf = gpd.GeoDataFrame.from_features(counties["features"], crs=4326)
mask = gdf.area >2    # Function to remove smaller countries to speed up 
gdf_selec = gdf.loc[mask]

fig = px.choropleth(df_filt[df_filt.sector =='Domestic Aviation'], locations= "country",
                    locationmode= "country names",
                    color="co2",
                    #hover_name="country",
                    animation_frame="date"
                    #color_continuous_scale="Blues_r"
                    )
fig.update_geos(fitbounds=given_country)     
fig.update_layout(
    title_text = "Life Expectancy",
    geo = dict(
        showframe = False,
        showcoastlines = True,
        projection_type = "equirectangular"        
    ),
    height=300, 
    margin={"r":0,"t":0,"l":0,"b":0}
)
st.plotly_chart(fig)