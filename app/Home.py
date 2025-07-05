import streamlit as st

st.set_page_config(layout="wide", page_title="Mapping Citizen Voices", page_icon="🗺️")

sidebar_markdown = """
This dashboard provides data-driven insights into participatory budgeting in Helsinki, showing how citizen proposals reflect spatial inequalities and thematic priorities.
"""

st.sidebar.title("About")
st.sidebar.info(sidebar_markdown)

st.title("🗺️ Mapping Citizen Voices")
st.subheader("Transforming Participatory Budgeting with Combined Data Streams in Helsinki")
st.write("")
st.markdown(
    """
    #### Purpose  

    Citizens’ proposals submitted to participatory budgeting (PB) contain valuable insights into local problems and community-led solutions.  
    However, when large volumes of proposals are submitted, it becomes difficult to interpret their themes, trends, and spatial patterns.

    This dashboard demonstrates how two publicly available datasets, citizen proposals and district-level statistics, can be combined to turn raw data into meaningful knowledge. Using [OmaStadi PB](https://omastadi.hel.fi/) as a case, this dashboard aims to support a systematic understanding of local needs and helps connect proposals to area-specific characteristics to enable more informed and equitable deliberation throughout the PB process.

    The source code for this dashboard is available at: [https://github.com/bokyong-shin/mapping_citizen_voices](https://github.com/bokyong-shin/mapping_citizen_voices)
    """
)

st.markdown(
    """
    #### Dashboard Structure  

    This dashboard is organised into three pages (left sidebar), each corresponding to a specific research question:  
    - 🏙️ **RQ1:** What are the socio-economic and demographic characteristics of Helsinki’s districts and major districts?  
    - 📄 **RQ2:** What are the consistent thematic topics in citizen proposals across three rounds of OmaStadi PB?  
    - 🔗 **RQ3:** How are district characteristics related to the thematic focus of citizen proposals?  

    Each page allows users to explore the data visually and interactively, reflecting the key findings discussed in the paper.
    """
)

st.markdown(
    """
    #### Data Sources  

    This dashboard is built on two key datasets collected through API calls:  
    - **District-level statistical data** from [Helsinki Map Service](https://kartta.hel.fi) and [Helsinki Region Infoshare (HRI)](https://hri.fi/en_gb/), retrieved on 10 March 2025  
    - **Citizen proposals** submitted to [OmaStadi PB](https://omastadi.hel.fi/) during the first three rounds (2018–2024)
    
    **Note:** This dashboard supports a demonstration of the data analysis and visualisation techniques used in the paper "Mapping Citizen Voices: Transforming Participatory Budgeting with Combined Data Streams in Helsinki". A more comprehensive analysis of the data, including methods and detailed descriptions, can be found in the paper once it is published.
    """
)