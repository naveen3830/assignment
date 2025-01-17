import streamlit as st
import requests

FASTAPI_BASE_URL = "http://127.0.0.1:8000"

st.title("Google Sheets Analysis")
st.header("Analyze Google Sheet")

sheet_id = st.text_input("Enter Google Sheet ID")

if st.button("Analyze Sheet"):
    if sheet_id:
        try:
            response = requests.post(
                f"{FASTAPI_BASE_URL}/analyze_sheet/",
                json={"sheet_id": sheet_id},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                st.success("Analysis complete. Results updated in Google Sheet and CSV.")
            else:
                st.error(f"Error: {response.json()['detail']}")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a valid Google Sheet ID.")

st.header("Download Analyzed CSV")
if st.button("Download CSV"):
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/download-csv/")
        if response.status_code == 200:
            with open("analyzed_sheet.csv", "wb") as f:
                f.write(response.content)
            st.download_button(
                label="Download Analyzed CSV",
                data=response.content,
                file_name="analyzed_sheet.csv",
                mime="text/csv",
            )
        else:
            st.error("File not found. Perform analysis first.")
    except Exception as e:
        st.error(f"Error: {e}")