import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# [NOTE] ตั้งค่าฟอนต์พื้นฐานสำหรับ Streamlit Cloud
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans'] 

st.set_page_config(page_title="Sun to Sort", layout="wide")

st.title("🌞 Sun to Sort: ระบบคำนวณพลังงานแสงอาทิตย์สำหรับศูนย์คัดแยกขยะ")
st.caption("โปรแกรมต้นแบบจากค่าย CalcTech Camp x CASIO | เขียนด้วย Python + Streamlit")

# ----------------------------
# 1. รับค่าจากผู้ใช้ (Inputs)
# ----------------------------
st.subheader("⚙️ ข้อมูลศูนย์คัดแยกและระบบโซลาร์เซลล์")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**ข้อมูลภาระการใช้พลังงาน (Demand)**")
    waste_type = st.selectbox("ประเภทขยะหลัก", ["พลาสติก", "กระดาษ", "อินทรีย์", "อื่น ๆ"], index=0)
    waste_amount = st.number_input("ปริมาณขยะต่อวัน (กิโลกรัม)", min_value=1.0, value=500.0)
    machine_count = st.number_input("จำนวนเครื่องจักร", min_value=1, step=1, value=5)
    power_per_machine = st.number_input("กำลังไฟเฉลี่ยต่อเครื่อง (วัตต์)", min_value=100.0, value=500.0)

with col2:
    st.markdown("**ข้อมูลการผลิตพลังงาน (Supply)**")
    work_hours = st.number_input("ชั่วโมงทำงานต่อวัน", min_value=1.0, max_value=24.0, value=8.0)
    sunlight_hours = st.number_input("ชั่วโมงแดดเฉลี่ยต่อวัน", min_value=1.0, max_value=12.0, value=5.0)
    panel_power = st.number_input("กำลังแผงต่อแผง (วัตต์)", min_value=100.0, value=300.0)
    
    # [NEW INPUT] จำนวนแผงที่ติดตั้งจริง
    actual_installed_panels = st.number_input("จำนวนแผงที่ติดตั้งจริง (แผง)", min_value=1, step=1, value=100) 

with col3:
    st.markdown("**ข้อมูลวิเคราะห์ความคุ้มค่า (Economics)**")
    # [NEW INPUT] ค่าติดตั้งและค่าไฟ
    investment_cost = st.number_input("เงินลงทุนติดตั้งระบบ (บาท)", min_value=1000.0, value=150000.0, step=1000.0)
    electricity_cost_per_kwh = st.number_input("ค่าไฟฟ้าต่อหน่วย (บาท/kWh)", min_value=0.1, value=4.5)
    
