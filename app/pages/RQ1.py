# Import libraries
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import streamlit_highcharts as hc

# Load data at the start to avoid reloading on every interaction
@st.cache_data
def load_data():
    indexes = pd.read_csv('app/data/indexes.csv')
    return indexes

def display_year_filters(df):
    year_list = list(df['Year'].unique())
    year_list.sort()
    year = st.sidebar.selectbox('Year', year_list, len(year_list)-1)
    return year

def display_map(df, year, statistics_column, geojson_file):
    df_year = df[(df['Year'] == year)]
    gdf = gpd.read_file(geojson_file).to_crs(epsg=4326)
    gdf = gdf.merge(df_year, on='Area', how='left')
    gdf[statistics_column] = gdf[statistics_column].round(3)
    st.header(f'{statistics_column} in year {year}')
    st.markdown(
        """
        Let's explore the socio-economic and demographic characteristics of Helsinki's districts.
        Especially, check out *'proportion of foreign language speakers'* and *'proportion of higher education'* in different years (in the left sidebar) to see how the city has become more segregated over time.   
        **Note**: Districts or years with missing data are displayed in white.
        """
    )
    map = folium.Map(location = [60.1800, 25.05], zoom_start=10.5, tiles='cartodb positron')
    
    folium.Choropleth(
        geo_data=gdf,
        name="choropleth",
        data=gdf,
        columns=["Area", statistics_column],
        key_on="feature.properties.Area",
        fill_color="OrRd",
        fill_opacity=0.7,
        line_opacity=0.1,
        nan_fill_color="white",
        highlight=True,
        legend_name=f'{statistics_column} in {year}',
    ).add_to(map)
    folium.GeoJson(
        gdf,
        style_function=lambda feature: {
            'fillColor': 'transparent',
            'color': 'black',
            'weight': 1.5,
            'fillOpacity': 0.0,
        },
        highlight_function=lambda feature: {
            'fillColor': '#ffff00',
            'color': '#ff0000',
            'weight': 3,
            'fillOpacity': 0.5,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['Area', statistics_column],
            aliases=['District:', f'{statistics_column}:'],
            localize=True
        )
    ).add_to(map)
    st_folium(map, width=1000, height=600)
    
    return df_year, statistics_column

def display_statistics(df_year, statistics_column):
    df_year_sorted = df_year.sort_values(by=statistics_column, ascending=False).head(10)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"{statistics_column} by District")
        categories = df_year_sorted['Area'].tolist()
        data = [round(x, 2) for x in df_year_sorted[statistics_column].tolist()]

        options = {
            'chart': {'type': 'bar', 'height': 500},
            'title': {'text': 'Top 10 districts'},
            'xAxis': {'categories': categories, 'title': {'text': 'District'}},
            'yAxis': {'title': {'text': statistics_column}},
            'series': [{'name': statistics_column, 'data': data}],
            'plotOptions': {
                'bar': {
                    'dataLabels': {
                        'enabled': True,
                        
                    }
                }
            }
        }

        hc.streamlit_highcharts(options)

    with col2:
        st.subheader(f"Average value across districts")
        avg_value = df_year[statistics_column].mean()
        st.metric(label=f"{statistics_column} on average", value=round(avg_value, 2))
        
def display_index_map(df, selected_index, geojson_file):
    years = sorted(df["Year"].unique())
    selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)
    df_year = df[df["Year"] == selected_year]

    if df_year.empty:
        st.warning(f"No data available for {selected_year}.")
        return

    gdf = gpd.read_file(geojson_file).to_crs(epsg=4326)
    gdf = gdf.merge(df_year, on="Area", how="left")

    gdf[selected_index] = gdf[selected_index].round(2)

    st.subheader(f"{selected_index} Map ({selected_year})")
    st.markdown("""
                Let’s explore the four indices across Helsinki’s districts. 
                Pay particular attention to the *Economic Prosperity Index* and *Socioeconomic Dependency Index* (in the left sidebar), which reveal a somewhat contrasting pattern between the western and eastern parts of the city.
                """
    )

    map_center = [60.1800, 25.05]
    map = folium.Map(location=map_center, zoom_start=10.5, tiles="cartodb positron")

    folium.Choropleth(
        geo_data=gdf,
        name="choropleth",
        data=gdf,
        columns=["Area", selected_index],
        key_on="feature.properties.Area",
        fill_color="Greys",
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_color="white",
        highlight=True,
        legend_name=f"{selected_index} ({selected_year})",
    ).add_to(map)

    folium.GeoJson(
        gdf,
        style_function=lambda feature: {
            "fillColor": "transparent",
            "color": "black",
            "weight": 1.5,
            "fillOpacity": 0.0,
        },
        highlight_function=lambda feature: {
            "fillColor": "#ffff00",
            "color": "#ff0000",
            "weight": 3,
            "fillOpacity": 0.5,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["Area", selected_index],
            aliases=["District:", f"{selected_index}:"],
            localize=True,
        ),
    ).add_to(map)

    st_folium(map, width=1000, height=600)

    return selected_index

