import pandas as pd
import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
from streamlit_extras.metric_cards import style_metric_cards
import arabic_reshaper
from bidi.algorithm import get_display
from wordcloud import WordCloud, STOPWORDS

# Set page config FIRST as required by Streamlit
st.set_page_config(page_title="لوحة استقالات الموظفين", layout="wide")

# Load the external CSS file
with open('styles.css', 'r', encoding='utf-8') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Define your color palette
palette = {
    "darkest": "#0d1b2a",
    "dark": "#1b263b",
    "medium": "#415a77",
    "light": "#778da9",
    "offwhite": "#e0e1dd"
}

# File and sheet name - adjust path as needed
file_path = "Simple HR Data.xlsx"
sheet_name = "الدوران + معدل البقاء"

# Rename dict matching your headers
rename_dict = {
    'الرقم': 'EmployeeID',
    'اسم الموظف': 'EmployeeName',
    'المسمى الوظيفي': 'JobTitle',
    'المسمى': 'Position',
    'القسم': 'Department',
    'الإدارة': 'Unit',
    'تاريخ بدء العمل': 'DateOfStart',
    'تاريخ الترك': 'DateOfLeaving',
    'الجنس': 'Gender',
    'تاريخ الميلاد': 'BirthDate',
    'الحالة الاجتماعية': 'MaritalStatus',
    'فترة العمل': 'WorkDuration',
    'الترك قبل 4.4': 'LeaveBefore4_4',
    'العمر عند الترك': 'AgeAtExit',
    'شريحة العمر': 'AgeGroup',
    'الشهر': 'Month',
    'السبب': 'ResignationReason',
    'Turn Over': 'Turnover',
    'معدل المدة': 'TimeAvg',
    'RN Turn Over': 'RN_Turnover'
}

# Load and rename
df = pd.read_excel(file_path, sheet_name=sheet_name)
df = df.rename(columns=rename_dict)

# Convert dates safely
df['BirthDate'] = pd.to_datetime(df['BirthDate'], errors='coerce')
df['DateOfStart'] = pd.to_datetime(df['DateOfStart'], errors='coerce')
df['DateOfLeaving'] = pd.to_datetime(df['DateOfLeaving'], errors='coerce')

# Extract month info for birth and leaving
df['BirthMonth'] = df['BirthDate'].dt.month
df['LeavingMonth'] = df['DateOfLeaving'].apply(lambda x: x.to_period('M').to_timestamp() if pd.notnull(x) else pd.NaT)

# Layout with max-width wrapper
content_col, filters_col = st.columns([3, 1])

with filters_col:
    st.markdown("<h4 style='text-align:right;'>🎛️ عوامل التصفية</h4>", unsafe_allow_html=True)

    with st.container():
        gender_filter = st.selectbox("الجنس", options=["الكل"] + sorted(df['Gender'].dropna().unique().tolist()))
        dept_filter = st.selectbox("القسم", options=["الكل"] + sorted(df['Department'].dropna().unique().tolist()))
        unit_filter = st.selectbox("الإدارة", options=["الكل"] + sorted(df['Unit'].dropna().unique().tolist()) if 'Unit' in df.columns else ["الكل"])

        # These three will now be aligned to the right
        reason_filter = st.multiselect("سبب الاستقالة", options=sorted(df['ResignationReason'].dropna().unique()), default=sorted(df['ResignationReason'].dropna().unique()))
        age_group_filter = st.multiselect("شريحة العمر", options=sorted(df['AgeGroup'].dropna().unique()), default=sorted(df['AgeGroup'].dropna().unique()))
        marital_filter = st.multiselect("الحالة الاجتماعية", options=sorted(df['MaritalStatus'].dropna().unique()), default=sorted(df['MaritalStatus'].dropna().unique()))

# Apply filters
filtered_df = df.copy()
if gender_filter != "الكل":
    filtered_df = filtered_df[filtered_df['Gender'] == gender_filter]
