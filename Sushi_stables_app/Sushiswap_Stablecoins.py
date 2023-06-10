
import streamlit as st
import pandas as pd
from shroomdk import ShroomDK
import os
import plotly.express as px
import sys
import os
import config



#layout = wide
st.set_page_config(layout="wide",page_title = "Sushiswap Stablecoins")
print(f"Initializing ShroomSDK with API Key: {config.shroomdk_key}")

@st.cache_data
def querying_pagination(query_string):
    sdk = ShroomDK(config.shroomdk_key)
    
    # Query results page by page and saves the results in a list
    # If nothing is returned then just stop the loop and start adding the data to the dataframe
    result_list = []
    for i in range(1,11): # max is a million rows @ 100k per page
        data=sdk.query(query_string,page_size=100000,page_number=i)
        if data.run_stats.record_count == 0:  
            break
        else:
            result_list.append(data.records)
        
    # Loops through the returned results and adds into a pandas dataframe
    result_df=pd.DataFrame()
    for idx, each_list in enumerate(result_list):
        if idx == 0:
            result_df=pd.json_normalize(each_list)
        else:
            result_df=pd.concat([result_df, pd.json_normalize(each_list)])

    return result_df

sushi_stables_query = """
with stables_in_eth as (
select date_trunc('month',block_timestamp) as month,
  symbol_in as symbol,
  sum(amount_in_usd) as Amount_in_USD,
  count(tx_hash) as tx_count
from ethereum.core.ez_dex_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM')
and platform = 'sushiswap'
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_eth as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD,
  count(tx_hash) as tx_count
from ethereum.core.ez_dex_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM')
and platform = 'sushiswap'
group by 1,2
order by month DESC, amount_out_usd DESC
),
eth_stables as (
select stables_in_eth.month,
   stables_in_eth.symbol,
   'Ethereum' as blockchain,
   stables_in_eth.tx_count + stables_out_eth.tx_count as tx_count,
   Amount_in_USD, 
   Amount_out_USD,
   Amount_in_USD + Amount_out_USD as total_volume,
   Amount_in_USD - Amount_out_USD as net_stablecoin_volume
from stables_in_eth
left join stables_out_eth
  on stables_in_eth.month = stables_out_eth.month and stables_in_eth.symbol = stables_out_eth.symbol
),
stables_in_op as (
select date_trunc('month',block_timestamp) as month,
  symbol_in as symbol,
  sum(amount_in_usd) as Amount_in_USD,
  count(tx_hash) as tx_count
from optimism.core.ez_dex_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
and platform = 'sushiswap'
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_op as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD,
  count(tx_hash) as tx_count
from optimism.core.ez_dex_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
and platform = 'sushiswap'
group by 1,2
order by month DESC, amount_out_usd DESC
),
op_stables as (
select stables_in_op.month,
   stables_in_op.symbol,
   'optimism' as blockchain,
   stables_in_op.tx_count + stables_out_op.tx_count as tx_count,
   Amount_in_USD, 
   Amount_out_USD,
   Amount_in_USD + Amount_out_USD as total_volume,
   Amount_in_USD - Amount_out_USD as net_stablecoin_volume
from stables_in_op
left join stables_out_op
  on stables_in_op.month = stables_out_op.month and stables_in_op.symbol = stables_out_op.symbol
),
stables_in_arb as (
select date_trunc('month',block_timestamp) as month,
  symbol_in as symbol,
  sum(amount_in_usd) as Amount_in_USD,
  count(tx_hash) as tx_count
from arbitrum.core.ez_dex_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
and platform = 'sushiswap'
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_arb as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD,
  count(tx_hash) as tx_count
from arbitrum.core.ez_dex_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
and platform = 'sushiswap'
group by 1,2
order by month DESC, amount_out_usd DESC
),
arbitrum_stables as (
select stables_in_arb.month,
   stables_in_arb.symbol,
   'arbitrum' as blockchain,
    stables_in_arb.tx_count + stables_out_arb.tx_count as tx_count,
   Amount_in_USD, 
   Amount_out_USD,
   Amount_in_USD + Amount_out_USD as total_volume,
   Amount_in_USD - Amount_out_USD as net_stablecoin_volume
from stables_in_arb
left join stables_out_arb
  on stables_in_arb.month = stables_out_arb.month and stables_in_arb.symbol = stables_out_arb.symbol
),
stables_in_ava as (
select date_trunc('month',block_timestamp) as month,
  symbol_in as symbol,
  sum(amount_in_usd) as Amount_in_USD,
  count(tx_hash) as tx_count
from avalanche.core.ez_dex_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
and platform = 'sushiswap'
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_ava as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD,
  count(tx_hash) as tx_count
from avalanche.core.ez_dex_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
and platform = 'sushiswap'
group by 1,2
order by month DESC, amount_out_usd DESC
),
ava_stables as (
select stables_in_ava.month,
   stables_in_ava.symbol,
   'avalanche' as blockchain,
    stables_in_ava.tx_count + stables_out_ava.tx_count as tx_count,
   Amount_in_USD, 
   Amount_out_USD,
   Amount_in_USD + Amount_out_USD as total_volume,
   Amount_in_USD - Amount_out_USD as net_stablecoin_volume
from stables_in_ava
left join stables_out_ava
  on stables_in_ava.month = stables_out_ava.month and stables_in_ava.symbol = stables_out_ava.symbol
),
stables_in_bsc as (
select date_trunc('month',block_timestamp) as month,
  symbol_in as symbol,
  sum(amount_in_usd) as Amount_in_USD,
  count(tx_hash) as tx_count
from bsc.core.ez_dex_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD','USDJ')
and platform = 'sushiswap'
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_bsc as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD,
  count(tx_hash) as tx_count
from bsc.core.ez_dex_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD','USDJ')
and platform = 'sushiswap'
group by 1,2
order by month DESC, amount_out_usd DESC
),
bsc_stables as (
select stables_in_bsc.month,
   stables_in_bsc.symbol,
   'bsc' as blockchain,
    stables_in_bsc.tx_count + stables_out_bsc.tx_count as tx_count,
   Amount_in_USD, 
   Amount_out_USD,
   Amount_in_USD + Amount_out_USD as total_volume,
   Amount_in_USD - Amount_out_USD as net_stablecoin_volume
from stables_in_bsc
left join stables_out_bsc
  on stables_in_bsc.month = stables_out_bsc.month and stables_in_bsc.symbol = stables_out_bsc.symbol
),
stables_in_gno as (
select date_trunc('month',block_timestamp) as month,
  symbol_in as symbol,
  sum(amount_in_usd) as Amount_in_USD,
  count(tx_hash) as tx_count
from gnosis.core.ez_dex_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
and platform = 'sushiswap'
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_gno as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD,
  count(tx_hash) as tx_count
from gnosis.core.ez_dex_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
and platform = 'sushiswap'
group by 1,2
order by month DESC, amount_out_usd DESC
),
gno_stables as (
select stables_in_gno.month,
   stables_in_gno.symbol,
   'gnosis' as blockchain,
    stables_in_gno.tx_count + stables_out_gno.tx_count as tx_count,
   Amount_in_USD, 
   Amount_out_USD,
   Amount_in_USD + Amount_out_USD as total_volume,
   Amount_in_USD - Amount_out_USD as net_stablecoin_volume
from stables_in_gno
left join stables_out_gno
  on stables_in_gno.month = stables_out_gno.month and stables_in_gno.symbol = stables_out_gno.symbol
),
stables_in_poly as (
select date_trunc('month',block_timestamp) as month,
  symbol_in as symbol,
  sum(amount_in_usd) as Amount_in_USD,
  count(tx_hash) as tx_count
from polygon.core.ez_dex_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
and platform = 'sushiswap'
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_poly as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD,
  count(tx_hash) as tx_count
from polygon.core.ez_dex_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
and platform = 'sushiswap'
group by 1,2
order by month DESC, amount_out_usd DESC
),
poly_stables as (
select stables_in_poly.month,
   stables_in_poly.symbol,
   'polygon' as blockchain,
    stables_in_poly.tx_count + stables_out_poly.tx_count as tx_count,
   Amount_in_USD, 
   Amount_out_USD,
   Amount_in_USD + Amount_out_USD as total_volume,
   Amount_in_USD - Amount_out_USD as net_stablecoin_volume
from stables_in_poly
left join stables_out_poly
  on stables_in_poly.month = stables_out_poly.month and stables_in_poly.symbol = stables_out_poly.symbol
)
select *
from eth_stables
union all 
select *
from op_stables
union all 
select *
from arbitrum_stables
union all
select *
from ava_stables
union all 
select *
from bsc_stables
union all
select *
from gno_stables
union all
select *
from poly_stables
"""
df = querying_pagination(sushi_stables_query)
# Title and introduction
st.title("🍣 Stablecoin Activity on SushiSwap")
main_text = """
This dashboard showcases stablecoin trading activity on SushiSwap across prominent blockchains such as Ethereum, Optimism, Arbitrum, and more. It provides valuable insights into monthly trading volumes, transaction counts, and net stablecoin volumes. The main page of this dashboard aims to answer the following questions:
"""