def main():
    APP_TITLE = "RQ1: What are the socio-economic and demographic characteristics of Helsinki’s districts?"

    st.set_page_config(APP_TITLE, layout='wide')
    st.title(APP_TITLE)
    
    st.markdown(
        """
        This page presents composite indices based on district-level statistics in Helsinki to illustrate varying characteristics across 34 districts.  
        The data was retrieved from the [Helsinki Map Service](https://kartta.hel.fi) and [Helsinki Region Infoshare](https://hri.fi/en_gb/) on 10 March 2025, with 2023 being the most recent year available at the time.  
        """
    )
    
    district_data = pd.read_csv('app/data/district_data.csv')

    notes = {
        "Population": "The total number of people living in a given area.",
        "Demographic dependency ratio": "The ratio of dependents (aged 0-14 and 65+) to the working-age population (15-64 years), indicating economic pressure on the productive population. E.g., 76 dependents for every 100 working-age individuals.",
        "Proportion of youth (0-14)": "The percentage of the total population that is aged between 0 and 14 years.",
        "Proportion of elderly (65+)": "The percentage of the total population that is aged 65 years and older.",
        "Proportion of working age (15-64)": "The percentage of the total population that is aged between 15 and 64 years, representing the economically active segment.",
        "Proportion of foreign language": "The percentage of the population that speaks a language other than the official or predominant language(s) as their first language.",
        "Proportion of finnish and sami": "The percentage of the population whose native language is Finnish or Sami, the official languages of Finland.",
        "Proportion of swedish": "The percentage of the population whose native language is Swedish, Finland's second official language.",
        "Proportion of males": "The percentage of the total population that identifies as male.",
        "Proportion of females": "The percentage of the total population that identifies as female.",
        "Proportion of higher education": "The percentage of the population that has attained a higher education degree, such as a university or college degree.",
        "Proportion of basic education": "The percentage of the population that has not attained over a secondary education degree.",
        "Proportion of upper secondary education": "The percentage of the population that has completed upper secondary education, such as high school or vocational training.",
        "Proportion of lower tertiary education": "The percentage of the population that has completed lower tertiary education, such as an associate degree or equivalent.",
        "Proportion of one person household": "The percentage of households that consist of a single individual.",
        "Proportion of four or more persons household": "The percentage of households that consist of four or more individuals.",
        "Unemployment rate": "The percentage of the labor force that is unemployed and actively seeking employment.",
        "Proportion of creative class in workforce": "According to Florida (2002, p.8), a creative class is defined as people in design, education, arts, music and entertainment, whose economic function is to create new ideas, new technology and/or creative content. \nBased on the definition, it refers to workforces in J. Information and Communication (Informaatio ja viestintä), M. Professional, Scientific, and Technical Activities (Ammatillinen, tieteellinen ja tekninen toiminta), N. Administrative and Support Service Activities (Hallinto- ja tukipalvelutoiminta), P. Education (Koulutus), and R. Arts, Entertainment and Recreation (Taiteet, viihde ja virkistys).",
        "Income subject to state taxation euro average": "The average income in euros that is subject to state taxation, indicating the economic prosperity of the area.",
        "Gini coefficient disposable income": "A measure of income inequality within a population, where 0 represents perfect equality and 100 represents perfect inequality.",
        "Proportion of buildings constructed before 1980 in total housing stock": "The percentage of the total housing stock that was constructed before 1980, indicating the age of the housing infrastructure.",
        "Proportion of private rental apartments": "The percentage of housing units that are privately owned and rented out. It often implies higher living costs compared to other housing tenures.",
        "Proportion of subsidised rental apartments": "The percentage of housing units that are part of government-subsidised housing programmes, such as the Avara programme or interest-subsidised rental schemes.",
        "Population density": "The number of people living per square kilometer or square mile of land area.",
        "Service points for dog areas per 1000 persons": "The number of service points for dog areas (e.g., parks, toilets, beaches) available per 1,000 residents.",
        "Service points for parks and green areas per 1000 persons": "The number of service points for parks and green areas (e.g., wading pools, green area maintenance, park chess boards) available per 1,000 residents.",
        "Service points for playgrounds per 1000 persons": "The number of service points for playgrounds (e.g., supervised/no supervised activities) available per 1,000 residents.",
        "Service points for cultural activities per 1000 persons": "The number of service points for cultural activities (e.g., libraries and museums, hobbies, renting recreational spaces) available per 1,000 residents.",
        "Service points for circular economy per 1000 persons": "The number of service points supporting circular economy activities (e.g., borrowing and renting services, recycling, shared spaces, shared transport) available per 1,000 residents.",
        "Service points for daycare and pre primary education per 1000 persons": "The number of service points for daycare and pre-primary education available per 1,000 residents.",
        "Service points for child and family services per 1000 persons": "The number of service points for child and family services (e.g., child welfare, social assistance) available per 1,000 residents.",
        "Service points for social welfare services per 1000 persons": "The number of service points for social welfare services (e.g., elderly, children, disabled) available per 1,000 residents."
    }
    
    stats_options = [col for col in district_data.columns[3:] if col.lower() not in ['latitude', 'longitude']]
    statistics_column = st.sidebar.selectbox(
        'Select Statistic', 
        stats_options, 
        index=0
    )
    selected_year = display_year_filters(district_data)
    st.sidebar.markdown(f"**Note:**<br>{notes.get(statistics_column, 'No additional information available for this statistic.')}", unsafe_allow_html=True)
    df_year, selected_stat = display_map(district_data, selected_year, statistics_column, 'app/data/districts.geojson')
    display_statistics(df_year, selected_stat)
    
    indexes = load_data()
    
    st.markdown("### Socioeconomic and Demographic Characteristics of Helsinki’s Districts")
    
    st.markdown(
        """
        Four indices are constructed to identify spatial challenges in Helsinki by aggregating multiple indicators into composite indicators: 
        
        - Demographic Diversity Index (DDI): Uses Simpson's diversity index to quantify heterogeneity in demographic composition.
        - Economic Prosperity Index (EPI): Computed using a weighted mean, emphasising income levels, inequality, unemployment, and education.
        - Socioeconomic Dependency Index (SDI): Uses the geometric mean to balance dependencies across population groups.
        - Public Service Accessibility Index (PSAI): Employs the weighted mean to ensure equal representation of diverse service categories.
        """
    )
    
    with st.expander("Click to see how each index is calculated."):
        st.markdown("### 1. Demographic Diversity Index (CDI)")
        st.markdown(
            """
            The Demographic Diversity Index (CDI) quantifies heterogeneity in population characteristics by measuring the probability that two randomly selected individuals belong to different demographic groups. This index applies Simpson’s Diversity Index with Sullivan’s Extension to account for multiple demographic dimensions and aggregate them into a single composite diversity measure (McLaughlin et al., 2016).
            
            McLaughlin, J. E., McLaughlin, G. W., McLaughlin, J. S., & White, C. Y. (2016). Using Simpson’s diversity index to examine multidimensional models of diversity in health professions education. *International Journal of Medical Education*, 7, 1–5.
            """
        )
        st.latex(r"""
        CDI_j = 1 - \sum_{c=1}^{C} \sum_{p=1}^{P} (Y_{c,p})^2
        """)
        st.markdown(
            r"""
            Where:  
            - CDI_j = Composite Demographic Diversity Index for district j  
            - C = Total number of demographic categories considered  
            - P = Number of demographic groups within category c  
            - Y_c,p = Proportion of individuals in category p within demographic category c

            This formulation follows Sullivan’s Extension of Simpson’s Index,  
            allowing for the aggregation of education, age, gender, language, and workforce diversity into a single measure.
            """
        )
        st.markdown(
            """
            **Indicators Included:**  
            - **Education:**  
                - Proportion of basic education  
                - Proportion of upper secondary education  
                - Proportion of lower tertiary education  
                - Proportion of higher education  
            - **Age Structure:**  
                - Proportion of youth (0–14)  
                - Proportion of elderly (65+)  
                - Proportion of working-age population (15–64)  
            - **Gender Composition:**  
                - Proportion of males  
                - Proportion of females  
            - **Linguistic Diversity:**  
                - Proportion of foreign language speakers  
                - Proportion of Finnish and Sámi speakers  
                - Proportion of Swedish speakers  
            - **Workforce Structure:**  
                - Proportion of creative class in the workforce  
                - Proportion of non-creative class in the workforce  

            **Interpretation:**  
            - Higher CDI values indicate greater demographic diversity.  
            - Lower CDI values suggest a more homogeneous population.
            """
        )

        st.markdown("### 2. Economic Prosperity Index (EPI)")
        st.markdown(
            """
            The Economic Prosperity Index (EPI) measures the economic well-being of each district by evaluating 
            income levels, income equality, workforce stability, and educational attainment. It includes:
            
            - Average taxable income – Higher values indicate greater prosperity.  
            - Gini coefficient (inverted) – Reflects income equality.  
            - Unemployment rate (inverted) – Indicates stronger labour market conditions.  
            - Proportion of highly educated residents – Represents human capital.

            The index is calculated using a weighted sum:
            """
        )
        st.latex(r"""
        \text{EPI} = 0.4 \times \text{Income} + 0.2 \times (1 - \text{Gini}) + 
        0.2 \times (1 - \text{Unemployment}) + 0.2 \times \text{Higher Education Proportion}
        """)
        st.markdown(
            """
            **Interpretation:**  
            - Higher values = stronger prosperity and equality.  
            - Lower values = economic and social challenges.
            """
        )

        st.markdown("### 3. Socioeconomic Dependency Index (SDI)")
        st.markdown(
            """
            The Socioeconomic Dependency Index (SDI) captures population groups that may require additional support, based on:
            - Large household sizes  
            - Linguistic diversity  
            - Dependency ratios  
            - Proportion in subsidised housing

            The index uses a geometric mean:
            """
        )
        st.latex(r"""
        \text{SDI} = \left( \prod_{i=1}^{4} X_i \right)^{\frac{1}{4}}
        """)
        st.markdown(
            """
            **Interpretation:**  
            - Higher SDI = greater dependency and need for services.  
            - Lower SDI = more self-sufficient population.
            """
        )

        st.markdown("### 4. Public Service Accessibility Index (PSAI)")
        st.markdown(
            """
            The Public Service Accessibility Index (PSAI) measures access to key services, including:
            - Green areas  
            - Childcare  
            - Cultural activities  
            - Social welfare

            Calculated as an average of eight standardised indicators:
            """
        )
        st.latex(r"""
        \text{PSAI} = \frac{1}{8} \sum_{i=1}^{8} X_i
        """)
        st.markdown(
            """
            **Interpretation:**  
            - Higher PSAI = better access to services.  
            - Lower PSAI = potential gaps in public service provision.
            """
        )

    st.markdown("#### Timeseries of District-Level Indexes")
    st.markdown("""
                From 2018 to 2023, Helsinki districts saw increasing demographic diversity and socioeconomic dependency, while economic prosperity slightly declined. 
                The trends suggest that Helsinki’s population is becoming more diverse and increasingly reliant on public support, while economic prosperity shows signs of stagnation. 
                However, the linear coefficients indicate that the rates of change are minimal, largely due to the short five-year observation period. 
                """
    )
    st.image('app/data/indices_timeseries.png')
    
    district_indexes_data = district_data.merge(indexes, on=["Area", "Year"], how="left")

    index_options = [
        "Demographic Diversity Index",
        "Economic Prosperity Index",
        "Socioeconomic Dependency Index",
        "Public Service Accessibility Index"
    ]
    selected_index = st.sidebar.selectbox("Select an Index to Visualise", index_options)

    selected_stat = display_index_map(district_indexes_data, selected_index, 'app/data/districts.geojson')

if __name__ == "__main__":
    main()