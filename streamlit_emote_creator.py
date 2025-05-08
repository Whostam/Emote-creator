import os
import streamlit as st
import openai
from dotenv import load_dotenv
from openai.exceptions import InvalidRequestError

# Optionally load local environment variables from a .env file
load_dotenv()

# Retrieve the OpenAI API key from Streamlit secrets or environment variables
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# Page configuration
st.set_page_config(
    page_title="AI Emote Creator",
    layout="centered",
)

st.title("🖼️ AI Emote Creator with Sora-enabled API")

# File uploader for original emotes
uploaded_files = st.file_uploader(
    "Upload your original emotes (PNG or JPG)",
    type=["png", "jpg"],
    accept_multiple_files=True
)

# Controls: number of variations and output size
num_variations = st.slider(
    "Variations per emote", min_value=1, max_value=5, value=3
)
size = st.selectbox(
    "Output emote size", options=["256x256", "512x512", "1024x1024"]
)

# Function to generate style-preserving variations
def generate_variations(image_file, n, size):
    response = openai.images.create_variation(
        image=image_file,
        n=n,
        size=size
    )
    return [item.url for item in response.data]

# Generate button behavior
if st.button("Generate New Emotes"):
    if not uploaded_files:
        st.warning("Please upload at least one emote to get started.")
    else:
        results = {}
        with st.spinner("Creating emote variations..."):
            for file in uploaded_files:
                try:
                    urls = generate_variations(file, num_variations, size)
                    results[file.name] = urls
                except InvalidRequestError as e:
                    # Handle billing limit reached or other invalid requests
                    code = e.error.get('code') if hasattr(e, 'error') else None
                    if code == "billing_hard_limit_reached":
                        st.error(
                            "Your billing hard limit has been reached. "
                            "Please visit your OpenAI dashboard to increase your limit or add funds: "
                            "https://platform.openai.com/account/billing/limits"
                        )
                    else:
                        st.error(f"API request error for {file.name}: {e}")
                except Exception as e:
                    st.error(f"Unexpected error with {file.name}: {e}")

        # Display successful results
        for original, urls in results.items():
            st.subheader(f"From: {original}")
            cols = st.columns(len(urls))
            for col, img_url in zip(cols, urls):
                col.image(img_url, use_column_width=True)
