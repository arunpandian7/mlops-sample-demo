import streamlit as st
import pandas as pd
from PIL import Image
import sqlite3
import os

# Path to the image directory
IMAGE_DIR = "/home/arun/Dev/mlops-sample/backend/images"

# Database file path
DATABASE_URL = "/home/arun/Dev/mlops-sample/backend/db.sqlite"

# Function to fetch feedback data from the database
def fetch_feedback_data():
    conn = sqlite3.connect(DATABASE_URL)
    query = """
    SELECT id, filename, classification, feedback
    FROM images
    WHERE feedback IS NOT NULL
    """
    data = pd.read_sql(query, conn)
    conn.close()
    return data

# Function to load images and display them
def load_image(image_filename):
    image_path = os.path.join(IMAGE_DIR, image_filename)
    image = Image.open(image_path)
    return image

# Streamlit Page
st.title("Image Feedback Data")

# Fetch feedback data from the SQLite database
data = fetch_feedback_data()

print(data)

if not data.empty:
    st.write(f"Found {len(data)} records with feedback.")

    # Create a new column to store the images
    data["Image"] = data["filename"].apply(lambda x: load_image(x))

    # Display the data in the table with images
    for index, row in data.iterrows():
        st.write(f"**Image ID**: {row['id']}")
        st.image(row["Image"], caption=f"Filename: {row['filename']}", use_column_width=True)
        st.write(f"**Classification**: {row['classification']}")
        feedback_text = "Correct" if row["feedback"] else "Wrong"
        st.write(f"**Feedback**: {feedback_text}")
        st.write("---")

else:
    st.write("No feedback data available.")
