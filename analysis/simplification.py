
from pandas import DataFrame, concat
from solves import StatisticCollection


def simplify(stats: StatisticCollection) -> StatisticCollection:
    data = stats.as_dataframe().dropna()

    daily = data.groupby(data['date'].dt.date)

    idxmin = daily['result'].idxmin()
    idxmax = daily['result'].idxmax()
    min_and_max  = concat([data.loc[idxmin], data.loc[idxmax]])

    data = concat([daily.first(), daily.last(), min_and_max])
    data.index.name = 'day'
    data = data.set_index('date').drop_duplicates().sort_values(by='date').reset_index()

    return StatisticCollection.from_dataframe(data)

