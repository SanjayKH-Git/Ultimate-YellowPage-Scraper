import json
import streamlit as st
from yp_scraper import yp_au_scrape, yp_us_scrape, yp_ca_scrape, yp_nz_scrape
import os
import sqlite3
import pandas as pd
import base64

if __name__ == "__main__":
    try:
        st.header("YP Tech7c Tool")

        st.write("Enter the Searching Data")

        # Country dropdown options
        countries = [
            "Australia ---> https://www.yellowpages.com.au",
            "USA ---> https://www.yellowpages.com",
            "Canada ---> https://www.yellowpages.ca",
            "New Zealand ---> https://yellow.co.nz",
        ]
        # st.write(os.getcwd())
        # Form inputs
        country = st.selectbox("Select Country", countries)
        name = st.text_input("Search Name")
        city = st.text_input("City")

        st.markdown(
            "<h3 style='text-align:center; color:blue;'>OR</h3>",
            unsafe_allow_html=True,
        )
        direct_url = st.text_input("Direct URL")

        # Submit button
        if st.button("Collect Data"):
            # Validation check
            if country and name and city or direct_url:
                if not direct_url:
                    st.write(f"Collecting Data for : {name}, {city}, {country}")

                if country.startswith("Australia"):
                    All_result_dict = yp_au_scrape(name, city, direct_url)
                elif country.startswith("USA"):
                    All_result_dict = yp_us_scrape(name, city, direct_url)
                elif country.startswith("Canada"):
                    All_result_dict = yp_ca_scrape(name, city, direct_url)
                elif country.startswith("New Zealand"):
                    All_result_dict = yp_nz_scrape(name, city, direct_url)

                result_df = pd.DataFrame(All_result_dict.values())
                json_format = json.dumps(All_result_dict)
                # print(All_result_dict)

                csv_col, json_col, sqlite_col = st.columns(3)

                csv_data = result_df.to_csv(index=False).encode("utf-8")

                csv_base64 = base64.b64encode(csv_data).decode("utf-8")
                csv_button_html = f"""
                    <button style="background-color: #7b38d8; border: none; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 4px;">
                        <a href="data:file/csv;base64,{csv_base64}" download="CSV_output.csv" style="color: #37ff00; text-decoration: none; font-weight: bold">Download CSV</a>
                    </button>
                """
                csv_col.markdown(csv_button_html, unsafe_allow_html=True)

                json_format_bytes = json_format.encode("utf-8")
                json_base64 = base64.b64encode(json_format_bytes).decode("utf-8")
                json_button_html = f"""
                    <button style="background-color: #0881c2; border: none; color: white; padding: 10px 20px; text-align: center; cursor: pointer; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 4px;">
                        <a href="data:file/json;base64,{json_base64}" download="JSON_output.json" style="color: #e2ff05; text-decoration: none; font-weight: bold; ">Download JSON</a>
                    </button>
                """
                json_col.markdown(json_button_html, unsafe_allow_html=True)

                # Create a temporary file for SQLite database
                temp_file_name = "yp_sqlite_output.db"
                with sqlite3.connect(temp_file_name) as conn:
                    # Replace 'your_table_name' with the desired table name
                    result_df.to_sql("yp_table", conn, index=False, if_exists="replace")

                # Create download button for SQLite

                with open(temp_file_name, "rb") as db_file:
                    db_bytes = db_file.read()

                sqlite_base64 = base64.b64encode(db_bytes).decode("utf-8")
                sqlite_button_html = f"""
                    <button style="background-color: #ff08f7; border: none; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 4px;">
                        <a href="data:file/csv;base64,{sqlite_base64}" download={temp_file_name} style="color: #9fe1e3; text-decoration: none; font-weight: bold">Download SQLite</a>
                    </button>
                """
                sqlite_col.markdown(sqlite_button_html, unsafe_allow_html=True)

            else:
                st.warning("Please fill in all the inputs before collecting data.")

    except Exception as e:
        st.warning("Check Your Inputs or Refresh the Page !")
        print(e)
