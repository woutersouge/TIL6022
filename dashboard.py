import streamlit as st

import json
import plotly.express as px
import pandas as pd
import geopandas as gpd
import geojson
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from calendar import month
from matplotlib import animation
#Description
#Open dataset
dataset = 'TILL6022_Emission_Dataset.csv'
df = pd.read_csv(dataset, delimiter=',', encoding='ISO-8859-1') #,parse_dates = ['date']
country_bb = pd.read_csv('country_bb.csv', delimiter=',', encoding='ISO-8859-1')

df.date = pd.to_datetime(df.date)
df_filt = df.groupby(['country','sector']).resample('MS',on='date').sum()    #D for Day, MS for month, QS to quarter, Y for year
df_filt = df_filt.reset_index()
df_filt.date = np.datetime_as_string(df_filt.date, unit='D')

# Side bar code
sidebar = st.sidebar
sidebar.title('Carbon Emissions in Transport')
given_time = sidebar.selectbox('Select time period to visualise', ['Day','Month','Quartile','Year'])
if given_time == 'Day':
    date_filt = 'D'
elif given_time == 'Month':
    date_filt = 'MS'
elif given_time == 'Quartile':
    date_filt = 'QS'
elif given_time == 'Year':
    date_filt = 'Y'
sidebar.write('Test 123')

default_country = int(np.where(df['country'].unique() == 'WORLD')[0])
given_country = sidebar.selectbox('Select country to visualise', df.country.unique(), index = default_country)

default_sector = int(np.where(df['sector'].unique() == 'Total')[0])
given_sector = sidebar.selectbox('Select sector to visualise', df.sector.unique(), index = default_sector)

zoom_factor = 3
#Drop down menus


if (given_country == 'WORLD' or given_country == 'ROW' or given_country == 'EU27 & UK'):
    latrange = [-90,90]
    lonrange = [-180,180]
elif given_country == 'US':
    given_country = 'United States'
    given_country_bb = country_bb[country_bb.country == given_country]
    latrange = [float(given_country_bb['latmin'])-zoom_factor,float(given_country_bb['latmax'])+zoom_factor]
    lonrange = [float(given_country_bb['lonmin'])-zoom_factor,float(given_country_bb['lonmax'])+zoom_factor]
else:
    given_country_bb = country_bb[country_bb.country == given_country]
    latrange = [float(given_country_bb['latmin'])-zoom_factor,float(given_country_bb['latmax'])+zoom_factor]
    lonrange = [float(given_country_bb['lonmin'])-zoom_factor,float(given_country_bb['lonmax'])+zoom_factor]

df_filt = df.groupby(['country','sector']).resample(date_filt,on='date').sum()    #D for Day, MS for month, QS to quarter, Y for year
df_filt = df_filt.reset_index()
df_filt.date = np.datetime_as_string(df_filt.date, unit='D')

data_sector = df_filt[df_filt.sector == given_sector]
if given_country == 'WORLD':
    leg_min = float(data_sector[data_sector.country != 'WORLD']['co2'].min())
    leg_max = float(data_sector[data_sector.country != 'WORLD']['co2'].max())
elif len(df_filt[df_filt.sector == given_sector].country.unique())>1:
    leg_min = float(data_sector[data_sector.country == given_country]['co2'].min())
    leg_max = float(data_sector[data_sector.country == given_country]['co2'].max())


# filter dataset on Transport sectors: 'International Shipping' or 'International Aviation' or 'Domestic Aviation' or 'Ground Transport'
transport_datas = ['International Shipping', 'International Aviation', 'Domestic Aviation', 'Ground Transport']
transport_data =  df_filt[df_filt.sector.isin(transport_datas)]

# Transport_not_World = transport_data[transport_data.country != 'WORLD'].groupby(['country', 'date']).sum()

#reset index for optimal dataset and split date into years

