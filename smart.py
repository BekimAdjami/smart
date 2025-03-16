import tinytuya
import pandas as pd
import streamlit as st
import time
import matplotlib.pyplot as plt
import os

# Tuya Device Details
DEVICE_ID = "bfe6eea0f884ddbebagvmx"
LOCAL_KEY = "e5Og=a|_{c-tD`.>"
IP_ADDRESS = "192.168.1.18"

device = tinytuya.OutletDevice(DEVICE_ID, IP_ADDRESS, LOCAL_KEY)
device.set_version(3.3)

# Initialize DataFrame in session state
if "df" not in st.session_state:
    if os.path.exists("power_usage.csv"):
        st.session_state.df = pd.read_csv("power_usage.csv")
    else:
        st.session_state.df = pd.DataFrame(columns=["Time", "Power (W)", "Voltage (V)", "Current (mA)", "Energy (kWh)"])

st.title("Smart Socket Dashboard")
st.write("Live power consumption and statistics from your Tuya Smart Plug.")

# Fetch real-time data
def get_realtime_data():
    data = device.status()
    power = data.get("dps", {}).get("19", 0) / 10
    voltage = data.get("dps", {}).get("20", 0) / 10
    current = data.get("dps", {}).get("18", 0)
    energy = data.get("dps", {}).get("17", 0) / 1000
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp, power, voltage, current, energy

# Button to refresh data
if st.button("Update Data"):
    timestamp, power, voltage, current, energy = get_realtime_data()
    new_row = pd.DataFrame([[timestamp, power, voltage, current, energy]], columns=st.session_state.df.columns)
    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)

    # Save CSV only if running locally
    if not os.environ.get("STREAMLIT_SERVER"):
        st.session_state.df.to_csv("power_usage.csv", index=False)

# Display data
st.subheader("Current Readings")
st.write(st.session_state.df.iloc[-1] if not st.session_state.df.empty else "No data yet")

# Plot data
st.subheader("Power Usage Over Time")
if not st.session_state.df.empty:
    st.session_state.df["Time"] = pd.to_datetime(st.session_state.df["Time"])
    fig, ax = plt.subplots()
    ax.plot(st.session_state.df["Time"], st.session_state.df["Power (W)"], label="Power (W)", color="blue")
    ax.set_xlabel("Time")
    ax.set_ylabel("Power (W)")
    ax.legend()
    st.pyplot(fig)
else:
    st.write("No data available yet. Click 'Update Data' to start.")
