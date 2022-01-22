import pandas as pd

from datetime import timedelta, datetime


class TimelineTransformerUtil:

    def __init__(self):
        print("init TimelineTransformerUtil")

    @staticmethod
    def create_match_summoner_dict(timeline_dict, match_summary_array):
        participant_map = {'0': {'puuid': '-', 'name': 'Minions'}}
        for p in timeline_dict['info']['participants']:

            participant_map[str(p['participantId'])] = {
                'puuid': p['puuid'],
                'name': [summ['summonerName'] for summ in match_summary_array if summ['puuid'] == p['puuid']][0]
            }
        return participant_map

    @staticmethod
    def calc_datetime(start_dt, delta_event):
        return start_dt + timedelta(milliseconds = delta_event)

    @staticmethod
    def get_key_event_player(event_type):
        if event_type in ["ITEM_PURCHASED", "ITEM_DESTROYED", "ITEM_UNDO", "ITEM_SOLD", "SKILL_LEVEL_UP", "LEVEL_UP", "CHAMPION_TRANSFORM"]:
            return "participantId"
        elif event_type in ["CHAMPION_KILL", "CHAMPION_SPECIAL_KILL", "WARD_KILL", "ELITE_MONSTER_KILL", "BUILDING_KILL", "TURRET_PLATE_DESTROYED"]:
            return "killerId"
        elif event_type in ["WARD_PLACED"]:
            return "creatorId"
        elif event_type in ["PAUSE_END", "GAME_END"]:
            return None
        else:
            print(f"could not find player key for event: {event_type}")
            return None

    @staticmethod
    def get_key_event_opponent(event_type):
        if event_type in ["CHAMPION_KILL"]:
            return "victimId"
        elif event_type in ["WARD_PLACED", "BUILDING_KILL", "CHAMPION_SPECIAL_KILL", "CHAMPION_TRANSFORM", "TURRET_PLATE_DESTROYED", "ELITE_MONSTER_KILL", "WARD_KILL", "ITEM_DESTROYED", "ITEM_UNDO",  "ITEM_PURCHASED", "ITEM_SOLD", "GAME_END", "PAUSE_END", "SKILL_LEVEL_UP", "LEVEL_UP"]:
            return None
        else:
            print(f"could not find opponent key for event: {event_type}")
            return None

    @staticmethod
    def is_event_for_every_player(event_type):
        return event_type in ["PAUSE_END", "GAME_END"]

    @staticmethod
    def get_player_name(participant_map, player_num):
        return participant_map[str(player_num)]['name']

    @staticmethod
    def utc_datetime_from_ts_millis(ts) -> datetime:
        return datetime.utcfromtimestamp(ts / 1000)

    @staticmethod
    def create_match_timeline_df(timeline_dict, match_summary_array):
        datetimes = []
        event_types = []
        event_players = []
        event_opponents = []
        event_assistings = []

        participant_summary = TimelineTransformerUtil.create_match_summoner_dict(timeline_dict, match_summary_array)

        match_timeline_start = None
        match_timeline_end = None
        for frame in timeline_dict['info']['frames']:
            for event in frame['events']:
                dt = None
                event_delta = event['timestamp']
                event_type = event['type']
                event_assisting = None
                event_player = None
                player_key = TimelineTransformerUtil.get_key_event_player(event_type)
                if player_key is not None:
                    event_player = TimelineTransformerUtil.get_player_name(participant_summary, event[player_key])

                event_opponent=None
                opponent_key = TimelineTransformerUtil.get_key_event_opponent(event_type)
                if opponent_key is not None:
                    event_opponent = TimelineTransformerUtil.get_player_name(participant_summary, event[opponent_key])

                if 'realTimestamp' in event:
                    if match_timeline_start is None:
                        match_timeline_start = TimelineTransformerUtil.utc_datetime_from_ts_millis(event['realTimestamp'])
                        dt = match_timeline_start
                    else:
                        match_timeline_end = TimelineTransformerUtil.utc_datetime_from_ts_millis(event['realTimestamp'])
                        dt = match_timeline_end
                else:
                    dt = TimelineTransformerUtil.calc_datetime(match_timeline_start, event_delta)

                if 'assistingParticipantIds' in event:
                    event_assisting = []
                    for id in event['assistingParticipantIds']:
                        ass = TimelineTransformerUtil.get_player_name(participant_summary, id)
                        event_assisting.append(ass)

                if TimelineTransformerUtil.is_event_for_every_player(event_type):
                    for i in range(1, 11):
                        datetimes.append(dt)
                        event_types.append(event_type)
                        event_players.append(TimelineTransformerUtil.get_player_name(participant_summary, i))
                        event_opponents.append(event_opponent)
                        event_assistings.append(event_assisting)
                else:
                    datetimes.append(dt)
                    event_types.append(event_type)
                    event_players.append(event_player)
                    event_opponents.append(event_opponent)
                    event_assistings.append(event_assisting)

        match_timeline_df = pd.DataFrame({
            'datetime': datetimes,
            'event_types': event_types,
            'event_summoner': event_players,
            'event_opponents': event_opponents,
            'event_assistings': event_assistings
        })
        match_timeline_df = match_timeline_df.set_index('datetime')
        match_timeline_df['rounded'] = match_timeline_df.index.ceil('S')
        match_timeline_df.sort_index(inplace=True)
        return match_timeline_df

    @staticmethod
    def get_event_types_of_timeline(timeline_df, add_whitelist=True):
        blacklisted_types = ['PAUSE_END', 'GAME_END']
        event_types = [type for type in timeline_df['event_types'].unique() if type not in blacklisted_types]

        if add_whitelist:
            whitelisted_types = ['ALL']
            for evt in whitelisted_types:
                event_types.insert(0, evt)
        return event_types

    @staticmethod
    def get_event_types_of_timeline_for_summoner(df_timeline, summoner_name):
        filtered_df = df_timeline[df_timeline['event_summoner'] == summoner_name]
        return TimelineTransformerUtil.get_event_types_of_timeline(filtered_df, False)

    @staticmethod
    def get_events_by_player_desc_df(df_timeline, summary_array, event_type=None):
        filtered_df = df_timeline
        if event_type is not None:
            filtered_df = df_timeline[df_timeline['event_types'] == event_type]
        events_by_player_desc = filtered_df.groupby(['event_summoner']) \
            .size() \
            .reset_index(name='count') \
            .sort_values('count', ascending=True)

        summary_df = pd.DataFrame(summary_array)
        events_by_player_desc = events_by_player_desc.merge(summary_df[['summonerName', 'win']], how='inner', left_on = 'event_summoner', right_on = 'summonerName')
        events_by_player_desc.drop(columns=['summonerName'], inplace=True)
        events_by_player_desc.sort_values(['win', 'count'], inplace=True, ascending=[True, False])
        return events_by_player_desc


