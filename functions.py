#################   MY LIBRARY  #######################

import io
import streamlit as st
import pandas as pd

# this function allow me to visualize df.info()
def get_df_info(df):

    buffer = io.StringIO()
    df.info(buf=buffer)
    lines = buffer.getvalue().split('\n')

    # st.dataframe(lines[0:3])
    # st.dataframe(lines)

    for x in lines:
        st.text(x)
        

def getCorrelatedFeature(corrdata, threshold):
    feature = []
    value = []
    
    for i,index in enumerate(corrdata.index):
        if abs(corrdata[index])> threshold:
            feature.append(index)
            value.append(corrdata[index])
            
    df = pd.DataFrame(data = value, index = feature, columns=['Corr Value'])
    return df