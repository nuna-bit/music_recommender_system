import streamlit as st
import numpy as np
import pandas as pd

# load the data
dna_vector = np.load('target_taste_vector.npy')
candidates = pd.read_csv('discovery_pool.csv')

st.title("🎵 My Musical DNA Explorer")

# sidebars/sliders
st.sidebar.header("Discovery Filters")
threshold = st.sidebar.slider("Match Confidence", 0.0, 1.0, 0.4)
max_pop = st.sidebar.slider("Max Popularity (Hidden Gem Filter)", 0, 100, 50)

# filtering the data
filtered_gems = candidates[
    (candidates['refined_match'] >= threshold) & 
    (candidates['popularity'] <= max_pop)
].sort_values(by='refined_match', ascending=False)

# displaying the results
if not filtered_gems.empty:
    # success message and big metric card
    st.success(f"Found {len(filtered_gems)} matches for your current settings!")
    
    col1, col2 = st.columns(2)
    with col1:
        top_name = filtered_gems.iloc[0]['name']
        st.metric("Top Recommendation", top_name)
    with col2:
        top_score = filtered_gems.iloc[0]['refined_match']
        st.metric("Match Score", f"{top_score:.2f}")

    # actual table
    st.write("### Recommended Artists")
    st.dataframe(filtered_gems[['name', 'refined_match', 'popularity']])
else:
    # warning message if the sliders are too strict
    st.warning("No artists match this high of a confidence level. Try lowering the sliders!")

