# Arabic HR Resignation Analysis Dashboard

This interactive dashboard helps analyze employee resignation data in Arabic, providing insights into resignation patterns and reasons.

## Features

- 📊 Interactive visualizations of resignation data
- 🔍 Filtering capabilities by gender and department
- 📝 Word cloud analysis of resignation reasons
- 📈 Demographic breakdown of resignations
- 🌐 Full Arabic language support with RTL formatting

## Setup Instructions

1. Install Python 3.8 or higher
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure you have the data file `Simple HR Data.xlsx` in the same directory as `main.py`
4. Run the dashboard:
   ```bash
   streamlit run main.py
   ```

## Data Requirements

The Excel file should contain the following columns:
- الجنس (Gender)
- القسم (Department)
- سبب_الاستقالة (Resignation Reason)
- العمر (Age)
- سنوات_الخبرة (Years of Experience)

## Usage

1. The dashboard will open in your default web browser
2. Use the sidebar filters to analyze specific segments of the data
3. Interact with the charts to explore the data further
4. Toggle the "عرض البيانات الخام" (Show Raw Data) checkbox to view the underlying data

## Note

Make sure you have a font that supports Arabic characters installed on your system. The default is set to 'arial.ttf', but you may need to change this in the code if you're using a different font. 