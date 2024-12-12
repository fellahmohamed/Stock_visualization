import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# --- PAGE CONFIGURATION ---
# Set page config to make the layout wide
st.set_page_config(layout="wide")

# --- TITLE AND INTRODUCTION ---
# Title and description for the app
st.title("Stock Price Viewer")
st.markdown("""
    This app allows you to visualize stock data for any company symbol. 
    You can select the period and choose between a candlestick or line chart.
    Additional technical indicators are available.
""", unsafe_allow_html=True)

# --- SIDEBAR INPUTS ---
# Sidebar inputs for user interaction
st.sidebar.header("Stock Data Inputs")
symbol = st.sidebar.text_input("Enter Stock Symbol", value="AAPL")
period = st.sidebar.selectbox("Select Period", options=["1d", "1mo", "3mo", "6mo", "1y", "5y"], index=1)
plot_type = st.sidebar.radio("Select Plot Type", options=["Candlestick", "Line"])
show_sma = st.sidebar.checkbox("Show 50-Day SMA", value=True)
show_bollinger = st.sidebar.checkbox("Show Bollinger Bands")

# --- RETRIEVE STOCK DATA ---
# Retrieve stock data based on user inputs
ticker = yf.Ticker(symbol)
data = ticker.history(period=period)

# --- ADDITIONAL COMPANY INFO ---
# Fetch additional company information
company_info = ticker.info
company_name = company_info.get('longName', 'N/A')
sector = company_info.get('sector', 'N/A')
industry = company_info.get('industry', 'N/A')
high_price = data['High'].max()
low_price = data['Low'].min()

# Display company info with improved styling
st.markdown(f"""
    <h2 style="color: #2C3E50; font-size: 26px; font-weight: bold;">{company_name}</h2>
    <p style="color: #34495E; font-size: 18px;">Sector: <span style="color: #2980B9;">{sector}</span></p>
    <p style="color: #34495E; font-size: 18px;">Industry: <span style="color: #2980B9;">{industry}</span></p>
    <p style="color: #34495E; font-size: 18px;">Highest Price in Period: <span style="color: #27AE60;">${high_price:.2f}</span></p>
    <p style="color: #34495E; font-size: 18px;">Lowest Price in Period: <span style="color: #E74C3C;">${low_price:.2f}</span></p>
""", unsafe_allow_html=True)

# --- PLOT CREATION ---
# Create the appropriate plot based on plot type
if plot_type == "Candlestick":
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        increasing=dict(line=dict(color='green'), fillcolor='green'),  # Green for increasing
        decreasing=dict(line=dict(color='red'), fillcolor='red')       # Red for decreasing
    )])
else:
    # Line plot with green and red sections
    fig = go.Figure()

    # Add green and red sections to the line chart
    for i in range(1, len(data)):
        color = 'green' if data['Close'][i] > data['Close'][i-1] else 'red'
        fig.add_trace(go.Scatter(
            x=[data.index[i-1], data.index[i]],
            y=[data['Close'][i-1], data['Close'][i]],
            mode='lines',
            line=dict(color=color, width=2),
            showlegend=False
        ))

    # Optionally add the moving average if selected
    if show_sma:
        data['SMA50'] = data['Close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['SMA50'],
            mode='lines',
            name='50-Day SMA',
            line=dict(color='blue', width=2)
        ))

    # Optionally add Bollinger Bands
    if show_bollinger:
        data['SMA50'] = data['Close'].rolling(window=50).mean()
        data['StdDev'] = data['Close'].rolling(window=50).std()
        data['UpperBand'] = data['SMA50'] + (data['StdDev'] * 2)
        data['LowerBand'] = data['SMA50'] - (data['StdDev'] * 2)
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['UpperBand'],
            mode='lines',
            name='Upper Bollinger Band',
            line=dict(color='orange', dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['LowerBand'],
            mode='lines',
            name='Lower Bollinger Band',
            line=dict(color='orange', dash='dash')
        ))

# --- CHART LAYOUT CUSTOMIZATION ---
# Customize the chart layout with better design
fig.update_layout(
    title=f"<b>{symbol}</b> {plot_type} Chart ({period})",
    title_x=0.4,
    title_font=dict(size=18, color="white"),
    yaxis_title="Price (USD)",
    xaxis_title="Date",
    plot_bgcolor="#f2f2f2",  # Light gray background for the plot
    # paper_bgcolor="#ffffff",  # White background for the page
    xaxis_rangeslider_visible=False,
    template="plotly_dark",  # Dark theme for a better visual appeal

)

# Display the chart
st.plotly_chart(fig, use_container_width=True)

