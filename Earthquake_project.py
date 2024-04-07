import warnings 
warnings.filterwarnings('ignore')

import pandas as pd
from termcolor import colored
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
df = pd.read_csv(r'c:\Users\Home\Downloads\earthquake_1995-2023.csv')
data = df.copy()
_ = data.columns[data.isna().any()]
print(colored(f'\nThere are {len(_)} columns with missing values:', color='red', attrs=['bold', 'blink']))
print('{}\n'.format(_.values))

_, ax = plt.subplots(figsize=(24, 5))
sns.barplot(data=data.isna(), ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha='center')
ax.axhline(0.25, ls='--', c='r')
ax.axhline(0.1, ls='--', c='k')
_ = None
def make_world_fig(data, lat, lon, hover_name, size, cl_disc_seq, zoom, height):
    fig = px.scatter_mapbox(data, lat=lat, lon=lon, 
        hover_name=hover_name,
        size=size,
        color_discrete_sequence=cl_disc_seq,
        zoom=zoom, height=height
    )

    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox_style="white-bg",
        mapbox_layers=[{
            "below": 'traces',
            "sourcetype": "raster",
            "sourceattribution": "United States Geological Survey",
            "source": [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
        ]}]
    )

    return fig
# Creating visually differentiable values      v Diminishing the difference, to avoid vanishing points in map
data['power'] = pow(10, data['magnitude']) / pow(3, data['magnitude'])
data['power'] = data['power'].round(0)

fig = make_world_fig(data, 'latitude', 'longitude', 'magnitude', 'power', ["red"], 1.5, 500)
fig.show()
data['sig'] = data['sig'] ** 2 / 10_000 # Creating visually differentiable values for sig
data['sig'] = data['sig'].round(0)

fig = make_world_fig(data, 'latitude', 'longitude', 'magnitude', 'sig', ["red"], 1.5, 500)
fig.show()
tsun = data[data['tsunami'] == 1]

fig = make_world_fig(tsun, 'latitude', 'longitude', 'magnitude', 'sig', ["orange"], 1.5, 500)
fig.show()
fig = px.scatter(df.assign(tsunami=df["tsunami"].astype(str)),
                 x='magnitude', 
                 y='sig', 
                 color='tsunami',
                 color_discrete_sequence=['#F0F600', '#D81159'],
                 trendline='ols', 
                 trendline_scope="trace")

fig.update_layout(
    title='Magnitude and Impact Correlation',
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='white'),
    xaxis_showgrid=False, 
    yaxis_showgrid=False,
)

fig.show()
# Preparing data
data['location'] = data['location'].str.split(', ').str[-1]
s = data['location'].value_counts().sort_values(ascending=False).reset_index()
top_15 = s.iloc[:15, 0].to_list()
s['location'] = s['location'].apply(lambda x: 'Other' if x not in top_15 else x)
s = s.groupby('location').agg('sum').reset_index().sort_values(by='count', ascending=False)

# Exploding indexes
pull = [0] * len(s)
for i in range(4):
    pull[i] = 0.14

# Color Gradient
gradient = ['#D81159', '#EA320D', '#D70F0F', '#EE5622', 
            '#F18805', '#F0A202', '#F0F600', '#ECA72C',
            '#C37D92', '#8F3985', '#8F2D56', '#D88C9A',
            '#FF729F', '#A4036F', '#A675A1', '#8A1C7C']

# Plotting
fig3 = px.pie(s, names='location', values='count', title='Tremor occurrences by country | region', color_discrete_sequence=gradient)
fig3.update_traces(hole=0.3, pull=pull)
fig3.update_layout(
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='white')
)
fig3.show()
# Adding year column and creating Other location ('minor activity countries')
data['year'] = pd.to_datetime(data['date_time']).dt.year
data['location'] = data['location'].apply(lambda x: 'Other' if x not in top_15 else x)

# Creating Dataframe for fig
time = data.groupby(['location', 'year']).agg('count').reset_index()[['location', 'year', 'title']]
to_print = ['World', 'Indonesia', 'Minor Activity Countries', 'Japan', 'Papua New Guinea'] # columns to be printed

# Contains all years from 1995 - 2023
all_years = [x for x in range(1995, 2024)]

# Creating Indonesia and Other columns
indonesia = time[time['location'] == 'Indonesia'].set_index('year')
other = time[time['location'] == 'Other'].set_index('year')
japan = time[time['location'] == 'Japan'].set_index('year').reindex(all_years, fill_value=0)
papua = time[time['location'] == 'Papua New Guinea'].set_index('year').reindex(all_years, fill_value=0)
# Adding the two columns above into world
world = data.groupby('year').agg('count')[['title']]
world['idn'] = indonesia['title']
world['oth'] = other['title']
world['jpn'] = japan['title']
world['png'] = papua['title']

world.columns = to_print
world = world.reset_index()

# Plotting...
fig1 = px.line(world, x='year', y=to_print,
               title='Number of tremors by year (World, Indonesia, Japan, Papue New Guinea, and Minor Activity Countries)')

# Adjusting details
fig1.update_layout(
    plot_bgcolor='black',
    paper_bgcolor='black',
    font=dict(color='white'),
    xaxis=dict(showgrid=False, title='Year'),
    yaxis=dict(showgrid=False, title='Number of Tremors')
)

# Line colors
line_colors = ['#5F0F40', '#9A031E', '#FB8B24', '#E2CFEA', '#0F4C5C']
for i, color in enumerate(line_colors):
    fig1.update_traces(selector=dict(name=to_print[i]), line=dict(color=color))

fig1.show()