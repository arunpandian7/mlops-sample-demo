import streamlit as st
import requests
from PIL import Image
import io

# Backend API endpoints
CLASSIFY_URL = "http://127.0.0.1:8000/classify/"
FEEDBACK_URL = "http://127.0.0.1:8000/feedback/{image_id}"

# File uploader for image classification
st.title("Image Classifier with Feedback")
st.write("Upload an image to classify:")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # Send image to the classification API
    st.write("Classifying the image...")
    
    # Send image to FastAPI backend
    files = {"file": uploaded_file.getvalue()}
    response = requests.post(CLASSIFY_URL, files=files)
    
    if response.status_code == 200:
        result = response.json()
        st.write(f"**Classification Result**: {result['classification']}")
        image_id = result['id']
        
        # Feedback section
        st.write("Was this classification correct?")
        feedback = st.radio("Select feedback", ("Correct", "Wrong"))
        
        if st.button("Submit Feedback"):
            feedback_value = True if feedback == "Correct" else False
            feedback_response = requests.post(FEEDBACK_URL.format(image_id=image_id), params={"feedback": feedback_value})
            if feedback_response.status_code == 200:
                st.write("Feedback submitted successfully!")
            else:
                st.write("Failed to submit feedback.")
    else:
        st.write("Error in classification")
