import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math # สำหรับ math.ceil

# [NOTE] ตั้งค่าฟอนต์พื้นฐานสำหรับ Streamlit Cloud
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans'] 

st.set_page_config(page_title="Sun to Sort v2", layout="wide")

st.title("🌞 Sun to Sort: ระบบจำลองพลังงานโซลาร์สำหรับศูนย์คัดแยกขยะ")
st.caption("โปรแกรมต้นแบบจากค่าย CalcTech Camp x CASIO | เขียนด้วย Python + Streamlit")

# ----------------------------
# 1. Inputs - ข้อมูลที่ผู้ใช้ต้องกรอก
# ----------------------------
st.header("1. ข้อมูลนำเข้า")

# === ส่วนที่ 1: ข้อมูลทั่วไปและโซลาร์เซลล์ ===
st.subheader("1.1 ข้อมูลทั่วไปและระบบโซลาร์เซลล์")
col_gen1, col_gen2 = st.columns(2)

with col_gen1:
    location = st.text_input("ตำแหน่งที่ตั้ง (เช่น กรุงเทพฯ)", "กรุงเทพฯ")
    # [FIX] ค่าเริ่มต้นสำหรับชั่วโมงแดดเฉลี่ย (แก้ไขได้)
    sun_hours = st.number_input("ชั่วโมงแดดเฉลี่ยต่อวัน (ชั่วโมง)", min_value=1.0, max_value=12.0, value=4.5, step=0.1)
    panel_power_W = st.number_input("กำลังแผงต่อแผง (วัตต์)", min_value=100, value=370, step=10)
    # [FIX] ค่าเริ่มต้นสำหรับ derating_factor
    derating_factor = st.number_input("ค่าลดทอนประสิทธิภาพ (เช่น 0.75 สำหรับ 75%)", min_value=0.5, max_value=1.0, value=0.75, step=0.01)

with col_gen2:
    days_in_month = st.number_input("จำนวนวันในเดือน (วัน)", min_value=28, max_value=31, value=30, step=1)
    # [FIX] ค่าเริ่มต้นสำหรับ co2_factor
    co2_factor = st.number_input("CO₂ Factor (kg CO₂ / kWh)", min_value=0.1, value=0.45, step=0.01)
    price_per_kwh = st.number_input("ค่าไฟฟ้าต่อหน่วย (บาท/kWh)", min_value=0.1, value=4.5, step=0.1)
    installation_cost = st.number_input("เงินลงทุนติดตั้งระบบ (บาท)", min_value=0.0, value=150000.0, step=1000.0)


# === ส่วนที่ 2: ข้อมูลขยะและพลังงานที่ใช้ ===
st.subheader("1.2 ข้อมูลการคัดแยกขยะและพลังงานที่ใช้")

# [NEW] Checkboxes สำหรับเลือกประเภทขยะ
st.markdown("เลือกประเภทขยะที่ศูนย์รับ:")
selected_waste_types = []
col_waste_types = st.columns(4)
if col_waste_types[0].checkbox("พลาสติก", value=True): selected_waste_types.append("พลาสติก")
if col_waste_types[1].checkbox("กระดาษ", value=True): selected_waste_types.append("กระดาษ")
if col_waste_types[2].checkbox("ขยะอินทรีย์", value=True): selected_waste_types.append("ขยะอินทรีย์")
if col_waste_types[3].checkbox("โลหะ", value=True): selected_waste_types.append("โลหะ")

# [NEW] Dictionary สำหรับเก็บค่าเริ่มต้น Wh/kg (สามารถแก้ไขได้)
default_energy_per_kg = {
    "พลาสติก": 20,
    "กระดาษ": 15,
    "ขยะอินทรีย์": 10,
    "โลหะ": 30
}

waste_data = {}
st.markdown("---")
st.markdown("**กรอกปริมาณขยะและพลังงานที่ใช้ต่อกิโลกรัมสำหรับแต่ละประเภท:**")

