import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yfinance as yf
st.set_option('deprecation.showPyplotGlobalUse', False)

st.title('Nifty50 Stock Price App')

st.markdown("""
This app retrieves the list of the **Nifty50** (from Wikipedia) and its corresponding **stock closing price** (year-to-date)!
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
* **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/NIFTY_50).
""")

st.sidebar.header('User Input Features')

# Web scraping of Nifty50 data

@st.cache_data
def load_data():
    url = "https://en.wikipedia.org/wiki/NIFTY_50"
    html = pd.read_html(url, header = 0)
    df = html[2]
    return df

df = load_data()
df['Yahoo_Symbol'] = 'Hello World'
df.Yahoo_Symbol = df.Symbol + '.NS'

sector = df.groupby('Sector[18]')

# Sidebar - Sector selection
sorted_sector_unique = df['Sector[18]'].unique()
selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

# filtering data
df_selected_sector = df[(df['Sector[18]'].isin(selected_sector))]
st.header('Display Companies in Selected Sector')
st.write('Data Dimension: ' + str(df_selected_sector.shape[0]) + ' rows and ' + str(df_selected_sector.shape[1]) + ' columns.')
st.dataframe(df_selected_sector)


# download Nifty50 data
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="Nifty50.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

data = yf.download(tickers = list(df.Yahoo_Symbol),
                   period= 'ytd',
                   interval = '1d',
                   group_by = 'ticker',
                   auto_adjust = True,
                   prepost = True,
                   threads = True,
                   proxy = None)


# Plot Closing Price of Query Symbol
def price_plot(symbol):
    if ('.NS' not in symbol):
        symbol = symbol + ".NS"
    df2 = pd.DataFrame(data[symbol].Close)
    df2['Date'] = df2.index

    # fill the colour
    plt.fill_between(df2.Date, df2.Close, color='skyblue', alpha=0.4)

    # plot the closing prices, i.e. make the oultline
    plt.plot(df2.Date, df2.Close, color='skyblue', alpha=1)
    plt.xticks(rotation=90)
    plt.title(symbol, fontweight='bold')
    plt.xlabel("Date", fontweight='bold')
    plt.ylabel("Closing price", fontweight='bold')
    return st.pyplot()

num_company = st.sidebar.slider('Number of Companies', 1, 5)

if st.button('Show Plots'):
    st.header('Stock Closing Price')
    for company in list(df_selected_sector.Yahoo_Symbol)[:num_company]:
        price_plot(company)