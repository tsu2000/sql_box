import streamlit as st
import pandas as pd

import io
import requests
import json

from PIL import Image
from streamlit_extras.badges import badge

def main():

    col1, col2, col3 = st.columns([0.03, 0.265, 0.035])
    
    with col1:
        url = 'https://github.com/tsu2000/sql_box/raw/main/sql.png'
        response = requests.get(url)
        img = Image.open(io.BytesIO(response.content))
        st.image(img, output_format = 'png')

    with col2:
        st.title('&nbsp; SQL Sandbox Playground')

    with col3:
        badge(type = 'github', name = 'tsu2000/sql_box', url = 'https://github.com/tsu2000/sql_box')

    st.markdown('A simple web app for learning the basics of SQL using a sample database and schemas from a MySQL server. Only one SQL query can be executed at the time. To execute a SQL query, type your query into the text area and click `Execute` to see the results. There are currently **2** questions available to practice basic SQL queries. **Note:** Do not use the `USE` keyword when referring to different schemas. Instead, select tables using the `schema + table` notation. (i.e. `sql_store.customers`)')

    # Connect to MySQL Database
    conn = st.experimental_connection('mydb', type = 'sql')
    
    opt = st.selectbox('Select a feature:', ['All MySQL Query Practice Questions', 'About Database'])

    st.write(conn)

    st.write('---')
    
    if opt == 'All MySQL Query Practice Questions':
        questions(engine = conn)
    elif opt == 'About Database':
        about(engine = conn)


def questions(engine):

    col_a, col_b = st.columns(2)

    # Read in .json question bank
    question_bank = pd.read_json('question_bank.json')
    question_df = pd.DataFrame(question_bank)
    question_df.set_index('id', inplace = True)
    
    with col_a:
        st.markdown("#### Questions:")

        # Get attributes for current question
        q_index = st.selectbox('Select a question:', question_df.index)
        current_q = question_df.loc[q_index]

        st.markdown('**Description:**')
        st.write(current_q['question_description'])

        colx, coly = st.columns(2)

        with colx:
            st.markdown('**Table Details:**')
            st.dataframe(current_q['table_details'], use_container_width = True)

        with coly:
            st.markdown('**Column Data Types:**')
            for i, j in zip(current_q['all_tables'], current_q['column_types']):
                dtdf = pd.DataFrame(index = j.keys(), data = j.values()).rename(columns = {0: "Type"})
                dtdf.index.name = i
                st.dataframe(dtdf, use_container_width = True)

        st.write('---')

        st.markdown('**Correct Answer:**')
        try:
            cor_ans = engine.query(current_q['correct_answer'])
            st.dataframe(cor_ans, use_container_width = True, hide_index = True)

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.stop()

    with col_b:
        st.markdown("#### Query Answer:")
        sql_query = st.text_area("Enter your SQL query (single query allowed only):", "SELECT * \nFROM sql_store.customers", height = 250)
        if st.button("Execute"):
            try:
                result = engine.query(sql_query)
                st.dataframe(result, use_container_width = True, hide_index = True)

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.stop()


def about(engine):
    st.markdown('The sample MySQL Database consists of 4 different schemas simulating company data: `sql_hr`, `sql_inventory`, `sql_invoicing`, and `sql_store`. Each of these schemas has a different number of tables in them. Make your choice in the selectbox to view the full structure and contents of each schema.')
    
    schema_opt = st.selectbox('Select a schema:', ['sql_hr', 'sql_inventory', 'sql_invoicing', 'sql_store'])

    if schema_opt == 'sql_hr':
        table_names = ['employees', 'offices']

    elif schema_opt == 'sql_inventory':
        table_names = ['products']
        
    elif schema_opt == 'sql_invoicing':
        table_names = ['clients', 'invoices', 'payment_methods', 'payments']
           
    elif schema_opt == 'sql_store':
        table_names = ['customers', 'order_item_notes', 'order_items', 'orders', 'order_statuses', 'products', 'shippers']
        
    for name in table_names:
        try:
            st.markdown(f"### {schema_opt}.{name}")
            full_table = engine.query(f"SELECT * FROM {schema_opt}.{name}")
            st.dataframe(full_table, use_container_width = True, hide_index = True)

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.stop()

if __name__ == "__main__":
    st.set_page_config(page_title = 'SQL Playground', page_icon = '🛝', layout = 'wide')
    main()
