class MakeNice4UIMapper:

    @staticmethod
    def format_event(evt):
        tmp = evt.title()
        return tmp.replace('_', '-')

    @staticmethod
    def events_to_nice(event_types_upper):
        nice_event_types = []
        for evt in event_types_upper:
            tmp = MakeNice4UIMapper.format_event(evt)
            nice_event_types.append(tmp)
        return nice_event_types

    @staticmethod
    def nice_to_event(nice_type):
        nice_type = nice_type.replace('-', '_')
        event = nice_type.upper()
        if event == 'ALL':
            return None
        else:
            return event

    @staticmethod
    def calc_metric_value_pct(summoner_dict, summoners_list, property):
        value = summoner_dict[property]
        value_total = sum([summ[property] for summ in summoners_list])
        delta = round((value/value_total) * 100)
        return value, f"{delta} %"
