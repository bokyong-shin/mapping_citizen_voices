import streamlit as st

st.set_page_config(layout="wide", page_title="Mapping Citizen Voices", page_icon="🗺️")

# Sidebar content
sidebar_markdown = """
This application supports the review process for the manuscript "Mapping Citizen Voices" submitted to Government Information Quarterly.

It presents data-driven insights into participatory budgeting in Helsinki, showcasing how citizen proposals reflect spatial inequalities and thematic priorities.
"""

st.sidebar.title("About")
st.sidebar.info(sidebar_markdown)

# Main page title and subheader
st.title("🗺️ Mapping Citizen Voices")
st.subheader(
    "Exploring citizen ideas in Helsinki’s OmaStadi participatory budgeting platform."
)

st.markdown(
    """
    #### Purpose  

    This dashboard provides an in-depth analysis of citizen ideas submitted to **OmaStadi**, Helsinki’s participatory budgeting platform.  
    It traces how proposals evolve through the PB cycle and connects spatial charateristics using **topic modelling** and **spatial analysis**.
    """
)

st.markdown(
    """
    #### Data Sources  

    This application is built on two key datasets:  
    - **District-level statistical data** retrieved from [Helsinki Map Service](https://kartta.hel.fi) and [Helsinki Region Infoshare (HRI)](https://hri.fi/en_gb/) as of **10 March 2025**.  
    - **Citizen proposals** submitted to [OmaStadi participatory budgeting](https://omastadi.hel.fi/) during the first three rounds (2018–2024).
    """
)

