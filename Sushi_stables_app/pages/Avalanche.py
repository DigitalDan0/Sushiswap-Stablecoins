import streamlit as st
import pandas as pd
from shroomdk import ShroomDK
import plotly.express as px
from Sushiswap_Stablecoins import querying_pagination, config

from PIL import Image
import base64

@st.cache_data
def load_svg(filename: str, width: int = None, height: int = None) -> str:
    with open(filename, "r") as f:
        content = f.read()

    if width and height:
        content = content.replace('<svg', f'<svg width="{width}" height="{height}"', 1)

    return content


svg_logo = load_svg("Sushi_stables_app/avax.svg",width=40,height=40)
st.markdown(f'<h1 style="font-size: 3em; font-weight: bold;">{svg_logo} Avalanche Stablecoin Swaps</h1>', unsafe_allow_html=True)

query = """
with stables_in_ava as (
select date_trunc('month',block_timestamp) as month,
  symbol_in as symbol,
  sum(amount_in_usd) as Amount_in_USD
from avalanche.sushi.ez_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_ava as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD
from avalanche.sushi.ez_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
group by 1,2
order by month DESC, amount_out_usd DESC
)
select stables_in_ava.month,
   stables_in_ava.symbol, 
   Amount_in_USD, 
   Amount_out_USD,
   Amount_in_USD + Amount_out_USD as total_volume,
   Amount_in_USD - Amount_out_USD as net_stablecoin_volume
from stables_in_ava
left join stables_out_ava
  on stables_in_ava.month = stables_out_ava.month and stables_in_ava.symbol = stables_out_ava.symbol
"""
query2 = """
with stables_in_ava as (
select date_trunc('month',block_timestamp) as month,
  symbol_in as symbol,
  sum(amount_in_usd) as Amount_in_USD
from avalanche.sushi.ez_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_ava as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD
from avalanche.sushi.ez_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
group by 1,2
order by month DESC, amount_out_usd DESC
)
select stables_in_ava.month,
   stables_in_ava.symbol, 
   Amount_in_USD, 
   Amount_out_USD,
   Amount_in_USD + Amount_out_USD as total_volume,
   Amount_in_USD - Amount_out_USD as net_stablecoin_volume
from stables_in_ava
left join stables_out_ava
  on stables_in_ava.month = stables_out_ava.month and stables_in_ava.symbol = stables_out_ava.symbol
  where stables_in_ava.symbol != 'MIM'
"""


df = querying_pagination(query)
#title of the page
#st.title("Ethereum Stablecoin Volume ")
#subtitle of the page
st.markdown(' ')
st.markdown("This page shows a deeper dive into the total volume and net inflows/outflows of stablecoins on Sushiswap Avalanche")

# Stacked bar chart for total_volume
fig_total_volume = px.bar(df,
                          x='month',
                          y='total_volume',
                          color='symbol',
                          barmode='stack',
                          title='Total Stablecoin Swap Volume on Avalanche per Token',
                          labels={'month': 'Month', 'total_volume': 'Total Volume', 'symbol': 'Stablecoin'})

# Stacked bar chart for net_stablecoin_volume
fig_net_stablecoin_volume = px.bar(df,
                                   x='month',
                                   y='net_stablecoin_volume',
                                   color='symbol',
                                   #barmode='stack',
                                   title='Net Stablecoin Swap Volume on Avalanche per Token',
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
                               title='Normalized Monthly Stablecoin Swap Volume on Avalanche per Token',
                               labels={'month': 'Month', 'normalized_volume': 'Normalized Volume (%)', 'symbol': 'Stablecoin'})


col1, col2 = st.columns(2)
col1.plotly_chart(fig_total_volume, use_container_width=True)
col2.plotly_chart(fig_normalized_volume, use_container_width=True)
st.plotly_chart(fig_net_stablecoin_volume, use_container_width=True)

df2 = querying_pagination(query2)

st.markdown("This section shows the same charts without MIM, which had a huge spike in volume in May 2021")

# Stacked bar chart for total_volume
fig_total_volume2 = px.bar(df2,
                          x='month',
                          y='total_volume',
                          color='symbol',
                          barmode='stack',
                          title='Total Stablecoin Swap Volume on Avalanche per Token',
                          labels={'month': 'Month', 'total_volume': 'Total Volume', 'symbol': 'Stablecoin'})

# Stacked bar chart for net_stablecoin_volume
fig_net_stablecoin_volume2 = px.bar(df2,
                                   x='month',
                                   y='net_stablecoin_volume',
                                   color='symbol',
                                   #barmode='stack',
                                   title='Net Stablecoin Swap Volume on Avalanche per Token',
                                   labels={'month': 'Month', 'net_stablecoin_volume': 'Net Stablecoin Volume', 'symbol': 'Stablecoin'})

# Calculate the total volume per month
monthly_total_volume2 = df2.groupby('month')['total_volume'].sum().reset_index()

# Merge the total volume per month with the original dataframe
df_normalized2 = df2.merge(monthly_total_volume2, on='month', suffixes=('', '_monthly_total'))

# Calculate the normalized volume for each stablecoin
df_normalized2['normalized_volume'] = (df_normalized2['total_volume'] / df_normalized2['total_volume_monthly_total']) * 100


# Stacked bar chart for normalized volume
fig_normalized_volume2 = px.bar(df_normalized2,
                               x='month',
                               y='normalized_volume',
                               color='symbol',
                               barmode='stack',
                               title='Normalized Monthly Stablecoin Swap Volume on Avalanche per Token',
                               labels={'month': 'Month', 'normalized_volume': 'Normalized Volume (%)', 'symbol': 'Stablecoin'})


col1, col2 = st.columns(2)
col1.plotly_chart(fig_total_volume2, use_container_width=True)
col2.plotly_chart(fig_normalized_volume2, use_container_width=True)
st.plotly_chart(fig_net_stablecoin_volume2, use_container_width=True)

#subtitle conclusions
st.subheader(" Conclusions")
st.write('''Avalanche has had some interesting Stablecoin dynamics over its lifetime. The predominant stablecoin was USDT until around the end of 2021. We then see a huge spike in outflows of Magic Internet Money (MIM) - this spike likely was due to the collapse of Wonderland and traders fleeing the market. After the dust settled, USDC rose as the major stablecoin on Avalanche, but its volume steadily decreased and as of writing in March 2023, there has been no stablecoin swap volume on Avalanche this month.''')

