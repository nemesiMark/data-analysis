import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from functions import get_df_info, getCorrelatedFeature
import toml

# 0) Prima del clone andando in alto a DX sul progetto git, premo fork e la creo
#
# 1)  Come scaricare la cartella creata su GitHub
#           git clone https://github.com/nemesiMark/app.git

# 1-bis) se voglio sincronizzarmi premo su vscode e sotto trova, in IFTS23 premo i tre puntini e clicco "esegui pull"
#
# 2)  Come uplodare file su GitHub
#           git add .
#           git commit -m "nome modifica"
#           git push

# 3)  Come runnare su streamlit
#           steamlit run app0.py


def main():

    with open('.streamlit/config.toml', 'r') as f:
        config = toml.load(f)

    st.header("Data Transformation")
    #st.markdown("<h1 style='text-align: center; color: black;'>Data Transformation</h1>", unsafe_allow_html=True)
    # -----------------------------------------------------------------------------------------------------------
    uploaded_file = st.file_uploader("Choose your file XLSX:")

    if uploaded_file is not None:

        df = pd.DataFrame()

        if uploaded_file.name[-4:] != "xlsx":

            ##################################### TRANSFORMATION #####################################
            st.warning("XLSX file is required.")

        else:
            df = pd.read_excel(uploaded_file)

            numeric_cols = df.select_dtypes(
                include=['int', 'float']).columns.tolist()
            
            df1 = df.copy()
            df_standardized = df.copy()
            #df_standardized[numeric_cols] = StandardScaler(
            #).fit_transform(df[numeric_cols])

            ##################################### SHOW THE DATAFRAME #####################################
            st.header("Dataframe view -------------- {} x {}".format(df.shape[0], df.shape[1]))
            st.dataframe(df)
            #############################################################################################
            myPCA = 0

            choose = 0

            st.header("Operation Selector")
            choose = st.radio("", ["Info", "Describe", "Correlation",
                                "Box Plot", "Histogram", "PCA"], horizontal=True)
            

            if choose == "Info":

                get_df_info(df)

            if choose == "Describe":

                st.text("Information on dataframe:")
                st.dataframe(df.describe().T)

            

            if choose == "Correlation":

                if df[numeric_cols].isna().any().any():
                    st.warning("Nan values in numeric columns.")

                else:
                    # Riga per visualizzare la tabella numerica di correlazione
                    # st.dataframe(df.corr())
                    # se la figura dovesse risultare piccola posso aumentare la figsize=(20,10) espressa in pollici
                    corrmat = df[numeric_cols].corr()
                    
                    trashold = st.number_input("Select the value of the trashold", 0.0, 1.0, 0.9, format="%.2f")
                    col_selected = st.selectbox("Select column target", numeric_cols)
                    
                    corr_value = getCorrelatedFeature(corrmat[col_selected],trashold)
                    
                    df_rid = df[corr_value.index]
                    
                    if df_rid.empty:
                        st.warning("Reduce the trashold")
                        
                    else:
                        fig, ax = plt.subplots(figsize=(20, 10))
                        sns.heatmap(df_rid.corr(), annot=True, ax=ax)
                        ax.set_title("Heatmap of correlation")
                        st.pyplot(fig)
                        
                        # elimino la colonna selezionata
                        del df_rid[col_selected]
                        
                        text = "The correlation is between <span style='color:orange; font-weight:bold'>{}</span> and the list: <span style='color:orange; font-weight:bold'>{}</span>".format(col_selected, df_rid.columns.to_list())
                        st.markdown(text, unsafe_allow_html=True)


            if choose == "Box Plot":

                fig, ax = plt.subplots(figsize=(20, 10))
                df.boxplot(ax=ax)
                ax.set_title("Box Plot for outlyers")
                st.pyplot(fig)

            if choose == "Histogram":

                fig, ax = plt.subplots(figsize=(20, 10))
                df.hist(ax=ax)
                ax.set_title("Histogram")
                st.pyplot(fig)

            if choose == "PCA":

                if df[numeric_cols].isna().any().any():
                    st.warning("Nan values in numeric columns.")

                else:
                    cols_selected = st.multiselect("Select columns for PCA", options=numeric_cols, default=numeric_cols)

                    df_standardized[numeric_cols] = StandardScaler().fit_transform(df[numeric_cols])

                    myPCA = PCA().fit(df_standardized[cols_selected])
                    fig = plt.figure(figsize=(20, 10))
                    plt.plot(range(1, len(myPCA.explained_variance_ratio_)+1),
                            myPCA.explained_variance_ratio_, alpha=0.8, marker='*', label="Explained Variance")
                    y_label = plt.ylabel("Explained Variance")
                    x_label = plt.xlabel("Components")
                    plt.plot(range(1, len(myPCA.explained_variance_ratio_)+1), np.cumsum(
                        myPCA.explained_variance_ratio_), c='r', marker='.', label="Cumulative Explained Variance")
                    plt.legend()
                    plt.title('Percentage of variance explained by component')
                    st.pyplot(fig)

                    st.header("Dataframe Standardized: Mean=0 SD=1")
                    st.dataframe(df_standardized[cols_selected].describe().T)

                    num = st.slider(
                        'Percentage of precision:', 0, 100, 90)
                    total_explained_variance = myPCA.explained_variance_ratio_.cumsum()
                    n_over = len(
                        total_explained_variance[total_explained_variance >= num/100])
                    n_to_reach = total_explained_variance.shape[0] - n_over + 1
                    st.text(
                        f"To explain {num}% of variance with PCS, we need the first {n_to_reach} principal components")

                    fig, ax = plt.subplots(figsize=(20, 10))
                    sns.heatmap(myPCA.components_, cmap='seismic', xticklabels=list(df[cols_selected].columns),
                                vmin=-np.max(np.abs(myPCA.components_)), vmax=np.max(np.abs(myPCA.components_)),
                                annot=True, ax=ax)
                    ax.set_title("Weights that the PCA assigns to each component.")
                    st.pyplot(fig)
                    
            
            numerics_cols = df1.select_dtypes(include=['int','float']).columns
            string_cols = df1.select_dtypes(include=['object']).columns
            datetime_cols = df1.select_dtypes(include=['datetime']).columns
            #bool_cols = df1.select_dtypes(include=['bool']).columns


            st.sidebar.header("DATA CLEANING")

            numerics_cols_selected = st.sidebar.multiselect("INT64-FLOAT64 COLUMNS", numerics_cols)
            decimale = st.sidebar.number_input('Enter a NUMBER:', value=0.0, step=0.01)

            string_cols_selected = st.sidebar.multiselect("OBJECT COLUMNS", string_cols)
            stringa = st.sidebar.text_input('Enter a STRING:', value="---")

            datetime_cols_selected = st.sidebar.multiselect("DATETIME COLUMNS", datetime_cols)
            data = st.sidebar.text_input('Enter a DATE: gg/mm/aaaa', value="01/01/2000")

            click = st.sidebar.button("Process data cleaning")
            
            if click:

                df1[numerics_cols_selected] = df[numerics_cols_selected].fillna(decimale)

                df1[string_cols_selected] = df[string_cols_selected].fillna(stringa)

                df1[datetime_cols_selected] = df[datetime_cols_selected].fillna(data)


                st.header("AFTER CLEANING")
                st.dataframe(df1)
                
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df1.to_excel(writer, index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.save()
                    st.sidebar.header("FILE CLEANED AVAILABLE")
                    st.sidebar.download_button(
                        label="Download Excel Result",
                        data=buffer,
                        file_name= uploaded_file.name[:-5] + "_CLEANED" + ".xlsx",
                        mime="application/vnd.ms-excel")
                

if __name__ == "__main__":
    main()
