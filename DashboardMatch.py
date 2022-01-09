import streamlit as st

from ml.LanguageDetector import LanguageDetector
from service.DataService import DataService


class DashboardMatch:

    def __init__(self, data_service: DataService, language_detector: LanguageDetector):
        self.data_service: DataService = data_service
        self.language_detector: LanguageDetector = language_detector

    def refresh(self):
        st.header("Match Dashboard")
        st.subheader("LoL Match and Twitch Chat Data")

        st.markdown("""
              League of Legends is one of the most popular video games. It's genre is Mulitplayer Online Battle Arena. Two teams fight each other for the win of a match.   
              Some players play League of Legends and stream it on Twitch TV. Users watch them and can write messages in a chat.   
              This Dashboard allows us to **view various** matches and the **corresponding chat** data **at once**.
            """)

        selected_player = st.selectbox(label="Select a Player", options=self.data_service.get_available_players())

        player_matches = self.data_service.get_df_match_history_of_player(selected_player)
        player_summoners = self.data_service.get_df_summoners_of_player(selected_player)

        selected_match_id = st.selectbox(label="Select a Match", options=player_matches['matchId'])

        match_summary_array = self.data_service.get_match_summary_array(selected_player, selected_match_id)

        players = []
        for player in [match['summonerName'] for match in match_summary_array]:
            if len(player_summoners[player_summoners['summoner_name'] == player]) > 0:
                players.append(f"{player} ({selected_player})")
            else:
                players.append(player)
        selected_player_of_match = st.selectbox(label="Select a Player", options=players)

        chat_of_match = self.data_service.get_chat_of_match(selected_player, selected_match_id)
        if len(chat_of_match) > 0:
            st.dataframe(data=chat_of_match)

            timecategory_counts = chat_of_match['timecategory'].value_counts()
            before_cnt = timecategory_counts['BEFORE_MATCH']
            during_cnt = timecategory_counts['DURING_MATCH']
            after_cnt = timecategory_counts['AFTER_MATCH']
            st.caption(f"{len(chat_of_match)} Messages have been capture. {before_cnt} before, {during_cnt} during, {after_cnt} after the match")
        else:
            st.markdown("""
                **No chat was collected for the selected match** 
            """)


