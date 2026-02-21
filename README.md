# 🎵⏪ Play Back - Music Streaming History Deep Dive
No matter which music streaming service you use, Play Back unlocks personalized insights into your listening habits. Explore your streaming history with interactive charts and graphs, from high-level streaming patterns to detailed yearly and quarterly heatmaps. Take your analysis to the next level by using Machine Learning to uncover your unique listening session types. Get started with your last.fm data, or explore my own music streaming history to get an idea of what you can uncover.

You have multiple options for interacting with this app:
* [Leverage the published version on the streamlit.app website](#try-it-on-streamlit)
* [Run the entire Streamlit app locally](#run-the-streamlit-app-locally)
* [Only run the streaming data processing and clustering algorithm](#run-the-scripts-only)

See below for instructions for all 3 options. 

Please feel free to provide any feedback by opening an issue or connecting with me on [LinkedIn](https://www.linkedin.com/in/jacqueline-kc-lee/). 

# Try it On Streamlit

# Run the Streamlit App Locally

## Installation & Setup

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