bullet_points = [
    "Which stablecoins are most actively traded on SushiSwap across Ethereum, Optimism, Arbitrum, and other chains?",
    "Which chain has seen the most stablecoin activity pick up in the last 3 months?"
]

in_depth_analysis_bullet = "For a more in-depth analysis of swap data on each individual chain, feel free to navigate through the pages available in the sidebar."

st.write(main_text)

for point in bullet_points:
    st.markdown(f"* {point}")

st.markdown(f"{in_depth_analysis_bullet}")

# Stablecoin volume by token
col1, col2 = st.columns(2)
df_tokens = df.groupby(['month', 'symbol'], as_index=False).agg({'total_volume': 'sum', 'net_stablecoin_volume': 'sum'})
df_tokens = df_tokens.sort_values(['month', 'total_volume'], ascending=[True, False])
fig1 = px.bar(df_tokens, x="month", y="total_volume", color="symbol", barmode="stack", title="Monthly Volume by Token")
col1.plotly_chart(fig1, use_container_width=True)

#stablexoin tx count by token
df_tx_count = df.groupby(['month', 'symbol'], as_index=False).agg({'tx_count': 'sum'})
df_tx_count = df_tx_count.sort_values(['month', 'tx_count'], ascending=[True, False])
fig_tx = px.bar(df_tx_count, x="month", y="tx_count", color="symbol", barmode="stack", title="Monthly Tx Count by Token")
col1.plotly_chart(fig_tx, use_container_width=True)

