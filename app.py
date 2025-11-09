import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# [NOTE] ตั้งค่าฟอนต์พื้นฐานสำหรับ Streamlit Cloud และรองรับภาษาไทย
# Dejavu Sans เป็นฟอนต์มาตรฐานที่ใช้ได้บน Streamlit Cloud
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
    # รับค่าปริมาณขยะ (ไม่ได้ใช้ในการคำนวณไฟฟ้า แต่ใช้เป็นข้อมูลศูนย์)
    waste_amount = st.number_input("ปริมาณขยะต่อวัน (กิโลกรัม)", min_value=1.0, value=500.0) 
    machine_count = st.number_input("จำนวนเครื่องจักร", min_value=1, step=1, value=5)
    power_per_machine = st.number_input("กำลังไฟเฉลี่ยต่อเครื่อง (วัตต์)", min_value=100.0, value=500.0)

with col2:
    st.markdown("**ข้อมูลการผลิตพลังงาน (Supply)**")
    work_hours = st.number_input("ชั่วโมงทำงานต่อวัน", min_value=1.0, max_value=24.0, value=8.0)
    sunlight_hours = st.number_input("ชั่วโมงแดดเฉลี่ยต่อวัน", min_value=1.0, max_value=12.0, value=5.0)
    panel_power = st.number_input("กำลังแผงต่อแผง (วัตต์)", min_value=100.0, value=300.0)
    
    # จำนวนแผงที่ติดตั้งจริง (ใช้ในการคำนวณผลผลิตจริง)
    actual_installed_panels = st.number_input("จำนวนแผงที่คาดว่าจะติดตั้ง (แผง)", min_value=1, step=1, value=100) 

with col3:
    st.markdown("**ข้อมูลวิเคราะห์ความคุ้มค่า (Economics)**")
    # เงินลงทุนติดตั้งระบบ (ใช้ในการคำนวณคืนทุน)
    investment_cost = st.number_input("เงินลงทุนติดตั้งระบบ (บาท)", min_value=1000.0, value=150000.0, step=1000.0)
    # ค่าไฟฟ้าต่อหน่วย
    electricity_cost_per_kwh = st.number_input("ค่าไฟฟ้าต่อหน่วย (บาท/kWh)", min_value=0.1, value=4.5)
    
