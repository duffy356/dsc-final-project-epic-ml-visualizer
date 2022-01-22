import numpy as np

class ChatTransformerUtil:

    def __init__(self):
        print("init ChatTransformerUtil")

    @staticmethod
    def create_resampled_messages_per_sec_df(df_session_chat_messages, sample_rate=1):
        mask = (df_session_chat_messages['chatbot'] == False) & (df_session_chat_messages['personal_msg'] == False) & (df_session_chat_messages['command'] == False)
        sample_rate = f"{sample_rate}S"

        print(df_session_chat_messages.index.min())
        messages_per_sec = df_session_chat_messages.loc[(mask)].resample(sample_rate).size()
        timecategories_df = df_session_chat_messages['timecategory'].loc[~df_session_chat_messages.index.duplicated(keep = 'first')]
        messages_per_sec = messages_per_sec.to_frame().join(timecategories_df)
        messages_per_sec.columns = ['count_messages', 'timecategory']
        messages_per_sec['timecategory'] = messages_per_sec['timecategory'].fillna(method="ffill")
        return messages_per_sec

    @staticmethod
    def get_timecategory_counts(chat_df):
        timecategory_counts = chat_df['timecategory'].value_counts()
        before_cnt = 0
        during_cnt = 0
        after_cnt = 0
        if 'BEFORE_MATCH' in timecategory_counts.index:
            before_cnt = timecategory_counts['BEFORE_MATCH']
        if 'DURING_MATCH' in timecategory_counts.index:
            during_cnt = timecategory_counts['DURING_MATCH']
        if 'AFTER_MATCH' in timecategory_counts.index:
            after_cnt = timecategory_counts['AFTER_MATCH']
        return before_cnt, during_cnt, after_cnt

    @staticmethod
    def nearest_idx(items, pivot):
        time_diff = np.abs(items - pivot)
        return time_diff.argmin(0)
