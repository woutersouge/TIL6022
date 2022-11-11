import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

### Description
# This python script launches a streamlit app that visualises all results in graphs online, with an understandable GUI.
# On windows you can launch it by opening a PowerShell Window in the folder of the python file using "streamlit run dashboard.py"

st. set_page_config(layout="wide")

#Open dataset

dataset = 'B:/Documenten/TU_Delft/Master/Module_1/Python/Assignment/TIL6022/TILL6022_Emission_Dataset.csv'
bounding_boxes = 'B:/Documenten/TU_Delft/Master/Module_1/Python/Assignment/TIL6022/country_bb.csv'
df = pd.read_csv(dataset, delimiter=',', encoding='ISO-8859-1')
country_bb = pd.read_csv(bounding_boxes, delimiter=',', encoding='ISO-8859-1')
transport_sectors = ['Total', 'International Aviation', 'Domestic Aviation', 'Ground Transport']

# Side bar code using inputs
sidebar = st.sidebar
sidebar.title('Carbon Emissions in Transport')
sidebar.write('Made for TIL6022 by Wouter Sougé, Max Hendriks and Tim Traas')
given_time = sidebar.selectbox('Select time period to visualise', ['Day','Week','Month','Quartile'],index = 1)

if given_time == 'Day':
    date_filt = 'D'
elif given_time == 'Week':
    date_filt = 'W-MON'
elif given_time == 'Month':
    date_filt = 'MS'
elif given_time == 'Quartile':
    date_filt = 'QS'

default_country = int(np.where(df['country'].unique() == 'WORLD')[0])
given_country = sidebar.selectbox('Select country to visualise', df.country.unique(), index = default_country)
default_sector = transport_sectors.index('Total')
given_sector = sidebar.selectbox('Select sector to visualise', transport_sectors, index = default_sector)
df.date = pd.to_datetime(df['date'])
df_filt = df.groupby(['country','sector']).resample(date_filt,on='date').sum()
df_filt = df_filt.reset_index()
box_pts = 4
box = np.ones(box_pts)/box_pts
df_filt["co2_smooth"] = np.convolve(df_filt.co2, box, mode='same')

df_filt = df_filt.set_index('date')
date_min = df_filt.index.min()
date_max = df_filt.index.max()
index_min = df_filt.index == date_min
index_max = df_filt.index == date_max
df_filt = df_filt.reset_index()

df_filt.date = np.datetime_as_string(df_filt.date, unit='D')
index_min_1 = pd.Series(df_filt.index[index_min])
index_min_2 = pd.Series(df_filt.index[index_min]+1)
index_max_1 = pd.Series(df_filt.index[index_max])
index_max_2 = pd.Series(df_filt.index[index_max]-1)
index_series = pd.Index(index_max_1.append([index_max_2,index_min_1,index_min_2], ignore_index=True))
df_filt.drop(index_series, axis=0, inplace= True)

zoom_factor = 3

if (given_country == 'WORLD' or given_country == 'ROW' or given_country == 'EU27 & UK'):
    latrange = [-90,90]
    lonrange = [-180,180]
elif given_country == 'US':
    bb_country = 'United States'
    given_country_bb = country_bb[country_bb.country == bb_country]
    latrange = [float(given_country_bb['latmin'])-zoom_factor,float(given_country_bb['latmax'])+zoom_factor]
    lonrange = [float(given_country_bb['lonmin'])-zoom_factor*2,float(given_country_bb['lonmax'])+zoom_factor*2]
elif given_country == 'UK':
    bb_country = 'United Kingdom'
    given_country_bb = country_bb[country_bb.country == bb_country]
    latrange = [float(given_country_bb['latmin'])-zoom_factor,float(given_country_bb['latmax'])+zoom_factor]
    lonrange = [float(given_country_bb['lonmin'])-zoom_factor*2,float(given_country_bb['lonmax'])+zoom_factor*2]
else:
    given_country_bb = country_bb[country_bb.country == given_country]
    latrange = [float(given_country_bb['latmin'])-zoom_factor,float(given_country_bb['latmax'])+zoom_factor]
    lonrange = [float(given_country_bb['lonmin'])-zoom_factor*5,float(given_country_bb['lonmax'])+zoom_factor*5]

data_sector = df_filt[df_filt.sector == given_sector]
if given_country == 'WORLD':
    leg_min = float(data_sector[data_sector.country != 'WORLD']['co2'].min())
    leg_max = float(data_sector[data_sector.country != 'WORLD']['co2'].max())
elif len(df_filt[df_filt.sector == given_sector].country.unique())>1:
    leg_min = float(data_sector[data_sector.country == given_country]['co2'].min())
    leg_max = float(data_sector[data_sector.country == given_country]['co2'].max())


# filter dataset on Transport sectors:'International Aviation' or 'Domestic Aviation' or 'Ground Transport'
transport_data =  df_filt[df_filt.sector.isin(transport_sectors)]
transport_data[["year", "month", "day"]] = transport_data["date"].str.split("-", expand = True)
transport_data['same_year'] = '2019' + '-' + transport_data['month'].astype(str) + '-' + transport_data['day'] # Same year is created to visualize in same plot
Years = transport_data.year.unique()
Countries = transport_data.country.unique()

### Figures

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
    height = 600,
    width = 1200,
    
    margin=dict(l=0, r=0, t=0, b=0)

)

