
# Mapping Citizen Voices: Transforming Participatory Budgeting with Combined Data Streams in Helsinki

This project analyses citizen proposals submitted to the OmaStadi participatory budgeting programme in Helsinki. By combining citizen-generated proposals with district-level socio-economic statistics, the app offers a more integrated and interactive dashboard of local needs and priorities. 

## Getting Started

You have two options to explore the dashboard:

### Option 1: Try the App Online

Visit this URL: [**mapping-citizen-voices.app**](https://mappingcitizenvoices.streamlit.app)

---

### Option 2: Run Locally with Poetry

If you prefer running the app on your local machine:

1.**Clone the repository:**
```bash
    git clone https://github.com/bokyong-shin/mapping_citizen_voices.git
    cd mapping_citizen_voices
```

2.**Install Poetry:**
```bash
pip install poetry
```

3.**Install dependencies using Poetry:**
```bash
poetry install
```

4.**Activate the Poetry shell:**
```bash
poetry shell
```
5.**Install the Finnish language model for spaCy:**
```bash
python -m spacy download fi_core_news_sm
```
6.**Run the App:**
```bash
streamlit run app/Home.py
```
---

## Licence

This project is for academic and research purposes. Please cite appropriately if you use or adapt this work.

