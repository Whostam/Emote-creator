# streamlit_emote_creator.py

import os
import streamlit as st
import openai

# Set your OpenAI API key as an environment variable:
#   export OPENAI_API_KEY="your_key_here"
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_variations(image_file, num_variations: int, size: str = "256x256"):
    """
    Create style-preserving variations of an uploaded image.
    Uses the DALL·E 2 variations endpoint under the hood.
    """
    response = openai.Image.create_variation(
        image=image_file,       # file-like (e.g. BytesIO from st.file_uploader)
        n=num_variations,       # how many new emotes per original
        size=size               # "256x256", "512x512", etc.
    )
    # API returns URLs by default; we can display those directly in Streamlit
    return [data["url"] for data in response["data"]]

# Streamlit UI
st.title("🖼️ AI Emote Creator with Sora-enabled API")

uploaded_files = st.file_uploader(
    "Upload your original emotes",
    type=["png", "jpg"],
    accept_multiple_files=True
)

num_variations = st.slider(
    "Variations per emote",
    min_value=1, max_value=5, value=3
)

size = st.selectbox(
    "Output emote size",
    options=["256x256", "512x512", "1024x1024"]
)

if st.button("Generate New Emotes"):
    if not uploaded_files:
        st.warning("Please upload at least one emote to get started.")
    else:
        all_urls = []
        with st.spinner("Creating emote variations..."):
            for file in uploaded_files:
                # Streamlit gives us an UploadedFile, which behaves like a file-like object
                urls = generate_variations(file, num_variations, size)
                all_urls.extend(urls)

        # Display results in a grid
        cols = st.columns(num_variations)
        idx = 0
        for i, orig in enumerate(uploaded_files):
            st.subheader(f"From: {orig.name}")
            row_urls = all_urls[idx : idx + num_variations]
            idx += num_variations
            for col, img_url in zip(cols, row_urls):
                col.image(img_url, use_column_width=True)