# transport_data = Transport_not_World.reset_index(['country', 'date'])
transport_data[["year", "month", "day"]] = transport_data["date"].str.split("-", expand = True)
transport_data['same_year'] = '2019' + '-' + transport_data['month'].astype(str) + '-' + transport_data['day'] # Same year is created to visualize in same plot
transport_data2 = transport_data[(transport_data.year == '2019') | (transport_data.year == '2020')]
# transport_data["date"].str.split("-", expand = True)
fig_transport = go.Figure()
# add trace
Years = ['2019', '2020']
Countries = ['UK', 'US', 'China', 'EU27 & UK', 'France', 'Germany', 'India', 'Italy', 'Japan', 'Russia', 'Spain']
months = list(transport_data.month.unique())

### Figures

fig_world = px.choropleth(df_filt[df_filt.sector == given_sector], 
                    # geojson= counties,
                    # featureidkey='ISO_A3',
                    locations= 'country',
                    locationmode= "country names",
                    color='co2',
                    range_color= [leg_min, leg_max],
                    #hover_name="country",
                    animation_frame= 'date'
)
fig_world.update_geos(lataxis_range=latrange, lonaxis_range=lonrange)  
fig_world.update_layout(
    title_text = "CO2 emmissions transport sector",
    geo = dict(
        showframe = False,
        showcoastlines = True,
        projection_type = "equirectangular",
    ),
    # height=1000,
    # width  = 1000
    

)
st.plotly_chart(fig_world, use_container_width=True)

fig_transport = make_subplots(rows = 4, 
                    cols = 1,
                    subplot_titles = ('Total', 'International Aviation', 'Domestic Aviation', 'Ground Transport'))

for i in Years:
        z = transport_data[(transport_data.country == given_country) & (transport_data.year == i)]
        Int_Av = transport_data2[(transport_data2.country == given_country) & (transport_data2.year == i) & (transport_data2.sector == 'International Aviation')]
        Do_Av = transport_data2[(transport_data2.country == given_country) & (transport_data2.year == i) & (transport_data2.sector == 'Domestic Aviation')]
        Gr_Trans = transport_data2[(transport_data2.country == given_country) & (transport_data2.year == i) & (transport_data2.sector == 'Ground Transport')]
        lop = fig_transport.add_traces(
                [
                    go.Scatter(x=list(z.same_year),
                        y=list(z.co2),
                        name= given_country + i,
                        visible = True),        
                    go.Scatter(x=list(Int_Av.same_year),
                            y=list(Int_Av.co2),
                            name= 'International Aviation' + given_country + i,
                            visible = True),
                    go.Scatter(x=list(Do_Av.same_year),
                            y=list(Do_Av.co2),
                            name= 'Domestic Aviation' + given_country + i,
                            visible = True),
                    go.Scatter(x=list(Gr_Trans.same_year),
                            y=list(Gr_Trans.co2),
                            name= 'Ground Transport' + given_country + i,
                            visible = True)
                ], rows=list(range(1,5)), cols=[1,1,1,1]
                )

fig_transport.update_layout(
    height = 1500
)

fig_transport.update_layout(xaxis_title = 'Date', yaxis_title = 'CO2 emissions x 1000 (ppm)')
fig_transport.update_layout(title_text = 'CO2 emissions comparison 2019 versus 2020')
fig_transport.update_layout(xaxis=dict(tickformat="%d-%B"),
                 xaxis2=dict(tickformat="%d-%B"),
                 xaxis3=dict(tickformat="%d-%B"),
                 xaxis4=dict(tickformat="%d-%B")
                 )
fig_transport['layout']['yaxis2']['title']='CO2 emissions x 1000 (ppm)'
fig_transport['layout']['yaxis3']['title']='CO2 emissions x 1000 (ppm)'
fig_transport['layout']['yaxis4']['title']='CO2 emissions x 1000 (ppm)'
fig_transport['layout']['xaxis2']['title']='Date'
fig_transport['layout']['xaxis3']['title']='Date'
fig_transport['layout']['xaxis4']['title']='Date'


st.plotly_chart(fig_transport, use_container_width=True)
