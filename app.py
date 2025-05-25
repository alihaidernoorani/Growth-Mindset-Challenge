import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Set Streamlit page configuration
st.set_page_config(page_title="File Converter", page_icon="📂", layout="wide")

# App title and description
st.title("📂 File Converter")
st.write("Easily transform your files between CSV and Excel formats with optional data cleaning and visualization.")

# File uploader allowing CSV and Excel files
files = st.file_uploader("Upload your file(s)", type=['csv', 'xlsx'], accept_multiple_files=True)

# Process each uploaded file
if files:
    for file in files:
        # Determine file extension
        ext = os.path.splitext(file.name)[-1].lower()

        # Read file into DataFrame
        try:
            if ext == '.csv':
                df = pd.read_csv(file)
            elif ext == '.xlsx':
                df = pd.read_excel(file)
            else:
                st.error(f"❌ Unsupported file type: {ext}")
                continue
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")
            continue

        # Display file preview
        st.subheader(f"📄 {file.name} - Preview")
        st.dataframe(df.head())

        # Data cleaning options
        modified = False  # Track if the dataframe was modified

        if st.checkbox(f"🗑️ Remove Duplicates - {file.name}"):
            df = df.drop_duplicates()
            st.success(f"✔ Duplicates removed from {file.name}")
            modified = True
            st.dataframe(df.head())

        if st.checkbox(f"🧹 Fill Missing Values - {file.name}"):
            df.fillna(df.select_dtypes(include=["number"]).mean(), inplace=True)
            st.success("✔ Missing values filled with column mean")
            modified = True
            st.dataframe(df.head())

        # Allow user to select columns to keep
        selected_columns = st.multiselect(f"📌 Select columns to keep - {file.name}", df.columns, default=df.columns)
        if set(selected_columns) != set(df.columns):
            df = df[selected_columns]
            modified = True
            st.dataframe(df.head())

        # Display bar chart for numeric columns
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"📈 Show Visualization for {file.name}"):
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) >= 2:
                st.bar_chart(df[numeric_cols].iloc[:, :2])
            else:
                st.warning("⚠ Not enough numeric columns for visualization.")

        # Choose output format
        output_format = st.radio(f"💾 Select output format for {file.name}", ["csv", "xlsx"])

        # Download button to save processed file
        if st.button(f"⬇ Download {file.name} as {output_format}"):
            output = BytesIO()
            try:
                if output_format == 'csv':
                    df.to_csv(output, index=False)
                    mime_type = "text/csv"
                    file_extension = "csv"
                else:
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Sheet1')
                        writer.close()
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    file_extension = "xlsx"

                output.seek(0)
                st.download_button(label=f"⬇ Download {file.name}.{file_extension}", 
                                   data=output, 
                                   file_name=f"{file.name.split('.')[0]}.{file_extension}", 
                                   mime=mime_type)
            except Exception as e:
                st.error(f"❌ Error processing {file.name}: {e}")