# Stablecoin volume by token (normalized)
df_normalized = df_tokens.copy()
df_normalized['total_volume_normalized'] = df_normalized.groupby(['month'])['total_volume'].apply(lambda x: x / x.sum())
fig2 = px.bar(df_normalized, x="month", y="total_volume_normalized", color="symbol", barmode="stack", title="Monthly Volume by Token (Normalized)")
col2.plotly_chart(fig2, use_container_width=True)

#stablecoin tx count by token (normalized)
df_tx_count_normalized = df_tx_count.copy()
df_tx_count_normalized['tx_count_normalized'] = df_tx_count_normalized.groupby(['month'])['tx_count'].apply(lambda x: x / x.sum())
fig_tx_normalized = px.bar(df_tx_count_normalized, x="month", y="tx_count_normalized", color="symbol", barmode="stack", title="Monthly Tx Count by Token (Normalized)")
col2.plotly_chart(fig_tx_normalized, use_container_width=True)

# Analysis and insights
st.subheader("Insights for Stablecoin Volume by Token")
st.write("""
Some insights can be derived from the above charts, such as:
- USDC is the top traded Stablecoin on Sushi with over $40B in trading volume all-time. 
- USDT and DAI are a close second and third with 21b and 18b in trading volume all-time
- In the summer of 2022 bull market, many alternative Stablecoins saw a surge in trading volume, eating away at the dominance of the top 3
- As the bull market ended, so did the surge in trading volume for alternative Stablecoins, and the top 3 Stablecoins regained dominance, accounting for 99% of trades in March 2023
- Looking at tx_count tells a slightly different story. While overall swap volume has trended down since 2021, the number of swaps has remained flat, indicating that users are swapping smaller amounts more frequently
""")