fig_transport = make_subplots(rows = 1, 
                    cols = 4,
                    subplot_titles = ('Total', 'International Aviation', 'Domestic Aviation', 'Ground Transport'))
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
                                y=list(trans_tot[(trans_tot.year == i)].co2),
                                name= 'Total' + given_country + i,
                                visible = True), 
                        go.Scatter(x=list(trans_int_av[(trans_int_av.year == i)].same_year),
                                y=list(trans_int_av[(trans_int_av.year == i)].co2),
                                name= 'International Aviation' + given_country + i,
                                visible = True),
                        go.Scatter(x=list(trans_do_av[(trans_do_av.year == i)].same_year),
                                y=list(trans_do_av[(trans_do_av.year == i)].co2),
                                name= 'Domestic Aviation' + given_country + i,
                                visible = True),
                        go.Scatter(x=list(trans_gr_tr[(trans_gr_tr.year == i)].same_year),
                                y=list(trans_gr_tr[(trans_gr_tr.year == i)].co2),
                                name= 'Ground Transport' + given_country + i,
                                visible = True)
                ], rows=[1,1,1,1], cols=[1,2,3,4]
        )

fig_transport.update_layout(
    height = 500,
    width = 1800
)

fig_transport.update_layout(xaxis_title = 'Date', yaxis_title = 'CO2 emissions x 1000 (ppm)')
fig_transport.update_layout(title_text = 'CO2 emissions comparison 2019 until 2022')
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
diff_list = []

# Total sectors deviation
Delta_Total = trans_tot[(trans_tot.country == given_country)]
for d in range(len(Delta_Total)-1):
        Diff = abs(Delta_Total['co2_smooth'].iloc[d] - Delta_Total['co2_smooth'].iloc[d+1])
        Co2Value = Delta_Total['co2_smooth'].iloc[d-1]
        diff_list.append(Diff)
        Date_country.append(Delta_Total.iloc[d]['date'])
Max_Diff = max(diff_list)
percent_Delta = ("%g" % round((Max_Diff/Co2Value)*100,1))
index_maxvalue = diff_list.index(Max_Diff)
maxDATE = Date_country[index_maxvalue]
Delta_Country.append(Max_Diff)
Date_country_max.append(maxDATE)
Percentage_Delta.append(percent_Delta)

# Domestic sector 
Do_Av = trans_do_av[(trans_do_av.country == given_country)]
diff_list_Do = []
for d in range(len(Do_Av)-1):
        Diff = abs(Do_Av['co2_smooth'].iloc[d] - Do_Av['co2_smooth'].iloc[d+1])
        Co2Value_Do = Do_Av['co2_smooth'].iloc[d-1]
        diff_list_Do.append(Diff)
        Date_country_Do.append(Do_Av.iloc[d]['date'])
Max_Diff_Do = max(diff_list_Do)
percent_Delta_Do = round((Max_Diff_Do/Co2Value_Do)*100,1)
index_maxvalue_Do = diff_list_Do.index(Max_Diff_Do)
maxDATE_Do = Date_country_Do[index_maxvalue_Do]
Delta_Country_Do.append(Max_Diff_Do)
Date_country_max_Do.append(maxDATE_Do)
Percentage_Delta_Do.append(percent_Delta_Do)

# Ground Transport 
Gr_Trans = trans_gr_tr[(trans_gr_tr.country == given_country)]
diff_list_Trans = []
for d in range(len(Gr_Trans)-1):
        Diff = abs(Gr_Trans['co2_smooth'].iloc[d] - Gr_Trans['co2_smooth'].iloc[d+1])
        Co2Value_Trans = Gr_Trans['co2_smooth'].iloc[d-1]
        diff_list_Trans.append(Diff)
        Date_country_Trans.append(Gr_Trans.iloc[d]['date'])
Max_Diff_Trans = max(diff_list_Trans)
Percent_Delta_Trans = round((Max_Diff_Trans/Co2Value_Trans)*100, 1)
Delta_Country_Trans.append(Max_Diff_Trans)
index_maxvalue_Trans = diff_list_Trans.index(Max_Diff_Trans)
maxDATE_Trans = Date_country_Trans[index_maxvalue_Trans]
Date_country_max_Trans.append(maxDATE_Trans)
Percentage_Delta_Trans.append(Percent_Delta_Trans)

# International Aviation
Int_Av = trans_int_av[(trans_int_av.country == given_country)]
diff_list_Int = []
for d in range(len(Int_Av)-1):
        Diff = abs(Int_Av['co2_smooth'].iloc[d] - Int_Av['co2_smooth'].iloc[d+1])
        Co2Value_Int = Int_Av['co2_smooth'].iloc[d-1]
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
    {'Date Total': Date_country_max,
     'Total Delta': Delta_Country,
     'Percentage Total [%]': Percentage_Delta,
     'Date Ground Transportation': Date_country_max_Trans,
     'Ground Transportation Delta': Delta_Country_Trans,
     'Percentage Ground Transportation [%]': Percentage_Delta_Trans,
     'Domestic Aviation Delta': Delta_Country_Do,
     'Percentage Domestic Aviation [%]': Percentage_Delta_Do,
     'Date Domestic Aviation': Date_country_max_Do,
     'International Aviation Delta': Delta_Country_Int,
     'Percentage International Aviation [%]': Percentage_Delta_Int,
     'Date International Aviation': Date_country_max_Int
    })
DeltaTrans = DeltaTable.transpose()
DeltaTrans.style.background_gradient(cmap='Blues')
DeltaTrans.columns = [given_country]
with st.sidebar:
    st.table(DeltaTrans)
with st.container():
    st.plotly_chart(fig_world, use_container_width=True)
    st.plotly_chart(fig_transport, use_container_width=True)
