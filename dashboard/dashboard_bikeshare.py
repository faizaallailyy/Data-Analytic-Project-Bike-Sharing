import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
from babel.numbers import format_currency

sns.set(style='dark')

# Helper functions needed to set up various dataframes
def create_yearly_rentals_df(hour_df):
    yearly_rentals_df = hour_df.groupby(by='year')['count'].sum().reset_index()
    return yearly_rentals_df

def create_monthly_rentals_df(hour_df):
    monthly_rentals_df = hour_df.resample(rule='M', on='dateday').agg({
        "casual": "sum",
        "registered": "sum",
        "count": "sum"
    })
    monthly_rentals_df.index = monthly_rentals_df.index.strftime('%b-%y')
    monthly_rentals_df = monthly_rentals_df.reset_index()
    monthly_rentals_df.rename(columns={
        "dateday": "yearmonth",
        "count": "total_rental_bike",
        "casual": "casual_rider",
        "registered": "registered_rider"
    }, inplace=True)
    return monthly_rentals_df

def create_daily_rentals_df(hour_df):
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_rentals_df = hour_df.groupby(['weekday'])['count'].sum().reindex(weekday_order).reset_index()
    return daily_rentals_df

def create_hourly_rentals_df(hour_df):
    hourly_rentals_df = hour_df.groupby(by='hour')['count'].sum().reset_index()
    return hourly_rentals_df

def create_weatherly_rentals_df(hour_df):
    weatherly_rentals_df = hour_df.groupby('weather').agg({
        'casual': 'sum',
        'registered': 'sum',
        'count': 'sum'
    }).reset_index()
    weatherly_rentals_df = pd.melt(weatherly_rentals_df,
                                      id_vars=['weather'],
                                      value_vars=['casual', 'registered'],
                                      var_name='type_of_riders',
                                      value_name='count_riders')
    
    weatherly_rentals_df['wheater'] = pd.Categorical(weatherly_rentals_df['weather'],
                                             categories=['Clear/Party Cloudy', 'Misty/Cloudy', 'light Snow/Rain', 'Severe Weather'])
    
    weatherly_rentals_df = weatherly_rentals_df.sort_values('weather')
    return weatherly_rentals_df

def create_seasonly_rentals_df(hour_df):
    seasonly_rentals_df = hour_df.groupby('season').agg({
    'casual': 'sum',
    'registered': 'sum',
    'count': 'sum'
    }).reset_index()
    seasonly_rentals_df = pd.melt(seasonly_rentals_df,
                                      id_vars=['season'],
                                      value_vars=['casual', 'registered'],
                                      var_name='type_of_riders',
                                      value_name='count_riders')
    
    seasonly_rentals_df['season'] = pd.Categorical(seasonly_rentals_df['season'],
                                             categories=['Spring', 'Summer', 'Fall', 'Winter'])
    
    seasonly_rentals_df = seasonly_rentals_df.sort_values('season')
    
    return seasonly_rentals_df

# Load cleaned Data
hour_df = pd.read_csv('hour_df.csv')

# Convert 'dateday' column to datetime type
hour_df['dateday'] = pd.to_datetime(hour_df['dateday'])

# Filter data
min_date = hour_df["dateday"].min().date()  # Extract date from datetime
max_date = hour_df["dateday"].max().date()  # Extract date from datetime


with st.sidebar:
    # add capital bikeshare logo
    st.image("https://github.com/faizaallailyy/picture2/blob/main/3f1c98f07bf8d4713d03725e555f79f7.jpg?raw=true")

    st.sidebar.header("Filter:")

    # retrieve start_date & end_date from date_input
    start_date, end_date = st.date_input(
        label="Date Filter", min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = hour_df[
    (hour_df["dateday"] >= str(start_date)) &
    (hour_df["dateday"] <= str(end_date))
]

# setting up various dataframes
yearly_rentals_df = create_yearly_rentals_df(hour_df)
monthly_rentals_df = create_monthly_rentals_df(hour_df)
daily_rentals_df = create_daily_rentals_df(hour_df)
hourly_rentals_df = create_hourly_rentals_df(hour_df)
weatherly_rentals_df = create_weatherly_rentals_df(hour_df)
seasonly_rentals_df = create_seasonly_rentals_df(hour_df)


st.header('Bike Sharing Dashboard')
st.markdown("##")

col1, col2, col3 = st.columns(3)

with col1:
    total_all_rentals_bikes = main_df['count'].sum()
    st.metric("Total All Rental Bikes", value=total_all_rentals_bikes)
with col2:
    total_rented_bike_casual = main_df['casual'].sum()
    st.metric("Total Rented Bike by Casual Rider", value=total_rented_bike_casual)
with col3:
    total_rented_bike_registered = main_df['registered'].sum()
    st.metric("Total Rented Bike by Registered Rider", value=total_rented_bike_registered)

st.markdown("---")

fig = px.pie(yearly_rentals_df,
             values='count',
             names='year',
             color='year', 
             title="Total Rentals per Year",
             hole=0.5,
             width=400, 
             height=400) 
# st.plotly_chart(fig, use_container_width=True)

total_casual_users = hour_df['casual'].sum()
total_registered_users = hour_df['registered'].sum()

donut_data = pd.DataFrame({
    'user_type': ['Casual Users', 'Registered Users'],
    'count': [total_casual_users, total_registered_users]
})

fig1 = px.pie(donut_data, values='count', 
             names='user_type', 
             title='Comparison of Casual and Registered Riders', 
             hole=0.5,
             width=400, 
             height=400)
# st.plotly_chart(fig1)

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig, use_container_width=True)
right_column.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(monthly_rentals_df,
              x='yearmonth',
              y=['casual_rider', 'registered_rider', 'total_rental_bike'],
              color_discrete_sequence=["skyblue", "navy", "orange"],
              markers=True,
              title="Monthly Count of Rental Bikes")

# Update layout
fig2.update_layout(xaxis_title='', yaxis_title='Total Rental Bikes', xaxis_tickangle=45)

# Display plot
st.plotly_chart(fig2, use_container_width=True)

fig3 = px.line(daily_rentals_df, 
               x='weekday', 
               y='count', 
               markers=True, 
               title='Total Rental Bikes per Day').update_layout(xaxis_title='Weekday', yaxis_title='Total Rental Bikes')

# Display plot
st.plotly_chart(fig3)

fig4 = px.bar(hourly_rentals_df, x='hour', y='count', title='Total Rental Bikes per Hour')
fig4.update_xaxes(title='Hour', tickmode='linear')
fig4.update_yaxes(title='Total Rental Bikes')

# Display plot
st.plotly_chart(fig4)

fig5 = px.bar(weatherly_rentals_df,
              x='weather',
              y=['count_riders'],
              color='type_of_riders',
              color_discrete_sequence=["navy", "skyblue", "red"],
              title='Count of Rental Bikes by Weather and Rider Type').update_layout(xaxis_title='', yaxis_title='Total Rental Bikes')

#st.plotly_chart(fig5, use_container_width=True)

fig6 = px.bar(seasonly_rentals_df,
              x='season',
              y=['count_riders'],
              color='type_of_riders',
              color_discrete_sequence=["navy", "skyblue", "red"],
              title='Count of Rental Bikes by Season and Rider Type').update_layout(xaxis_title='', yaxis_title='Total Rental Bikes')

#st.plotly_chart(fig6, use_container_width=True)

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig5, use_container_width=True)
right_column.plotly_chart(fig6, use_container_width=True)