if dept_filter != "الكل":
    filtered_df = filtered_df[filtered_df['Department'] == dept_filter]
if 'Unit' in filtered_df.columns and unit_filter != "الكل":
    filtered_df = filtered_df[filtered_df['Unit'] == unit_filter]
filtered_df = filtered_df[
    filtered_df['ResignationReason'].isin(reason_filter) &
    filtered_df['AgeGroup'].isin(age_group_filter) &
    filtered_df['MaritalStatus'].isin(marital_filter)
]

# Define Plotly color sequence from your palette
color_sequence = [palette['medium'], palette['light'], palette['dark'], palette['darkest'], palette['offwhite']]

with content_col:
    st.markdown("""<div style="max-width:1200px; margin:auto;">""", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:right;'>📊 لوحة تحليل استقالات الموظفين</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:right;'>أداة تساعد إدارة الموارد البشرية على تحليل وفهم اتجاهات ترك الموظفين للعمل.</p>", unsafe_allow_html=True)

    # KPIs
    def custom_kpi(label: str, value: str):
        st.markdown(f"""
        <div style="
            text-align: right;
            font-weight: 700;
            margin-bottom: 1.5rem;
            background-color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            color: #0d1b2a;
        ">
            <div style="font-size: 1.2rem;">{label}</div>
            <div style="font-size: 2.5rem; color: #415a77;">{value}</div>
        </div>
        """, unsafe_allow_html=True)


    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        custom_kpi("📉 عدد المستقيلين", str(len(filtered_df)))

    with kpi2:
        custom_kpi("🏢 عدد الأقسام", str(filtered_df['Department'].nunique()))

    with kpi3:
        avg_dur = filtered_df['WorkDuration'].mean()
        avg_str = f"{avg_dur:.1f}" if avg_dur else "غير متوفر"
        custom_kpi("⏳ متوسط فترة العمل (شهور)", avg_str)

    style_metric_cards()

    tabs = st.tabs([
        "📌 أسباب الاستقالة",
        "👥 توزيع الجنس",
        "☁️ سحابة الكلمات",
        "📊 شريحة العمر",
        "💍 الحالة الاجتماعية",
        "📅 شهر الميلاد",
        "📈 معدل الدوران الشهري",
        "🏢 الدوران حسب القسم والوحدة",
        "📅 الموظفون الجدد مقابل المستقيلين",
        "⏳ مدة العمل حسب القسم والجنس",
        "🚩 أقسام عالية الدوران",
        "📊 تحليلات إضافية"  # ⬅️ Add this
    ])


    # Tab 0: Resignation reasons pie
    with tabs[0]:
        pie_df = filtered_df.copy()
        pie_df["ResignationReason"] = pie_df["ResignationReason"].fillna("غير محدد")
        fig = px.pie(
            pie_df,
            names="ResignationReason",
            title="توزيع أسباب الاستقالة    ",
            hole=0.45,
            color_discrete_sequence=color_sequence
        )
        fig.update_layout(title={'x': 1, 'xanchor': 'right'}, legend=dict(x=1, xanchor='right'))
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    # Tab 1: Gender distribution
    with tabs[1]:
        gender_counts = filtered_df['Gender'].fillna("غير محدد").value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        fig = px.bar(
            gender_counts,
            x='Gender',
            y='Count',
            text='Count',
            title="توزيع المستقيلين حسب الجنس    ",
            color_discrete_sequence=color_sequence
        )
        fig.update_layout(title={'x': 1, 'xanchor': 'right'}, xaxis_title = 'الجنس', yaxis_title='عدد المستقيلين')
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        st.markdown("### سحابة الكلمات لأسباب الاستقالة    ")

        # Drop NaNs and ensure only non-empty strings are kept
        reasons = [str(r).strip() for r in filtered_df['ResignationReason'].dropna() if str(r).strip()]
        
        # Reshape Arabic words correctly
        reshaped_reasons = [
            get_display(arabic_reshaper.reshape(reason))
            for reason in reasons if any(char >= '\u0600' and char <= '\u06FF' for char in reason)
        ]

        reasons_text = " ".join(reshaped_reasons)

        if reasons_text.strip():
            custom_stopwords = set(STOPWORDS).union({'من', 'في', 'على', 'أن', 'إلى', 'عن', 'و', 'وأن'})
            try:
                wordcloud = WordCloud(
                    font_path='arial',
                    background_color=palette['offwhite'],
                    width=800,
                    height=400,
                    colormap='viridis',
                    regexp=r"[\u0600-\u06FF]+",
                    stopwords=custom_stopwords
                ).generate(reasons_text)

                fig_wc, ax = plt.subplots(figsize=(10, 4))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig_wc)
            except ValueError:
                st.warning("لا توجد كلمات كافية لتوليد سحابة كلمات.")
        else:
            st.warning("لا توجد بيانات صالحة لتوليد سحابة كلمات.")


    # Tab 3: Age group + WorkDuration
    with tabs[3]:
        age_counts = filtered_df['AgeGroup'].fillna("غير محدد").value_counts().reset_index()
        age_counts.columns = ['AgeGroup', 'Count']
        fig1 = px.bar(
            age_counts,
            x='AgeGroup',
            y='Count',
            text='Count',
            title="توزيع المستقيلين حسب شريحة العمر    ",
            color_discrete_sequence=color_sequence
        )
        fig1.update_layout(title={'x': 1, 'xanchor': 'right'}, xaxis_title = 'شريحة العمر', yaxis_title='عدد المستقيلين')
        st.plotly_chart(fig1, use_container_width=True)

        if 'WorkDuration' in filtered_df.columns:
            fig2 = px.histogram(
                filtered_df,
                x='WorkDuration',
                nbins=20,
                title="توزيع فترة العمل    ",
                color_discrete_sequence=[palette['medium']]
            )
            fig2.update_layout(title={'x': 1, 'xanchor': 'right'}, xaxis_title = 'فترة العمل (شهور)', yaxis_title='عدد المستقيلين')
            st.plotly_chart(fig2, use_container_width=True)

    # Tab 4: Marital status pie
    with tabs[4]:
        ms_counts = filtered_df['MaritalStatus'].fillna("غير محدد").value_counts().reset_index()
        ms_counts.columns = ['MaritalStatus', 'Count']
        fig = px.pie(
            ms_counts,
            names='MaritalStatus',
            values='Count',
            title="الحالة الاجتماعية    ",
            hole=0.4,
            color_discrete_sequence=color_sequence
        )
        fig.update_layout(title={'x': 1, 'xanchor': 'right'}, xaxis_title = 'الحالة الاجتماعية', yaxis_title='عدد المستقيلين')
        st.plotly_chart(fig, use_container_width=True)

    # Tab 5: Birth month bar
    with tabs[5]:
        month_map = {
            1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
            5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
            9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
        }
        bm_df = filtered_df.copy()
        bm_df['BirthMonth'] = pd.to_numeric(bm_df['BirthMonth'], errors='coerce')
        bm_df['BirthMonthName'] = bm_df['BirthMonth'].map(month_map).fillna("غير معروف")
        bm_ordered = [month_map[i] for i in range(1, 13)]
        counts = bm_df['BirthMonthName'].value_counts().reindex(bm_ordered, fill_value=0).reset_index()
        counts.columns = ['BirthMonthName', 'Count']
        fig = px.bar(
            counts,
            x='BirthMonthName',
            y='Count',
            text='Count',
            title="عدد المستقيلين حسب شهر الميلاد    ",
            color_discrete_sequence=color_sequence
        )
        fig.update_layout(title={'x': 1, 'xanchor': 'right'}, xaxis_title = 'الشهر', yaxis_title='عدد المستقيلين')
        st.plotly_chart(fig, use_container_width=True)

    # Tab 6: Monthly turnover trend (leavers count)
    with tabs[6]:
        monthly_leavers = filtered_df.dropna(subset=['DateOfLeaving'])
        monthly_leavers['YearMonth'] = monthly_leavers['DateOfLeaving'].dt.to_period('M').dt.to_timestamp()
        monthly_counts = monthly_leavers.groupby('YearMonth').size().reset_index(name='LeaversCount')
        fig = px.line(
            monthly_counts,
            x='YearMonth',
            y='LeaversCount',
            markers=True,
            title='معدل الدوران الشهري    ',
            color_discrete_sequence=[palette['medium']]
        )
        fig.update_layout(title={'x': 1, 'xanchor': 'right'}, xaxis_title='الشهر', yaxis_title='عدد المستقيلين')
        st.plotly_chart(fig, use_container_width=True)

    # Tab 7: Turnover by Department and Unit
    with tabs[7]:
        turnover_dept = filtered_df.dropna(subset=['DateOfLeaving'])
        dept_unit_counts = turnover_dept.groupby(['Department', 'Unit']).size().reset_index(name='LeaversCount')
        fig = px.bar(
            dept_unit_counts,
            x='Department',
            y='LeaversCount',
            color='Unit',
            barmode='group',
            title='الدوران حسب القسم والوحدة    ',
            color_discrete_sequence=color_sequence
        )
        fig.update_layout(title={'x': 1, 'xanchor': 'right'}, xaxis_title = 'القسم', yaxis_title='عدد المستقيلين')
        st.plotly_chart(fig, use_container_width=True)

    # Tab 8: New hires vs leavers by month
    with tabs[8]:
        hires = filtered_df.dropna(subset=['DateOfStart']).copy()
        hires['YearMonthStart'] = hires['DateOfStart'].dt.to_period('M').dt.to_timestamp()
        leavers = filtered_df.dropna(subset=['DateOfLeaving']).copy()
        leavers['YearMonthLeave'] = leavers['DateOfLeaving'].dt.to_period('M').dt.to_timestamp()
        hires_counts = hires.groupby('YearMonthStart').size().reset_index(name='NewHires')
        leavers_counts = leavers.groupby('YearMonthLeave').size().reset_index(name='Leavers')
        hires_counts = hires_counts.rename(columns={'YearMonthStart':'YearMonth'})
        leavers_counts = leavers_counts.rename(columns={'YearMonthLeave':'YearMonth'})
        combined = pd.merge(hires_counts, leavers_counts, on='YearMonth', how='outer').fillna(0).sort_values('YearMonth')
        fig = px.line(
            combined,
            x='YearMonth',
            y=['NewHires', 'Leavers'],
            markers=True,
            title='الموظفون الجدد مقابل المستقيلين    ',
            color_discrete_sequence=[palette['medium'], palette['light']]
        )
        fig.update_layout(title={'x': 1, 'xanchor': 'right'}, xaxis_title='الشهر', yaxis_title='عدد الموظفين')
        st.plotly_chart(fig, use_container_width=True)

    # Tab 9: Avg work duration by Dept and Gender
    with tabs[9]:
        if 'WorkDuration' in filtered_df.columns and filtered_df['WorkDuration'].notnull().any():
            avg_duration = filtered_df.groupby(['Department', 'Gender'])['WorkDuration'].mean().reset_index()
            fig = px.bar(
                avg_duration,
                x='Department',
                y='WorkDuration',
                color='Gender',
                barmode='group',
                title='متوسط فترة العمل حسب القسم والجنس    ',
                text=avg_duration['WorkDuration'].round(1),
                color_discrete_sequence=color_sequence
            )
            fig.update_layout(title={'x': 1, 'xanchor': 'right'}, xaxis_title = 'القسم', yaxis_title='متوسط فترة العمل (شهور)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد بيانات كافية لفترة العمل.")

    # Tab 10: High turnover departments alert
    with tabs[10]:
        turnover_threshold = st.slider("تحديد حد الدوران العالي", min_value=0, max_value=100, value=20)
        turnover_rates = filtered_df.groupby('Department').apply(
            lambda x: len(x.dropna(subset=['DateOfLeaving'])) / max(len(x),1) * 100
        ).reset_index(name='TurnoverRate')
        high_turnover = turnover_rates[turnover_rates['TurnoverRate'] >= turnover_threshold].sort_values('TurnoverRate', ascending=False)

        st.markdown(f"###  الأقسام التي لديها معدل دوران أعلى من%{turnover_threshold}")
        if not high_turnover.empty:
            st.dataframe(high_turnover.style.format({"TurnoverRate": "{:.2f}%"}))
            fig = px.bar(
                high_turnover,
                x='Department',
                y='TurnoverRate',
                title='الأقسام ذات معدل الدوران العالي    ',
                color_discrete_sequence=[palette['dark']]
            )
            fig.update_layout(title={'x': 1, 'xanchor': 'right'}, xaxis_title='القسم',yaxis_title='معدل الدوران (%)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد أقسام تتجاوز حد معدل الدوران المحدد.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Tab 11: Advanced Insights
    with tabs[11]:
        st.markdown("### ⏰ مدة العمل قبل الاستقالة")
        fig = px.histogram(
            filtered_df,
            x="WorkDuration",
            nbins=20,
            title="مدة العمل قبل الاستقالة",
            color_discrete_sequence=["#415a77"]
        )
        fig.update_layout(title={'x': 1, 'xanchor': 'right'}, xaxis_title="فترة العمل", yaxis_title="عدد الموظفين")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📌 نسبة الاستقالات المبكرة (قبل 4.4 أشهر)")
        early_leave_counts = filtered_df['LeaveBefore4_4'].fillna("كلا").value_counts().reset_index()
        early_leave_counts.columns = ['LeaveBefore4_4', 'Count']
        fig = px.pie(
            early_leave_counts,
            names="LeaveBefore4_4",
            values="Count",
            hole=0.4,
            title="الترك قبل 4.4 أشهر",
            color_discrete_sequence=["#1b263b", "#778da9"]
        )
        fig.update_layout(title={'x': 1, 'xanchor': 'right'})
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 👔 عدد المستقيلين حسب المسمى الوظيفي")
        job_counts = filtered_df['JobTitle'].value_counts().reset_index()
        job_counts.columns = ['JobTitle', 'Count']
        fig = px.bar(
            job_counts,
            x='JobTitle',
            y='Count',
            text='Count',
            title="عدد المستقيلين حسب المسمى الوظيفي",
            color_discrete_sequence=["#778da9"]
        )
        fig.update_layout(title={'x': 1, 'xanchor': 'right'}, xaxis_title="المسمى الوظيفي", yaxis_title="عدد")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📊 أسباب الاستقالة حسب شريحة العمر")
        if 'ResignationReason' in filtered_df.columns and 'AgeGroup' in filtered_df.columns:
            reason_age_df = filtered_df.groupby(['AgeGroup', 'ResignationReason']).size().reset_index(name='Count')
            fig = px.bar(
                reason_age_df,
                x='AgeGroup',
                y='Count',
                color='ResignationReason',
                barmode='stack',
                text='Count',
                title="أسباب الاستقالة حسب شريحة العمر",
                color_discrete_sequence=["#415a77", "#778da9", "#1b263b"]
            )
            fig.update_layout(title={'x': 1, 'xanchor': 'right'}, xaxis_title="شريحة العمر", yaxis_title="عدد المستقيلين")
            st.plotly_chart(fig, use_container_width=True)


# Footer
st.markdown("---")
st.caption("🛠️ تم التصميم باستخدام Streamlit و Plotly - البيانات من ملف HR")
