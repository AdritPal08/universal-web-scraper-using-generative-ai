import streamlit as st
from streamlit_tags import st_tags_sidebar
from streamlit_lottie import st_lottie
import pandas as pd
import json
import io
from datetime import datetime
from scraper import fetch_html_selenium, save_raw_data, format_data, save_formatted_data, calculate_price,html_to_markdown_with_readability, create_dynamic_listing_model,create_listings_container_model

from assets import PRICING


# Initialize Streamlit app
st.set_page_config(page_title="Smart Web Scraper", page_icon="🦑", layout="centered", initial_sidebar_state = "auto")
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
st.header(":red[Smart] :green[Web Scraper] 🦑",divider= 'rainbow')
st.write("~ Effortless Data Extraction, Powered by : Generative AI")

# Sidebar components
st.sidebar.title("Web Scraper Settings")
model_selection = st.sidebar.selectbox("Select Model", options=list(PRICING.keys()), index=0)
url_input = st.sidebar.text_input("Enter URL")


# Tags input specifically in the sidebar
tags = st.sidebar.empty()  # Create an empty placeholder in the sidebar
tags = st_tags_sidebar(
    label='Enter Fields to Extract:',
    text='Press enter to add a tag',
    value=[],  # Default values if any
    suggestions=[],  # You can still offer suggestions, or keep it empty for complete freedom
    maxtags=-1,  # Set to -1 for unlimited tags
    key='tags_input'
)

st.sidebar.divider()

# Process tags into a list
fields = tags

# Initialize variables to store token and cost information
input_tokens = output_tokens = total_cost = 0  # Default values

# Buttons to trigger scraping
# Define the scraping function
def perform_scrape():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw_html = fetch_html_selenium(url_input)
    markdown = html_to_markdown_with_readability(raw_html)
    save_raw_data(markdown, timestamp)
    DynamicListingModel = create_dynamic_listing_model(fields)
    DynamicListingsContainer = create_listings_container_model(DynamicListingModel)
    formatted_data, tokens_count = format_data(markdown, DynamicListingsContainer,DynamicListingModel,model_selection)
    input_tokens, output_tokens, total_cost = calculate_price(tokens_count, model=model_selection)
    df = save_formatted_data(formatted_data, timestamp)

    return df, formatted_data, markdown, input_tokens, output_tokens, total_cost, timestamp

# Handling button press for scraping
if 'perform_scrape' not in st.session_state:
    st.session_state['perform_scrape'] = False

if st.sidebar.button("Scrape"):
    with st.spinner('Please wait... Data is being scraped.'):
        
        st.session_state['results'] = perform_scrape()
        st.session_state['perform_scrape'] = True
else:
    st_lottie("https://lottie.host/2999ffaf-e333-4814-bbda-c0ff9bc950e4/1IbFxCQE8w.json")
    
if st.session_state.get('perform_scrape'):
    df, formatted_data, markdown, input_tokens, output_tokens, total_cost, timestamp = st.session_state['results']
    # Display the DataFrame and other data
    st.write("Scraped Data:", df)
    st.sidebar.markdown("## Token Usage")
    st.sidebar.markdown(f"**Input Tokens:** {input_tokens}")
    st.sidebar.markdown(f"**Output Tokens:** {output_tokens}")
    st.sidebar.markdown(f"**Total Cost:** :green-background[***${total_cost:.4f}***]")
    st.sidebar.divider()
    
    st.sidebar.markdown(
        """
        🚀 Created by : [**Adrit**](https://www.linkedin.com/in/adritpal/)
        """,
            unsafe_allow_html=True
        )
    
    # Create columns for download buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("Download JSON", data=json.dumps(formatted_data.dict() if hasattr(formatted_data, 'dict') else formatted_data, indent=4), file_name=f"{timestamp}_data.json")
    with col2:
        # Convert formatted data to a dictionary if it's not already (assuming it has a .dict() method)
        if isinstance(formatted_data, str):
            # Parse the JSON string into a dictionary
            data_dict = json.loads(formatted_data)
        else:
            data_dict = formatted_data.dict() if hasattr(formatted_data, 'dict') else formatted_data

        
        # Access the data under the dynamic key
        first_key = next(iter(data_dict))  # Safely get the first key
        main_data = data_dict[first_key]   # Access data using this key

        # Create DataFrame from the data
        df = pd.DataFrame(main_data)

        # data_dict=json.dumps(formatted_data.dict(), indent=4)
        # st.download_button("Download CSV", data=df.to_csv(index=False), file_name=f"{timestamp}_data.csv")
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        # st.download_button("Download Excel", data=df.to_excel(index=False), file_name=f"{timestamp}_data.xlsx")
        st.download_button(
    label="Download Excel",
    data=buffer.getvalue(),
    file_name=f"{timestamp}_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
    with col3:
        st.download_button("Download Markdown", data=markdown, file_name=f"{timestamp}_data.md")
else:
    with st.sidebar:
        st_lottie("https://lottie.host/7322a23c-d92e-4467-a97c-5c79051cf448/J3Ryv8x755.json",height=200, width=200)

# Ensure that these UI components are persistent and don't rely on re-running the scrape function
if 'results' in st.session_state:
    df, formatted_data, markdown, input_tokens, output_tokens, total_cost, timestamp = st.session_state['results']
        