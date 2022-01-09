from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import TextClassificationPipeline
from iso639 import languages
import pandas as pd


class LanguageDetector:

    def __init__(self):
        print("init Language Detector")
        self.tokenizer = AutoTokenizer.from_pretrained("models/", local_files_only=True)
        self.model = AutoModelForSequenceClassification.from_pretrained("models/", local_files_only=True)
        self.pipeline = TextClassificationPipeline(
            model=self.model,
            tokenizer=self.tokenizer,
            return_all_scores=True
        )

    def evaluate_scores(self, text):
        scores = self.pipeline(text)
        print(f"evaluated '{text}'")

        df = pd.DataFrame(scores[0])
        df.sort_values(by='score', ascending=False, inplace=True)
        df = df.reset_index(drop=True)
        df['label'] = df['label'].apply(lambda x: languages.get(alpha2=x).name)
        df['score'] = df['score'] * 100
        for idx, row in df[0:5].iterrows():
            print(f"Pobability of {row['label']} is {round(row['score'], 2)} %")
        return df
