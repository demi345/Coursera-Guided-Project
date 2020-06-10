import pandas as pd  #import pandas
import numpy as np #import numpy
import streamlit as st #import streamlit to build the application
import pydeck as pdk
import plotly.express as px
DATA_URL = (r'C:\Users\demis\OneDrive\Desktop\Project\Motor_Vehicle_Collisions_-_Crashes.csv') #get the data from the file

st.title('Motor Vehicle Collisions in New York City') #name the title
st.markdown('This application is a streamlit dashboard to analyze motro Vehicle Collisions in NYC 🗽')

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE','CRASH_TIME']]) #read the file
    data.dropna(subset=['LATITUDE','LONGITUDE'],inplace=True) #drop not available data
    lowercase = lambda x: str(x).lower() # lowercase for LATITUDE and LONGITUDE
    data.rename(lowercase,axis='columns',inplace=True)
    data.rename(columns={'crash_date_crash_time':'date/time'},inplace=True) ## rename column name from crash_date_crash_time to date/time
    return data
data = load_data(100000) #load 100000 nrows
original_data = data

st.header = ('Where is the most injured in NYC ?') # where is the most injured in NYC
injured_people = st.slider("Number of people injured in Vehicle Collisions",0,19)
st.map(data.query('injured_persons >= @injured_people')[['longitude','latitude']].dropna(how='any')) # visulize the data on map

st.header = ('How many Collisions occur during given time of a day?') # how many Collisions happens during given time
hour = st.sidebar.slider('Hour to look at',0,23) # creat select box to select given Hour
data = data[data['date/time'].dt.hour == hour] # filtering data and intereactive tables

st.markdown('Vehicle Collisions between %i:0 and %i:0'% ( hour,(hour+1) % 24)) # plot filtered data on 3D plot
midpoint  =(np.average(data['latitude']),np.average(data['longitude']))

st.write(pdk.Deck(          #3D map
    map_style = 'mapbox://styles /mapbox/light-v9',
    initial_view_state = {'latitude':midpoint[0],'longitude':midpoint[1],'zoom':11,'pitch':50},
    layers=[pdk.Layer('HexagonLayer',
    data = data [['date/time','latitude','longitude']],
    get_position=['longitude','latitude'],
    radius = 100,
    extruded=True,
    pickable=True,
    elevation_scale=4,
    elevation_range=[0,1000],
    ),
    ],
    ))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour,(hour + 1)%24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
    ]
hist = np.histogram(filtered['date/time'].dt.minute,bins=60,range=(0,60))[0] # charts and histogram
chart_data = pd.DataFrame ({'minute':range(60),'crashes':hist})
fig=px.bar(chart_data,x = 'minute', y ='crashes',hover_data=['minute','crashes'], height = 400)
st.write(fig)

st.header =("Top 5 dangerous streets by affected type") # select data using dropdown
select = st.selectbox("Affected type of people",['Pedestrians','Cylists','Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[['on_street_name','injured_pedestrians']].sort_values(by=['injured_pedestrians'],ascending=False).dropna(how='any')[:5])
elif select == 'Cyclist':
    st.write(original_data.query("injured_cyclists >= 1")[['on_street_name','injured_cyclists']].sort_values(by=['injured_cyclists'],ascending=False).dropna(how='any')[:5])
else:
    st.write(original_data.query("injured_motorists >= 1")[['on_street_name','injured_motorists']].sort_values(by=['injured_motorists'],ascending=False).dropna(how='any')[:5])




if st.checkbox('Show Raw Data',False): #to show the row data
    st.subheader('Raw Data')
    st.write(data)
