import os
import pickle
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

    def get_available_players(self):
        dsc_path = self.get_dsc_data_file_path()
        players = []
        for d in os.listdir(dsc_path):
            folder_path = dsc_path.joinpath(d)
            if os.path.isdir(folder_path):
                players.append(d)
        return players

    def get_df_match_history_of_player(self, player_name):
        match_summaries = self.read_prepared_file(player_name, "match_summaries")
        return pd.DataFrame(match_summaries)

    def get_df_summoners_of_player(self, player_name):
        summoner_mappings = self.read_prepared_df_file(player_name, "summoner_mapping")
        return pd.DataFrame(summoner_mappings)

    def get_match_summary_array(self, player_name, match_id):
        filename = f"match_participant_summaries_{match_id}"
        return self.read_prepared_file(player_name, filename)

    def get_chat_of_match(self, player_name, match_id):
        chat_df = self.read_prepared_df_file(player_name, 'chat_df', 'datetime')
        return chat_df[chat_df['matchId'] == match_id]
