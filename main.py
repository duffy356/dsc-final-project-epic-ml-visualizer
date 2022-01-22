import streamlit as st
import tokenizers

from DashboardLanguageClassifier import DashboardLanguageClassifier
from DashboardMatch import DashboardMatch
from ml.LanguageDetector import LanguageDetector
from service.DataService import DataService


@st.cache(suppress_st_warning=True,
          hash_funcs= {
              tokenizers.Tokenizer: lambda _: None,
              tokenizers.AddedToken: lambda _: None
          },
          allow_output_mutation=True)
def get_language_detector():
    return LanguageDetector()


def get_data_service():
    return DataService()


st.set_page_config("EPIC | dashboard", layout='wide')

mode = st.sidebar.selectbox(label="Mode", options=("Match Dashboard", "Language Classification"))

if mode == "Match Dashboard":
    dashboard = DashboardMatch(get_data_service(), get_language_detector())
    dashboard.refresh()
elif mode == "Language Classification":
    dashboard = DashboardLanguageClassifier(get_data_service(), get_language_detector())
    dashboard.refresh()
else:
    st.title("Invalid Dashboard Mode selected!")




