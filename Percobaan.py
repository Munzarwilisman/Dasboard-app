import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import os

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard PLTU ANGGREK", layout="wide")

# Pastikan folder data tersedia
os.makedirs("data", exist_ok=True)

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Menu Utama",
        options=["Home", "Performance Indikator", "Kesiapan Peralatan"],
        icons=["house", "bar-chart", "gear"],
        menu_icon="cast",
        default_index=0,
    )

# Load atau simpan data ke session_state
if "df" not in st.session_state:
    if os.path.exists("data/last_upload.csv"):
        df = pd.read_csv("data/last_upload.csv")
        st.session_state.df = df

# Halaman Home: Dashboard Parameter Langsung
if selected == "Home":
    st.title("\U0001F4C8 Dashboard Parameter PLTU OM-2")
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

    st.markdown("### \U0001F4C8 Grafik Tren Parameter")

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
    st.title("\U0001F4CA Performance Indikator")

    if "df" not in st.session_state:
        uploaded_file = st.file_uploader("\U0001F4C4 Upload file data (CSV atau Excel)", type=["csv", "xlsx"])

        if uploaded_file is not None:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                df.to_csv("data/last_upload.csv", index=False)
            else:
                df = pd.read_excel(uploaded_file)
                df.to_csv("data/last_upload.csv", index=False)
            st.session_state.df = df
            st.success("\u2705 Data berhasil diunggah!")
        else:
            st.info("Silakan upload file terlebih dahulu untuk menampilkan grafik.")
            st.stop()
    else:
        df = st.session_state.df
        st.dataframe(df.head())

    columns = df.columns.tolist()
    date_columns = df.select_dtypes(include=["datetime", "object"]).columns.tolist()
    exclude_columns = [col for col in columns if col in date_columns]
    columns_to_display = [col for col in columns if col not in exclude_columns]

    st.markdown("---")
    st.subheader("\U0001F4C8 Dashboard Parameter")

    date_column = None
    for col in columns:
        if pd.to_datetime(df[col], errors='coerce').notna().all():
            date_column = col
            break

    if date_column:
        df[date_column] = pd.to_datetime(df[date_column])
        df['Month'] = df[date_column].dt.month_name()

    for col in columns_to_display:
        with st.expander(f"\U0001F7B2 {col}"):
            st.subheader("\U0001F4CA Statistika")
            st.write(f"**Mean:** {df[col].mean():.2f}")
            st.write(f"**Median:** {df[col].median():.2f}")
            st.write(f"**Std Dev:** {df[col].std():.2f}")
            st.write(f"**Min:** {df[col].min():.2f}")
            st.write(f"**Max:** {df[col].max():.2f}")

            st.subheader("\U0001F4CA Histogram Distribusi")
            fig_hist = px.histogram(df, x=col, title=f"Distribusi {col}")
            st.plotly_chart(fig_hist, use_container_width=True)

            chart_types = ["Line", "Bar", "Area", "Scatter"]
            chart_type = st.selectbox(f"Pilih Tipe Grafik untuk {col}", options=chart_types, key=col)

            if date_column:
                if chart_type == "Line":
                    fig = px.line(df, x='Month', y=col)
                elif chart_type == "Bar":
                    fig = px.bar(df, x='Month', y=col)
                elif chart_type == "Area":
                    fig = px.area(df, x='Month', y=col)
                elif chart_type == "Scatter":
                    fig = px.scatter(df, x='Month', y=col)
            else:
                if chart_type == "Line":
                    fig = px.line(df, x=df.index, y=col)
                elif chart_type == "Bar":
                    fig = px.bar(df, x=df.index, y=col)
                elif chart_type == "Area":
                    fig = px.area(df, x=df.index, y=col)
                elif chart_type == "Scatter":
                    fig = px.scatter(df, x=df.index, y=col)

            st.plotly_chart(fig, use_container_width=True)

            st.subheader("\U0001F4CA Box Plot")
            fig_box = px.box(df, y=col, title=f"Box Plot {col}")
            st.plotly_chart(fig_box, use_container_width=True)

# Halaman Kesiapan Peralatan (Google Sheet)
elif selected == "Kesiapan Peralatan":
    st.title("\U0001F527 Kesiapan Peralatan PLTU OM-2")
    st.markdown("Berikut adalah tampilan langsung dari Google Spreadsheet:")

    sheet_id = "1vh_3k_6uacjs96Bpr9ap_gQ-6T3CF-xQfFYt2AuSNvo"
    st.markdown(
        f"""
        <iframe src="https://docs.google.com/spreadsheets/d/{sheet_id}/embed" width="100%" height="600"></iframe>
        """,
        unsafe_allow_html=True
    )
    st.markdown(f"[\U0001F4C4 Buka Google Sheet di tab baru](https://docs.google.com/spreadsheets/d/{sheet_id}/edit)")
