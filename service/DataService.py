import os
import pickle
from datetime import timedelta
from pathlib import Path
import dotenv
import pandas as pd
import pyAesCrypt


class DataService:

    def __init__(self):
        print("init dataService")

    def get_password(self):
        env_pw = os.environ.get('PICKLE_PW')
        if env_pw is not None:
            return env_pw

        dotenv.load_dotenv(os.path.join(Path(os.getcwd()), '.env'))
        return os.environ.get('PICKLE_PW')

    def get_dsc_data_file_path(self):
        src_path = Path(os.getcwd())
        return src_path.joinpath('dsc_data')

    def get_player_file_path(self, player_name):
        dsc_data = self.get_dsc_data_file_path()
        return dsc_data.joinpath(player_name)

    def get_file_path(self, player_name, file):
        player_path = self.get_player_file_path(player_name)
        filename = f'{file}.pkl'
        aes_filename = f'{filename}.aes'
        return player_path.joinpath(filename), player_path.joinpath(aes_filename)

    def read_prepared_file(self, player_name, file):
        destination_file, aes_file = self.get_file_path(player_name, file)

        if not os.path.exists(destination_file):
            pyAesCrypt.decryptFile(aes_file, destination_file, self.get_password())

        with open(destination_file, "rb") as src:
            obj = pickle.load(src)
            print(f'read {destination_file}')

        os.remove(destination_file)

        return obj

    def read_prepared_df_file(self, player_name, df_file, index_col=None):
        destination_file, aes_file = self.get_file_path(player_name, df_file)

        if not os.path.exists(destination_file):
            pyAesCrypt.decryptFile(aes_file, destination_file, self.get_password())

        df = pd.read_csv(destination_file, index_col=index_col)
        print(f'read {destination_file}')

        os.remove(destination_file)

        return df

    def get_available_streamers(self):
        dsc_path = self.get_dsc_data_file_path()
        players = []
        for d in os.listdir(dsc_path):
            folder_path = dsc_path.joinpath(d)
            if os.path.isdir(folder_path):
                players.append(d)
        return players

    def add_duration(self, item):
        start = item['start_date']
        duration = item['gameDuration_ms']
        if duration < 10000:
            return start + timedelta(seconds=duration)
        else:
            return start + timedelta(milliseconds=duration)

    def get_df_match_history_of_streamer(self, player_name):
        match_summaries = self.read_prepared_file(player_name, "match_summaries")
        df = pd.DataFrame(match_summaries)
        df.rename(columns={"gameStartTimestamp_date": "start_date"}, inplace=True)
        df['end_date'] = df[['start_date', 'gameDuration_ms']].apply(self.add_duration, axis=1)
        df['matchSelectbox'] = (df.index + 1).astype(str) + " | " + df['matchId'] + " (" + df['start_date'].dt.round('1s').astype(str) + " to " + df['end_date'].dt.round('1s').dt.time.astype(str) +")"
        return df

    def get_df_summoners_of_streamer(self, player_name):
        summoner_mappings = self.read_prepared_df_file(player_name, "summoner_mapping")
        return pd.DataFrame(summoner_mappings)

    def get_match_summary_array(self, player_name, match_id):
        filename = f"match_participant_summaries_{match_id}"
        return self.read_prepared_file(player_name, filename)

    def get_match_timeline_dict(self, player_name, match_id):
        filename = f"match_timeline_{match_id}"
        return self.read_prepared_file(player_name, filename)

    def get_chat_of_match_df(self, player_name, match_id):
        chat_df = self.read_prepared_df_file(player_name, 'chat_df', None)
        datetime_index = pd.DatetimeIndex(chat_df['datetime'])
        chat_df.set_index(datetime_index, inplace=True)
        return chat_df[chat_df['matchId'] == match_id]
