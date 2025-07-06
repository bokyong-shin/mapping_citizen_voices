# Import libraries
import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import plotly.graph_objects as go
import streamlit_highcharts as hc
import gensim
from sklearn.model_selection import train_test_split
import spacy
nlp = spacy.load("fi_core_news_sm")

import random
import matplotlib.pyplot as plt
import re

# Load data at the start to avoid reloading on every interaction
@st.cache_data
def load_data():
    pro_merged = pd.read_csv('app/data/pro_merged.csv')
    sample_proposals = pd.read_csv('app/data/sample_proposals.csv')
    topic_numbers = pd.read_csv('app/data/topic_numbers.csv')
    lda_model = gensim.models.ldamodel.LdaModel.load("app/data/lda_model.model")
    dictionary = gensim.corpora.Dictionary.load("app/data/lda_dictionary.dict")
    propsals_by_round_district = pd.read_csv('app/data/proposals_by_round_district.csv')
    top_proposals = pd.read_csv('app/data/top_proposals_per_topic.csv')
    district_topic_data = pd.read_csv("app/data/district_topic_proportions.csv")
    return pro_merged, sample_proposals, topic_numbers, lda_model, dictionary, propsals_by_round_district, top_proposals, district_topic_data

@st.cache_data
def get_sampled_df(pro_merged):
    sampled_df = pro_merged.dropna(subset=['latitude', 'longitude'])
    sampled_df, _ = train_test_split(sampled_df, test_size=1 - (100 / len(sampled_df)), stratify=sampled_df['selected'], random_state=42)
    return sampled_df

def display_map(pro_merged):
    st.subheader('2. Proposals on a Map')
    st.write("""
             When a proposal is submitted, a proposer can mark the location of the proposal on a map, a crucial information for understanding the association between the proposal content and its geographical context.
             Let's explore the red and green markers on the map, which represent the proposals that were not selected and selected, respectively.
             """)
    sampled_df = get_sampled_df(pro_merged)

    m = folium.Map(location=[60.1699, 24.9384], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in sampled_df.iterrows():
        icon_color = 'green' if row['selected'] == 'Selected' else 'red'
        icon = folium.Icon(color=icon_color, icon='ok-sign' if row['selected'] == 'Selected' else 'remove-sign')
        
        popup_content = (
            f"<b>Title:</b> {row['title']}<br>"
            f"<b>Round:</b> {row['round']}<br>"
            f"<b>Versions Count:</b> {row['versionsCount']}<br>"
            f"<b>Total Comments:</b> {row['total_comments_count']}<br>"
            f"<b>District:</b> {row['district']}"
        )
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_content, max_width=250),
            icon=icon
        ).add_to(marker_cluster)

    legend_html = '''
         <div style="position: fixed; 
                     bottom: 25px; left: 25px; width: 150px; height: 90px; 
                     background-color: white; border:2px solid grey; z-index:9999; font-size:14px;">
         &nbsp;<b>Vote result</b><br>
         &nbsp;<i class="fa fa-map-marker fa-2x" style="color:green"></i>&nbsp;Selected<br>
         &nbsp;<i class="fa fa-map-marker fa-2x" style="color:red"></i>&nbsp;Not Selected
         </div>
         '''
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=1000, height=600)
    
def display_random_sample(sample_proposals):
    st.subheader("1. What is a 'proposal'?")
    st.markdown("""
        **Citizen Proposal**: A document presenting an idea or plan others can review and decide upon, usually in a structured, written format.            
    """)

    if 'sampled_proposal' not in st.session_state:
        st.session_state.sampled_proposal = None

    if st.button('Get a Random Sample'):
        random_index = random.randint(0, len(sample_proposals) - 1)
        st.session_state.sampled_proposal = sample_proposals.iloc[random_index]

    if st.session_state.sampled_proposal is not None:
        sampled_proposal = st.session_state.sampled_proposal
        st.write(f"**Title:** {sampled_proposal['title']}")
        st.write(f"**Text:** {sampled_proposal['texts']}")
        st.write(f"**Round:** {sampled_proposal['round']}")
        st.write(f"**District:** {sampled_proposal['district']}")
    
