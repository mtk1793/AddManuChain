import streamlit as st
import pandas as pd

def data_table(df, use_container_width=True):
    '''Enhanced data display component'''
    return st.dataframe(df, use_container_width=use_container_width)

