import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# [NOTE] ตั้งค่าฟอนต์พื้นฐานสำหรับ Streamlit Cloud เพื่อแก้ปัญหาตัวอักษรกล่องสี่เหลี่ยม
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans'] 

st.set_page_config(page_title="Sun to Sort", layout="wide")

st.title("🌞 Sun to Sort: ระบบคำนวณพลังงานแสงอาทิตย์สำหรับศูนย์คัดแยกขยะ")
st.caption("โปรแกรมต้นแบบจากค่าย CalcTech Camp x CASIO | เขียนด้วย Python + Streamlit")

# ----------------------------
# 1. รับค่าจากผู้ใช้ (Inputs)
# ----------------------------
st.subheader("⚙️ ข้อมูลศูนย์คัดแยกและระบบโซลาร์เซลล์")

col1, col2 = st.columns(2)
with col1:
    waste_type = st.selectbox("ประเภทขยะหลัก", ["พลาสติก", "กระดาษ", "อินทรีย์", "อื่น ๆ"], index=0)
    # [INPUT] ปริมาณและเครื่องจักรที่เกี่ยวข้องกับการใช้พลังงาน
    waste_amount = st.number_input("ปริมาณขยะต่อวัน (กิโลกรัม)", min_value=1.0, value=500.0)
    machine_count = st.number_input("จำนวนเครื่องจักร", min_value=1, step=1, value=5)
    power_per_machine = st.number_input("กำลังไฟต่อเครื่อง (วัตต์)", min_value=100.0, value=500.0)

with col2:
    # [INPUT] ปัจจัยในการผลิตพลังงาน
    work_hours = st.number_input("ชั่วโมงทำงานต่อวัน", min_value=1.0, max_value=24.0, value=8.0)
    sunlight_hours = st.number_input("ชั่วโมงแดดเฉลี่ยต่อวัน", min_value=1.0, max_value=12.0, value=5.0)
    panel_power = st.number_input("กำลังแผงต่อแผง (วัตต์)", min_value=100.0, value=300.0)

# ----------------------------
# 2. คำนวณ (ใช้ st.button เพื่อสั่งให้คำนวณเมื่อพร้อม)
# ----------------------------
if st.button("☀️ คำนวณพลังงาน"):
    
    # (1) พลังงานที่ใช้จริงต่อวัน (Demand)
    energy_used = (machine_count * power_per_machine * work_hours) / 1000  # kWh per day
    
    # (2) พลังงานผลิตได้ต่อแผงต่อวัน (Supply Per Panel)
    # 0.75 คือค่าประสิทธิภาพของระบบ (Efficiency)
    energy_per_panel = (panel_power * sunlight_hours * 0.75) / 1000        # kWh per panel per day
    
    # (3) จำนวนแผงที่ต้องใช้ (Panels Needed)
    panels_needed = energy_used / energy_per_panel if energy_per_panel > 0 else 0
    
    # (4) คาร์บอนที่ลดได้ต่อเดือน (CO₂ Reduction)
    co2_saved = energy_used * 0.43 * 30  # kgCO₂/month (0.43 kgCO₂/kWh)
    
    # (5) พลังงานผลิตได้รวมทั้งหมด (Total Supply)
    total_energy_produced = energy_per_panel * panels_needed 
    
    # ----------------------------
    # 3. แสดงผล (Metrics)
    # ----------------------------
    st.subheader("🔍 ผลลัพธ์การคำนวณ: ความสมดุลของระบบ")
    
    col_met1, col_met2, col_met3, col_met4 = st.columns(4)
    col_met1.metric("พลังงานที่ใช้ต่อวัน", f"{energy_used:.2f} kWh")
    col_met2.metric("พลังงานผลิตได้รวมต่อวัน", f"{total_energy_produced:.2f} kWh")
    col_met3.metric("จำนวนแผงที่ต้องใช้", f"{panels_needed:.1f} แผง")
    col_met4.metric("คาร์บอนที่ลดได้ต่อเดือน", f"{co2_saved:.1f} kgCO₂")

    # ----------------------------
    # 4. สร้างกราฟ (ภาษาอังกฤษล้วน)
    # ----------------------------
    st.subheader("📊 Energy Balance Chart") 
    fig, ax = plt.subplots(figsize=(8, 4)) 

    categories = ["Energy Used", "Energy Produced"]
    values = [energy_used, total_energy_produced]

    ax.bar(categories, values, color=["#ffb703", "#219ebc"])
    ax.set_ylabel("Energy (kWh)") 
    ax.set_title("Actual Energy Use vs. Required Production") 
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    st.pyplot(fig) 

    # ----------------------------
    # 5. ดาวน์โหลดผลลัพธ์
    # ----------------------------
    df = pd.DataFrame({
        "Item": ["Actual Energy Use (kWh)", "Total Energy Produced (kWh)", "Panels Needed", "CO2 Saved (kg/month)"], 
        "Value": [energy_used, total_energy_produced, panels_needed, co2_saved]
    })

    st.download_button(
        label="📥 Download Results (CSV)", 
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="sun_to_sort_result.csv",
        mime="text/csv",
    )

st.info("💡 คำแนะนำ: กดปุ่ม '☀️ คำนวณพลังงาน' เพื่อดูผลลัพธ์และกราฟ")
