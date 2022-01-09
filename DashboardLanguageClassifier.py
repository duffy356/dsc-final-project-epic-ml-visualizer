import streamlit as st

from ml.LanguageDetector import LanguageDetector
from service.DataService import DataService


class DashboardLanguageClassifier:

    def __init__(self, data_service: DataService, language_detector: LanguageDetector):
        self.data_service: DataService = data_service
        self.language_detector: LanguageDetector = language_detector

    def refresh(self):
        st.title("Language Classification Dashboard")

        user_input = st.text_area("Enter a text that should be checked", "This is an example text.")

        if user_input:
            df = self.language_detector.evaluate_scores(user_input)
            st.dataframe(data=df)