# Stablecoin volume by blockchain
col3, col4 = st.columns(2)
df_blockchain = df.groupby(['month', 'blockchain'], as_index=False).agg({'total_volume': 'sum', 'net_stablecoin_volume': 'sum'})
df_blockchain = df_blockchain.sort_values(['month', 'total_volume'], ascending=[True, False])
fig3 = px.bar(df_blockchain, x="month", y="total_volume", color="blockchain", barmode="stack", title="Monthly Volume by Blockchain")
col3.plotly_chart(fig3, use_container_width=True)

# Stablecoin volume by blockchain (normalized)
df_normalized_bchain = df.copy()
df_normalized_bchain['total_volume_normalized'] = df_normalized_bchain.groupby(['month'])['total_volume'].apply(lambda x: x / x.sum())
df_normalized_bchain = df_normalized_bchain.sort_values(['month', 'total_volume_normalized'], ascending=[True, False])
fig4 = px.bar(df_normalized_bchain, x="month", y="total_volume_normalized", color="blockchain", barmode="stack", title="Monthly Volume by Blockchain (Normalized)")
col4.plotly_chart(fig4, use_container_width=True)

#stablecoin tx count by blockchain
df_tx_count_bchain = df.groupby(['month', 'blockchain'], as_index=False).agg({'tx_count': 'sum'})
df_tx_count_bchain = df_tx_count_bchain.sort_values(['month', 'tx_count'], ascending=[True, False])
fig_tx_bchain = px.bar(df_tx_count_bchain, x="month", y="tx_count", color="blockchain", barmode="stack", title="Monthly Tx Count by Blockchain")
col3.plotly_chart(fig_tx_bchain, use_container_width=True)

#stablecoin tx count by blockchain (normalized)
df_tx_count_normalized_bchain = df_tx_count_bchain.copy()
df_tx_count_normalized_bchain['tx_count_normalized'] = df_tx_count_normalized_bchain.groupby(['month'])['tx_count'].apply(lambda x: x / x.sum())
fig_tx_normalized_bchain = px.bar(df_tx_count_normalized_bchain, x="month", y="tx_count_normalized", color="blockchain", barmode="stack", title="Monthly Tx Count by Blockchain (Normalized)")
col4.plotly_chart(fig_tx_normalized_bchain, use_container_width=True)


# Analysis and insights
st.subheader("Insights for Stablecoin Volume by Blockchain")
st.write('''
- Ethereum consistently leads the market with fluctuating volumes, peaking at \$13.4B in May 2021 and but down to  \$176M in March 2023.
- Arbitrum has experienced significant growth since May 2021, maintaining the second-highest position, with its peak in February 2022 at \$662.2M.
- Polygon ranks third with relatively stable volumes since October 2021, after growing from September 2020.
- Binance Smart Chain (BSC) ranks fourth or fifth, showing growth but still lagging behind the top three.
- Gnosis and Avalanche have minimal trading volumes, with Gnosis at zero in some months and Avalanche briefly surging to \$2.1B in January 2022.
- Transaction counts show a vastly different story. Ethereum accounts for only 13% of transactions in March 2023, while Arbitrum accounts for 45% of transactions. This clearly shows the emergence of layer 2 solutions, which are cheaper and faster than Ethereum.
''')



