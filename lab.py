import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import plotly.express as px
import plotly.graph_objects as go

# Konfigurasi halaman
st.set_page_config(
    page_title="Simulasi Laboratorium Kimia Profesional",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inisialisasi state
def init_state():
    if 'campuran' not in st.session_state:
        st.session_state.campuran = []
    if 'reaksi' not in st.session_state:
        st.session_state.reaksi = ""
    if 'warna' not in st.session_state:
        st.session_state.warna = "#FFFFFF"
    if 'suhu' not in st.session_state:
        st.session_state.suhu = 25
    if 'gambar_reaksi' not in st.session_state:
        st.session_state.gambar_reaksi = None
    if 'log_percobaan' not in st.session_state:
        st.session_state.log_percobaan = []
    if 'volume_total' not in st.session_state:
        st.session_state.volume_total = 0

init_state()

# Database senyawa kimia lengkap dengan warna yang lebih realistis
SENYAWA_KIMIA = {
    # Logam
    "Natrium (Na)": {"warna": "#C0C0C0", "jenis": "logam alkali", "densitas": 0.97, "reaktivitas": 9},
    "Kalium (K)": {"warna": "#8F8FFF", "jenis": "logam alkali", "densitas": 0.86, "reaktivitas": 9},
    "Kalsium (Ca)": {"warna": "#E2E2E2", "jenis": "logam alkali tanah", "densitas": 1.54, "reaktivitas": 7},
    "Magnesium (Mg)": {"warna": "#D3D3D3", "jenis": "logam alkali tanah", "densitas": 1.74, "reaktivitas": 6},
    "Aluminium (Al)": {"warna": "#A8A8A8", "jenis": "logam", "densitas": 2.70, "reaktivitas": 5},
    "Besi (Fe)": {"warna": "#B5651D", "jenis": "logam transisi", "densitas": 7.87, "reaktivitas": 6},
    "Tembaga (Cu)": {"warna": "#B87333", "jenis": "logam transisi", "densitas": 8.96, "reaktivitas": 4},
    
    # Asam
    "Asam Klorida (HCl)": {"warna": "#F0F8FF", "jenis": "asam kuat", "densitas": 1.18, "reaktivitas": 8},
    "Asam Sulfat (H₂SO₄)": {"warna": "#F5F5F5", "jenis": "asam kuat", "densitas": 1.84, "reaktivitas": 9},
    "Asam Nitrat (HNO₃)": {"warna": "#FFF0F5", "jenis": "asam kuat", "densitas": 1.51, "reaktivitas": 8},
    "Asam Asetat (CH₃COOH)": {"warna": "#F8F8FF", "jenis": "asam lemah", "densitas": 1.05, "reaktivitas": 5},
    
    # Basa
    "Natrium Hidroksida (NaOH)": {"warna": "#F5F5DC", "jenis": "basa kuat", "densitas": 2.13, "reaktivitas": 8},
    "Kalium Hidroksida (KOH)": {"warna": "#FFFFF0", "jenis": "basa kuat", "densitas": 2.04, "reaktivitas": 8},
    "Amonium Hidroksida (NH₄OH)": {"warna": "#F0FFFF", "jenis": "basa lemah", "densitas": 0.91, "reaktivitas": 6},
    
    # Garam
    "Natrium Klorida (NaCl)": {"warna": "#FFFFFF", "jenis": "garam", "densitas": 2.16, "reaktivitas": 1},
    "Kalium Nitrat (KNO₃)": {"warna": "#F5F5F5", "jenis": "garam", "densitas": 2.11, "reaktivitas": 3},
    "Kalsium Karbonat (CaCO₃)": {"warna": "#FAFAD2", "jenis": "garam", "densitas": 2.71, "reaktivitas": 2},
    
    # Pelarut
    "Air (H₂O)": {"warna": "#ADD8E6", "jenis": "pelarut", "densitas": 1.00, "reaktivitas": 1},
    "Etanol (C₂H₅OH)": {"warna": "#F0FFF0", "jenis": "pelarut", "densitas": 0.79, "reaktivitas": 3},
    "Aseton (C₃H₆O)": {"warna": "#FFFACD", "jenis": "pelarut", "densitas": 0.79, "reaktivitas": 4},
    
    # Senyawa Organik
    "Glikosa (C₆H₁₂O₆)": {"warna": "#FFFFFF", "jenis": "organik", "densitas": 1.54, "reaktivitas": 2},
    "Sukrosa (C₁₂H₂₂O₁₁)": {"warna": "#FFFFF0", "jenis": "organik", "densitas": 1.59, "reaktivitas": 1},
    "Metana (CH₄)": {"warna": "#E0FFFF", "jenis": "hidrokarbon", "densitas": 0.00066, "reaktivitas": 5},
    
    # Senyawa Khusus
    "Permanganat Kalium (KMnO₄)": {"warna": "#800080", "jenis": "oksidator", "densitas": 2.70, "reaktivitas": 7},
    "Dikromat Kalium (K₂Cr₂O₇)": {"warna": "#FF4500", "jenis": "oksidator", "densitas": 2.68, "reaktivitas": 7},
    "Tembaga Sulfat (CuSO₄)": {"warna": "#00BFFF", "jenis": "garam", "densitas": 3.60, "reaktivitas": 4}
}

# Fungsi untuk membuat gambar labu takar
def buat_labu_takar(warna_cairan, volume_ml, tinggi_px=300, lebar_px=200):
    # Buat gambar transparan
    img = Image.new('RGBA', (lebar_px, tinggi_px), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Warna dasar labu takar (kaca bening dengan efek transparansi)
    warna_kaca = (220, 240, 255, 180)
    
    # Gambar labu takar (bagian bawah bulat, leher panjang)
    
    # Bagian bawah bulat
    draw.ellipse([(lebar_px//4, tinggi_px//3), (3*lebar_px//4, 5*tinggi_px//6)], 
                fill=warna_kaca, outline=(150, 150, 150, 255))
    
    # Leher labu
    draw.rectangle([(lebar_px//3, tinggi_px//6), (2*lebar_px//3, tinggi_px//3)], 
                  fill=warna_kaca, outline=(150, 150, 150, 255))
    
    # Mulut labu
    draw.rectangle([(lebar_px//3-10, tinggi_px//12), (2*lebar_px//3+10, tinggi_px//6)], 
                  fill=warna_kaca, outline=(150, 150, 150, 255))
    
    # Cairan di dalam labu (tinggi berdasarkan volume)
    tinggi_cairan = int((volume_ml / 1000) * (2*tinggi_px//3))  # Asumsi 1000ml = full
    
    # Gambar cairan
    if tinggi_cairan > 0:
        # Hitung koordinat cairan
        y_start = max(tinggi_px//3 + (5*tinggi_px//6 - tinggi_px//3 - tinggi_cairan), tinggi_px//3)
        y_end = 5*tinggi_px//6
        
        # Buat mask untuk bentuk cairan yang mengikuti bentuk labu
        mask = Image.new('L', (lebar_px, tinggi_px), 0)
        mask_draw = ImageDraw.Draw(mask)
        
        # Gambar bentuk cairan
        mask_draw.ellipse([(lebar_px//4, y_start - (lebar_px//2 - lebar_px//4)), 
                          (3*lebar_px//4, y_end)], fill=255)
        
        # Gambar cairan dengan mask
        cairan = Image.new('RGBA', (lebar_px, tinggi_px), warna_cairan)
        img.paste(cairan, (0, 0), mask)
    
    # Tambahkan skala volume
    for i in range(1, 6):
        y_pos = 5*tinggi_px//6 - i*(tinggi_px//6)
        draw.line([(3*lebar_px//4 + 5, y_pos), (3*lebar_px//4 + 15, y_pos)], 
                 fill=(100, 100, 100, 255), width=1)
    
    return img

# Fungsi untuk mencampur warna
def campur_warna(warna1, warna2, rasio=0.5):
    # Konversi hex ke RGB
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Konversi RGB ke hex
    def rgb_to_hex(rgb_color):
        return '#%02x%02x%02x' % rgb_color
    
    rgb1 = hex_to_rgb(warna1)
    rgb2 = hex_to_rgb(warna2)
    
    # Campur warna dengan rasio tertentu
    r = int(rgb1[0] * (1-rasio) + rgb2[0] * rasio)
    g = int(rgb1[1] * (1-rasio) + rgb2[1] * rasio)
    b = int(rgb1[2] * (1-rasio) + rgb2[2] * rasio)
    
    return rgb_to_hex((r, g, b))

# Fungsi untuk memprediksi reaksi
def prediksi_reaksi(campuran):
    senyawa = [item['senyawa'] for item in campuran]
    volume = sum(item['volume'] for item in campuran)
    
    # Contoh reaksi sederhana
    if "Asam Klorida (HCl)" in senyawa and "Natrium Hidroksida (NaOH)" in senyawa:
        return f"Reaksi netralisasi: HCl + NaOH → NaCl + H₂O\nVolume total: {volume} mL"
    elif "Asam Sulfat (H₂SO₄)" in senyawa and "Kalium Hidroksida (KOH)" in senyawa:
        return f"Reaksi netralisasi: H₂SO₄ + 2KOH → K₂SO₄ + 2H₂O\nVolume total: {volume} mL"
    elif "Tembaga Sulfat (CuSO₄)" in senyawa and "Besi (Fe)" in senyawa:
        return f"Reaksi penggantian: CuSO₄ + Fe → FeSO₄ + Cu\nVolume total: {volume} mL"
    elif "Permanganat Kalium (KMnO₄)" in senyawa and "Asam Sulfat (H₂SO₄)" in senyawa:
        return f"Reaksi oksidasi: KMnO₄ bertindak sebagai oksidator kuat\nVolume total: {volume} mL"
    else:
        return f"Campuran {', '.join(senyawa)}. Volume total: {volume} mL"

# Fungsi untuk menghitung warna campuran
def hitung_warna_campuran(campuran):
    if not campuran:
        return "#FFFFFF"
    
    total_volume = sum(item['volume'] for item in campuran)
    if total_volume == 0:
        return "#FFFFFF"
    
    warna_campuran = "#000000"
    for item in campuran:
        rasio = item['volume'] / total_volume
        warna_campuran = campur_warna(warna_campuran, item['warna'], rasio)
    
    return warna_campuran

# Fungsi untuk mengkonversi gambar ke base64
def gambar_ke_base64(gambar):
    buffered = io.BytesIO()
    gambar.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Tampilan Streamlit
st.title("🧪 Simulasi Laboratorium Kimia Profesional")
st.markdown("""
    *Simulasikan reaksi kimia dengan mencampur berbagai senyawa.*  
    Pilih senyawa dan volume yang ingin dicampur, lalu lihat hasil reaksinya!
""")

# Sidebar untuk input
with st.sidebar:
    st.header("⚗️ Kontrol Eksperimen")
    senyawa = st.selectbox("Pilih Senyawa Kimia", list(SENYAWA_KIMIA.keys()))
    volume = st.slider("Volume (mL)", 1, 100, 10)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Tambahkan Senyawa"):
            senyawa_info = SENYAWA_KIMIA[senyawa]
            st.session_state.campuran.append({
                "senyawa": senyawa,
                "warna": senyawa_info["warna"],
                "volume": volume,
                "jenis": senyawa_info["jenis"]
            })
            st.session_state.volume_total += volume
            st.session_state.log_percobaan.append(f"Menambahkan {volume} mL {senyawa}")
            st.rerun()
    
    with col2:
        if st.button("Reset Eksperimen"):
            st.session_state.campuran = []
            st.session_state.reaksi = ""
            st.session_state.warna = "#FFFFFF"
            st.session_state.suhu = 25
            st.session_state.gambar_reaksi = None
            st.session_state.log_percobaan.append("Reset semua campuran")
            st.session_state.volume_total = 0
            st.rerun()
    
    st.slider("Suhu (°C)", -20, 150, st.session_state.suhu, key="suhu")
    
    if st.button("Mulai Reaksi"):
        if st.session_state.campuran:
            st.session_state.reaksi = prediksi_reaksi(st.session_state.campuran)
            st.session_state.warna = hitung_warna_campuran(st.session_state.campuran)
            
            # Buat gambar labu takar dengan campuran
            st.session_state.gambar_reaksi = buat_labu_takar(
                st.session_state.warna, 
                st.session_state.volume_total
            )
            
            st.session_state.log_percobaan.append(f"Memulai reaksi pada {st.session_state.suhu}°C")
            st.rerun()
        else:
            st.warning("Tambahkan setidaknya satu senyawa untuk memulai reaksi")

# Tampilan utama
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🏺 Labu Takar")
    if st.session_state.gambar_reaksi:
        st.image(st.session_state.gambar_reaksi, use_column_width=True)
    else:
        # Tampilkan labu takar kosong
        img_kosong = buat_labu_takar("#FFFFFF", 0)
        st.image(img_kosong, use_column_width=True)
    
    st.metric("Volume Total", f"{st.session_state.volume_total} mL")
    st.color_picker("Warna Campuran", st.session_state.warna, disabled=True)

with col2:
    st.subheader("📝 Hasil Reaksi")
    if st.session_state.reaksi:
        st.info(st.session_state.reaksi)
        
        # Tampilkan grafik perubahan suhu
        data_suhu = pd.DataFrame({
            "Waktu": np.arange(0, 10, 0.5),
            "Suhu": st.session_state.suhu + np.random.normal(0, 2, 20).cumsum()
        })
        
        fig = px.line(data_suhu, x="Waktu", y="Suhu", title="Perubahan Suhu selama Reaksi")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Belum ada reaksi. Tambahkan senyawa dan klik 'Mulai Reaksi'.")
    
    st.subheader("📋 Daftar Campuran")
    if st.session_state.campuran:
        df = pd.DataFrame(st.session_state.campuran)
        st.dataframe(df[['senyawa', 'volume', 'jenis']], hide_index=True)
    else:
        st.info("Belum ada senyawa yang ditambahkan.")
    
    st.subheader("📜 Log Percobaan")
    for log in reversed(st.session_state.log_percobaan[-5:]):
        st.code(log)

# Informasi senyawa
st.subheader("📚 Database Senyawa Kimia")
st.dataframe(pd.DataFrame.from_dict(SENYAWA_KIMIA, orient='index'), use_container_width=True)