def display_coh_per(topic_data):
    st.subheader('3.1 Coherence and Perplexity Scores (10 iterations per topic number)')
    topic_grouped = topic_data.groupby('topic').agg({
        'coherence': ['mean', list],
        'perplexity': ['mean', list]
    }).reset_index()
    topics = topic_grouped['topic'].tolist()
    coherence_means = topic_grouped['coherence']['mean'].tolist()
    perplexity_means = topic_grouped['perplexity']['mean'].tolist()
    coherence_points = topic_grouped['coherence']['list'].tolist()
    perplexity_points = topic_grouped['perplexity']['list'].tolist()
    x = np.array(topics) 
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.25), dpi=600)  
    ax1 = axes[0]
    for i, scores in enumerate(coherence_points):
        ax1.scatter([topics[i]] * len(scores), scores, color='blue', alpha=0.3, label='Coherence (points)' if i == 0 else "")
    ax1.plot(x, coherence_means, color='blue', label='Mean Coherence', linewidth=2)
    ax1.set_xlabel("Num Topics")
    ax1.set_ylabel("Coherence Score")
    ax1.set_title("Coherence Score by Number of Topics")
    ax1.legend()
    ax1.set_xticks(x.astype(int))
    ax2 = axes[1]
    for i, scores in enumerate(perplexity_points):
        ax2.scatter([topics[i]] * len(scores), scores, color='red', alpha=0.3, label='Perplexity (points)' if i == 0 else "")
    ax2.plot(x, perplexity_means, color='red', label='Mean Perplexity', linewidth=2)
    ax2.set_xlabel("Num Topics")
    ax2.set_ylabel("Perplexity (lower is better)")
    ax2.set_title("Perplexity by Number of Topics")
    ax2.legend()
    ax2.set_xticks(x.astype(int))
    plt.tight_layout()
    st.pyplot(fig)

topic_summaries = {
    0: {
        "title": "Topic 1: Enhancing Parks with Playgrounds and Recreational Amenities",
        "description": "This topic focuses on improving and using (käyttö, 0.012) parks (puisto, 0.032) by adding essential amenities such as benches (penkki, 0.011), playgrounds (leikkipaikka, 0.008), and outdoor gyms (ulkokuntosali, 0.006). Proposals aim to create new (uusi, 0.011) and upgraded spaces that cater to children (lapsi, 0.010) and residents (asukas, 0.006). Enhancements include building better connections (yhteys, 0.006) between facilities and ensuring inclusive, accessible environments that promote active recreation and community well-being."
    },
    1: {
        "title": "Topic 2: Expanding Waterfront Access and Recreation",
        "description": "This topic highlights efforts to improve access (päästä, 0.008) to coastal areas (ranta, 0.010) and the sea (meri, 0.008), with proposals focusing on facilities like piers (laituri, 0.010) and saunas (sauna, 0.007). Initiatives aim to create spaces that connect residents (asukas, 0.007) to Helsinki’s (Helsinki, 0.006) waterfront environment and promote infrastructure that enables relaxation, recreation, and accessibility. The emphasis is on building (rakentaa, 0.007) and maintaining (tehdä, 0.006) community-friendly amenities that enhance the overall experience for both residents and visitors."
    },
    2: {
        "title": "Topic 3: Developing Inclusive Public Spaces and Services",
        "description": "This topic focuses on fostering civic engagement and creating inclusive services in Helsinki (Helsinki, 0.036). Proposals emphasise the importance of spaces (tila, 0.009) that bring people together and support diverse activities. Key ideas include promoting opportunities (mahdollisuus, 0.007) for all residents (kaikki, 0.011), enhancing public resources like libraries (kirjasto, 0.007), and encouraging sustainability efforts. The initiatives aim to empower diverse communities, enhance social interaction, and build a more connected and resilient urban environment."
    },
    3: {
        "title": "Topic 4: Improving Infrastructure for Accessibility and Safety",
        "description": "This topic focuses on improving infrastructure to enhance accessibility (liikenne, 0.008) and safety (turvallisuus, 0.008) while fostering community interaction (yhteisöllisyys, 0.007). Proposals address traffic flow (risteys, 0.008), pedestrian safety (suojatie, 0.008), and enhancing public spaces with practical amenities like benches (penkki, 0.009). These initiatives aim to create safer, more accessible environments that support both functionality and community engagement."
    },
    4: {
        "title": "Topic 5: Enhancing Pathways and Park Connectivity",
        "description": "This topic centres on upgrading pathways and park surroundings (puisto, 0.021), with an emphasis on better lighting (valaistus, 0.008), adding benches, and maintaining walkways. Proposals focus on making parks safer and more accessible for various uses, such as dog walking (koirapuisto, 0.007), commuting, and leisure. Key suggestions include clearing overgrowth, enhancing lighting, and creating pedestrian-friendly features that allow people to move safely (tulla, 0.007) and enjoy their surroundings (saada, 0.007)."
    },
    5: {
        "title": "Topic 6: Community Events and Participatory Programmes",
        "description": "This topic emphasises the creation of spaces (tila, 0.017) and events (tapahtuma, 0.017) that bring residents (asukas, 0.013) together through diverse activities (toiminta, 0.011). Proposals aim to organise (järjestää, 0.011) initiatives that address the needs of different (eri, 0.011) groups and provide shared (yhteinen, 0.010) and inclusive places (paikka, 0.010) for all (kaikki, 0.010)."
    },
    6: {
        "title": "Topic 7: Developing Spaces for Children and Youth",
        "description": "This topic emphasises the development of spaces (tila, 0.008) for children (lapsi, 0.031) and youth (nuori, 0.022), focusing on enhancing schools (koulu, 0.017), fields (kenttä, 0.014), and playgrounds (leikkipuisto, 0.008). Proposals aim to improve schoolyards (piha, 0.010) and other areas to ensure better use (käyttö, 0.009) and accessibility. Initiatives address the needs (tarvita, 0.007) of diverse groups, creating vibrant places (paikka, 0.006) that encourage activity, safety, and community interaction."
    }
}

