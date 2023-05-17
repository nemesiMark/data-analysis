#################   MY LIBRARY  #######################

import io
import streamlit as st

# this function allow me to visualize df.info()
def get_df_info(df):

    buffer = io.StringIO()
    df.info(buf=buffer)
    lines = buffer.getvalue().split('\n')

    # st.dataframe(lines[0:3])
    # st.dataframe(lines)

    for x in lines:
        st.text(x)