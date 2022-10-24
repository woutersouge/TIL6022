import streamlit as st
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import geopandas as gpd
import geojson
import folium
import numpy as np
import datetime
from shapely.geometry import Polygon, mapping
from calendar import month
from calendar import month_name as mn
from matplotlib import animation
import seaborn as sns
from statsmodels.nonparametric.kernel_regression import KernelReg
from datetime import datetime
#Description
#Open dataset
dataset = 'B:/Documenten/TU_Delft/Master/Module_1/Python/Assignment/TIL6022/TILL6022_Emission_Dataset.csv'
bounding_boxes = 'B:/Documenten/TU_Delft/Master/Module_1/Python/Assignment/TIL6022/country_bb.csv'
df = pd.read_csv(dataset, delimiter=',', encoding='ISO-8859-1') #,parse_dates = ['date']
country_bb = pd.read_csv(bounding_boxes, delimiter=',', encoding='ISO-8859-1')

# Side bar code
sidebar = st.sidebar
sidebar.title('Carbon Emissions in Transport')

### Select date 

given_time = sidebar.selectbox('Select time period to visualise', ['Day','Week','Month','Quartile','Year'])

if given_time == 'Day':
    date_filt = 'D'
elif given_time == 'Week':
    date_filt = 'W-MON'
elif given_time == 'Month':
    date_filt = 'MS'
elif given_time == 'Quartile':
    date_filt = 'QS'
elif given_time == 'Year':
    date_filt = 'Y'


sidebar.write('Test 123')

### Select Country
default_country = int(np.where(df['country'].unique() == 'WORLD')[0])
given_country = sidebar.selectbox('Select country to visualise', df.country.unique(), index = default_country)

### Select Sector
default_sector = int(np.where(df['sector'].unique() == 'Total')[0])
given_sector = sidebar.selectbox('Select sector to visualise', df.sector.unique(), index = default_sector)

### Datetime 

missing_EU = ['Belgium','Finland','Estonia','Austria','Luxembourg','Greece','Malta','Netherlands','Hungary','Bulgaria','Latvia','Lithuania','Slovenia','Croatia','Ireland','Portugal','Slovakia','Denmark','Polan']
df_dates = pd.to_datetime(df['date'])
df.date = df_dates
df_filt = df.groupby(['country','sector']).resample(date_filt,on='date').sum(numeric_only=True)    #D for Day, MS for month, QS to quarter, Y for year

### Smoothing data

box_pts = 4
box = np.ones(box_pts)/box_pts
smooth_data = np.convolve(df_filt.co2, box, mode='same')
df_filt.insert(4, "co2_smooth", smooth_data)
df_filt = df_filt.reset_index()
df_filt = df_filt.set_index('date')
date_min = df_filt.index.min()
date_max = df_filt.index.max()
index_min = df_filt.index == date_min
index_max = df_filt.index == date_max
df_filt = df_filt.reset_index()
df_dates = df_dates.to_numpy()
df_filt.date = np.datetime_as_string(df_filt.date, unit='D')
index_min_1 = pd.Series(df_filt.index[index_min])
index_min_2 = pd.Series(df_filt.index[index_min]+1)
index_max_1 = pd.Series(df_filt.index[index_max])
index_max_2 = pd.Series(df_filt.index[index_max]-1)
index_series = pd.Index(index_max_1.append([index_max_2,index_min_1,index_min_2], ignore_index=True))
df_filt = df_filt.drop(index_series, axis=0, inplace= True)

### World map zooming function (For world map smoothed data is not used)

zoom_factor = 3

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

data_sector = df_filt[df_filt.sector == given_sector]
if given_country == 'WORLD':
    leg_min = float(data_sector[data_sector.country != 'WORLD']['co2'].min())
    leg_max = float(data_sector[data_sector.country != 'WORLD']['co2'].max())
elif len(df_filt[df_filt.sector == given_sector].country.unique())>1:
    leg_min = float(data_sector[data_sector.country == given_country]['co2'].min())
    leg_max = float(data_sector[data_sector.country == given_country]['co2'].max())