def plot_topic_words_highcharts(lda_model, topic_num, topic_title):
    topic = lda_model.show_topic(topic_num, 15)
    categories = [word for word, prob in topic]
    values = [float(prob) for word, prob in topic]
    sorted_data = sorted(zip(categories, values), key=lambda x: x[1], reverse=True)
    categories, values = zip(*sorted_data)

    chart_title = f'Top 15 Words for Topic {topic_num + 1}'
    
    chart_options = {
        'chart': {'type': 'bar'},
        'title': {'text': chart_title},
        'xAxis': {'categories': categories, 'title': {'text': 'Words'}},
        'yAxis': {'title': {'text': None}, 'min': 0},
        'series': [{
            'name': f'Topic {topic_num + 1}',
            'data': list(values),
            'color': 'green'
        }]
    }
    hc.streamlit_highcharts(chart_options, height=500)

def display_topics(lda_model, topic_summaries, top_proposals):
    col1, col2 = st.columns(2)
    topic_num = col1.slider("Select Topic", 1, lda_model.num_topics, 1) - 1 
    topic_title = topic_summaries[topic_num]["title"]
    selected_topic = topic_summaries[topic_num]
    with col1:
        plot_topic_words_highcharts(lda_model, topic_num, topic_title)
    with col2:
        col2.subheader(selected_topic["title"])
        col2.write(selected_topic["description"])
        filtered_proposals = top_proposals[top_proposals['topic'] == topic_num + 1] 

        if not filtered_proposals.empty:
            top_proposals = filtered_proposals.iloc[5:7]  
            col2.markdown(f"#### Representative Proposals:")
            
            for i, proposal in top_proposals.iterrows():
                col2.write(f"**Title**: {proposal['title']}")
                col2.write(f"**Text**: {proposal['text']}")
                col2.write(f"**Probability**: {proposal['probability']:.3f}")
                col2.write("---")  
        else:
            col2.markdown(f"### No proposals available for {selected_topic['title']}")