for waste_type in selected_waste_types:
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        kg_per_day = st.number_input(f"ปริมาณ {waste_type} ต่อวัน (กก.)", min_value=0.0, value=100.0, key=f"{waste_type}_kg")
    with col_w2:
        energy_per_kg = st.number_input(f"พลังงานต่อ 1 กก. ของ {waste_type} (Wh/กก.)", min_value=0.0, value=float(default_energy_per_kg.get(waste_type, 10)), key=f"{waste_type}_energy")
    waste_data[waste_type] = {"kg_per_day": kg_per_day, "Wh_per_kg": energy_per_kg}

# === ส่วนที่ 3: ข้อมูลการทำงานและแบตเตอรี่ (Optional) ===
st.subheader("1.3 ข้อมูลการทำงานและสำรองพลังงาน")
col_ops1, col_ops2 = st.columns(2)

with col_ops1:
    machine_availability_hours_per_day = st.number_input("ชั่วโมงทำงานของศูนย์ต่อวัน (ชั่วโมง)", min_value=1.0, max_value=24.0, value=8.0, step=0.5)

with col_ops2:
    battery_backup_hours = st.number_input("ต้องการสำรองพลังงาน (ชั่วโมงสำรอง)", min_value=0.0, value=0.0, step=0.5)
    if battery_backup_hours > 0:
        V_system = st.number_input("แรงดันระบบแบตเตอรี่ (โวลต์)", min_value=12, value=48, step=12)
        DoD = st.number_input("ความลึกการจ่ายไฟของแบตเตอรี่ (DoD, 0-1)", min_value=0.1, max_value=1.0, value=0.8, step=0.05)
        inverter_efficiency = st.number_input("ประสิทธิภาพ Inverter (0-1)", min_value=0.5, max_value=1.0, value=0.9, step=0.01)


