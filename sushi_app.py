# Import necessary libraries
import streamlit as st
import pandas as pd
from shroomdk import ShroomDK
import os
import config
import plotly.express as px
import openai

openai_key = config.openai_key_2
openai.api_key = openai_key
#sdk = ShroomDK(config.shroomdk_key)

#title of the app Sushi Chain Dominance
st.title('🍣 Sushi Chain Dominance')
#subtitle of the app - introduction
st.subheader('Introduction')
#introduction to the app
st.write("Welcome to my SushiSwap Analytics Dashboard, designed to provide a centralized location for monitoring SushiSwap's volume and growth on various blockchains. This dashboard aims to answer questions such as which chains have the most volume and how SushiSwap's volume compares to other DEXes on chains such as Polygon, Avalanche, and Arbitrum. We will also compare SushiSwap's volume with Uniswap's volume on applicable chains. The dashboard includes charts such as volume by chain, monthly changes in volume, number of users LPing, top LP pools per chain, and a comparison of incentives and rewards for pools on each chain. Our goal is to provide insights to help make informed decisions regarding investment in SushiSwap.")

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



sushi_eth_top_pools_volumne="""
    WITH top_pools AS (
    SELECT 
        POOL_NAME,
        DATE_TRUNC('month', TO_TIMESTAMP(BLOCK_TIMESTAMP)) AS MONTH,
        SUM(AMOUNT_IN_USD) AS MONTHLY_VOLUME_USD
    FROM 
        ethereum.sushi.ez_swaps
    GROUP BY 
        POOL_NAME, 
        MONTH
), 
pools_ranked AS (
    SELECT 
        POOL_NAME,
        MONTH,
        MONTHLY_VOLUME_USD,
        RANK() OVER (PARTITION BY MONTH ORDER BY MONTHLY_VOLUME_USD DESC) AS pool_rank
    FROM 
        top_pools
    WHERE 
        MONTHLY_VOLUME_USD IS NOT NULL
), 
other_pools AS (
    SELECT 
        'Other Pools' AS POOL_NAME,
        MONTH,
        MONTHLY_VOLUME_USD,
        'other' as pool_rank
    FROM 
        pools_ranked
    WHERE 
        pool_rank > 5
),
other_pools_agg AS(
    SELECT 
            POOL_NAME,
            MONTH,
            SUM(MONTHLY_VOLUME_USD) AS MONTHLY_VOLUME_USD,
            pool_rank
        FROM other_pools
        GROUP BY POOL_NAME, MONTH, pool_rank
)


SELECT 
    MONTH,
    POOL_NAME,
    MONTHLY_VOLUME_USD
FROM 
    (
        SELECT * FROM pools_ranked
        WHERE pool_rank <= 5
        UNION ALL
        SELECT * FROM other_pools_agg
    ) AS combined_pools
ORDER BY 
    MONTH DESC, 
    MONTHLY_VOLUME_USD DESC

"""
sushi_eth_top_pools_volumne = querying_pagination(sushi_eth_top_pools_volumne)

sushi_stables_query = """
with stables_in_eth as (
select date_trunc('month',block_timestamp) as month,
  symbol_in as symbol,
  sum(amount_in_usd) as Amount_in_USD
from ethereum.sushi.ez_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM')
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_eth as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD
from ethereum.sushi.ez_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM')
group by 1,2
order by month DESC, amount_out_usd DESC
),
eth_stables as (
select stables_in_eth.month,
   stables_in_eth.symbol,
   'Ethereum' as blockchain,
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
  sum(amount_in_usd) as Amount_in_USD
from optimism.sushi.ez_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_op as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD
from optimism.sushi.ez_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
group by 1,2
order by month DESC, amount_out_usd DESC
),
op_stables as (
select stables_in_op.month,
   stables_in_op.symbol,
   'optimism' as blockchain,
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
  sum(amount_in_usd) as Amount_in_USD
from arbitrum.sushi.ez_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_arb as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD
from arbitrum.sushi.ez_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
group by 1,2
order by month DESC, amount_out_usd DESC
),
arbitrum_stables as (
select stables_in_arb.month,
   stables_in_arb.symbol,
   'arbitrum' as blockchain,
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
),
ava_stables as (
select stables_in_ava.month,
   stables_in_ava.symbol,
   'avalanche' as blockchain,
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
),
bsc_stables as (
select stables_in_bsc.month,
   stables_in_bsc.symbol,
   'bsc' as blockchain,
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
  sum(amount_in_usd) as Amount_in_USD
from gnosis.sushi.ez_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_gno as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD
from gnosis.sushi.ez_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
group by 1,2
order by month DESC, amount_out_usd DESC
),
gno_stables as (
select stables_in_gno.month,
   stables_in_gno.symbol,
   'gnosis' as blockchain,
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
  sum(amount_in_usd) as Amount_in_USD
from polygon.sushi.ez_swaps
where symbol_in in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
group by 1,2
order by month DESC, amount_in_usd DESC
),
stables_out_poly as (
select date_trunc('month',block_timestamp) as month,
  symbol_out as symbol,
  sum(amount_out_usd) as Amount_out_USD
from polygon.sushi.ez_swaps
where symbol_out in ('USDT', 'USDC', 'DAI','BUSD','TUSD','FRAX','USDP','USDD','GUSD','PAXG','XAUT','LUSD','EURT','USTC','ALUSD','EURS','MIM','USDX','DOLA','XSGD','RAI','GHO','OHM','sUSD')
group by 1,2
order by month DESC, amount_out_usd DESC
),
poly_stables as (
select stables_in_poly.month,
   stables_in_poly.symbol,
   'polygon' as blockchain,
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
sushi_stables = querying_pagination(sushi_stables_query)
st.dataframe(sushi_stables)

st.write(openai.Model.list())

gpt = openai.Model("gpt-3.5-turbo")
def generate_summary_and_conclusion(data):
    prompt = f"Please write a summary and conclusion for the following data: {data}"
    response = gpt.generate(prompt, max_length=200, temperature=0.5, stop=["\n"])
    return response.choices[0].text.strip()

summary_and_conclusion = generate_summary_and_conclusion(sushi_stables)
st.write(summary_and_conclusion)
#make a chart of the top pools by volume
sushi_eth_top_pools_volumne_bar = px.bar(sushi_eth_top_pools_volumne, x='month', y='monthly_volume_usd', color='pool_name', barmode='stack')
#title the chart - 'Monthly Sushiswap Volume on Ethereum - top 5 pools'
sushi_eth_top_pools_volumne_bar.update_layout(title='Monthly Sushiswap Volume on Ethereum - top 5 pools')
#make 2 columns - 1 for the chart and 1 for the text
col1, col2 = st.columns(2)
#put the chart in the first column
col1.plotly_chart(sushi_eth_top_pools_volumne_bar)

############ OPEN AI STUFF - NOT WORKING (maybe try langChain or llamaindex) ############
# sushi_eth_top_pools_volumne_str = sushi_eth_top_pools_volumne.to_string(index=False)
# prompt = "Describe the data in this table:\n" + sushi_eth_top_pools_volumne_str

# response = openai.ChatCompletion.create(
#   model="gpt-3.5-turbo",
#    messages=[
#         {"role": "system", "content": "You are a data scientist tasked with explaining data about sushiswap stored in this table {sushi_eth_top_pools_volume_str}"}
#     ]
# )
# col2.write(response.choices[0])
# #description = response.choices[0].text.strip()
# #print(description)

sushi_swap_volume = """
SELECT 
    DATE_TRUNC('month', TO_TIMESTAMP(BLOCK_TIMESTAMP)) AS MONTH,
    SUM(AMOUNT_IN_USD) AS MONTHLY_VOLUME_USD,
    'Arbitrum' as chain