# Net stablecoin volume by token and blockchain
col5, col6 = st.columns(2)
fig5 = px.bar(df_tokens, x="month", y="net_stablecoin_volume", color="symbol", title="Net Stablecoin Volume by Token")
col5.plotly_chart(fig5, use_container_width=True)

fig6 = px.bar(df_blockchain, x="month", y="net_stablecoin_volume", color="blockchain", title="Net Stablecoin Volume by Blockchain")
col5.plotly_chart(fig6, use_container_width=True)

# Analysis and insights

col6.write(' ')
col6.subheader("Insights for Net Stablecoin Volume by Token")
col6.write('''
- Net stablecoin volume shows the difference between inflow and outflow of stablecoins on Sushiswap
- Prior to 2022, the dominant stablecoins (USDC, USDT, and DAI) had a net inflow to the platform, with a few exceptions
- In 2022, we see the raise of alternative stablecoins, notably OHM, which had a net inflow of \$110M in May 2022. A large portion of that money seems to have come from USDC and DAI, which both experienced large outflows that month. 
- As OHM came crashing down in early 2022, we do not see a sinificant net inflow of other stablecoins, indicating that much of this value was simply lost
- Stablecoin inflow/outflows have remained relatively stable since, indicating that people aren't moving their stablecoins around as much as they were in 2022
''')

col6.write(' ')
col6.write(' ')
col6.write(' ') 

col6.subheader("Insights for Net Stablecoin Volume by Blockchain")
col6.write('''
- Net stablecoin volume by blockchain shows inflows and outflows of stablecoins on sushiswap to different blockchains
- We again see Ethereum dominating until the end of 2021, when alternative blockchains start to gain traction
- Arbitrum and Polygon have seen significant growth in net stablecoin volume since 2021
- While Ethereum is still the dominant blockchain, the growth of alternative blockchains is a sign of the growing decentralization of DeFi
'''
)

st.subheader('Conclusion')
st.write('''
Stablecoin swap data on Sushiswap shows that while Ethereum is still clearly the dominant blockchain, alternative blockchains are gaining traction.
USDC, USDT, and DAI are still the dominant stablecoins accross all chains. While we saw a brief period where alternative stablecoins gained traction, they have since lost their momentum and we have returned to the dominance of USDC, USDC, and DAI.
Since its debut in April 2022, Arbitrum has steadily risin in popularity, accounting for 20% of swap volume in March 2023. Polygon has seen a decline in its share of swap volume since October 2021, but is still holding a consistent share of swaps. By transaction count, however, layer 2 solutions are taking over. Arbitrum accounts for 45% of transactions, while Ethereum accounts for only 13%. This shows that layer 2 solutions are cheaper and faster than Ethereum, and are becoming the preferred choice for traders.
''')
st.write('''While analyzing chain specific data, I noticed a trend on both Binance Smart Chain and Avalanche. Both chains launched with a native stablecoin which dominated the volume early on, but as the chains have matured, the Crosschain giants slowly ate away at the market share. This tells me that traders value the interchain interoperability over the native stablecoin.
''')

st.subheader('Methodology')
st.write('''
In order to create this dashboard, we employed the following methodology:

Data Collection: We obtained data from the Flipside SDK, which provides comprehensive and accurate insights into the activities on Sushiswap. The source code for the dashboard can be found at https://github.com/dghughes84/Sushiswap-Stablecoins/tree/master/Sushi_stables_app. 

Identification of Stablecoins: To identify the stablecoins to be analyzed, we combined information from two sources. First, we referred to the top stablecoins listed on Coingecko. Second, we extracted the top pools by trade volume on Sushiswap and filtered out non-stablecoin pools.

Trade Volume Data Retrieval: Once we had a list of stablecoins to track, we collected the trade volume data for each stablecoin on Sushiswap. The data was then aggregated on a monthly basis to enable a clear understanding of stablecoin trends.

Calculation of Net Stablecoin Volume: We calculated the net stablecoin volume for each token by taking the difference between Amount_in_USD and Amount_out_USD. This metric provides insights into the net inflows and outflows of each stablecoin.
''')