def plot_topic_distribution(proposals_by_round_district, topic_summaries):
    """
    Plot a bar chart to show the distribution of topics across all proposals, 
    sorted by values and labeled with the topic titles.
    """
    st.subheader("3.3. Popular Topics")
    st.markdown("""
                The most frequent topics include enhancing pathways and park connectivity (Topic 5), developing spaces for children and youth (Topic 7), and creating inclusive public spaces and services (Topic 3).   
                These top-ranked themes suggest that residents prioritise the improvement and everyday use of public spaces across neighbourhoods.
                """
    )

    topic_columns = [f"Topic_{i}" for i in range(7)]  
    topic_distribution = proposals_by_round_district[topic_columns].sum()
    topic_distribution_normalized = topic_distribution / topic_distribution.sum()
    topic_titles = [topic_summaries[i]['title'] for i in range(7)]
    topics_sorted = sorted(zip(topic_titles, topic_distribution_normalized), key=lambda x: x[1], reverse=True)
    categories, values = zip(*topics_sorted)

    chart_options = {
        'chart': {'type': 'bar'},
        'title': {'text': 'Topic Distribution in Citizen Proposals'},
        'xAxis': {
            'categories': list(categories),
            'title': {'text': None}
        },
        'yAxis': {
            'min': 0,
            'title': {'text': None},
            'labels': {'overflow': 'justify'}
        },
        'series': [{
            'name': 'Proportion',
            'data': list(values),
            'color': 'blue'
        }]
    }
    hc.streamlit_highcharts(chart_options)
    
def prepare_heatmap_data(df):
    """
    Prepare the data for a heatmap where districts are on the y-axis
    and topics are on the x-axis.
    """
    topic_columns = [f"Topic_{i}" for i in range(7)]  
    heatmap_data = df.groupby('district')[topic_columns].mean().reset_index()

    heatmap_data.fillna(0, inplace=True)

    return heatmap_data

district_order = [
    "Pitäjänmäki", "Munkkiniemi", "Kaarela", "Haaga", "Reijola",  # Western
    "Lauttasaari", "Ullanlinna", "Kampinmalmi", "Taka-Töölö", "Vironniemi",  # Southern
    "Tuomarinkylä", "Länsi-Pakila", "Itä-Pakila", "Maunula", "Oulunkylä",  # Northern
    "Vanhakaupunki", "Pasila", "Alppiharju", "Kallio", "Vallila", # Central
    "Kulosaari", "Laajasalo", "Herttoniemi",   # Southeastern
    "Latokartano", "Pukinmäki", "Malmi", "Suutarila", "Puistola", "Jakomäki",  # Northeastern
    "Mellunkylä", "Myllypuro", "Vartiokylä", "Vuosaari",  # Eastern
    "Östersundom"  # Östersundom
]

def create_heatmap(df, topic_summaries, district_order):
    st.subheader("3.4 Heatmap of Topic Distribution by District")
    st.markdown("""
                The heatmap shows spatial variation in topic emphasis, with districts generally ordered from west to east. 
                While western districts tend to prioritise park connectivity, some northern areas (e.g., Itä-Pakila and Puistola) show stronger interest in youth-oriented spaces. If you check the proportion of youth in the RQ1 page, the northern part especially shows the highest levels. 
                Although clear west–east patterns are not consistent, several districts display distinctive priorities shaped by local needs and contexts.
                """
    )
    heatmap_data = prepare_heatmap_data(df)
    topic_titles = [topic_summaries[i]["title"] for i in range(7)]  
    heatmap_data = heatmap_data.set_index('district').reindex(district_order).reset_index()
    districts = heatmap_data['district'].tolist()
    data_matrix = []
    for topic_idx, topic in enumerate(topic_titles):
        for district_idx, district in enumerate(districts):
            data_matrix.append([district_idx, topic_idx, heatmap_data.iloc[district_idx, topic_idx + 1]])

    chart_options = {
        'chart': {
            'type': 'heatmap',
            'plotBorderWidth': 1,
            'height': 800 
        },
        'title': {'text': 'Topic Distribution by District'},
        'xAxis': {
            'categories': districts,  
            'title': {'text': 'Districts'},
            'labels': {
                'rotation': 45  
            }
        },
        'yAxis': {
            'categories': topic_titles,  
            'title': {'text': 'Topics'},
            'reversed': True
        },
        'colorAxis': {
            'min': 0,
            'minColor': '#FFFFFF',
            'maxColor': '#FF0000'  
        },
        'legend': {
            'align': 'right',
            'layout': 'vertical',
            'margin': 0,
            'verticalAlign': 'top',
            'y': 25,
            'symbolHeight': 280
        },
        'series': [{
            'name': 'Proportion of Topic in District',
            'borderWidth': 1,
            'data': data_matrix, 
            'dataLabels': {
                'enabled': True,
                'format': '{point.value:.2f}'
            }
        }],
        'tooltip': {
            'formatter': 'function() { return "<b>Topic: </b>" + this.series.yAxis.categories[this.point.y] + "<br><b>District: </b>" + this.series.xAxis.categories[this.point.x] + "<br><b>Proportion: </b>" + this.point.value.toFixed(4); }'
        }
    }
    hc.streamlit_highcharts(chart_options, height=800)

