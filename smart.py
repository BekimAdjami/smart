import tinytuya
import pandas as pd
import streamlit as st
import time
import matplotlib.pyplot as plt

# Tuya Device Details
DEVICE_ID = "bfe6eea0f884ddbebagvmx"
LOCAL_KEY = "e5Og=a|_{c-tD`.>"
IP_ADDRESS = "192.168.1.18"

device = tinytuya.OutletDevice(DEVICE_ID, IP_ADDRESS, LOCAL_KEY)
device.set_version(3.3)

# Create or load the DataFrame
csv_file = "power_usage.csv"
try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Time", "Power (W)", "Voltage (V)", "Current (mA)", "Energy (kWh)"])
    df.to_csv(csv_file, index=False)

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

# Auto-update every 5 seconds
placeholder = st.empty()
while True:
    timestamp, power, voltage, current, energy = get_realtime_data()
    new_row = pd.DataFrame([[timestamp, power, voltage, current, energy]], columns=df.columns)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(csv_file, index=False)
    
    with placeholder.container():
        st.subheader("Current Readings")
        st.write(df.iloc[-1])
        
        # Plot data
        st.subheader("Power Usage Over Time")
        df["Time"] = pd.to_datetime(df["Time"])
        fig, ax = plt.subplots()
        ax.plot(df["Time"], df["Power (W)"], label="Power (W)", color="blue")
        ax.set_xlabel("Time")
        ax.set_ylabel("Power (W)")
        ax.legend()
        st.pyplot(fig)
    
    time.sleep(5)
