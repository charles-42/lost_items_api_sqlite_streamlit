# SNCF Lost items analysis

This project queries lost object data in SNCF train stations and analyzes it.
The targeted skills are:
- requests
- sqlalchemy
- Object-oriented programming
- unittest
- streamlit."

## Table of Contents

- [SNCF Lost items analysis](#sncf-lost-items-analysis)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)


## Installation

1. Clone the repository: `git clone https://github.com/charles-42/lost_items_api_sqlite_streamlit.git`
2. Install the required packages: `pip install -r requirements.txt`
3. Create the database and download data: `python main.py`
4. Run the application: `streamlit run app.py`

## Usage

This project is a Streamlit application that analyzes lost items in French train stations using the OpenData API. The main features of the application are:

- Display a histogram of the number of lost items per week per type of object since 2018.
- Display a map of Paris with the number of lost items found for every million travelers, grouped by year and type of object.
- Display a scatterplot of the number of lost items found per day versus the temperature.
- Display a box plot of the number of lost items found per day grouped by season (summer, autumn, winter, spring).
- Display a heatmap of the median number of lost items found per day grouped by season and type of object.

