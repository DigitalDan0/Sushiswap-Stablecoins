import os
import sys
import streamlit as st
shroomdk_key = api_key = st.secrets["shroomdk_key"]

print(f"ShroomDK API Key: {shroomdk_key}")
# In your config.py
print(f"ShroomDK API Key: {shroomdk_key}", flush=True)

# In the main app file
print(f"Initializing ShroomSDK with API Key: {shroomdk_key}", flush=True)

print("Environment Variables:", flush=True)
print(os.environ, flush=True)