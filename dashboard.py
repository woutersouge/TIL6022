import streamlit as st
import json
import plotly.express as px
import pandas as pd

dataset = 'TILL6022_Emission_Dataset.csv'
df = pd.read_csv(dataset, delimiter=',', encoding='ISO-8859-1')

#Description
sidebar = st.sidebar
sidebar.title('Carbon total emission global data')
sidebar.write(
"""
This application is a simple example of dashboarding for visualising data.  
You can find the streamlit cheatsheet here: https://share.streamlit.io/daniellewisdl/streamlit-cheat-sheet/app.py  
"""
)

#Data
df = px.data.gapminder()
years = df.year.unique()

given_year = st.selectbox('Select year to visualise', years)
st.write('You selected year ' + str(given_year))

if given_year is not None:
    df_new = df.query('year=='+str(given_year))
    df_new = df_new.groupby('continent').sum()
    if df_new is not None:
        fig = px.bar(df_new, x=df_new.index, y="pop", color=df_new.index, range_y=[0,4000000000])
        st.plotly_chart(fig)    