import pandas as pd
import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from st_aggrid import AgGrid
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.stylable_container import stylable_container
from collections import Counter

# Set page config
st.set_page_config(page_title="لوحة استقالات الموظفين", layout="wide")

# Global RTL styling
st.markdown("""
    <style>
    .main, .css-1v0mbdj { direction: rtl; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# Load data
file_path = "Simple HR Data.xlsx"
sheet_name = "الدوران + معدل البقاء"
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Rename columns
df = df.rename(columns={
    'الجنس': 'Gender',
    'القسم': 'Department',
    'السبب': 'ResignationReason',
    'الحالة الاجتماعية': 'MaritalStatus',
    'شريحة العمر': 'AgeGroup',
    'فترة العمل': 'WorkDuration',
    'العمر عند الترك': 'AgeAtExit',
    'المسمى الوظيفي': 'JobTitle',
    'تاريخ الميلاد': 'BirthDate'
})

df['BirthDate'] = pd.to_datetime(df['BirthDate'], errors='coerce')
df['BirthMonth'] = df['BirthDate'].dt.month

# Layout: content left, filters right
content_col, filters_col = st.columns([3, 1])

# --- FILTERS ON THE RIGHT ---
with filters_col:
    st.markdown("<h4 style='text-align:right;'>🎛️ عوامل التصفية</h4>", unsafe_allow_html=True)

    st.markdown("<div style='text-align:right;'>الجنس</div>", unsafe_allow_html=True)
    gender_filter = st.selectbox("", df['Gender'].dropna().unique())

    st.markdown("<div style='text-align:right;'>القسم</div>", unsafe_allow_html=True)
    dept_filter = st.selectbox("", sorted(df['Department'].dropna().unique()))

    st.markdown("<div style='text-align:right;'>سبب الاستقالة</div>", unsafe_allow_html=True)
    reason_filter = st.multiselect("", df['ResignationReason'].dropna().unique(), default=df['ResignationReason'].dropna().unique())

    st.markdown("<div style='text-align:right;'>شريحة العمر</div>", unsafe_allow_html=True)
    age_group_filter = st.multiselect("", df['AgeGroup'].dropna().unique(), default=df['AgeGroup'].dropna().unique())

    st.markdown("<div style='text-align:right;'>الحالة الاجتماعية</div>", unsafe_allow_html=True)
    marital_filter = st.multiselect("", df['MaritalStatus'].dropna().unique(), default=df['MaritalStatus'].dropna().unique())

# --- CONTENT ON THE LEFT ---
with content_col:
    st.markdown("<h1 style='text-align:right;'>📊 لوحة تحليل استقالات الموظفين</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:right;'>أداة تساعد إدارة الموارد البشرية على تحليل وفهم اتجاهات ترك الموظفين للعمل.</p>", unsafe_allow_html=True)

    # Apply filters
    filtered_df = df[
        (df['Gender'] == gender_filter) &
        (df['Department'] == dept_filter) &
        df['ResignationReason'].isin(reason_filter) &
        df['AgeGroup'].isin(age_group_filter) &
        df['MaritalStatus'].isin(marital_filter)
    ]

    # KPIs
    with st.container():
        st.markdown("<div style='display: flex; justify-content: flex-end; gap: 2rem;'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col2:
            st.metric("📉 عدد المستقيلين", len(filtered_df))
        with col1:
            st.metric("🏢 عدد الأقسام", 1 if dept_filter else 0)
        st.markdown("</div>", unsafe_allow_html=True)
    style_metric_cards()

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📌 أسباب الاستقالة",
        "👥 توزيع الجنس",
        "☁️ سحابة الكلمات",
        "📊 شريحة العمر",
        "💍 الحالة الاجتماعية",
        "📅 شهر الميلاد"
    ])

    # Tab 1: Pie chart - Resignation reasons (NO reshaping)
    with tab1:
        pie_df = filtered_df.copy()
        pie_df["ResignationReason"] = pie_df["ResignationReason"].fillna("غير محدد")
        fig_pie = px.pie(
            pie_df,
            names="ResignationReason",
            title="توزيع أسباب الاستقالة",
            hole=0.45
        )
        fig_pie.update_layout(title={'x': 1, 'xanchor': 'right'}, legend=dict(x=1, xanchor='right'))
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    # Tab 2: Bar chart - Gender
    with tab2:
        gender_df = filtered_df.copy()
        gender_df["Gender"] = gender_df["Gender"].fillna("غير محدد")
        fig_bar = px.bar(
            gender_df.groupby("Gender").size().reset_index(name="Count"),
            x="Gender", y="Count", text="Count",
            title="توزيع المستقيلين حسب الجنس"
        )
        fig_bar.update_layout(title={'x': 1, 'xanchor': 'right'})
        st.plotly_chart(fig_bar, use_container_width=True)

    # Tab 3: Word cloud
    with tab3:
        st.markdown("### سحابة الكلمات لأسباب الاستقالة")
        text_list = filtered_df['ResignationReason'].dropna().tolist()
        word_freq = Counter(text_list)
        if word_freq:
            wordcloud = WordCloud(
                font_path='arial',
                background_color='white',
                width=800, height=400,
                colormap='viridis',
                regexp=r"[\u0600-\u06FF]+"
            ).generate_from_frequencies(word_freq)
            fig_wc, ax = plt.subplots(figsize=(10, 4))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig_wc)
        else:
            st.warning("لا توجد بيانات صالحة لتوليد سحابة كلمات.")

    # Tab 4: Age group + Work duration
    with tab4:
        st.markdown("### عدد المستقيلين حسب شريحة العمر")
        age_df = filtered_df.copy()
        age_df["AgeGroup"] = age_df["AgeGroup"].fillna("غير محدد")
        fig_age = px.bar(
            age_df.groupby("AgeGroup").size().reset_index(name="Count"),
            x="AgeGroup", y="Count", text="Count",
            title="توزيع المستقيلين حسب شريحة العمر"
        )
        fig_age.update_layout(title={'x': 1, 'xanchor': 'right'})
        st.plotly_chart(fig_age, use_container_width=True)

        st.markdown("### توزيع فترة العمل")
        if 'WorkDuration' in filtered_df.columns:
            fig_hist = px.histogram(filtered_df, x="WorkDuration", nbins=20, title="توزيع فترة العمل")
            fig_hist.update_layout(title={'x': 1, 'xanchor': 'right'})
            st.plotly_chart(fig_hist, use_container_width=True)

    # Tab 5: Pie chart - Marital Status
    with tab5:
        status_df = filtered_df.copy()
        status_df["MaritalStatus"] = status_df["MaritalStatus"].fillna("غير محدد")
        fig_status = px.pie(status_df, names="MaritalStatus", title="الحالة الاجتماعية", hole=0.4)
        fig_status.update_layout(title={'x': 1, 'xanchor': 'right'})
        st.plotly_chart(fig_status, use_container_width=True)

    # Tab 6: Birth month chart
    with tab6:
        st.markdown("### توزيع المستقيلين حسب شهر الميلاد")
        month_map = {
            1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
            5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
            9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
        }
        birth_chart_df = filtered_df.copy()
        birth_chart_df['BirthMonth'] = pd.to_numeric(birth_chart_df['BirthMonth'], errors='coerce')
        birth_chart_df['BirthMonthName'] = birth_chart_df['BirthMonth'].map(month_map).fillna("غير معروف")
        ordered_months = [month_map[m] for m in range(1, 13)]
        grouped = birth_chart_df.groupby("BirthMonthName").size().reset_index(name="Count")
        grouped["BirthMonthName"] = pd.Categorical(grouped["BirthMonthName"], categories=ordered_months, ordered=True)
        grouped = grouped.sort_values("BirthMonthName")
        fig_birth = px.bar(grouped, x="BirthMonthName", y="Count", text="Count", title="عدد المستقيلين حسب شهر الميلاد")
        fig_birth.update_layout(title={'x': 1, 'xanchor': 'right'})
        st.plotly_chart(fig_birth, use_container_width=True)

# Footer
st.markdown("---")
st.caption("🛠️ تم التصميم باستخدام Streamlit و Plotly و AgGrid - البيانات من ملف HR")