major_district_mapping = {
    "Pitäjänmäki": "Western", "Munkkiniemi": "Western", "Kaarela": "Western", "Haaga": "Western", "Reijola": "Western",
    "Lauttasaari": "Southern", "Ullanlinna": "Southern", "Kampinmalmi": "Southern", "Taka-Töölö": "Southern", "Vironniemi": "Southern",
    "Tuomarinkylä": "Northern", "Länsi-Pakila": "Northern", "Itä-Pakila": "Northern", "Maunula": "Northern", "Oulunkylä": "Northern",
    "Vanhakaupunki": "Central", "Pasila": "Central", "Alppiharju": "Central", "Kallio": "Central", "Vallila": "Central",
    "Kulosaari": "Southeastern", "Laajasalo": "Southeastern", "Herttoniemi": "Southeastern",
    "Latokartano": "Northeastern", "Pukinmäki": "Northeastern", "Malmi": "Northeastern", "Suutarila": "Northeastern", "Puistola": "Northeastern", "Jakomäki": "Northeastern",
    "Mellunkylä": "Eastern", "Myllypuro": "Eastern", "Vartiokylä": "Eastern", "Vuosaari": "Eastern",
    "Östersundom": "Östersundom"
}
    

combined_stopwords = set(spacy.lang.fi.stop_words.STOP_WORDS)

def preprocess(text):
    text = text.lower()
    text = re.sub(r',([^ ])', r', \1', text)
    text = re.sub(r'http\S+|www.\S+', '', text)
    text = re.sub(r'<[A-Za-z]+>', '', text)
    text = re.sub(r'[<>@#%&]', '', text)  
    text = re.sub(r'&[a-z]+;', '', text)  
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_punct and token.lemma_.lower() not in combined_stopwords]
    
    return tokens

def predict_topics(unseen_text, dictionary, lda_model, topic_summaries):
    unseen_tokenized_text = preprocess(unseen_text)
    unseen_bow = dictionary.doc2bow(unseen_tokenized_text)
    topic_distribution = lda_model.get_document_topics(unseen_bow, minimum_probability=0.0)
    
    bubble_chart_data = []
    for topic_id, proportion in topic_distribution:
        bubble_chart_data.append({
            "z": proportion * 100,  
            "name": topic_summaries[topic_id]["title"] 
        })
    return bubble_chart_data

def display_bar_chart(tree_map_data):
    sorted_data = sorted(tree_map_data, key=lambda x: x["z"], reverse=True)
    categories = [entry["name"] for entry in sorted_data]  
    data = [entry["z"] for entry in sorted_data]  
    colour_palette = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", 
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
    ]
    colours = colour_palette[:len(categories)]  
    chart_options = {
        "chart": {
            "type": "bar",
            "height": 500,
        },
        "title": {
            "text": "Predicted Topic Proportions"
        },
        "xAxis": {
            "categories": categories,
            "title": {"text": "Topics"},
            "labels": {
                "style": {"fontSize": "12px"}
            },
        },
        "yAxis": {
            "min": 0,
            "title": {"text": "Proportion (%)"},
            "labels": {"format": "{value}%"}
        },
        "series": [
            {
                "name": "Proportion",
                "data": [{"y": value, "color": colours[i]} for i, value in enumerate(data)],
            }
        ],
        "legend": {"enabled": False},
        "tooltip": {
            "pointFormat": "<b>{point.category}</b>: {point.y:.2f}%"
        },
        "plotOptions": {
            "bar": {
                "dataLabels": {
                    "enabled": True,
                    "format": "{y:.2f}%"  
                }
            }
        },
        "credits": {"enabled": False},  
    }
    hc.streamlit_highcharts(chart_options, height=600)

