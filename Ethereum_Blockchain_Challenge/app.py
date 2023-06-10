import os
import requests
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import plotly.express as px

load_dotenv()

dappradar_api_key = os.environ.get("DAPPRADAR_API_KEY")

import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

dappradar_api_key = os.environ.get("DAPPRADAR_API_KEY")

def get_dapps_data():
    api_key = os.environ["DAPPRADAR_API_KEY"]
    project = "4tsxo4vuhotaojtl"
    url = "https://api.dappradar.com/" + project + "/dapps"
    
    results_per_page = 25
    page = 1
    all_dapps = []

    while True:
        query = {
            "chain": "ethereum",
            "page": str(page),
            "resultsPerPage": str(results_per_page),
        }

        headers = {"X-BLOBR-KEY": api_key}

        response = requests.get(url, headers=headers, params=query)
        data = response.json()

        if not data:
            break

        all_dapps.extend(data)
        page += 1

    # Parse the data into a DataFrame
    dapps_df = pd.DataFrame(all_dapps)
    return dapps_df

# App title and description
st.title("Ethereum DApps Data")
st.write("This app displays the number of active DApps on the Ethereum network and their popular categories.")

# Get DApps data
dapps_data = get_dapps_data()

st.write(dapps_data)