#### Filter dataset on Transport sectors: 'International Shipping' or 'International Aviation' or 'Domestic Aviation' or 'Ground Transport'
transport_data = df_filt
transport_data =  transport_data[transport_data.sector.isin(['International Shipping', 'International Aviation', 'Domestic Aviation', 'Ground Transport'])]
print(transport_data)
#### reset index for optimal dataset and split date into years
transport_data[["year", "month", "day"]] = transport_data["date"].str.split("-", expand = True)
transport_data['same_year'] = '2019' + '-' + transport_data['month'].astype(str) + '-' + transport_data['day'] # Same year is created to visualize in same plot
transport_data2 = transport_data[(transport_data.year == '2019') | (transport_data.year == '2020')]


# add trace
Years = transport_data.year.unique()
Countries = transport_data.country.unique()

### Figures

### World map

fig_world = px.choropleth(df_filt[df_filt.sector == given_sector], 
                    locations= 'country',
                    locationmode= "country names",
                    color='co2',
                    range_color= [leg_min, leg_max],
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
    height=1000,
    width  = 1000
    

)
st.plotly_chart(fig_world, use_container_width=True)

### Scatter plots

fig_transport = go.Figure()
fig_transport = make_subplots(rows = 4, 
                    cols = 1,
                    subplot_titles = ('Total', 'International Aviation', 'Domestic Aviation', 'Ground Transport'))
# for i in Years[1]:
trans_tot = transport_data[(transport_data.country == given_country)].groupby(
        ['date'],as_index = False).agg({'country':'first','co2':'sum','co2_smooth':'sum','year':'first','month':'first','day':'first','same_year':'first'})
trans_int_av = transport_data[(transport_data.country == given_country)
                & (transport_data.sector == 'International Aviation')]
trans_do_av = transport_data[(transport_data.country == given_country)
                & (transport_data.sector == 'Domestic Aviation')]
trans_gr_tr = transport_data[(transport_data.country == given_country)
                & (transport_data.sector == 'Ground Transport')]
