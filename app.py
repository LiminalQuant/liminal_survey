import streamlit as st
from utils.engine import render_form, render_dashboard

st.set_page_config(page_title="КДЦБ| Feedback", layout="centered")

survey_config = "configs/new_year_2025_config.json"
survey_id = "new_year_2025"

menu = st.sidebar.radio("Меню", ["Опрос", "Аналитика"])

if menu == "Опрос":
    render_form(survey_config)
else:
    render_dashboard(survey_id)
