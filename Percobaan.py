import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import os

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard PLTU OM-2", layout="wide")

# Path penyimpanan file upload permanen
DATA_FILE = "uploaded_data.csv"

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

    # Cek apakah sudah ada data tersimpan
    if "df" not in st.session_state:
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            st.session_state.df = df
            st.success("✅ Data berhasil dimuat dari penyimpanan!")
        else:
            uploaded_file = st.file_uploader("📤 Upload file data (CSV atau Excel)", type=["csv", "xlsx"])
            if uploaded_file is not None:
                # Baca file
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                df.to_csv(DATA_FILE, index=False)  # Simpan ke file permanen
                st.session_state.df = df
                st.success("✅ Data berhasil diunggah dan disimpan!")
            else:
                st.info("Silakan upload file terlebih dahulu untuk menampilkan grafik.")
    
    if "df" in st.session_state:
        df = st.session_state.df
        st.dataframe(df.head())

        columns = df.columns.tolist()
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
            df[date_column] = pd.to_datetime(df[date_column])
            df['Month'] = df[date_column].dt.month_name()

        for col in columns_to_display:
            with st.expander(f"🔲 {col}"):
                # Statistika dasar
                st.subheader("📊 Statistika")
                st.write(f"**Mean:** {df[col].mean():.2f}")
                st.write(f"**Median:** {df[col].median():.2f}")
                st.write(f"**Std Dev:** {df[col].std():.2f}")
                st.write(f"**Min:** {df[col].min():.2f}")
                st.write(f"**Max:** {df[col].max():.2f}")

                # Histogram
                st.subheader("📊 Histogram Distribusi")
                fig_hist = px.histogram(df, x=col, title=f"Distribusi {col}")
                st.plotly_chart(fig_hist, use_container_width=True)

                # Pilih jenis grafik
                chart_types = ["Line", "Bar", "Area", "Scatter"]
                chart_type = st.selectbox(f"Pilih Tipe Grafik untuk {col}", options=chart_types, key=col)

                if date_column:
                    x_col = 'Month'
                else:
                    x_col = df.index

                # Grafik tren
                if chart_type == "Line":
                    fig = px.line(df, x=x_col, y=col, title=f"{col} - {chart_type} Chart")
                elif chart_type == "Bar":
                    fig = px.bar(df, x=x_col, y=col, title=f"{col} - {chart_type} Chart")
                elif chart_type == "Area":
                    fig = px.area(df, x=x_col, y=col, title=f"{col} - {chart_type} Chart")
                elif chart_type == "Scatter":
                    fig = px.scatter(df, x=x_col, y=col, title=f"{col} - {chart_type} Chart")

                st.plotly_chart(fig, use_container_width=True)

                # Box Plot
                st.subheader("📊 Box Plot")
                fig_box = px.box(df, y=col, title=f"Box Plot {col}")
                st.plotly_chart(fig_box, use_container_width=True)

        # Tombol reset/hapus data permanen
        st.markdown("---")
        if st.button("🗑️ Hapus Data yang Tersimpan"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
                del st.session_state["df"]
                st.warning("Data berhasil dihapus. Silakan upload ulang untuk menampilkan grafik.")
            else:
                st.info("Tidak ada data tersimpan yang perlu dihapus.")

# Halaman Kesiapan Peralatan (Google Sheets)
elif selected == "Kesiapan Peralatan":
    st.title("🔧 Kesiapan Peralatan PLTU OM-2")
    st.markdown("Berikut adalah tampilan langsung dari Google Spreadsheet:")

    sheet_id = "1vh_3k_6uacjs96Bpr9ap_gQ-6T3CF-xQfFYt2AuSNvo"

    st.markdown(
        f"""
        <iframe src="https://docs.google.com/spreadsheets/d/{sheet_id}/embed" width="100%" height="600"></iframe>
        """,
        unsafe_allow_html=True
    )

    st.markdown(f"[📄 Buka Google Sheet di tab baru](https://docs.google.com/spreadsheets/d/{sheet_id}/edit)")
