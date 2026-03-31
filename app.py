import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="รายงานการช่วยเหลือกลุ่มเปราะบาง", layout="wide")
st.title("📊 แดชบอร์ดติดตามผลการคลีนนิ่งข้อมูลและการช่วยเหลือกลุ่มเปราะบาง")
st.markdown("รายงานสรุปผลการดำเนินงานระดับประเทศ สำหรับผู้บริหาร")

# ---------------------------------------------------------
# 📌 ส่วนที่แก้ไข: ดึงข้อมูลจาก Google Sheets 
# ---------------------------------------------------------
# ใส่ ttl=600 เพื่อให้ระบบดึงข้อมูลใหม่จาก Google Sheets ทุกๆ 10 นาที (600 วินาที)
@st.cache_data(ttl=600)
def load_data():
    # ⚠️ นำลิงก์ CSV ที่ก๊อปปี้มาจาก Google Sheets มาวางแทนที่ในเครื่องหมายคำพูดด้านล่างนี้
    google_sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT67r-W0wEcuy5DNdjy8HMDip2AbOYbyIGU41gpvrcqv_H9OKc9fp2mHb0FK7XB-jWjfnrvycmaD3dj/pub?gid=1784574846&single=true&output=csv"
    
    # อ่านข้อมูลจากลิงก์
    df = pd.read_csv(google_sheet_url)
    return df

df = load_data()
# ---------------------------------------------------------

# คำนวณสรุปผลภาพรวม (KPI)
total_vulnerable = df['จำนวนคนเปราะบาง'].sum()
total_completed = df['จำนวนที่ดำเนินการแล้ว'].sum()
percent_completed = (total_completed / total_vulnerable) * 100 if total_vulnerable > 0 else 0

st.markdown("### 📌 สรุปภาพรวมระดับประเทศ")
col1, col2, col3 = st.columns(3)
col1.metric("👥 จำนวนคนเปราะบางที่ต้องตรวจสอบ (คน)", f"{total_vulnerable:,.0f}")
col2.metric("✅ ดำเนินการแล้วเสร็จ (คน)", f"{total_completed:,.0f}")
col3.metric("📈 คิดเป็นความคืบหน้า (%)", f"{percent_completed:.2f} %")

st.markdown("---")

# เตรียมข้อมูลสำหรับแผนที่ 
st.subheader("🗺️ แผนที่ Heatmap ความคืบหน้ารายจังหวัด")
df_province = df.groupby('จังหวัด').agg({
    'จำนวนคนเปราะบาง': 'sum',
    'จำนวนที่ดำเนินการแล้ว': 'sum'
}).reset_index()

@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json"
    r = requests.get(url)
    return r.json()

thailand_geojson = load_geojson()

# วาดกราฟแผนที่ Heatmap
fig_map = px.choropleth_mapbox(
    df_province,
    geojson=thailand_geojson,
    locations='จังหวัด',
    featureidkey='properties.name', 
    color='จำนวนที่ดำเนินการแล้ว',   
    color_continuous_scale="Blues", 
    mapbox_style="carto-positron",  
    zoom=4.5,
    center={"lat": 13.0, "lon": 100.0}, 
    opacity=0.8,
    hover_name='จังหวัด',
    hover_data={
        'จังหวัด': False, 
        'จำนวนคนเปราะบาง': True, 
        'จำนวนที่ดำเนินการแล้ว': True
    },
    labels={
        'จำนวนคนเปราะบาง': 'เปราะบางทั้งหมด (คน)', 
        'จำนวนที่ดำเนินการแล้ว': 'ดำเนินการแล้ว (คน)'
    }
)

fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")
st.subheader("📊 10 จังหวัดที่ดำเนินการได้มากที่สุด")
df_top10 = df_province.sort_values('จำนวนที่ดำเนินการแล้ว', ascending=False).head(10)

fig_bar = px.bar(
    df_top10, 
    x='จังหวัด', 
    y=['จำนวนคนเปราะบาง', 'จำนวนที่ดำเนินการแล้ว'], 
    barmode='group',
    labels={'value': 'จำนวน (คน)', 'variable': 'สถานะ'},
    color_discrete_map={'จำนวนคนเปราะบาง': '#e2e8f0', 'จำนวนที่ดำเนินการแล้ว': '#3b82f6'}
)
st.plotly_chart(fig_bar, use_container_width=True)