import streamlit as st
from PIL import Image

# Page Configurations
st.set_page_config(
    page_title="Upload das Medições"
)

# Sidebar with logo and introduction
image = Image.open('logo.png')
st.sidebar.image(image, width=120)
st.sidebar.markdown("# Indian Delivery Food Company")
st.sidebar.markdown("### Your Partner in Fast Delivery")
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Powered by Francisco Pena 🤓')

# Main Header
st.write("# Growth Dashboard")
st.markdown("""---""")

# Main Content with Subheaders
st.markdown("""
    Growth Dashboard was built to track the growth metrics for the Indian delivery food restaurant
    
    ### How to use this Growth Dashboard?
    - **Company View:**
        - **Management View:** General behavior metrics.
        - **Tactical View:** Weekly growth indicators.
        - **Geographic View:** Geolocation insights.
    - **Deliver Drivers View:**
        - Tracking of weekly growth indicators.
    - **Restaurant View:**
        - Weekly growth indicators for restaurants.
""")

# Contact Information
st.markdown("""
    ### Contact
    - For any doubt or suggestions 
        - [@franciscobpena](https://franciscobpena.github.io/porfolio_projetos/)
""")

# Footer
st.markdown("""
    <hr style="margin-top: 3rem;">
    <div style="text-align: center; color: #7F8C8D;">
        <p>&copy; 2024 Indian Delivery Food Company. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)
