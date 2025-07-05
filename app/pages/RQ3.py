# Import libraries
import streamlit as st
import pandas as pd
import re
import streamlit_highcharts as hc

# Set page configuration
st.set_page_config(page_title="🔗 RQ3: District Characteristics and Citizen Proposals", layout='wide')

# Load data at the start to avoid reloading on every interaction
@st.cache_data
def load_data():
    """
    Load datasets required for district-level analysis.
    """
    indexes = pd.read_csv('app/data/indexes.csv')  
    weighted_averages_cleaned = pd.read_csv('app/data/weighted_averages_cleaned.csv')  # Compressed district statistics (2018-2023)
    district_topic_data = pd.read_csv("app/data/district_topic_proportions.csv")
    
    return indexes, weighted_averages_cleaned, district_topic_data
indexes, weighted_averages_cleaned, district_topic_data = load_data()

district_list = sorted(weighted_averages_cleaned["Area"].unique())

### ---- 1. Time-Series Graph of Four Indices ---- ###
def plot_indices_time_series(indexes, selected_district):
    df = indexes[indexes["Area"] == selected_district]

    index_colors = {
        "Demographic Diversity Index": "blue",
        "Economic Prosperity Index": "green",
        "Socioeconomic Dependency Index": "red",
        "Public Service Accessibility Index": "orange"
    }
    series_data = []
    for index, color in index_colors.items():
        series_data.append({
            "name": index,
            "data": [[int(year), float(value)] for year, value in zip(df["Year"], df[index])],
            "color": color
        })

    options = {
        "chart": {"type": "spline"},
        "title": {"text": f"Four Indices Over Time: {selected_district}"},
        "xAxis": {"title": {"text": "Year"}, "categories": df["Year"].tolist()},
        "yAxis": {"title": {"text": "Index Value"}},
        "series": series_data,
        "legend": {"enabled": True}  
    }

    hc.streamlit_highcharts(options)

### ---- 2. Ranking of District-Level Statistics ---- ###
def plot_district_ranking(weighted_averages_cleaned, selected_district):
    """
    Plot a Highcharts bar chart ranking the selected district's statistics against all other districts.
    """
    df = weighted_averages_cleaned.set_index("Area")
    rankings = {
        column: (df[column].rank(ascending=False, method="min").loc[selected_district])
        for column in df.columns if column != "Area"
    }
    rankings_df = pd.DataFrame.from_dict(rankings, orient="index", columns=["Rank"]).reset_index()
    rankings_df = rankings_df.sort_values(by="Rank", ascending=True)
    categories = rankings_df["index"].tolist()
    data_values = rankings_df["Rank"].tolist()
    gradient_colors = [
        f"rgba(0, 0, 255, {0.2 + (0.8 * ((len(data_values) - i - 1) / len(data_values)))})"
        for i in range(len(data_values))
    ]
    options = {
        "chart": {"type": "bar", "height": 1000},  
        "title": {"text": f"District Ranking (2018-2023) for {selected_district}"},
        "xAxis": {
            "categories": categories,
            "title": {"text": "Statistic"},
            "labels": {
                "style": {
                    "fontSize": "15px",
                    "whiteSpace": "nowrap",  
                    "overflow": "justify",   
                }
            }
        },
        "yAxis": {
            "title": {"text": "Rank (Lower is Better)"},
            "reversed": True  
        },
        "series": [{
            "name": "Rank",
            "data": [{"y": value, "color": gradient_colors[i]} for i, value in enumerate(data_values)]
        }],
        "legend": {"enabled": False},
        "tooltip": {"enabled": True, "formatter": """function() { return '<b>' + this.x + '</b><br>Rank: ' + this.y; }"""},

        "plotOptions": {
            "bar": {
                "dataLabels": {
                    "enabled": True,
                    "align": "right",
                    "inside": False,  
                    "format": "{point.y:.0f}",  
                    "style": {
                        "fontSize": "12px",
                        "color": "#000000"  
                    }
                }
            }
        }
    }

    hc.streamlit_highcharts(options, height=1000)

