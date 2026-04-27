import streamlit as st
import numpy as np
import pandas as pd

# Load the "DNA" you saved
dna_vector = np.load('target_taste_vector.npy')
candidates = pd.read_csv('discovery_pool.csv')

st.title("My Musical DNA Explorer")

# Add a slider to filter by the 'refined_match' you already calculated
threshold = st.slider("Match Confidence", 0.0, 1.0, 0.4)
filtered_gems = candidates[candidates['refined_match'] >= threshold]

st.dataframe(filtered_gems[['name', 'refined_match', 'popularity']])