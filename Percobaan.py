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

# Halaman Home: Dashboard Parameter Langsung
if selected == "Home":
    st.title("📈 Dashboard Parameter PLTU OM-2")
    st.markdown("Tampilan ringkas dari semua parameter dalam bentuk grafik tren.")

    if "df" not in st.session_state:
        st.warning("Silakan upload data terlebih dahulu melalui menu 'Performance Indikator'.")
        st.stop()

    df = st.session_state.df

    # Mendeteksi kolom waktu
    date_column = None
    for col in df.columns:
        if pd.to_datetime(df[col], errors='coerce').notna().all():
            date_column = col
            df[date_column] = pd.to_datetime(df[date_column])
            df['Month'] = df[date_column].dt.strftime('%b %Y')
            break

    numerical_columns = df.select_dtypes(include='number').columns.tolist()

    st.markdown("### 📈 Grafik Tren Parameter")

    # Layout 2 kolom grafik per baris
    for i in range(0, len(numerical_columns), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(numerical_columns):
                colname = numerical_columns[i + j]
                with cols[j]:
                    st.markdown(f"**{colname}**")
                    if date_column:
                        df_sorted = df.sort_values(by=date_column)
                        fig = px.line(df_sorted, x="Month", y=colname, title="", markers=True)
                    else:
                        fig = px.line(df, x=df.index, y=colname, title="", markers=True)

                    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300)
                    st.plotly_chart(fig, use_container_width=True)

# Halaman Performance Indikator
elif selected == "Performance Indikator":
    st.title("📊 Performance Indikator")

    # Menggunakan session_state untuk menyimpan data
    if "df" not in st.session_state:
        uploaded_file = st.file_uploader("📄 Upload file data (CSV atau Excel)", type=["csv", "xlsx"])

        if uploaded_file is not None:
            # Baca file
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.session_state.df = df  # Simpan dataframe ke session_state
            st.success("✅ Data berhasil diunggah!")
        else:
            st.info("Silakan upload file terlebih dahulu untuk menampilkan grafik.")
    else:
        # Tampilkan data yang sudah ada di session_state
        df = st.session_state.df
        st.dataframe(df.head())

        # Opsi untuk memperbarui file
        uploaded_file = st.file_uploader("📄 Upload file data (CSV atau Excel) untuk mengganti data", type=["csv", "xlsx"])

        if uploaded_file is not None:
            # Baca file baru dan perbarui session_state
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.session_state.df = df  # Update session_state dengan data baru
            st.success("✅ Data berhasil diperbarui!")

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
        df[date_column] = pd.to_datetime(df[date_column])
        df['Month'] = df[date_column].dt.month_name()

    for col in columns_to_display:
        with st.expander(f"🔲 {col}"):
            st.subheader("📊 Statistika")
            st.write(f"**Mean:** {df[col].mean():.2f}")
            st.write(f"**Median:** {df[col].median():.2f}")
            st.write(f"**Std Dev:** {df[col].std():.2f}")
            st.write(f"**Min:** {df[col].min():.2f}")
            st.write(f"**Max:** {df[col].max():.2f}")

            st.subheader("📊 Histogram Distribusi")
            fig_hist = px.histogram(df, x=col, title=f"Distribusi {col}")
            st.plotly_chart(fig_hist, use_container_width=True)

            chart_types = ["Line", "Bar", "Area", "Scatter"]
            chart_type = st.selectbox(f"Pilih Tipe Grafik untuk {col}", options=chart_types, key=col)

            if date_column:
                if chart_type == "Line":
                    fig = px.line(df, x='Month', y=col, title=f"{col} - {chart_type} Chart")
                elif chart_type == "Bar":
                    fig = px.bar(df, x='Month', y=col, title=f"{col} - {chart_type} Chart")
                elif chart_type == "Area":
                    fig = px.area(df, x='Month', y=col, title=f"{col} - {chart_type} Chart")
                elif chart_type == "Scatter":
                    fig = px.scatter(df, x='Month', y=col, title=f"{col} - {chart_type} Chart")
            else:
                if chart_type == "Line":
                    fig = px.line(df, x=df.index, y=col, title=f"{col} - {chart_type} Chart")
                elif chart_type == "Bar":
                    fig = px.bar(df, x=df.index, y=col, title=f"{col} - {chart_type} Chart")
                elif chart_type == "Area":
                    fig = px.area(df, x=df.index, y=col, title=f"{col} - {chart_type} Chart")
                elif chart_type == "Scatter":
                    fig = px.scatter(df, x=df.index, y=col, title=f"{col} - {chart_type} Chart")

            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📊 Box Plot")
            fig_box = px.box(df, y=col, title=f"Box Plot {col}")
            st.plotly_chart(fig_box, use_container_width=True)

# Halaman Kesiapan Peralatan (Google Sheet)
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
