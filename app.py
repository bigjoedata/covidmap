import streamlit as st
import altair as alt
import pydeck# as pdk
import datetime
from datetime import date
from datetime import timedelta 
from itertools import cycle
import time
import random
import pandas as pd
import numpy as np
from utils import reduce_mem_usage 
from utils import import_data 

today = date.today()
yesterday = today - timedelta(days = 1) 

DATE = "date"

st.title("Covid Growth in the US")
st.markdown(
"""
This Streamlit app shows Covid growth in the US. Use the slider
to pick a specific day and look at how the charts change.
""")

@st.cache(persist=True)
def load_JHU_data():
    with st.spinner("Loading  ..."):
        JHU_time_series_covid19_confirmed_US_URL = ("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv")

        JHU_time_series_covid19_confirmed_global_URL = ("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")

        JHU_time_series_covid19_deaths_US_URL = ("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv")

        JHU_time_series_covid19_deaths_global_URL = ("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")

        JHU_time_series_covid19_recovered_global_URL = ("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")

        UID_ISO_FIPS_LookUp_Table_URL = ("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv")

        UID_ISO_FIPS_LookUp_Table = import_data(UID_ISO_FIPS_LookUp_Table_URL)
        JHU_time_series_covid19_confirmed_US = import_data(JHU_time_series_covid19_confirmed_US_URL)
        JHU_time_series_covid19_confirmed_global = import_data(JHU_time_series_covid19_confirmed_global_URL)
        JHU_time_series_covid19_deaths_US = import_data(JHU_time_series_covid19_deaths_US_URL)
        JHU_time_series_covid19_deaths_global = import_data(JHU_time_series_covid19_deaths_global_URL)
        JHU_time_series_covid19_recovered_global = import_data(JHU_time_series_covid19_recovered_global_URL)

        UID_Population = UID_ISO_FIPS_LookUp_Table[['UID', 'Population']].copy()
        ProvStateCountryPop = UID_ISO_FIPS_LookUp_Table.copy()

        JHU_time_series_covid19_confirmed_US2=JHU_time_series_covid19_confirmed_US.copy()
        #JHU_time_series_covid19_confirmed_US2.drop(['iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Province_State', 'Country_Region'], axis=1, inplace=True)
        JHU_time_series_covid19_confirmed_US2 = JHU_time_series_covid19_confirmed_US2.melt(id_vars=['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Province_State', 'Country_Region', 'Lat', 'Long_', 'Combined_Key'])
        JHU_time_series_covid19_confirmed_US2.rename(columns = {'variable':'Date', 'value':'Confirmed'}, inplace = True)
        #JHU_time_series_covid19_confirmed_US_melt = pd.merge(JHU_time_series_covid19_confirmed_US_melt, UID_Population, on='UID', how='left')
        JHU_time_series_covid19_deaths_US2 = JHU_time_series_covid19_deaths_US.copy()
        JHU_time_series_covid19_deaths_US2.drop(['iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Province_State', 'Country_Region', 'Lat', 'Long_', 'Combined_Key', 'Population'], axis=1, inplace=True)
        JHU_time_series_covid19_deaths_US2 = JHU_time_series_covid19_deaths_US2.melt(id_vars=['UID'])
        JHU_time_series_covid19_deaths_US2.rename(columns = {'variable':'Date', 'value':'Deaths'}, inplace = True)
        JHU_time_series_covid19_US = pd.merge(JHU_time_series_covid19_confirmed_US2, JHU_time_series_covid19_deaths_US2, on=['UID','Date'], how='outer')
        JHU_time_series_covid19_US = pd.merge(JHU_time_series_covid19_US, UID_Population, on='UID', how='left')
        JHU_time_series_covid19_US['US_Only'] = 1
        JHU_time_series_covid19_US.rename(columns = {'Long_':'Long'}, inplace = True)

        ProvStateCountryPop = UID_ISO_FIPS_LookUp_Table.copy()
        ProvStateCountryPop.drop(['Lat','Long_'], axis=1, inplace=True)

        JHU_time_series_covid19_confirmed_global2 = JHU_time_series_covid19_confirmed_global.copy()
        JHU_time_series_covid19_confirmed_global2 = JHU_time_series_covid19_confirmed_global2.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'])
        JHU_time_series_covid19_confirmed_global2.rename(columns = {'variable':'Date', 'value':'Confirmed'}, inplace = True)

        JHU_time_series_covid19_deaths_global2 = JHU_time_series_covid19_deaths_global.copy()
        JHU_time_series_covid19_deaths_global2 = JHU_time_series_covid19_deaths_global2.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'])
        JHU_time_series_covid19_deaths_global2.rename(columns = {'variable':'Date', 'value':'Deaths'}, inplace = True)

        JHU_time_series_covid19_Global = pd.merge(JHU_time_series_covid19_confirmed_global2, JHU_time_series_covid19_deaths_global2, on=['Date','Province/State', 'Country/Region', 'Lat', 'Long'], how='outer')
        JHU_time_series_covid19_Global.rename(columns = {'Province/State':'Province_State', 'Country/Region':'Country_Region'}, inplace = True)
        JHU_time_series_covid19_Global = pd.merge(JHU_time_series_covid19_Global, ProvStateCountryPop, on=['Province_State', 'Country_Region'], how='left')
        JHU_time_series_covid19_Global['US_Only'] = 0

        JHU_time_series_covid19_Combined = JHU_time_series_covid19_Global.append(JHU_time_series_covid19_US, sort=False)
        JHU_time_series_covid19_Combined['Confirmed'] = JHU_time_series_covid19_Combined['Confirmed'].fillna(0)
        JHU_time_series_covid19_Combined['Deaths'] = JHU_time_series_covid19_Combined['Deaths'].fillna(0)
        JHU_time_series_covid19_Combined['Date'] = pd.to_datetime(JHU_time_series_covid19_Combined['Date'])
        JHU_time_series_covid19_Combined.drop(['UID'], axis=1, inplace=True)

        for column_name in ['FIPS', 'Province_State', 'Country_Region', 'iso2', 'iso3', 'code3', 'Admin2', 'Combined_Key', 'US_Only']:
            try:
                JHU_time_series_covid19_Combined[column_name] = JHU_time_series_covid19_Combined[column_name].astype('category')
            except KeyError:
                pass

        JHU_time_series_covid19_Combined.rename(columns = {'Lat':'lat', 'Long':'lon', 'Date':'date'}, inplace = True)

        JHU_time_series_covid19_Combined['datestr'] = JHU_time_series_covid19_Combined['date'].dt.strftime("%Y-%m-%d")
        JHU_time_series_covid19_Combined['DeathsPerConfirmed'] = (JHU_time_series_covid19_Combined['Deaths'] / JHU_time_series_covid19_Combined['Confirmed'])#.replace(np.inf, 0).fillna(0)
        JHU_time_series_covid19_Combined['Deathsper100kpop'] = (100000*JHU_time_series_covid19_Combined['Deaths'] / JHU_time_series_covid19_Combined['Population'])
        JHU_time_series_covid19_Combined['Confirmedper100kpop'] = (100000*JHU_time_series_covid19_Combined['Confirmed'] / JHU_time_series_covid19_Combined['Population'])#.replace(np.inf, 0).fillna(0)

        for column_name in ['lat', 'lon','date']:
            try:
                JHU_time_series_covid19_Combined = JHU_time_series_covid19_Combined[JHU_time_series_covid19_Combined[column_name].notna()]
                JHU_time_series_covid19_Combined = JHU_time_series_covid19_Combined[JHU_time_series_covid19_Combined[column_name].notnull()]
            except KeyError:
                pass
        for column_name in ['Deaths', 'Confirmed', 'Population', 'Deathsper100kpop','Confirmedper100kpop', 'DeathsPerConfirmed']:
            try:
                JHU_time_series_covid19_Combined[column_name] = JHU_time_series_covid19_Combined[column_name].replace(np.inf, 0).fillna(0)
            except KeyError:
                pass

        JHU_time_series_covid19_Combined = JHU_time_series_covid19_Combined[~((JHU_time_series_covid19_Combined['Combined_Key'] == 'US'))]    
            
        JHU_time_series_covid19_Combined.drop(['Province_State', 'Country_Region', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Combined_Key', 'US_Only'], axis=1, inplace=True) 

        JHU_time_series_covid19_Combined = JHU_time_series_covid19_Combined[~((JHU_time_series_covid19_Combined['Confirmed'] == 0) & (JHU_time_series_covid19_Combined['Deaths'] == 0))]
        JHU_time_series_covid19_Combined = JHU_time_series_covid19_Combined[~((JHU_time_series_covid19_Combined['lat'] <.1) & (JHU_time_series_covid19_Combined['lon'] < .1))]
        JHU_time_series_covid19_Combined = JHU_time_series_covid19_Combined.dropna()
        JHU_time_series_covid19_Combined.reset_index()

        uniquedates = pd.DataFrame(columns=['date'])
        uniquedates['date'] = JHU_time_series_covid19_Combined['date'].drop_duplicates()
        uniquedates.set_index('date', inplace=True)

        return JHU_time_series_covid19_Combined, uniquedates

datamerged, uniquedates = load_JHU_data()

#st.write(datamerged)


#uniquedates = datamerged['date'].unique().dt.date

date_value = st.empty()
date_slider = st.empty()

st.subheader("Animation")
animations = {"None": None, "Slow": 0.4, "Medium": 0.2, "Fast": 0.05}
animate = st.radio("", options=list(animations.keys()), index=2)
animation_speed = animations[animate]
deck_map = st.empty()

raw_data = st.empty()

days_values = [(d.year, d.month, d.day) for d in uniquedates.index]
year, month, day = days_values[0]

def render_slider(year, month, day):
    key = random.random() if animation_speed else None
    day_value = date_slider.slider(
        "",
        min_value=0,
        max_value=len(uniquedates)-1,
        value=days_values.index((year, month, day)),
        format="",
        key=key,
    )
    year, month, day = days_values[day_value]
    d = date(year, month, day)
    date_value.subheader(f"Day: {d:%Y}-{d:%m}-{d:%d}")
    return year, month, day

def write_table(year, month, day):
    mask = datamerged[(datamerged['date'].dt.year == year) & (datamerged['date'].dt.month == month) & (datamerged['date'].dt.day == day)]
    st.write(mask)

def render_map(year, month, day):
    mask = datamerged[(datamerged['date'].dt.year == year) & (datamerged['date'].dt.month == month) & (datamerged['date'].dt.day == day)]
    midpoint = (np.average(datamerged["lat"]), np.average(datamerged["lon"]))
    max_elerange=datamerged['Confirmed'].max()
    deck_map.pydeck_chart(
        pydeck.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pydeck.ViewState(
                #latitude=midpoint[0],
                #longitude=midpoint[1],
                latitude=40.7128,
                longitude=-74.0060,
                zoom=2,
                pitch=30,
            ),
            layers=[
                pydeck.Layer(
                    "ColumnLayer",
                    data=mask,
                    disk_resolution=12,
                    auto_highlight=True,
                    radius=1000,
                    elevation_scale=50,
                    get_position="[lon, lat]",
                    get_color="[Deaths * 2550, 0 0, 150]",
                    get_elevation="[Deaths]",
                    elevation_range=[0, 'max_elerange'],
                    pickable=True,
                    extruded=True,
                    coverage=1
                ),
                pydeck.Layer(
                    "ScatterplotLayer",
                    data=mask,
                    disk_resolution=12,
                    auto_highlight=True,
                    radius=1000,
                    #elevation_scale=50,
                    get_position="[lon, lat]",
                    get_color="[DeathsPerConfirmed * 3000, 0, 0, 150]",
                    get_elevation="[cases]",
                    elevation_range=[0, 'max_elerange'],
                    #pickable=True,
                    #extruded=True,
                    coverage=1
                ),
            ],
        )
    )
    #st.write(mask)


if animation_speed:
    for year, month, day in cycle(days_values):
        time.sleep(animation_speed)
        render_slider(year, month, day)
        render_map(year, month, day)
else:
    year, month, day = render_slider(year, month, day)
    render_map(year, month, day)
    #write_table(year, month, day)

st.markdown(
"""
This is heavily indebted to:\n
https://davidcaron.dev/streamlit-bicycle-counts-montreal/ \n
https://github.com/streamlit/demo-uber-nyc-pickups/blob/master/app.py \n
https://github.com/CSSEGISandData/COVID-19

Other sources initially consulted include:\n
https://github.com/nytimes/covid-19-data\n
https://github.com/btskinner/spatial
""")

def main():
    pass

if __name__ == '__main__':
    main()