# ----------------------------
# 2. คำนวณ (ใช้ st.button)
# ----------------------------
if st.button("☀️ คำนวณและจำลองผลลัพธ์"):
    
    # === [คำนวณพลังงาน] ===
    days_in_month = 30 # สมมติฐาน 30 วันต่อเดือน
    
    # 1. พลังงานที่ใช้จริง
    energy_used_day = (machine_count * power_per_machine * work_hours) / 1000  # kWh/วัน
    energy_used_month = energy_used_day * days_in_month # kWh/เดือน
    
    # 2. พลังงานผลิตได้ต่อแผง
    energy_per_panel = (panel_power * sunlight_hours * 0.75) / 1000        # kWh/แผง/วัน (0.75 คือประสิทธิภาพ)
    
    # 3. จำนวนแผงที่ต้องการ (เพื่อครอบคลุม Demand พอดี)
    panels_needed = energy_used_day / energy_per_panel if energy_per_panel > 0 else 0
    
    # 4. พลังงานผลิตได้จริง (จากแผงที่ติดตั้งจริง)
    actual_production_day = energy_per_panel * actual_installed_panels
    
    # 5. พลังงานส่วนเกิน/ขาด (Surplus/Deficit)
    surplus_day = actual_production_day - energy_used_day 
    surplus_month = surplus_day * days_in_month

    # === [คำนวณความคุ้มค่า] ===
    # 6. ประหยัดค่าไฟ (Cost Savings)
    # *ใช้พลังงานที่ใช้จริงในการคำนวณ เพราะคือส่วนที่ประหยัดได้จาก Grid*
    cost_savings_month = energy_used_month * electricity_cost_per_kwh # บาท/เดือน
    
    # 7. คาร์บอนที่ลดได้
    co2_saved_month = energy_used_month * 0.43 # kgCO₂/เดือน (0.43 kgCO₂/kWh)
    
    # 8. ระยะเวลาคืนทุน (Payback Period)
    payback_period_years = investment_cost / (cost_savings_month * 12) if cost_savings_month > 0 else 0
    
    # ----------------------------
    # 3. แสดงผลลัพธ์และวิเคราะห์ (Metrics)
    # ----------------------------
    st.subheader("🔍 ผลลัพธ์และการวิเคราะห์: Sun to Sort Simulation")
    
    st.markdown("#### 🔋 ผลวิเคราะห์ด้านพลังงานและความสมดุล")
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    
    col_e1.metric("พลังงานที่ใช้ต่อเดือน", f"{energy_used_month:.0f} kWh")
    col_e2.metric("จำนวนแผงที่ต้องการ (ขั้นต่ำ)", f"{panels_needed:.0f} แผง")
    
    # [ANALYSIS] แสดง Surplus/Deficit พร้อมสี
    if surplus_day >= 0:
        col_e3.metric("พลังงานส่วนเกินต่อวัน", f"{surplus_day:.1f} kWh", delta=f"{surplus_month:.0f} kWh/เดือน", delta_color="normal")
        col_e4.metric("สถานะระบบ", "ผลิตไฟพอ", delta="✅ แผงที่ติดตั้งจริง > ที่ต้องการ", delta_color="inverse")
    else:
        col_e3.metric("พลังงานที่ขาดต่อวัน", f"{abs(surplus_day):.1f} kWh", delta=f"{abs(surplus_month):.0f} kWh/เดือน", delta_color="inverse")
        col_e4.metric("สถานะระบบ", "ผลิตไฟไม่พอ", delta="❌ แผงที่ติดตั้งจริง < ที่ต้องการ", delta_color="normal")
        
    st.markdown("#### 💰 ผลวิเคราะห์ด้านเศรษฐศาสตร์และสิ่งแวดล้อม")
    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.metric("ประหยัดค่าไฟต่อเดือน", f"{cost_savings_month:,.0f} บาท")
    col_c2.metric("ระยะเวลาคืนทุน", f"{payback_period_years:.2f} ปี")
    col_c3.metric("ลดคาร์บอนต่อเดือน", f"{co2_saved_month:.0f} kgCO₂")
    
    # ----------------------------
    # 4. สร้างกราฟเปรียบเทียบ (Demand vs. Actual Supply)
    # ----------------------------
    st.subheader("📊 Energy Balance Chart (Demand vs. Actual Production)") 
    fig, ax = plt.subplots(figsize=(8, 4)) 

    # [FIX] ใช้ Actual Production (จากแผงที่ติดตั้งจริง) มาเทียบกับ Energy Used
    categories = ["Energy Used (Demand)", "Energy Produced (Actual)"]
    values = [energy_used_day, actual_production_day]

    ax.bar(categories, values, color=["#ffb703", "#219ebc"])
    ax.set_ylabel("Energy (kWh/Day)") 
    ax.set_title("Actual Daily Energy Demand vs. Actual Solar Production") 
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    st.pyplot(fig) 

    # ----------------------------
    # 5. ดาวน์โหลดผลลัพธ์
    # ----------------------------
    df = pd.DataFrame({
        "Item": ["Energy Used (kWh/Month)", "Actual Production (kWh/Month)", "Panels Needed (Minimum)", "Surplus/Deficit (kWh/Month)", "Cost Savings (THB/Month)", "CO2 Saved (kg/Month)", "Payback Period (Years)"], 
        "Value": [energy_used_month, actual_production_day * days_in_month, panels_needed, surplus_month, cost_savings_month, co2_saved_month, payback_period_years]
    })

    st.download_button(
        label="📥 Download Full Results (CSV)", 
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="sun_to_sort_analysis.csv",
        mime="text/csv",
    )
