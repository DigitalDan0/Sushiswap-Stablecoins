import os
import sys
shroomdk_key = os.environ.get('shroomdk_key')

print(f"ShroomDK API Key: {shroomdk_key}")
# In your config.py
print(f"ShroomDK API Key: {shroomdk_key}", flush=True)

# In the main app file
print(f"Initializing ShroomSDK with API Key: {shroomdk_key}", flush=True)