for i in Years:
        lop = fig_transport.add_traces(
                [
                        go.Scatter(x=list(trans_tot[(trans_tot.year == i)].same_year),
                                y=list(trans_tot[(trans_tot.year == i)].co2_smooth),
                                name= 'Total' + given_country + i,
                                visible = True), 
                        go.Scatter(x=list(trans_int_av[(trans_int_av.year == i)].same_year),
                                y=list(trans_int_av[(trans_int_av.year == i)].co2_smooth),
                                name= 'International Aviation' + given_country + i,
                                visible = True),
                        go.Scatter(x=list(trans_do_av[(trans_do_av.year == i)].same_year),
                                y=list(trans_do_av[(trans_do_av.year == i)].co2_smooth),
                                name= 'Domestic Aviation' + given_country + i,
                                visible = True),
                        go.Scatter(x=list(trans_gr_tr[(trans_gr_tr.year == i)].same_year),
                                y=list(trans_gr_tr[(trans_gr_tr.year == i)].co2_smooth),
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

Delta_Country = []
Date_country = []
Date_country_max = []
Percentage_Delta = []
Delta_Country_Do = []
Date_country_Do = []
Date_country_max_Do = []
Percentage_Delta_Do = []
Delta_Country_Trans = []
Date_country_Trans = []
Date_country_max_Trans = []
Percentage_Delta_Trans = []
Delta_Country_Int = []
Date_country_Int = []
Date_country_max_Int = []
Percentage_Delta_Int = []
selected_delta = 'co2_smooth'

### Find maximum delta of country

Delta_Total = trans_tot[(trans_tot.country == given_country)]
diff_list = []
for d in range(len(Delta_Total)-1):
        Diff = abs(Delta_Total[selected_delta].iloc[d] - Delta_Total[selected_delta].iloc[d+1])
        Co2Value = Delta_Total[selected_delta].iloc[d-1]
        diff_list.append(Diff)
        Date_country.append(Delta_Total.iloc[d]['date'])
Max_Diff = max(diff_list)
percent_Delta = ("%g" % round((Max_Diff/Co2Value)*100,1))
index_maxvalue = diff_list.index(Max_Diff)
maxDATE = Date_country[index_maxvalue]
Delta_Country.append(Max_Diff)
Date_country_max.append(maxDATE)
Percentage_Delta.append(percent_Delta)

Do_Av = trans_do_av[(trans_do_av.country == given_country)]
diff_list_Do = []
for d in range(len(Do_Av)-1):
        Diff = abs(Do_Av[selected_delta].iloc[d] - Do_Av[selected_delta].iloc[d+1])
        Co2Value_Do = Do_Av[selected_delta].iloc[d-1]
        diff_list_Do.append(Diff)
        Date_country_Do.append(Do_Av.iloc[d]['date'])
Max_Diff_Do = max(diff_list_Do)
percent_Delta_Do = round((Max_Diff_Do/Co2Value_Do)*100,1)
index_maxvalue_Do = diff_list_Do.index(Max_Diff_Do)
maxDATE_Do = Date_country_Do[index_maxvalue_Do]
Delta_Country_Do.append(Max_Diff_Do)
Date_country_max_Do.append(maxDATE_Do)
Percentage_Delta_Do.append(percent_Delta_Do)

Gr_Trans = trans_gr_tr[(trans_gr_tr.country == given_country)]
diff_list_Trans = []
for d in range(len(Gr_Trans)-1):
        Diff = abs(Gr_Trans[selected_delta].iloc[d] - Gr_Trans[selected_delta].iloc[d+1])
        Co2Value_Trans = Gr_Trans[selected_delta].iloc[d-1]
        diff_list_Trans.append(Diff)
        Date_country_Trans.append(Gr_Trans.iloc[d]['date'])
Max_Diff_Trans = max(diff_list_Trans)
Percent_Delta_Trans = round((Max_Diff_Trans/Co2Value_Trans)*100, 1)
Delta_Country_Trans.append(Max_Diff_Trans)
index_maxvalue_Trans = diff_list_Trans.index(Max_Diff_Trans)
maxDATE_Trans = Date_country_Trans[index_maxvalue_Trans]
Date_country_max_Trans.append(maxDATE_Trans)
Percentage_Delta_Trans.append(Percent_Delta_Trans)

Int_Av = trans_int_av[(trans_int_av.country == given_country)]
diff_list_Int = []
for d in range(len(Int_Av)-1):
        Diff = abs(Int_Av[selected_delta].iloc[d] - Int_Av[selected_delta].iloc[d+1])
        Co2Value_Int = Int_Av[selected_delta].iloc[d-1]
        diff_list_Int.append(Diff)
        Date_country_Int.append(Int_Av.iloc[d]['date'])
Max_Diff_Int = max(diff_list_Int)
Percent_Delta_Int = round((Max_Diff_Int/Co2Value_Int)*100, 1)
Delta_Country_Int.append(Max_Diff_Int)
index_maxvalue_Int = diff_list_Int.index(Max_Diff_Int)
maxDATE_Int = Date_country_Int[index_maxvalue_Int]
Date_country_max_Int.append(maxDATE_Int)
Percentage_Delta_Int.append(Percent_Delta_Int)


DeltaTable = pd.DataFrame(
    [['Country', given_country],
     ['Biggest Delta', Delta_Country],
     ['Percentage biggest Delta', Percentage_Delta],
     ['Date biggest Delta', Date_country_max],
     ['Biggest Ground Transportation Delta', Delta_Country_Trans],
     ['Percentage biggest Ground Transportation Delta', Percentage_Delta_Trans],
     ['Date biggest Ground Transportation Delta', Date_country_max_Trans],
     ['Biggest Domestic Aviation Delta', Delta_Country_Do],
     ['Percentage biggest Domestic Aviation Delta', Percentage_Delta_Do],
     ['Date biggest Domestic Aviation Delta', Date_country_max_Do],
     ['Biggest International Aviation Delta', Delta_Country_Int],
     ['Percentage biggest International Aviation Delta', Percentage_Delta_Int],
     ['Date biggest International Aviation Delta', Date_country_max_Int]
    ])


DeltaTable.style.background_gradient(cmap='Blues',axis =1)