import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from io import BytesIO
import base64

# Title of the app
st.title("Data Visualization Web App")

# File upload
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

# Function to load CSV with different encoding options
def load_csv(file, header_row):
    encodings = ['utf-8', 'ISO-8859-1', 'latin1', 'unicode_escape']
    for encoding in encodings:
        try:
            df = pd.read_csv(file, encoding=encoding, header=header_row)
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
    fig = plt.figure()
    if plot_type == "3D Scatter Plot":
        ax = fig.add_subplot(111, projection='3d')
        if len(x_columns) >= 2 and len(y_columns) == 1:
            ax.scatter(df[x_columns[0]], df[x_columns[1]], df[y_columns[0]], label=f"{y_columns[0]} vs {x_columns[0]} and {x_columns[1]}")
            ax.set_xlabel(x_columns[0])
            ax.set_ylabel(x_columns[1])
            ax.set_zlabel(y_columns[0])
        else:
            st.error("For 3D Scatter Plot, please select exactly two columns for X Axis and one column for Y Axis.")
    else:
        ax = fig.add_subplot(111)
        if plot_type == "Line Plot":
            for y_column in y_columns:
                for x_column in x_columns:
                    ax.plot(df[x_column], df[y_column], label=f"{y_column} vs {x_column}")
        elif plot_type == "Scatter Plot":
            for y_column in y_columns:
                for x_column in x_columns:
                    ax.scatter(df[x_column], df[y_column], label=f"{y_column} vs {x_column}")
        elif plot_type == "Bar Plot":
            for y_column in y_columns:
                for x_column in x_columns:
                    ax.bar(df[x_column], df[y_column], label=f"{y_column} vs {x_column}")
        elif plot_type == "Histogram":
            for y_column in y_columns:
                ax.hist(df[y_column], bins=30, alpha=0.7, label=y_column)
        elif plot_type == "Box Plot":
            df[y_columns].plot(kind='box', ax=ax)

        ax.set_xlabel(" & ".join(x_columns))
        ax.set_ylabel(" & ".join(y_columns))
        ax.set_title(f"{plot_type} of {', '.join(y_columns)} vs {', '.join(x_columns)}")
        ax.legend()
    return fig

def export_graph(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_bytes = buf.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode()
    href = f'<a href="data:file/png;base64,{img_base64}" download="graph.png">Download Graph</a>'
    return href

# Container for dynamic content
placeholder = st.empty()

if uploaded_file is not None:
    # Add a slider to select the header row
    header_row = st.slider("Select the header row (0-indexed)", 0, 100, 16)  # Default to 16 for your case
    
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
        plot_type = st.selectbox("Select Plot Type", ["Line Plot", "Scatter Plot", "Bar Plot", "Histogram", "Box Plot", "3D Scatter Plot"])

        # Generate plot button
        if st.button("Generate Plot"):
            if x_columns and y_columns:
                fig = plot_graph(df, x_columns, y_columns, plot_type)
                placeholder.pyplot(fig)

                # Export graph
                st.markdown(export_graph(fig), unsafe_allow_html=True)
            else:
                st.error("Please select at least one column for both X and Y axes.")

        # Display column names on the right side
        st.write("### Column Names")
        st.write(df.columns.tolist())
else:
    st.write("Please upload a file to get started.")