def display_topic_trends(district_topic_data, selected_district, topic_colors=None):

    if topic_colors is None:
        topic_colors = {
            "Topic_1_Enhancing_Parks_with_Playgrounds_and_Recreational_Amenities": "#1f77b4",
            "Topic_2_Expanding_Waterfront_Access_and_Recreation": "#ff7f0e",
            "Topic_3_Developing_Inclusive_Public_Spaces_and_Services": "#2ca02c",
            "Topic_4_Improving_Infrastructure_for_Accessibility_and_Safety": "#d62728",
            "Topic_5_Enhancing_Pathways_and_Park_Connectivity": "#9467bd",
            "Topic_6_Community_Events_and_Participatory_Programmes": "#8c564b",
            "Topic_7_Developing_Spaces_for_Children_and_Youth": "#e377c2",
        }

    filtered_data = district_topic_data[district_topic_data["district"] == selected_district].sort_values(by="Year")
    filtered_data["Year"] = filtered_data["Year"].astype(int)
    min_value = filtered_data["Proportion"].min() * 100 if not filtered_data.empty else 0
    max_value = filtered_data["Proportion"].max() * 100 if not filtered_data.empty else 100
    y_min = max(0, min_value - 5)  
    y_max = max_value + 5  
    series_data = []
    for topic in filtered_data["Topic"].unique():
        topic_df = filtered_data[filtered_data["Topic"] == topic].sort_values(by="Year")
        series_data.append({
            "name": re.sub(r"Topic_\d+_", "", topic).replace("_", " "),  
            "data": [[int(year), float(prop) * 100] for year, prop in zip(topic_df["Year"], topic_df["Proportion"])],
            "color": topic_colors.get(topic, "#999999"),
            "marker": {"enabled": True, "radius": 4},  
            "lineWidth": 2,
            "states": {"inactive": {"opacity": 0.2}},  
            "dashStyle": "Solid" if "Enhancing" in topic else "Dash",  
        })

    chart_options = {
        "chart": {
            "type": "spline",  
            "events": {"load": "function() { initializeOpacity(this); }"}  
        },
        "title": {"text": f"Topic Trends Over Time in {selected_district}"},
        "xAxis": {"title": {"text": "Year"}, "categories": [int(year) for year in sorted(filtered_data["Year"].unique())]},
        "yAxis": {"title": {"text": "Proportion (%)"}, "min": y_min, "max": y_max},
        "legend": {"layout": "horizontal", "align": "center", "verticalAlign": "bottom"},
        "series": series_data,
        "tooltip": {
            "formatter": """function() { 
                return '<b>' + this.series.name + '</b><br>' + 
                '<b>Year:</b> ' + this.x + '<br>' + 
                '<b>Proportion:</b> ' + this.y.toFixed(2) + '%'; 
            }"""
        },
        "plotOptions": {
            "series": {
                "states": {
                    "inactive": {"opacity": 0.2}  
                },
                "events": {
                    "legendItemClick": "function() { toggleSeries(this); return false; }"  # Custom click behavior
                }
            }
        }
    }

    highlight_script = """
    function initializeOpacity(chart) {
        chart.series.forEach(function(series) {
            series.graphic.css({ opacity: 1 });
        });
    }
    function toggleSeries(clickedSeries) {
        clickedSeries.chart.series.forEach(function(series) {
            if (series !== clickedSeries) {
                series.graphic.css({ opacity: 0.2 });  // Dim others
            } else {
                series.graphic.css({ opacity: 1 });  // Highlight selected
            }
        });
    }
    """
    chart_options["chart"]["events"]["load"] = highlight_script
    hc.streamlit_highcharts(chart_options, height=500)
    

def main():
    """
    Main function to run the Streamlit app.
    """
    APP_TITLE = "RQ3: How are district characteristics related to the thematic focus of citizen proposals?"
    
    if "page_config_set" not in st.session_state:
        st.set_page_config(APP_TITLE, layout='wide')
        st.session_state.page_config_set = True
    st.title(APP_TITLE)
    st.markdown(
    """
    So far, **RQ1** (district-level statistics) and **RQ2** (citizen proposal topics) have been explored separately to translate raw data into useful information.  
    This page brings them together to map the relationship between district characteristics and citizen proposal topics.  
    By linking otherwise separate public datasets, we can gain a more comprehensive and community-informed understanding of citizen voices.
    """
    )
    st.write("")
    selected_district = st.selectbox("Select a District", district_list)
    col1, col2 = st.columns([5, 5], border=True)
    with col1:
        plot_indices_time_series(indexes, selected_district)
        display_topic_trends(district_topic_data, selected_district)
    with col2:
        plot_district_ranking(weighted_averages_cleaned, selected_district)
    st.write("")
    st.write('#### Pearson Correlation Coefficients between District Characteristics and Citizen Proposal Topics')
    st.write("")
    st.markdown(
    """
    The heatmap below shows the Pearson correlation coefficients between four district-level indices and the thematic focus of citizen proposals.  
    Significance levels are marked as: `*` (*p* < 0.1), `**` (*p* < 0.05), `***` (*p* < 0.01).  

    The analysis reveals how local socioeconomic and infrastructural conditions relate to citizens’ priorities in participatory budgeting.  
    Notably, *Topic 3 (Inclusive Public Spaces and Services)* shows strong, significant correlations with three indices: positively with economic prosperity and public service accessibility, and negatively with socioeconomic dependency. This suggests that more affluent, service-rich districts tend to propose ideas focused on inclusivity and civic infrastructure.

    In contrast, *Topic 7 (Spaces for Children and Youth)* is more prominent in economically or socially vulnerable areas, showing a negative correlation with prosperity and a positive one with dependency.  
    These patterns reflect a spatial and socioeconomic divide in citizen priorities: **with privileged districts emphasising community services, and less privileged ones focusing on youth needs and basic support.**
    """
    )
    st.image('app/data/correlation_heatmap.png')
    st.write("")
    st.markdown(
        """
        ### **Final Remark: Connecting City Data for Inclusive Decision-Making**  
        City data is often publicly accessible yet fragmented across different sources, making it difficult to process and utilise effectively.  
        By connecting city data, city governments can enable citizens to engage with community issues and make informed decisions.
        """
    )
if __name__ == "__main__":
    main()