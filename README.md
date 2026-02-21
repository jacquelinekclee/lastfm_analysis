# 🎵⏪ Play Back - Music Streaming History Deep Dive
No matter which music streaming service you use, Play Back unlocks personalized insights into your listening habits. Explore your streaming history with interactive charts and graphs, from high-level streaming patterns to detailed yearly and quarterly heatmaps. Take your analysis to the next level by using Machine Learning to uncover your unique listening session types. Get started with your last.fm data, or explore my own music streaming history to get an idea of what you can uncover.

The 3 main components of the Play Back app are:
1. Data Analysis: Get a high level overview of your music streaming history for a given years. Look at your listening habits, find out what new music discoveries you made, and compare your listening history across years. 
2. Data Visualization: Get a bird's-eye view of your streaming history with interactive streaming calendar heatmaps that look at your yearly and quarterly listening habits.
3. Machine Learning: Using unsupervised ML, specifically k-means clustering, go a level deeper into your music listening patterns. After extracting listening sessions, defined by consecutive streams with no less than 10 minutes apart, from your streaming data, train your own k-means clustering model that identifies your protypical listening sessions. I've also highlighted the listening session clusters ML extracted from my own data: 1) weekend wind downs of my favorite songs and artists, 2) quick new discovery sessions, 3) deep dive marathons, and 4) late night old faves.  

You have multiple options for interacting with this app:
* [Leverage the published version on the streamlit.app website](#try-it-on-streamlit)
* [Run the entire Streamlit app locally](#run-the-streamlit-app-locally)
* [Only run the streaming data processing and clustering algorithm](#run-the-scripts-only)

See below for instructions for all 3 options. 

Please feel free to provide any feedback by opening an issue or connecting with me on [LinkedIn](https://www.linkedin.com/in/jacqueline-kc-lee/). 

# Try it On Streamlit
Check out the Play Back app published in [Streamlit here](share_link)
[![Try it in Streamlit][share_badge]][share_link] 

# Run the Streamlit App Locally

## Installation & Environment Setup

1. Clone the repository:
```bash
   git clone https://github.com/jacquelinekclee/lastfm_analysis.git
   cd lastfm_analysis
```

2. Create a virtual environment (recommended):
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
   pip install -r requirements.txt
```

## Run the App
```bash
   streamlit run streamlit_app/0_🎵⏪_Play_Back_Home_Page.py
```

The Streamlit app will open in your browser at `http://localhost:8501`

# Run the Scripts Only
If you'd like to process your own streaming data and/or run the listening sessions clustering model, without running the full streamlit app, you can do so via the command line and the scripts in this repo. 

## Setup
First, follow the same [installation and setup](#installation--environment-setup) instructions above. 

### Download Your Raw Streaming Data
Leverage a [website like this one](https://mainstream.ghan.nl/export.html]) to download your raw streaming data from last.fm.

Then, **move this file** (should be .csv) into the `data/raw` directory. 

### Configurate Parameters
**Update `scrobbles_fp` in the `config/data_params.json` file** to a filename of your choice. This is essential!
Feel free to play around with any the configurations in `config/data_params.json`. 

## Run the Streaming Data Processing and K-Means Clustering of your Listening Sessions

### Run Both Workstreams
After [downloading your raw streaming data from last.fm](#download-your-raw-streaming-data) as described above, you can run both the data processing and k-means clustering model workstreams with the following script:
```bash
python3 run.py {n_clusters}
```
Where `n_clusters` is an optional parameter that defines how many clusters you want your k-means model to identify. If this is omitted, the default value is 4. `n_clusters` must be an integer of at least 2, and I recommend no greater than 6. 

### Run the Data Processing Workstream
To run just the data processing workstream:
```bash
python3 process_data.py
```

### Run the K-Means Clustering Workstream
To run just the listening sessions clustering model, you must have already processed your raw streaming data using the script above and ensure that `processed_scrobbles_fp` in `config/data_params.json` is updated and your processed streaming data csv file is in the `data/processed` directory:
```bash
python3 perform_clustering.py {n_clusters}
```
Where `n_clusters` is an optional parameter that defines how many clusters you want your k-means model to identify. 

### Run Scripts with Test Data
To test any of the scripts, simply include `test` as shown below. `test` must be the first argument provided. 
```bash
python3 run.py test {n_clusters}
```

[share_badge]: https://static.streamlit.io/badges/streamlit_badge_black_white.svg
[share_link]: https://lastfmanalysis.streamlit.app/