import streamlit as st 
import plotly.express as px 
 
def show_charts(df): 
 
    pie = px.pie(df, names='Category', values='Amount') 
    st.plotly_chart(pie) 
 
    bar = px.bar(df, x='Category', y='Amount') 
    st.plotly_chart(bar) 
 
    line = px.line(df, y='Amount') 
    st.plotly_chart(line)
