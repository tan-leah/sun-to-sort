import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm 

# NOTE: กำหนดให้ Matplotlib ใช้ฟอนต์พื้นฐานที่ Streamlit Cloud รองรับ
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans'] 


st.set_page_config(page_title="Sun to Sort", layout="wide")

st.title("🌞 Sun to Sort: ระบบคำนวณพลังงานแสงอาทิตย์สำหรับศูนย์คัดแยกขยะ")
st.caption("โปรแกรมต้นแบบจากค่าย CalcTech Camp x CASIO | เขียนด้วย Python + Streamlit")

# ----------------------------
# รับค่าจากผู้ใช้ (Inputs)
# ----------------------------
col1, col2 = st.columns(2)
with col1:
    waste_type = st.selectbox("ประเภทขยะหลัก", ["พลาสติก", "กระดาษ", "อินทรีย์", "อื่น ๆ"], index=1) # index=1 เพื่อเลือกกระดาษเป็นค่าเริ่มต้น
    waste_amount = st.number_input("ปริมาณขยะต่อวัน (กิโลกรัม)", min_value=1.0, value=500.0)
    machine_count = st.number_input("จำนวนเครื่องจักร", min_value=1, step=1, value=5)
    power_per_machine = st.number_input("กำลังไฟต่อเครื่อง (วัตต์)", min_value=100.0, value=500.0)

with col2:
    work_hours = st.number_input("ชั่วโมงทำงานต่อวัน", min_value=1.0, max_value=24.0, value=8.0)
    sunlight_hours = st.number_input("ชั่วโมงแดดเฉลี่ยต่อวัน", min_value=1.0, max_value=12.0, value=5.0)
    panel_power = st.number_input("กำลังแผงต่อแผง (วัตต์)", min_value=100.0, value=300.0)

# ----------------------------
# คำนวณและแสดงผลอัตโนมัติ (Real-time update)
# ----------------------------

# คำนวณ
energy_used = (machine_count * power_per_machine * work_hours) / 1000  # kWh per day
energy_per_panel = (panel_power * sunlight_hours * 0.75) / 1000        # kWh per panel per day (0.75 is assumed efficiency)
panels_needed = energy_used / energy_per_panel if energy_per_panel > 0 else 0
co2_saved = energy_used * 0.43 * 30  # kgCO₂/month (using 0.43 kgCO₂/kWh as assumed average)
total_energy_produced = energy_per_panel * panels_needed 

# แสดงผล (Metrics)
st.subheader("🔍 ผลลัพธ์การคำนวณ")
st.metric("พลังงานที่ใช้ต่อวัน", f"{energy_used:.2f} kWh")
st.metric("พลังงานที่ผลิตได้ต่อแผงต่อวัน", f"{energy_per_panel:.2f} kWh")
st.metric("จำนวนแผงที่ต้องใช้", f"{panels_needed:.1f} แผง")
st.metric("คาร์บอนที่ลดได้ต่อเดือน", f"{co2_saved:.1f} kgCO₂")

# ----------------------------
# สร้างกราฟ (ภาษาอังกฤษล้วน)
# ----------------------------
st.subheader("📊 Energy Comparison Chart") 
fig, ax = plt.subplots(figsize=(8, 4)) # กำหนดขนาดกราฟให้ดูดีขึ้น

# [FIX] ใช้ค่าที่คำนวณจริง: energy_used และ total_energy_produced
categories = ["Energy Used", "Energy Produced"]
values = [energy_used, total_energy_produced]

# สร้างกราฟแท่ง
ax.bar(categories, values, color=["#ffb703", "#219ebc"])

# [FIX] กำหนดชื่อแกนและชื่อกราฟเป็นภาษาอังกฤษล้วน (แก้ปัญหาฟอนต์)
ax.set_ylabel("Energy (kWh)") 
ax.set_title("Actual Energy Use vs. Required Production") 

# [NOTE] เพื่อความง่ายในการอ่านค่า อาจเพิ่มเส้น Grid
ax.grid(axis='y', linestyle='--', alpha=0.7)

st.pyplot(fig) # แสดงกราฟ

# ----------------------------
# ดาวน์โหลดผลลัพธ์เป็น CSV
# ----------------------------
df = pd.DataFrame({
    "Item": ["Actual Energy Use", "Total Energy Produced", "Panels Needed", "CO2 Saved (kg/month)"], 
    "Value": [energy_used, total_energy_produced, panels_needed, co2_saved]
})

st.download_button(
    label="📥 Download Results (CSV)", 
    data=df.to_csv(index=False).encode('utf-8'),
    file_name="sun_to_sort_result.csv",
    mime="text/csv",
)

st.info("💡 คำแนะนำ: ปรับค่าชั่วโมงแดดและกำลังแผงเพื่อดูการเปลี่ยนแปลงของผลลัพธ์แบบเรียลไทม์")