FROM 
    arbitrum.sushi.ez_swaps
WHERE
    AMOUNT_IN_USD IS NOT NULL
GROUP BY 
    MONTH


union all

SELECT 
    DATE_TRUNC('month', TO_TIMESTAMP(BLOCK_TIMESTAMP)) AS MONTH,
    SUM(AMOUNT_IN_USD) AS MONTHLY_VOLUME_USD,
    'Ethereum' as chain
FROM 
    ethereum.sushi.ez_swaps
WHERE
    AMOUNT_IN_USD IS NOT NULL
GROUP BY 
    MONTH

union all

SELECT 
    DATE_TRUNC('month', TO_TIMESTAMP(BLOCK_TIMESTAMP)) AS MONTH,
    SUM(AMOUNT_IN_USD) AS MONTHLY_VOLUME_USD,
    'Avalanche' as chain
FROM 
    avalanche.sushi.ez_swaps
WHERE
    AMOUNT_IN_USD IS NOT NULL
GROUP BY 
    MONTH

union all

SELECT 
    DATE_TRUNC('month', TO_TIMESTAMP(BLOCK_TIMESTAMP)) AS MONTH,
    SUM(AMOUNT_IN_USD) AS MONTHLY_VOLUME_USD,
    'Gnosis' as chain
FROM 
     gnosis.sushi.ez_swaps
WHERE
    AMOUNT_IN_USD IS NOT NULL
GROUP BY 
    MONTH

union all

SELECT 
    DATE_TRUNC('month', TO_TIMESTAMP(BLOCK_TIMESTAMP)) AS MONTH,
    SUM(AMOUNT_IN_USD) AS MONTHLY_VOLUME_USD,
    'Optimism' as chain
FROM 
     optimism.sushi.ez_swaps
WHERE
    AMOUNT_IN_USD IS NOT NULL
GROUP BY 
    MONTH

union all

SELECT 
    DATE_TRUNC('month', TO_TIMESTAMP(BLOCK_TIMESTAMP)) AS MONTH,
    SUM(AMOUNT_IN_USD) AS MONTHLY_VOLUME_USD,
    'Polygon' as chain
FROM 
     polygon.sushi.ez_swaps
WHERE
    AMOUNT_IN_USD IS NOT NULL
GROUP BY 
    MONTH

"""
sushi_swap_volume = querying_pagination(sushi_swap_volume)
sushi_swap_volume

sushi_swap_volume_bar = px.bar(sushi_swap_volume, x='month', y='monthly_volume_usd', color='chain', barmode='stack')

st.plotly_chart(sushi_swap_volume_bar)

#graph swap data by chain but show the percent of the total volume each chain had each month
sushi_swap_volume_noralized = sushi_swap_volume.groupby(['month','chain']).sum().reset_index()
sushi_swap_volume_noralized['percent_of_total'] = sushi_swap_volume_noralized.groupby('month')['monthly_volume_usd'].apply(lambda x: 100 * x / float(x.sum()))
sushi_swap_volume_noralized = sushi_swap_volume_noralized.sort_values('percent_of_total', ascending=False)
#bar chart showing sushi_swap_volume_noralized
sushi_swap_volume_noralized_bar = px.bar(sushi_swap_volume_noralized, x='month', y='percent_of_total', color='chain', barmode='stack')
st.plotly_chart(sushi_swap_volume_noralized_bar)





