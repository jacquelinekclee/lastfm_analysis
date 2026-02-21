import plotly.graph_objects as go
import pandas as pd

def create_scrobbles_heatmap(processed_scrobbles, year = 2025, quarter = 0):
    """
    generate heatmap of daily streaming data for given year 
    Args:
        processed_scrobbles (pd.DataFrame): dataframe of processed scrobbles data 
        year (int): year to generate heatmap for (default, 2025)
        quarter (int): quarter of the year 
    Returns:
        plotly.graph_objects.Figure: heatmap of daily streaming data 
    """
    color_schemes = {
        0:'purpor',
        1:'purp',
        2:'sunsetdark',
        3:'orrd',
        4:'blues'
    }
    processed_scrobbles_filt, heatmap_data, hover_data, month_starts = prepare_heatmap_data(processed_scrobbles, year, quarter)
    if quarter == 0:
        title = f"{year} Listening Activity"
    else:
        title = f"Q{quarter} {year} Listening Activity"
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values, # streams 
        x=heatmap_data.columns.values, # week number 
        y=[0, 1, 2, 3, 4, 5, 6], # days of week  
        text=hover_data.values, 
        hovertemplate='%{text}<extra></extra>',
        colorscale=color_schemes[quarter],
        showscale=True,
        colorbar=dict(title="Streams"),
        zmin=0
    ))
    fig.update_xaxes(
        tickmode='array',
        tickvals=month_starts['week_start'].tolist(),
        ticktext=month_starts['month'].tolist(),
        side='top'
    )
    fig.update_yaxes(
        tickmode='array',
        tickvals=[0, 1, 2, 3, 4, 5, 6],
        ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        autorange = 'reversed'
    )
    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title="",
        height=400,
        xaxis=dict(side='top')
    )
    return processed_scrobbles_filt, fig 

def prepare_heatmap_data(processed_scrobbles, year, quarter):
    """
    extract listening sessions from the scrobbles, where a listening session
    is any consecutive streaming where a break is only 10 minutes or less.
    this threshold tries to accommodate longer song lengths. 
    Args:
        processed_scrobbles (pd.DataFrame): dataframe of sorted, processed scrobbles 
        year (int): year to generate heatmap for (default, 2025)
        quarter (int): quarter of the year 
    Returns:
        tuple (processed_scrobbles, pd.DataFrame, pd.DataFrame, pd.DataFrame):
            the original df of processed scrobbles, the data for the heatmap,
            the text for the visualization, and data for the week number that starts each month
    """
    if quarter == 1:
        min_month = 1
        max_month = 3
        max_days = 31
    elif quarter == 2:
        min_month = 4
        max_month = 6
        max_days = 30
    elif quarter == 3:
        min_month = 7
        max_month = 9
        max_days = 30
    elif quarter == 4:
        min_month = 10
        max_month = 12
        max_days = 31
    else:
        min_month = 1
        max_month = 12
        max_days = 31
    if quarter == 0:
        processed_scrobbles = processed_scrobbles.loc[
            (processed_scrobbles.year == year)
        ].copy()
    else:
        processed_scrobbles = processed_scrobbles.loc[
            (processed_scrobbles.year == year) & 
            (processed_scrobbles.datetime.dt.quarter == quarter)
        ].copy()
    daily_data = processed_scrobbles.groupby('date').agg(
        streams=('song_title', 'count'),
        artists=('primary_artist', 'nunique'),
        weekday = ('weekday', 'first'),
        month = ('month', 'first'),
        top_artist=('primary_artist', 
                    lambda artists: artists.value_counts().index[0] if len(artists) > 0 else 'None')
    ).reset_index()

    daily_data['date'] = pd.to_datetime(daily_data['date'])
    date_range = pd.date_range(
        start=f'{year}-{str(min_month).zfill(2)}-01',
        end=f'{year}-{str(max_month).zfill(2)}-{max_days}', 
        freq='D'
    )
    full_season = pd.DataFrame({'date': date_range.date})
    full_season['date'] = pd.to_datetime(full_season['date'])
    calendar_data = full_season.merge(daily_data, on='date', how='left')
    calendar_data.fillna(0, inplace=True)
    calendar_data['date'] = pd.to_datetime(calendar_data['date'])
    calendar_data['month'] = calendar_data['date'].dt.month_name()
    calendar_data['week'] = calendar_data['date'].dt.isocalendar().week
    calendar_data['day_of_week'] = calendar_data['date'].dt.dayofweek
    
    if quarter == 0 or quarter == 4:
        calendar_data.loc[(calendar_data['month'] == 'December') & (calendar_data['week'] == 1), 'week'] = 53

    calendar_data['hover_text'] = calendar_data.apply(
        lambda row: f"<b>{row['date'].strftime('%B %d, %Y')}</b><br>" +
                    f"Streams: {int(row['streams'])}<br>" +
                    f"Unique Artists: {int(row['artists'])}<br>" +
                    f"Top Artist: {row['top_artist']}" if row['streams'] > 0 
                    else f"<b>{row['date'].strftime('%B %d, %Y')}</b><br>No streams",
        axis=1
    )
    heatmap_data = calendar_data.pivot_table(
        index='day_of_week', 
        columns='week', 
        values='streams',
        aggfunc='sum' 
    ).fillna(0)
    hover_data = calendar_data.pivot_table(
        index='day_of_week', 
        columns='week', 
        values='hover_text',
        aggfunc='first' 
    )
    # get first week number for each month 
    month_starts = calendar_data.groupby('month').agg(
        week_start=('week', 'min'),
    ).reset_index().sort_values('week_start')
    return processed_scrobbles, heatmap_data, hover_data, month_starts