def display_topic_trends(district_topic_data, topic_colors=None):
    st.subheader("3.5 Topic Trends Over Time by District")

    if topic_colors is None:
        topic_colors = {
            "Topic_1_Enhancing_Parks_with_Playgrounds_and_Recreational_Amenities": "#1f77b4",
            "Topic_2_Expanding_Waterfront_Access_and_Recreation": "#ff7f0e",
            "Topic_3_Building_Inclusive_Community_Services_and_Engagement": "#2ca02c",
            "Topic_4_Improving_Infrastructure_for_Accessibility_and_Safety": "#d62728",
            "Topic_5_Enhancing_Pathways_and_Park_Connectivity": "#9467bd",
            "Topic_6_Creating_Community_Spaces_for_Collective_Events_and_Activities": "#8c564b",
            "Topic_7_Developing_Spaces_for_Children_and_Youth": "#e377c2"
        }
    district_options = district_topic_data['district'].unique()
    selected_district = st.selectbox("Select a District", district_options)
    district_data = district_topic_data[district_topic_data['district'] == selected_district]
    district_data_melted = district_data.melt(id_vars=['district', 'year'], 
                                                value_vars=[f"Topic_{i}" for i in range(7)],
                                                var_name='topic', value_name='proportion')
    district_data_melted['color'] = district_data_melted['topic'].map(topic_colors)
    fig = go.Figure()

    for topic in district_data_melted['topic'].unique():
        topic_data = district_data_melted[district_data_melted['topic'] == topic]
        fig.add_trace(go.Scatter(x=topic_data['year'], 
                                  y=topic_data['proportion'], 
                                  mode='lines+markers',
                                  name=topic,
                                  line=dict(color=topic_data['color'].iloc[0], width=2),
                                  marker=dict(size=6)))

    fig.update_layout(title=f"Topic Trends in Proposals for {selected_district}",
                      xaxis_title="Year",
                      yaxis_title="Proportion",
                      legend_title="Topics",
                      template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

def main():
    APP_TITLE = "RQ2: What are the consistent thematic topics in citizen proposals across three rounds of OmaStadi PB?"
    if "page_config_set" not in st.session_state:
        st.set_page_config(APP_TITLE, layout='wide')
        st.session_state.page_config_set = True
    st.title(APP_TITLE)
    st.markdown("""
        This page provides an in-depth analysis citizen ideas submitted to [OmaStadi participatory budgeting](https://omastadi.hel.fi/) in Helsinki.
        It explores how these ideas go through the whole cycle of PB, and offers insights into key themes through topic modeling.
    """)
    st.write("")
    pro_merged, sample_proposals, topic_numbers, lda_model, dictionary, proposals_by_round_district, top_proposals, district_topic_data = load_data()
    display_random_sample(sample_proposals)
    st.write("__")
    display_map(pro_merged)
    st.write("")
    st.markdown("""
        ### 3. Major themes (topics)
    """)
    st.markdown("""
        We now move on to applying the Latent Dirichlet Allocation (LDA) model to identify major topics from the citizen proposals.
    """)
    with st.expander("What is LDA?"):
        st.markdown("""
            LDA (Latent Dirichlet Allocation) is a generative probabilistic model that is used to discover topics in a collection of documents.  
            
            It assumes that each document is a mixture of topics, and each topic is characterised by a distribution over words. The model works by inferring the hidden topic structure from the observed words in the documents. Despite the recent advancements in neural topic models, LDA remains a popular choice for topic modeling due to its simplicity and interpretability, especially in the context of text data like citizen proposals.  
            
            For more information, you can refer to the original paper by Blei, Ng, and Jordan (2003):
            Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent dirichlet allocation. Journal of Machine Learning Research, 3(Jan), 993–1022.
        """)
    
    st.markdown("""
                Two metrics are used to define the optimal number of topics: 
                - Coherence Score: Coherence measures the interpretability and semantic consistency of topics by comparing word pair co-occurrences within the topics. Higher coherence scores suggest better and more meaningful topics.
                - Perplexity Score: Perplexity measures how well a probabilistic model predicts a sample. In the context of LDA, lower perplexity values indicate that the model has a better predictive power for unseen data.

                The following chart displays the coherence and perplexity scores for different numbers of topics in the LDA model. The goal is to select the number of topics that strikes a balance between a high coherence score and a low perplexity score, ensuring that the topics are both interpretable and predictive.
                As shown in the chart, the optimal number of topics is **7**, which has a high coherence score and a low perplexity score.
    """)
    
    display_coh_per(topic_numbers)
    st.subheader('3.2 Topic Summaries')
    st.markdown("""
        The citizen proposals submitted to the OmaStadi participatory budgeting programme reveal a blend of space-oriented and function-oriented priorities, closely tied to the daily urban activities of Helsinki’s residents. 
        Topics range from enhancing public spaces like sports parks, playgrounds, and green areas to addressing functional improvements such as traffic infrastructure, lighting for safety, and outdoor fitness facilities.    
        Notably, Topic 2 reflects a unique characteristic of the Helsinki case: it centres on waterfront-related proposals, which is primarily due to the city’s extensive coastline and strong public interest in improving access to and the usability of coastal areas.
        """)
    display_topics(lda_model, topic_summaries, top_proposals)
    plot_topic_distribution(proposals_by_round_district, topic_summaries)
    create_heatmap(proposals_by_round_district, topic_summaries, district_order)
    st.subheader('3.5 Predict Topics for New Proposals')
    st.write("""
        Once the model has been trained on historical data, it can be used to predict the topic distribution for new proposals submitted by citizens.
        Please note that the model is trained on Finnish-language proposals, so it only works with texts written in Finnish.
        
        For instance, try copy and paste a proposal text from this proposal about improving the Herttoniemi sports park (https://omastadi.hel.fi/processes/osbu-2019/f/171/proposals/124?):
        
        __________________________ Copy and paste the proposal text below __________________________
        
        Herttoniemen liikuntapuisto on häpeällisen huonossa kunnossa ja mahdollisuuksiinsa nähden aivan liian vähällä käytöllä. Perusparannus tulee aloittaa tekonurmen asentamisesta hiekkakentälle.
        - jalkapallo on Suomen suosituin harrastus ja lajin suosio kasvaa erityisesti tyttöjen keskuudessa.
        - uudella tekonurmella olisi potentiaalisesti tuhansia käyttäjiä.
        - alueella toimii paikallinen seura HerTo, ja metroaseman läheisyyden vuoksi kenttä palvelisi hyvin myös useita muita joukkueita.
        - aivan kentän viereen rakennetaan runsaasti uutta asumista.
        - Herttoniemen yhteiskoulussa toimii jalkapalloluokkia.
        - tekonurmi ei estä kentän jäädytttämistä luistelukäyttöön talvisin.
        - kumirouheen tilalle voi valita kierrätettävän Saltex Biofill luomu-täyteaineen.
        
        ___________________________ Copy and paste the proposal text above __________________________
        """)
    user_input = st.text_area(
        "Enter text (or multiple texts separated by new lines):",
        placeholder="Type your proposal here..."
    )
    if st.button("Predict Topics"):
        if len(user_input.strip()) < 100:
            st.warning("Please enter at least 100 characters for better prediction results.")
        else:
            st.write(f"**This is the input:** {user_input}")
            prediction_results = predict_topics(user_input, dictionary, lda_model, topic_summaries)
            display_bar_chart(prediction_results)

if __name__ == "__main__":
    main()