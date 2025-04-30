import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard PLTU OM-2", layout="wide")

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Menu Utama",
        options=["Home", "Performance Indikator", "Kesiapan Peralatan"],
        icons=["house", "bar-chart", "gear"],
        menu_icon="cast",
        default_index=0,
    )

# Halaman Home
if selected == "Home":
    st.title("🏠 Selamat Datang di Dashboard Monitoring")
    st.markdown("Sistem monitoring kesiapan peralatan PLTU Wilayah OM-2 tahun 2025.")
    st.image("adf44650-27aa-4790-9134-6446bfd2747c.png", caption="Tampilan Dashboard Asli", use_column_width=True)

# Halaman Performance Indikator
elif selected == "Performance Indikator":
    st.title("📊 Performance Indikator")

    # Menggunakan session_state untuk menyimpan data
    if "df" not in st.session_state:
        uploaded_file = st.file_uploader("📤 Upload file data (CSV atau Excel)", type=["csv", "xlsx"])

        if uploaded_file is not None:
            # Baca file
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.session_state.df = df
            st.success("✅ Data berhasil diunggah!")
        else:
            st.info("Silakan upload file terlebih dahulu untuk menampilkan grafik.")
    else:
        df = st.session_state.df
        st.dataframe(df.head())

    # Mendapatkan nama parameter/kolom
    columns = df.columns.tolist()

    # Filter kolom tanggal atau bulan agar tidak dibuatkan card
    date_columns = df.select_dtypes(include=["datetime", "object"]).columns.tolist()
    exclude_columns = [col for col in columns if col in date_columns]
    columns_to_display = [col for col in columns if col not in exclude_columns]

    st.markdown("---")
    st.subheader("📈 Dashboard Parameter")

    # Pilih kolom tanggal atau bulan untuk digunakan sebagai X-Axis
    date_column = None
    for col in columns:
        if pd.to_datetime(df[col], errors='coerce').notna().all():
            date_column = col
            break

    if date_column:
        # Mengubah kolom tanggal menjadi format bulan (jika ada)
        df[date_column] = pd.to_datetime(df[date_column])
        df['Month'] = df[date_column].dt.month_name()  # Ekstrak nama bulan

    # Buat kartu untuk setiap parameter kecuali tanggal/bulan
    for col in columns_to_display:
        with st.expander(f"🔲 {col}"):
            # Statistika dasar
            st.subheader("📊 Statistika")
            st.write(f"**Mean:** {df[col].mean():.2f}")
            st.write(f"**Median:** {df[col].median():.2f}")
            st.write(f"**Std Dev:** {df[col].std():.2f}")
            st.write(f"**Min:** {df[col].min():.2f}")
            st.write(f"**Max:** {df[col].max():.2f}")
            
            # Visualisasi distribusi data (Histogram)
            st.subheader("📊 Histogram Distribusi")
            fig_hist = px.histogram(df, x=col, title=f"Distribusi {col}")
            st.plotly_chart(fig_hist, use_container_width=True)

            # Pilih jenis grafik
            chart_types = ["Line", "Bar", "Area", "Scatter"]
            chart_type = st.selectbox(f"Pilih Tipe Grafik untuk {col}", options=chart_types, key=col)

            # Membuat grafik berdasarkan pilihan tipe
            if date_column:
                # Grafik menggunakan bulan sebagai X-Axis
                if chart_type == "Line":
                    fig = px.line(df, x='Month', y=col, title=f"{col} - {chart_type} Chart")
                elif chart_type == "Bar":
                    fig = px.bar(df, x='Month', y=col, title=f"{col} - {chart_type} Chart")
                elif chart_type == "Area":
                    fig = px.area(df, x='Month', y=col, title=f"{col} - {chart_type} Chart")
                elif chart_type == "Scatter":
                    fig = px.scatter(df, x='Month', y=col, title=f"{col} - {chart_type} Chart")
            else:
                # Grafik tanpa bulan sebagai X-Axis, menggunakan index atau waktu lainnya
                if chart_type == "Line":
                    fig = px.line(df, x=df.index, y=col, title=f"{col} - {chart_type} Chart")
                elif chart_type == "Bar":
                    fig = px.bar(df, x=df.index, y=col, title=f"{col} - {chart_type} Chart")
                elif chart_type == "Area":
                    fig = px.area(df, x=df.index, y=col, title=f"{col} - {chart_type} Chart")
                elif chart_type == "Scatter":
                    fig = px.scatter(df, x=df.index, y=col, title=f"{col} - {chart_type} Chart")

            # Tampilkan grafik
            st.plotly_chart(fig, use_container_width=True)
            
            # Visualisasi Box Plot
            st.subheader("📊 Box Plot")
            fig_box = px.box(df, y=col, title=f"Box Plot {col}")
            st.plotly_chart(fig_box, use_container_width=True)

# Halaman Kesiapan Peralatan (menampilkan Google Sheet)
elif selected == "Kesiapan Peralatan":
    st.title("🔧 Kesiapan Peralatan PLTU OM-2")
    st.markdown("Berikut adalah tampilan langsung dari Google Spreadsheet:")

    # Google Sheet ID dari link yang kamu berikan
    sheet_id = "1vh_3k_6uacjs96Bpr9ap_gQ-6T3CF-xQfFYt2AuSNvo"

    # Tampilkan embed dari Google Spreadsheet
    st.markdown(
        f"""
        <iframe src="https://docs.google.com/spreadsheets/d/{sheet_id}/embed" width="100%" height="600"></iframe>
        """,
        unsafe_allow_html=True
    )

    st.markdown(f"[📄 Buka Google Sheet di tab baru](https://docs.google.com/spreadsheets/d/{sheet_id}/edit)")
