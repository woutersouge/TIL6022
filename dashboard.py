import streamlit as st
import json
import plotly.express as px
import pandas as pd
import geopandas as gpd
import geojson
import folium

#Description
sidebar = st.sidebar
sidebar.title('Streamlit example')
sidebar.write('Test')
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

#Open dataset
dataset = 'TILL6022_Emission_Dataset.csv'
df = pd.read_csv(dataset, delimiter=',', encoding='ISO-8859-1')
vf = df[df.sector == 'Total']
#Open Json of world map
with open("B:\Documenten\TU_Delft\Master\Module_1\Python\Assignment\TIL6022\countries.geojson") as f:
    counties = geojson.load(f)
gdf = gpd.GeoDataFrame.from_features(counties["features"], crs=4326)
mask = gdf.area >2    # Function to remove smaller countries to speed up 
gdf_selec = gdf.loc[mask]

fig = px.choropleth(vf, locations= "country",
                    locationmode= "country names",
                    color="co2",
                    #hover_name="country",
                    animation_frame="date"
                    #color_continuous_scale="Blues_r"
                    )
fig.update_layout(
    title_text = "Life Expectancy",
    geo = dict(
        showframe = False,
        showcoastlines = True,
        projection_type = "equirectangular"
    )
)
st.plotly_chart(fig)