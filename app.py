import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

data_url = ("/home/rhyme/Desktop/Project/Motor_Vehicle_Collisions_-_Crashes.csv")
st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a Streamlit dashboard that can be used to analyze motor vehicle collisions in NYC Ã°ÂÂÂ½Ã°ÂÂÂ¥Ã°ÂÂÂ")


@st.cache(persist=True)

def load_data(nrows):
    data = pd.read_csv(data_url,nrows=nrows,parse_dates =[ ['CRASH_DATE','CRASH_TIME']] )
    data.dropna(subset=['LATITUDE','LONGITUDE'],inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase,axis='columns',inplace=True)
    data.rename(columns={'crash_date_crash_time':'date/time'},inplace=True)
    return data

data = load_data(100000)

#ça pour voir l carte et nbr de personne dans un accident dans NYC
st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of persons injured in vahicle collisions",0,19)
st.map(data.query("injured_persons >= @injured_people")[["latitude","longitude"]].dropna(how="any"))

#ça par rapport a heur et date de la journÃÂ©e
st.header("how many collisions occur during a given time of day?")
hour = st.slider("hour to look at",0,23)
data = data[data['date/time'].dt.hour == hour]
midpoint = (np.average(data['latitude']),np.average(data['longitude']))

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour,(hour+1) % 24))
st.write(pdk.Deck(
         map_style="mapbox://styles/mapbox/light-v9",
         initial_view_state = {
         "latitude":midpoint[0],
         "longitude":midpoint[1],
         "zoom":11,
         "pitch":50,
         },
         layers = [
         pdk.Layer(
         "HexagonLayer",
         data=data[['date/time','latitude','longitude']],
         get_position = ['longitude','latitude'],
         radius = 100,
         extruded = True,
         pickable = True,
         elevation_scale = 4,
         elevation_range = [0,1000],
         ),
         ],
))

st.subheader('breakdown by minute between %i:00 and %i:00' % (hour, (hour + 1) % 24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
    ]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("top 5 dangerous streets in nyc by affected type".title())
select = st.selectbox('affected type of people', ["pedestrians", "cyclists", "motorists"])

if select == "pedestrians":
    st.write(data.query("injured_pedestrians >=1")
             [["on_street_name", "injured_pedestrians"]].sort_values(
        by=['injured_pedestrians'], ascending=False).dropna(how='any')[:5])

if select == "cyclists":
    st.write(data.query("injured_cyclist >=1")
             [["on_street_name", "injured_cyclist"]].sort_values(
        by=['injured_cyclist'], ascending=False).dropna(how='any')[:5])

elif select == "motorists":
    st.write(data.query("injured_motorist >=1")
             [["on_street_name", "injured_motorist"]].sort_values(
        by=['injured_motorist'], ascending=False).dropna(how='any')[:5])


if st.checkbox("Show Raw Data",False):
   st.subheader('Raw Data')
   st.write(data)