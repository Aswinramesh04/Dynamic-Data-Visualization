import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from io import BytesIO
import base64
import plotly.express as px
import plotly.graph_objects as go

# Title of the app
st.title("Data Visualization Web App")

# File upload
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

# Function to load CSV with different encoding options
def load_csv(file, header_row):
    encodings = ['utf-8', 'ISO-8859-1', 'latin1', 'unicode_escape']
    for encoding in encodings:
        try:
            df = pd.read_csv(file, encoding=encoding, header=header_row, low_memory=False, dtype=str)
            return df
        except Exception as e:
            st.write(f"Failed to load with encoding {encoding}: {e}")
    return None

# Function to load Excel
def load_excel(file, header_row):
    try:
        df = pd.read_excel(file, header=header_row)
        return df
    except Exception as e:
        st.write(f"Failed to load Excel file: {e}")
    return None

def plot_graph(df, x_columns, y_columns, plot_type):
    if plot_type == "3D Scatter Plot":
        if len(x_columns) >= 2 and len(y_columns) == 1:
            fig = px.scatter_3d(df, x=x_columns[0], y=x_columns[1], z=y_columns[0])
        else:
            st.error("For 3D Scatter Plot, please select exactly two columns for X Axis and one column for Y Axis.")
            return None
    else:
        if plot_type == "Line Plot":
            fig = px.line(df, x=x_columns[0], y=y_columns)
        elif plot_type == "Scatter Plot":
            fig = px.scatter(df, x=x_columns[0], y=y_columns)
        elif plot_type == "Bar Plot":
            fig = px.bar(df, x=x_columns[0], y=y_columns)
        elif plot_type == "Box Plot":
            fig = px.box(df, y=y_columns)

    return fig

def export_graph(fig):
    buf = BytesIO()
    fig.write_image(buf, format="png")
    buf.seek(0)
    img_bytes = buf.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode()
    href = f'<a href="data:file/png;base64,{img_base64}" download="graph.png">Download Graph</a>'
    return href

# Container for dynamic content
placeholder = st.empty()

if uploaded_file is not None:
    # Add a slider to select the header row
    header_row = st.slider("Select the header row (0-indexed)", 0, 100, 0)  # Default to 0
    
    if uploaded_file.name.endswith('.csv'):
        df = load_csv(uploaded_file, header_row)
    else:
        df = load_excel(uploaded_file, header_row)
    
    if df is not None:
        st.write("### Uploaded Data")
        st.write(df.head())

        # User selects the columns for x and y axes
        x_columns = st.multiselect("Select the X Axis columns", df.columns)
        y_columns = st.multiselect("Select the Y Axis columns", df.columns)

        # User selects the type of plot
        plot_type = st.selectbox("Select Plot Type", ["Line Plot", "Scatter Plot", "Bar Plot", "Box Plot", "3D Scatter Plot"])

        # Generate plot button
        if st.button("Generate Plot"):
            if x_columns and y_columns:
                fig = plot_graph(df, x_columns, y_columns, plot_type)
                if fig is not None:
                    placeholder.plotly_chart(fig)

                    # Export graph
                    st.markdown(export_graph(fig), unsafe_allow_html=True)
            else:
                st.error("Please select at least one column for both X and Y axes.")

        # Display column names on the right side
        st.write("### Column Names")
        st.write(df.columns.tolist())
else:
    st.write("Please upload a file to get started.")