# ----------------------------
# 2. ปุ่มคำนวณและแสดงผลลัพธ์
# ----------------------------
st.markdown("---")
if st.button("☀️ คำนวณและจำลองผลลัพธ์"):
    st.header("2. ผลลัพธ์การจำลองและวิเคราะห์")

    # === [สูตร / การคำนวณหลัก] ===

    # 1. พลังงานที่ต้องการต่อวัน (Wh) และ kWh
    energy_needed_per_day_Wh = sum(data["kg_per_day"] * data["Wh_per_kg"] for data in waste_data.values())
    energy_needed_per_day_kWh = energy_needed_per_day_Wh / 1000

    # 2. พลังงานที่ผลิตได้จากแผงหนึ่งแผงต่อวัน (kWh)
    daily_output_kWh_per_panel = (panel_power_W * sun_hours * derating_factor) / 1000

    # 3. จำนวนแผงที่ต้องใช้ (ปัดขึ้น)
    if daily_output_kWh_per_panel > 0:
        needed_panels = math.ceil(energy_needed_per_day_kWh / daily_output_kWh_per_panel)
    else:
        needed_panels = 0 # ป้องกันหารด้วยศูนย์

    # 4. พลังงานผลิตได้รวมทั้งหมด (จากจำนวนแผงที่ "ต้องการ")
    total_production_kWh_per_day = needed_panels * daily_output_kWh_per_panel
    monthly_production_kWh = total_production_kWh_per_day * days_in_month

    # 5. พลังงานใช้ต่อเดือน
    monthly_consumption_kWh = energy_needed_per_day_kWh * days_in_month

    # 6. ประหยัดค่าไฟต่อเดือน (บาท)
    # ใช้พลังงานที่ใช้จริงในการคำนวณการประหยัด (ส่วนที่ใช้จากโซลาร์ แทน Grid)
    monthly_saving_Baht = monthly_consumption_kWh * price_per_kwh 

    # 7. ระยะเวลาคืนทุน (ปี)
    if installation_cost > 0 and monthly_saving_Baht > 0:
        payback_years = installation_cost / (monthly_saving_Baht * 12)
    else:
        payback_years = float('inf') # ไม่มีค่าหรือคืนทุนไม่ได้

    # 8. การลด CO₂ ต่อเดือน (kg)
    monthly_co2_reduction_kg = monthly_consumption_kWh * co2_factor

    # 9. การคำนวณแบตเตอรี่ (ถ้าต้องการสำรอง)
    battery_Ah = 0
    if battery_backup_hours > 0 and machine_availability_hours_per_day > 0:
        energy_for_backup_kWh = (energy_needed_per_day_kWh / machine_availability_hours_per_day) * battery_backup_hours
        battery_wh_needed = energy_for_backup_kWh * 1000
        if V_system * DoD * inverter_efficiency > 0:
            battery_Ah = battery_wh_needed / (V_system * DoD * inverter_efficiency)
        

    # === แสดงผลลัพธ์ (Metrics) ===
    st.subheader("2.1 สรุปผลลัพธ์หลัก")
    
    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    col_res1.metric("พลังงานใช้จริงต่อวัน", f"{energy_needed_per_day_kWh:.2f} kWh")
    col_res2.metric("พลังงานผลิตได้ต่อวัน (จากแผงที่ต้องการ)", f"{total_production_kWh_per_day:.2f} kWh")
    col_res3.metric("จำนวนแผงโซลาร์ที่ต้องการ", f"{needed_panels:.0f} แผง")
    col_res4.metric("ลด CO₂ ต่อเดือน", f"{monthly_co2_reduction_kg:.0f} kgCO₂")

    st.markdown("---")

    st.subheader("2.2 การวิเคราะห์ด้านเศรษฐศาสตร์")
    col_eco1, col_eco2 = st.columns(2)
    col_eco1.metric("ประหยัดค่าไฟฟ้าต่อเดือน", f"{monthly_saving_Baht:,.0f} บาท")
    if payback_years != float('inf'):
        col_eco2.metric("ระยะเวลาคืนทุน", f"{payback_years:.2f} ปี")
    else:
        col_eco2.metric("ระยะเวลาคืนทุน", "ไม่สามารถคำนวณได้")

    if battery_Ah > 0:
        st.subheader("2.3 การคำนวณแบตเตอรี่สำรอง")
        st.metric("ความจุแบตเตอรี่ที่ต้องการ (สำหรับสำรอง)", f"{battery_Ah:,.0f} Ah")


    # === สร้างกราฟเปรียบเทียบ ===
    st.subheader("2.4 Energy Balance Chart") 
    fig, ax = plt.subplots(figsize=(8, 4)) 

    categories = ["Energy Needed (Daily)", "Energy Produced (Daily)"]
    values = [energy_needed_per_day_kWh, total_production_kWh_per_day]

    ax.bar(categories, values, color=["#ffb703", "#219ebc"])
    ax.set_ylabel("Energy (kWh/Day)") 
    ax.set_title("Daily Energy Demand vs. Solar Production") 
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    st.pyplot(fig) 

    # === ดาวน์โหลดผลลัพธ์ ===
    st.subheader("2.5 ดาวน์โหลดผลลัพธ์")
    results_data = {
        "Metric": [
            "Energy Needed (kWh/Day)", "Energy Needed (kWh/Month)",
            "Daily Output per Panel (kWh)", "Panels Needed (Units)",
            "Total Daily Production (kWh)", "Total Monthly Production (kWh)",
            "Monthly Electricity Savings (THB)", "Payback Period (Years)",
            "Monthly CO2 Reduction (kg)", "Battery Capacity Needed (Ah)"
        ],
        "Value": [
            energy_needed_per_day_kWh, monthly_consumption_kWh,
            daily_output_kWh_per_panel, needed_panels,
            total_production_kWh_per_day, monthly_production_kWh,
            monthly_saving_Baht, payback_years,
            monthly_co2_reduction_kg, battery_Ah
        ]
    }
    df_results = pd.DataFrame(results_data)
    
    st.download_button(
        label="📥 ดาวน์โหลดผลลัพธ์ทั้งหมด (CSV)", 
        data=df_results.to_csv(index=False).encode('utf-8'),
        file_name="sun_to_sort_full_analysis.csv",
        mime="text/csv",
    )

st.info("💡 กรอกข้อมูลในช่องด้านบนแล้วกดปุ่ม '☀️ คำนวณและจำลองผลลัพธ์' เพื่อดูการวิเคราะห์")
