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
    
    Many cities invite residents to suggest ideas for how public money should be spent in their neighbourhoods. This process is called [*participatory budgeting*](https://en.wikipedia.org/wiki/Participatory_budgeting) (PB). Citizen proposals often provide valuable insights into local challenges and community priorities.  

    However, when a large number of proposals are submitted, it can be difficult to understand common themes, trends, or differences between areas. In major case cities like Barcelona, Helsinki, New York, Paris, and Seoul, hundreds to thousands of proposals are submitted in each round, making it especially challenging to analyse and respond to citizen input effectively.
    
    This dashboard shows how two public datasets, citizen proposals and district-level statistics, can be combined to make sense of this information. Using the [OmaStadi PB programme](https://omastadi.hel.fi/) in Helsinki as an example, the dashboard helps identify local needs and connects proposals to the specific characteristics of each area. The goal is to support more informed and equitable decision-making throughout the participatory process.

    The source code for this dashboard is available at: [https://github.com/bokyong-shin/mapping_citizen_voices](https://github.com/bokyong-shin/mapping_citizen_voices)
    
    **Lastest update:** 7 Jul, 2025.
    """
)

st.markdown(
    """
    #### Dashboard Structure  

    This dashboard is organised into three pages (left sidebar), each corresponding to a specific research question (RQ):  
    - 🏙️ **RQ1:** What are the socio-economic and demographic characteristics of Helsinki’s districts?  
    - 📄 **RQ2:** What are the consistent thematic topics in citizen proposals across three rounds of OmaStadi PB?  
    - 🔗 **RQ3:** How are district characteristics related to the thematic focus of citizen proposals?  
    """
)

st.markdown(
    """
    #### Data Sources  

    This dashboard is built on two key datasets collected through API calls:  
    - **District-level statistical data** from [Helsinki Map Service](https://kartta.hel.fi) and [Helsinki Region Infoshare (HRI)](https://hri.fi/en_gb/), retrieved on 10 March 2025  
    - **Citizen proposals** submitted to [OmaStadi PB](https://omastadi.hel.fi/) during the first three rounds (2018–2024)
    """
)