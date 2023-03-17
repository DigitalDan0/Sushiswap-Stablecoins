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

svg_logo = load_svg("Sushi_stables_app/eth.svg")
st.markdown(f'<h1 style="font-size: 3rem; font-weight: bold;">{svg_logo} Ethereum Stablecoin Swaps</h1>', unsafe_allow_html=True)


query = """
with stables_in_eth as (
select date_trunc('month',block_timestamp) as month,
  symbol_in as symbol,
  sum(amount_in_usd) as Amount_in_USD,
  'ethereum' as blockchain
from ethereum.sushi.ez_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM')
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_eth as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD,
  'ethereum' as blockchain
from ethereum.sushi.ez_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM')
group by 1,2
order by month DESC, amount_out_usd DESC
)
select stables_in_eth.month,
   stables_in_eth.symbol,
   stables_in_eth.blockchain,
   Amount_in_USD, 
   Amount_out_USD,
   Amount_in_USD + Amount_out_USD as total_volume,
   Amount_in_USD - Amount_out_USD as net_stablecoin_volume
from stables_in_eth
left join stables_out_eth
  on stables_in_eth.month = stables_out_eth.month and stables_in_eth.symbol = stables_out_eth.symbol
"""

df = querying_pagination(query)
#title of the page
#st.title("Ethereum Stablecoin Volume ")
#subtitle of the page
st.markdown(' ')
st.markdown("This page shows a deeper dive into the total volume and net inflows/outflows of stablecoins on Sushiswap Ethereum")

# Stacked bar chart for total_volume
fig_total_volume = px.bar(df,
                          x='month',
                          y='total_volume',
                          color='symbol',
                          barmode='stack',
                          title='Total Stablecoin Swap Volume on Ethereum per Token',
                          labels={'month': 'Month', 'total_volume': 'Total Volume', 'symbol': 'Stablecoin'})

# Stacked bar chart for net_stablecoin_volume
fig_net_stablecoin_volume = px.bar(df,
                                   x='month',
                                   y='net_stablecoin_volume',
                                   color='symbol',
                                   #barmode='stack',
                                   title='Net Stablecoin Swap Volume on Ethereum per Token',
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
                               title='Normalized Monthly Stablecoin Swap Volume on Ethereum per Token',
                               labels={'month': 'Month', 'normalized_volume': 'Normalized Volume (%)', 'symbol': 'Stablecoin'})


col1, col2 = st.columns(2)
col1.plotly_chart(fig_total_volume, use_container_width=True)
col2.plotly_chart(fig_normalized_volume, use_container_width=True)
st.plotly_chart(fig_net_stablecoin_volume, use_container_width=True)

#subtitle conclusions
st.subheader(" Conclusions")
st.write('''
Ethereum data reveals a parallel narrative to the crosschain data. Ethereum's dominance is bolstered by USDC, USDT, and DAI, the three major stablecoins that have consistently held sway over the market. Interestingly, late 2021 witnessed a surge in volume for OHM and other alternative stablecoins, momentarily disrupting the established order. However, the triumvirate of USDC, USDT, and DAI swiftly reclaimed their position, now accounting for an impressive 99% share of swap volume, further cementing their status as the leading stablecoins on the Ethereum network.''')