from typing import Optional

import streamlit as st

import pandas as pd
import numpy as np

import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

from ml.LanguageDetector import LanguageDetector
from service.ChatTransformerUtil import ChatTransformerUtil
from service.DataService import DataService
from service.MakeNice4UIMapper import MakeNice4UIMapper
from service.TimelineTransformerUtil import TimelineTransformerUtil


class DashboardMatch:
    # data
    streamer_matches: pd.DataFrame
    match_timeline_dict: dict
    match_summary_array: []
    match_summoner_dict: dict
    match_timeline_df: pd.DataFrame
    events_by_team: pd.DataFrame
    chat_of_match: pd.DataFrame
    messages_per_sec_df: pd.DataFrame
    timeline_summoner_filtered: pd.DataFrame

    # selections (from selectboxes)
    selected_streamer: str

    selected_match_id: str
    selected_match_event_type: Optional[str]

    selected_summoner_of_match: str
    selected_summoner_event_types: [str]

    def __init__(self, data_service: DataService, language_detector: LanguageDetector):
        self.data_service: DataService = data_service
        self.language_detector: LanguageDetector = language_detector
        self.timeline_converter_service: TimelineTransformerUtil = TimelineTransformerUtil()
        self.chat_transformer_util: ChatTransformerUtil = ChatTransformerUtil()
        self.make_nice_util: MakeNice4UIMapper = MakeNice4UIMapper()

    def refresh(self):
        st.header("Match Dashboard")
        st.subheader("LoL Match and Twitch Chat Data")

        st.markdown("""
              League of Legends is one of the most popular video games. It's genre is Mulitplayer Online Battle Arena. Two teams fight each other for the win of a match.   
              Some streamers play League of Legends and stream it on Twitch TV. Users watch them and can write messages in a chat.   
              This Dashboard allows us to **view various** matches and the **corresponding chat** data **at once**.
            """)

        self.draw_streamer_area()

        self.draw_match_event_area()

        self.draw_summoner_event_area()

        # read chat
        self.chat_of_match = self.data_service.get_chat_of_match_df(self.selected_streamer, self.selected_match_id)
        if len(self.chat_of_match) > 0:
            self.draw_chat_histogram_and_chat()
        else:
            st.markdown("""
                **No chat was collected for the selected match** 
            """)

    def draw_streamer_area(self):
        st.markdown("""
            #### Select a streamer
            Some streamers made their hobby to their job and they spend a lot of time by sharing their playing experience
            with viewers of streaming platforms.  
            This section shows how many matches the selected streamer played per day and how many matches the streamer played on average per weekday.
        """)

        all_streamers = self.data_service.get_available_streamers()
        self.selected_streamer = st.selectbox(label="Select a Streamer", options=all_streamers)

        self.streamer_matches = self.data_service.get_df_match_history_of_streamer(self.selected_streamer)
        st.caption(f"Found {len(self.streamer_matches)} Matches. This app does not contain the whole dataset!")

        # left graph
        day_range = pd.date_range(self.streamer_matches['start_date'].dt.date.min(), self.streamer_matches['start_date'].dt.date.max())

        matches_per_day = self.streamer_matches['start_date'] \
            .dt.floor('d') \
            .value_counts()

        matches_per_day.index = pd.DatetimeIndex(matches_per_day.index)
        matches_per_day = matches_per_day.reindex(day_range, fill_value=0)
        matches_per_day = matches_per_day.reset_index()
        matches_per_day.rename(columns={"index": "date", "start_date": "count"}, inplace=True)

        fig_per_day = px.bar(matches_per_day, x="date", y='count',
                             title=f'Total matches per day of streamer {self.selected_streamer}',
                             labels={"date": "Date", "count": "Total matches"})

        # right graph
        matches_by_weekday = matches_per_day.groupby(matches_per_day[matches_per_day['count'] > 0]['date'].dt.day_name()) \
            .mean() \
            .rename_axis('dayname') \
            .reset_index()

        fig_by_weekday = px.histogram(matches_by_weekday, x="dayname", y='count', title=f'Average matches by weekday of streamer {self.selected_streamer}',
                                      labels= {"dayname": "", "count": "games per weekday"},
                                      category_orders={
                               "dayname": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                           })

        mean_matches = matches_by_weekday['count'].mean()
        fig_by_weekday.add_shape(type="line", line_color="blue", line_width=3, opacity=1, line_dash="dot",
                      x0=0, x1=1, y0=mean_matches, xref="paper", y1=mean_matches, yref="y")

        # make 2 columns
        col1, col2 = st.columns(2)
        col2.plotly_chart(fig_by_weekday)
        col1.plotly_chart(fig_per_day)

    def draw_match_event_area(self):
        st.markdown("""
              #### Choose a match
              
              To find details of a specific match, the first step is to choose a match that was streamed by the selected streamer!
            """)

        l_selectbox, r_selectbox = st.columns(2)

        # match selectbox
        selected_match = l_selectbox.selectbox(label="Select a Match", options=self.streamer_matches['matchSelectbox'])
        self.selected_match_id = selected_match[selected_match.index('|') + 2 : selected_match.index(' (')]
        self.match_summary_array = self.data_service.get_match_summary_array(self.selected_streamer, self.selected_match_id)

        # load data for event and further
        self.match_timeline_dict = self.data_service.get_match_timeline_dict(self.selected_streamer, self.selected_match_id)
        self.match_summoner_dict = self.timeline_converter_service.create_match_summoner_dict(self.match_timeline_dict, self.match_summary_array)
        self.match_timeline_df = self.timeline_converter_service.create_match_timeline_df(self.match_timeline_dict, self.match_summary_array)

        # event type selectbox
        match_event_types_upper = self.timeline_converter_service.get_event_types_of_timeline(self.match_timeline_df)
        nice_match_event_types = self.make_nice_util.events_to_nice(match_event_types_upper)
        nice_match_evt_type = r_selectbox.selectbox(label="Select an In-Game Event-Type", options=nice_match_event_types)
        self.selected_match_event_type = self.make_nice_util.nice_to_event(nice_match_evt_type)

        st.markdown("""
            :bulb: You can choose an In-Game Event-Type.  
            The following graphs will show the occurences of that specific event accross the summoners of both teams.  
            The winning team is displayed in greens and the loosing team is colored in red. If you choose the In-Game Event-Type all, then all different Events will be aggregated.
        """)

        self.events_by_team = self.timeline_converter_service.get_events_by_player_desc_df(self.match_timeline_df, self.match_summary_array, self.selected_match_event_type)

        # plot event type per team member
        if self.selected_match_event_type is None:
            title_label = "Total occurences of ALL In-Game-Events by summoner"
            count_label = "ALL In-Game-Events"
        else:
            title_label = f"Total occurences of In-Game-Event '{self.make_nice_util.format_event(self.selected_match_event_type)}' by summoner"
            count_label = f"occurences of '{self.make_nice_util.format_event(self.selected_match_event_type)}'"

        fig_barplot = px.bar(self.events_by_team, x="count", y='event_summoner', color="win",
                             title=title_label,
                             labels={"event_summoner": "Summoner", "count": count_label, "win": "Match won?"},
                             category_orders={
                                 "win": [True, False]
                             },
                             color_discrete_map={ # replaces default color mapping by value
                                 True: "#3CBC8D", False: "#E9422E"
                             },)

        # plot event by team
        pie_df = self.events_by_team.groupby(['win']).sum('count').reset_index()
        fig_pie = px.pie(pie_df, names='win', values='count', color="win",
                         title="relative by team",
                         color_discrete_map={ # replaces default color mapping by value
                             True: "#3CBC8D", False: "#E9422E"
                         })

        left_match_fig, right_match_fig = st.columns([2, 1])
        left_match_fig.plotly_chart(fig_barplot)
        right_match_fig.plotly_chart(fig_pie)

    def draw_summoner_event_area(self):
        st.markdown("""
              #### Choose a summoner
              
              A character played by a real person somewhere around the world is called summoner within the League of Legends universe.  
              In the next sections we will would like to show specific events of the selected summoner!
            """)

        l_selectbox, r_selectbox = st.columns(2)

        # summoner selectbox
        match_summoners = self.data_service.get_df_summoners_of_streamer(self.selected_streamer)
        nice_summoners = []
        default_idx = 0
        for i, summoner in enumerate([match['summonerName'] for match in self.match_summary_array]):
            if len(match_summoners[match_summoners['summoner_name'] == summoner]) > 0:
                nice_summoners.append(f"{summoner} ({self.selected_streamer})")
                default_idx = i
            else:
                nice_summoners.append(summoner)
        selected_summoner_raw = l_selectbox.selectbox(label="Select a Summoner", options=nice_summoners, index=default_idx)
        if ' (' in selected_summoner_raw:
            self.selected_summoner_of_match = selected_summoner_raw[:selected_summoner_raw.index(' (')]
        else:
            self.selected_summoner_of_match = selected_summoner_raw


        # event type selectbox
        summoner_event_types_upper = self.timeline_converter_service.get_event_types_of_timeline_for_summoner(self.match_timeline_df, self.selected_summoner_of_match)
        nice_summoner_event_types = self.make_nice_util.events_to_nice(summoner_event_types_upper)
        default_summoner_events = [evt for evt in nice_summoner_event_types if 'Kill' in evt and not 'Ward' in evt]
        nice_summoner_evt_type_lst = r_selectbox.multiselect(label="Select an In-Game Event-Type",
                                                             options=nice_summoner_event_types,
                                                             default=default_summoner_events)
        self.selected_summoner_event_types = []
        for selected_type in nice_summoner_evt_type_lst:
            nice = self.make_nice_util.nice_to_event(selected_type)
            self.selected_summoner_event_types.append(nice)

        # draw summoner metrics
        summoner_summary_dict = [summ_summ for summ_summ in self.match_summary_array if summ_summ['summonerName'] == self.selected_summoner_of_match][0]
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Team Position", summoner_summary_dict['teamPosition'].title())
        m2.metric("Champion", summoner_summary_dict['championName'])
        m3.metric("Level", summoner_summary_dict['champLevel'])
        m4.metric("Deaths", summoner_summary_dict['deaths'])
        m5.metric("Champion Kills", summoner_summary_dict['kills'])
        m6.metric("Minions Killed", summoner_summary_dict['totalMinionsKilled'])

        m7, m8, m9, m10, m11, m12 = st.columns(6)
        value, delta = self.make_nice_util.calc_metric_value_pct(summoner_summary_dict, self.match_summary_array, 'physicalDamageDealt')
        m7.metric("Physical Damage Dealt", value, delta)
        value, delta = self.make_nice_util.calc_metric_value_pct(summoner_summary_dict, self.match_summary_array, 'magicDamageDealt')
        m8.metric("Magic Damage Dealt", value, delta)
        value, delta = self.make_nice_util.calc_metric_value_pct(summoner_summary_dict, self.match_summary_array, 'physicalDamageDealtToChampions')
        m9.metric("Physical Damage Dealt Champions", value, delta)
        value, delta = self.make_nice_util.calc_metric_value_pct(summoner_summary_dict, self.match_summary_array, 'magicDamageDealtToChampions')
        m10.metric("Magic Damage Dealt To Champions", value, delta)
        value, delta = self.make_nice_util.calc_metric_value_pct(summoner_summary_dict, self.match_summary_array, 'physicalDamageTaken')
        m11.metric("Physical Damage Taken", value, delta)
        value, delta = self.make_nice_util.calc_metric_value_pct(summoner_summary_dict, self.match_summary_array, 'magicDamageTaken')
        m12.metric("Magic Damage Taken", value, delta)

        st.markdown("""
            The next section shows how the selected In-Game-Event-Type of the summoner relate to chat messages.  
            It takes some time - rendering is a uniquely matplotlib graph
        """)

    def draw_game_event_text_graph(self):
        # prepare active and passive summoner events
        active_summoner = self.match_timeline_df.loc[self.match_timeline_df['event_summoner'] == self.selected_summoner_of_match][['event_types', 'rounded']]
        passive_summoner = self.match_timeline_df.loc[self.match_timeline_df['event_opponents'] == self.selected_summoner_of_match][['rounded']]
        passive_summoner['event_types'] = self.match_timeline_df.loc[self.match_timeline_df['event_opponents'] == self.selected_summoner_of_match]['event_types'] + '_PASSIVE'

        timeline_summoner = active_summoner.append(passive_summoner)
        timeline_summoner.set_index('rounded', inplace=True)
        timeline_summoner = timeline_summoner.sort_values('rounded')

        # reindex to same size ! R E I N D E X!
        aligned_datetime_index = pd.date_range(timeline_summoner.index.min(), timeline_summoner.index.max(), freq='1S').round('S')
        self.messages_per_sec_df = self.messages_per_sec_df.reindex(index=aligned_datetime_index)
        self.messages_per_sec_df['count_messages'] = self.messages_per_sec_df['count_messages'].fillna(0)
        if len(self.selected_summoner_event_types) > 0:
            event_filter = timeline_summoner["event_types"].isin(self.selected_summoner_event_types)
            self.timeline_summoner_filtered = timeline_summoner[event_filter]
        else:
            self.timeline_summoner_filtered = timeline_summoner
        plot_title = f'In-Game-Events and Chat-Histogram per Second'

        f, ax = plt.subplots(2, 1, figsize = (20,7), gridspec_kw={'height_ratios': [5, 1]}, sharex=True)

        # events unique of event timeline
        events_unique = self.timeline_summoner_filtered['event_types'].unique()
        events_unique = np.sort(events_unique)[::-1] # reverse

        # plot chat histogram at bottom
        plotting_series = self.messages_per_sec_df['count_messages']
        before_cnt, during_cnt, after_cnt = self.chat_transformer_util.get_timecategory_counts(self.messages_per_sec_df)
        colors = np.repeat(['#0DA9FF', '#0000FF', '#0DA9FF'], [before_cnt, during_cnt, after_cnt])
        plotting_series.plot.bar(ax=ax[1], xticks=[], log=True, legend=False, **{'color':colors})

        # set X axis labels
        x_ticks = [self.messages_per_sec_df.index.get_loc(summoner_idx) for summoner_idx in self.timeline_summoner_filtered.index]
        x_tick_labels = [str(self.messages_per_sec_df.index[idx].time()) for idx in x_ticks]

        ax[1].set_xticks(x_ticks)
        ax[1].set_xticklabels(labels=x_tick_labels, rotation=90)

        # plot events at top
        num_events = len(events_unique)
        offsets = list(range(10, num_events * 10 + 1, 10))
        colors = sns.color_palette("bright", num_events).as_hex()
        positions = []
        for i, col in enumerate(events_unique):
            positions.append([self.messages_per_sec_df.index.get_loc(idx) for idx in self.timeline_summoner_filtered[self.timeline_summoner_filtered['event_types'] == col].index])

        ax[0].eventplot(positions, colors=colors, lineoffsets=offsets, linelengths=10)

        # set y labels of upper plot
        ax[0].set_yticks(offsets)
        nice_events_unique = self.make_nice_util.events_to_nice(events_unique)
        ax[0].set_yticklabels(labels=nice_events_unique)

        ax[0].set_facecolor((.95, .95, .95, 0.95))
        ax[1].set_facecolor((.95, .95, .95, 0.95))
        plt.subplots_adjust(wspace=0, hspace=0)

        ax[0].set_title(plot_title)

        st.pyplot(plt)

        before_cnt, during_cnt, after_cnt = self.chat_transformer_util.get_timecategory_counts(self.chat_of_match)
        st.caption(
            f"{len(self.chat_of_match)} Messages have been captured. {before_cnt} before, {during_cnt} during, {after_cnt} after the match")

    def draw_chat_histogram_and_chat(self):
        # filter and transform chat of that match
        self.messages_per_sec_df = self.chat_transformer_util.create_resampled_messages_per_sec_df(self.chat_of_match)
        self.draw_game_event_text_graph()

        st.markdown("""
            #### Filter Chat
            In this section we can take a detailled look at the chat around the In-Game-Events
        """)

        # Chat event type select box
        evt_df = self.timeline_summoner_filtered.copy()
        evt_df.sort_values('event_types', inplace=True)
        evt_df['evt_num'] = evt_df.groupby('event_types').cumcount() + 1
        evt_df['selectBox'] = evt_df['evt_num'].astype(str) + ' | ' + evt_df['event_types']

        # selectbox
        nice_selected_match_event = st.selectbox(label="Select an Event", options=evt_df['selectBox'])
        sel_evt_num = int(nice_selected_match_event[:nice_selected_match_event.index('|') - 1])
        self_evt_type = nice_selected_match_event[nice_selected_match_event.index('|') + 2:]
        selected_match_event = evt_df[(evt_df['evt_num'] == sel_evt_num) & (evt_df['event_types'] == self_evt_type)]

        # start end slider
        chat_range = pd.date_range(self.chat_of_match.index.min(), self.chat_of_match.index.max(), freq='1S').round('S')
        chat_start_idx = selected_match_event.index[0]
        chat_end_idx = chat_start_idx + pd.to_timedelta(15, unit='S')

        start_chat_selection, end_chat_selection = st.select_slider(
            'Select a time range for the selected chat',
            options=chat_range,
            value=(chat_start_idx, chat_end_idx),
            format_func=lambda x: x.strftime("%H:%M:%S"))
        st.write('You selected chat between', start_chat_selection, 'and', end_chat_selection)

        start_idx = self.chat_transformer_util.nearest_idx(self.chat_of_match.index, start_chat_selection)
        end_idx = self.chat_transformer_util.nearest_idx(self.chat_of_match.index, end_chat_selection)

        filtered_chat = self.chat_of_match[start_idx:end_idx]
        mask = (filtered_chat['chatbot'] == False) & (filtered_chat['personal_msg'] == False) & (filtered_chat['command'] == False)
        col1, col2 = st.columns([1, 2])
        col1.dataframe(data=filtered_chat[mask][['author_name', 'text']])

        with col2.container():
            import streamlit.components.v1 as components
            entered = st.text_input("enter an emote", value="")
            if len(entered) > 0:
                # embed streamlit docs in a streamlit app
                components.iframe(f"https://www.slanglang.net/emotes/{entered}/", height=600, scrolling=True)


