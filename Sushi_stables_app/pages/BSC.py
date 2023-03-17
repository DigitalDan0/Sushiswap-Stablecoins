import streamlit as st
import pandas as pd
from shroomdk import ShroomDK
import plotly.express as px
from Sushiswap_Stablecoins import querying_pagination, config

from PIL import Image
import base64

@st.cache_data
def load_svg(filename: str) -> str:
    with open(filename, "r") as f:
        content = f.read()
    return content

svg_logo = load_svg("sushi_stables_app/bnb.svg")
st.markdown(f'<h1 style="font-size: 3rem; font-weight: bold;">{svg_logo} BSC Stablecoin Swaps</h1>', unsafe_allow_html=True)

#f'<img src="data:image/png;base64,{ethereum_logo_base64}" width="30" height="30" style="vertical-align: middle; padding-bottom: 5px;"/> Ethereum Stablecoin Volume'

query = """with stables_in_bsc as (
select date_trunc('month',block_timestamp) as month,
  symbol_in as symbol,
  sum(amount_in_usd) as Amount_in_USD
from bsc.sushi.ez_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD','USDJ')
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_bsc as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD
from bsc.sushi.ez_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD','USDJ')
group by 1,2
order by month DESC, amount_out_usd DESC
)
select stables_in_bsc.month,
   stables_in_bsc.symbol, 
   Amount_in_USD, 
   Amount_out_USD,
   Amount_in_USD + Amount_out_USD as total_volume,
   Amount_in_USD - Amount_out_USD as net_stablecoin_volume
from stables_in_bsc
left join stables_out_bsc
  on stables_in_bsc.month = stables_out_bsc.month and stables_in_bsc.symbol = stables_out_bsc.symbol
"""

df = querying_pagination(query)
#title of the page
#st.title("Ethereum Stablecoin Volume ")
#subtitle of the page
st.markdown(' ')
st.markdown("This page shows a deeper dive into the total volume and net inflows/outflows of stablecoins on Sushiswap BSC")

# Stacked bar chart for total_volume
fig_total_volume = px.bar(df,
                          x='month',
                          y='total_volume',
                          color='symbol',
                          barmode='stack',
                          title='Total Stablecoin Swap Volume on BSC per Token',
                          labels={'month': 'Month', 'total_volume': 'Total Volume', 'symbol': 'Stablecoin'})

# Stacked bar chart for net_stablecoin_volume
fig_net_stablecoin_volume = px.bar(df,
                                   x='month',
                                   y='net_stablecoin_volume',
                                   color='symbol',
                                   #barmode='stack',
                                   title='Net Stablecoin Swap Volume on BSC per Token',
                                   labels={'month': 'Month', 'net_stablecoin_volume': 'Net Stablecoin Volume', 'symbol': 'Stablecoin'})

# Calculate the total volume per month
monthly_total_volume = df.groupby('month')['total_volume'].sum().reset_index()

# Merge the total volume per month with the original dataframe
df_normalized = df.merge(monthly_total_volume, on='month', suffixes=('', '_monthly_total'))

# Calculate the normalized volume for each stablecoin
df_normalized['normalized_volume'] = (df_normalized['total_volume'] / df_normalized['total_volume_monthly_total']) * 100


# Stacked bar chart for normalized volume
fig_normalized_volume = px.bar(df_normalized,
                               x='month',
                               y='normalized_volume',
                               color='symbol',
                               barmode='stack',
                               title='Normalized Monthly Stablecoin Swap Volume on BSC per Token',
                               labels={'month': 'Month', 'normalized_volume': 'Normalized Volume (%)', 'symbol': 'Stablecoin'})


col1, col2 = st.columns(2)
col1.plotly_chart(fig_total_volume, use_container_width=True)
col2.plotly_chart(fig_normalized_volume, use_container_width=True)
st.plotly_chart(fig_net_stablecoin_volume, use_container_width=True)

#subtitle conclusions
st.subheader(" Conclusions")
st.write('''
Binance Smart Chain launched with its own stablecoin BUSD, which started as the most popular stablecoin on Sushiswap BSC. Over time, USDT has gained market share from BUSD, and as of March 2023, accounts for 86% of the total stablecoin volume on Sushiswap BSC. While USDC does have a presence on BSC, it has never really caught on and only captures a small portion of the swaps.
''')