# ----------------------------
# 2. คำนวณ (ใช้ st.button)
# ----------------------------
if st.button("☀️ คำนวณและจำลองผลลัพธ์"):
    
    # === [คำนวณพลังงาน] ===
    days_in_month = 30 # สมมติฐาน 30 วันต่อเดือน
    system_efficiency = 0.75 # ประสิทธิภาพระบบโซลาร์เซลล์ (75%)
    co2_factor = 0.43 # ค่าปัจจัยการลดคาร์บอน (0.43 kgCO₂/kWh)
    
    # 1. พลังงานที่ใช้จริง (Demand)
    # (จำนวนเครื่อง x กำลังไฟ/เครื่อง x ชั่วโมงทำงาน) / 1000 (เปลี่ยนวัตต์เป็นกิโลวัตต์)
    energy_used_day = (machine_count * power_per_machine * work_hours) / 1000  # kWh/วัน
    energy_used_month = energy_used_day * days_in_month # kWh/เดือน
    
    # 2. พลังงานผลิตได้ต่อแผง
    # (กำลังแผง x ชั่วโมงแดด x ประสิทธิภาพ) / 1000
    energy_per_panel = (panel_power * sunlight_hours * system_efficiency) / 1000  # kWh/แผง/วัน
    
    # 3. จำนวนแผงที่ต้องการ (เพื่อครอบคลุม Demand พอดี)
    panels_needed = energy_used_day / energy_per_panel if energy_per_panel > 0 else 0
    
    # 4. พลังงานผลิตได้จริง (Actual Supply)
    actual_production_day = energy_per_panel * actual_installed_panels
    
    # 5. พลังงานส่วนเกิน/ขาด (Surplus/Deficit)
    surplus_day = actual_production_day - energy_used_day 
    surplus_month = surplus_day * days_in_month

    # === [คำนวณความคุ้มค่า] ===
    # 6. ประหยัดค่าไฟ (Cost Savings)
    # เราประหยัดได้เท่ากับพลังงานที่ "ใช้จริง" (เพราะเป็นส่วนที่ทดแทนจากการซื้อ Grid)
    cost_savings_month = energy_used_month * electricity_cost_per_kwh # บาท/เดือน
    cost_savings_year = cost_savings_month * 12 # บาท/ปี
    
    # 7. คาร์บอนที่ลดได้
    co2_saved_month = energy_used_month * co2_factor # kgCO₂/เดือน
    
    # 8. ระยะเวลาคืนทุน (Payback Period)
    payback_period_years = investment_cost / cost_savings_year if cost_savings_year > 0 else 0
    
    # ----------------------------
    # 3. แสดงผลลัพธ์และวิเคราะห์ (Metrics)
    # ----------------------------
    st.subheader("🔍 ผลลัพธ์และการวิเคราะห์: Sun to Sort Simulation")
    
    st.markdown("#### 🔋 ผลวิเคราะห์ด้านพลังงานและความสมดุล")
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    
    col_e1.metric("พลังงานที่ใช้ต่อเดือน (Demand)", f"{energy_used_month:,.0f} kWh")
    col_e2.metric("จำนวนแผงที่ต้องการ (ขั้นต่ำ)", f"{panels_needed:,.0f} แผง")
    
    # แสดง Surplus/Deficit พร้อมสี
    if surplus_day >= 0:
        col_e3.metric("พลังงานส่วนเกินต่อวัน (Surplus)", f"{surplus_day:.1f} kWh", delta=f"{surplus_month:,.0f} kWh/เดือน", delta_color="normal")
        col_e4.metric("สถานะระบบ", "ผลิตไฟพอ", delta="✅ แผงที่ติดตั้งจริง > ที่ต้องการ", delta_color="inverse")
    else:
        col_e3.metric("พลังงานที่ขาดต่อวัน (Deficit)", f"{abs(surplus_day):.1f} kWh", delta=f"{abs(surplus_month):,.0f} kWh/เดือน", delta_color="inverse")
        col_e4.metric("สถานะระบบ", "ผลิตไฟไม่พอ", delta="❌ แผงที่ติดตั้งจริง < ที่ต้องการ", delta_color="normal")
        
    st.markdown("#### 💰 ผลวิเคราะห์ด้านเศรษฐศาสตร์และสิ่งแวดล้อม")
    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.metric("ประหยัดค่าไฟต่อเดือน", f"{cost_savings_month:,.0f} บาท")
    col_c2.metric("ระยะเวลาคืนทุน", f"{payback_period_years:.2f} ปี")
    col_c3.metric("ลดคาร์บอนต่อเดือน", f"{co2_saved_month:,.0f} kgCO₂")
    
    st.divider() # เพิ่มเส้นแบ่งส่วน

    # ----------------------------
    # 4. กราฟ 1: Energy Balance (กราฟแท่ง)
    # ----------------------------
    st.subheader("📊 Energy Balance Chart (Demand vs. Actual Production)") 
    fig, ax = plt.subplots(figsize=(8, 4)) 

    # ข้อมูลสำหรับกราฟแท่ง
    categories = ["Energy Used (Demand)", "Energy Produced (Actual)"]
    values = [energy_used_day, actual_production_day]

    ax.bar(categories, values, color=["#ffb703", "#219ebc"])
    ax.set_ylabel("Energy (kWh/Day)") 
    ax.set_title("Actual Daily Energy Demand vs. Actual Solar Production") 
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    st.pyplot(fig) 

    # ----------------------------------------
    # 5. กราฟ 2: Payback Analysis (กราฟเส้น)
    # ----------------------------------------
    st.subheader("📈 Financial Payback Analysis (Cumulative Savings)")

    # กำหนดจำนวนปีที่ต้องการจำลอง (เช่น 10 ปี)
    max_years = 10
    
    # สร้างข้อมูลสำหรับกราฟเส้น
    data = []
    cumulative_savings = 0
    
    # วนลูปเพื่อคำนวณการประหยัดสะสมในแต่ละปี
    for year in range(1, max_years + 1):
        cumulative_savings += cost_savings_year # เพิ่มค่าประหยัดต่อปี
        data.append({
            'Year': year,
            'Cumulative Savings (THB)': cumulative_savings,
        })

    df_payback = pd.DataFrame(data)

    # สร้างกราฟเส้น
    fig_line, ax_line = plt.subplots(figsize=(10, 5)) 

    # Plot เส้น Investment Cost (เงินลงทุน - เส้นคงที่)
    ax_line.plot(df_payback['Year'], [investment_cost] * max_years, 
                 label='Investment Cost (THB)', color='red', linestyle='--')
                 
    # Plot เส้น Cumulative Savings (การประหยัดสะสม - เส้นเพิ่มขึ้น)
    ax_line.plot(df_payback['Year'], df_payback['Cumulative Savings (THB)'], 
                 label='Cumulative Savings (THB)', color='#2a9d8f', linewidth=3)

    # ใส่จุด Payback (ถ้าคำนวณได้และอยู่ในช่วงการจำลอง)
    if payback_period_years > 0 and payback_period_years <= max_years:
        payback_x = payback_period_years 
        payback_y = investment_cost
        
        # วาดเส้นแนวตั้งตรงจุดคืนทุน
        ax_line.axvline(x=payback_x, color='gray', linestyle=':', linewidth=1)
        # วาดจุดคืนทุน
        ax_line.plot(payback_x, payback_y, 'o', color='black', markersize=8, label='Payback Point')
        
        # เพิ่มข้อความกำกับ
        ax_line.text(payback_x + 0.1, payback_y * 0.9, f'Payback: {payback_period_years:.2f} Years', 
                     fontsize=10, color='red')

    ax_line.set_xlabel("Year")
    ax_line.set_ylabel("Cost/Savings (THB)")
    ax_line.set_title("Financial Payback Analysis")
    ax_line.legend()
    ax_line.grid(axis='both', linestyle='--', alpha=0.7)
    # จำกัดแกน Y ให้เริ่มต้นที่ 0 และมีค่าสูงสุดที่เหมาะสม
    ax_line.set_ylim(0, max(investment_cost * 1.2, df_payback['Cumulative Savings (THB)'].max() * 1.1))

    st.pyplot(fig_line)
    
    st.divider() # เพิ่มเส้นแบ่งส่วน

    # ----------------------------
    # 6. ดาวน์โหลดผลลัพธ์
    # ----------------------------
    df_results = pd.DataFrame({
        "Item": ["Energy Used (kWh/Month)", "Actual Production (kWh/Month)", "Panels Needed (Minimum)", "Surplus/Deficit (kWh/Month)", "Cost Savings (THB/Month)", "CO2 Saved (kg/Month)", "Payback Period (Years)"], 
        "Value": [energy_used_month, actual_production_day * days_in_month, panels_needed, surplus_month, cost_savings_month, co2_saved_month, payback_period_years]
    })

    st.download_button(
        label="📥 Download Full Results (CSV)", 
        data=df_results.to_csv(index=False).encode('utf-8'),
        file_name="sun_to_sort_analysis.csv",
        mime="text/csv",
    )
