import pandas as pd
import pickle
import streamlit as st

@st.cache_data
def load_data():
    return pd.read_csv("data/cleaned_data.csv")

@st.cache_resource
def load_similarity():
    with open("model/cosine_similarity.pkl", "rb") as f:
        return pickle.load(f)