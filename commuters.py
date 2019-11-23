# _________________________
#
# ----- START

# Import libraries
import streamlit as st
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
#from IPython.display import HTML
#import matplotlib as mpl
import matplotlib.pyplot as plt
from plotly import graph_objs as go
import seaborn as sns

# Setup ssl
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def main():
    """Interactive EDA: Commuters in the US"""
    
    
    # _________________________
    #
    # ----- FUNCTIONS
    
    # LOAD DATA
#    @st.cache
    def load(url):
        html = urllib.request.urlopen(url, context=ctx).read()
        soup = BeautifulSoup(html, 'html.parser')
        return soup('body')[0]
    
    # PARSE HTML
    def parse(name, rawdata, br):
        
        # Create empty dataframes
        df = pd.DataFrame(columns=['city', 'state_name', name + ' percentage'])
        
        # Check if relevant lines contain line break
        if br:
            lines = re.findall(r"(?<=href).*?(?=<br\/>)", rawdata.decode())
        else:
            lines = re.findall(r"(?<=href).*?\%", rawdata.decode())
        
        # Find data in lines
        for line in lines:
            city = re.search(r"(?<=title=\").*?(?=(\,|\">))", line)
            state = re.search(r"(?<=, )(\.| |[a-zA-Z0-9])*?(?=</a>)", line)
            percentage = re.search(r"([0-9]|\.)*?(?=%)", line)
            
            # Add data to dataframe
            df = df.append({'city': city.group(0), 'state_name': state.group(0), name + ' percentage': float(percentage.group(0))}, ignore_index=True)
        return df

    # ADD TRACE TO CHOROPLETH MAP
    def choro_trace(percentage, legend_name, selected_color):
        fig.add_trace(go.Scattergeo(
            lon = commuters_df.loc[commuters_df[percentage] != 0]['lng'],
            lat = commuters_df.loc[commuters_df[percentage] != 0]['lat'],
            name = legend_name,
            text = commuters_df.loc[commuters_df[percentage] != 0]['city']+
                ': '+commuters_df.loc[commuters_df[percentage] != 0][percentage].astype(str) + '%',
            showlegend = True,
            marker = dict(
                size=commuters_df.loc[commuters_df[percentage] != 0][percentage]*2,
                color=colors[selected_color],
                line_width=0)
        ))


    # _________________________
    #
    # ----- LAYOUT
    
    colors = ['#70ABBA', '#B5DB95', '#FFD882', '#393E46']


    # _________________________
    #
    # ----- INTRODUCTION
    
    st.title("Non-Motorized Commuters in the US")
    
#    st.subheader("Use the following interactive visualizations to explore the non-motorized commuter culture in US cities.")
   
    st.markdown("To improve performance, all data is pre-loaded and formatted by default.")
    
    real_time_data = False
    if st.checkbox("Load data in real time", value=False, key=None):
        real_time_data = True

    st.markdown("Data Sources: Wikipedia, simplemaps.com") 

    st.subheader("Data Visualization")
    
    st.markdown("Use the following dropdown menu to display cities with high percentages of certain commuter types. \
                If nothing is selected, the total number of non-motorized commuters is displayed.")


    # _________________________
    #
    # ----- LOAD DATA
    
    if real_time_data:
        # Source: Wikipedia
        bicycle_url = ('https://en.wikipedia.org/wiki/List_of_U.S._cities_with_most_bicycle_commuters')
        pedestrian_url = ('https://en.wikipedia.org/wiki/List_of_U.S._cities_with_most_pedestrian_commuters')
        public_transit_url = ('https://en.wikipedia.org/wiki/List_of_U.S._cities_with_high_transit_ridership')
        
        # Load data from Wikipedia
        bicycles_raw = load(bicycle_url)
        pedestrians_raw = load(pedestrian_url)
        public_transit_raw = load(public_transit_url)
        
        # Load data from simpledata
#        us_data = pd.read_csv('../us-commuters-data/simplemaps_uscities_basicv1/uscities.csv')
        us_data = pd.read_csv('https://raw.githubusercontent.com/bauhofer/data/master/uscities.csv')
        
        #Load US universities and colleges data
        # Local
#        us_colleges = pd.read_csv('../us-commuters-data/us-colleges-and-universities.csv', sep=';')
        # Global
#        us_colleges = pd.read_csv('https://raw.githubusercontent.com/bauhofer/data/master/us-colleges-and-universities.csv', sep=';')
    
    
    # _________________________
    #
    # ----- DATA CLEANING
    
        # Parse data
        bicycles_df = parse('bicycle', bicycles_raw, br=True)
        pedestrians_df = parse('pedestrian', pedestrians_raw, br=True)
        public_transit_df = parse('public_transit', public_transit_raw, br=False)
    
        # Merge dataframes
        commuters_df = pd.merge(bicycles_df,pedestrians_df,how='outer',on='city').fillna(np.nan)
        commuters_df['state_name_x'] = commuters_df['state_name_x'].where(pd.notnull, commuters_df['state_name_y'])
        commuters_df = commuters_df.drop(['state_name_y'], axis=1).rename(columns = {"state_name_x": "state_name"})
        
        commuters_df = pd.merge(commuters_df,public_transit_df,how='outer',on='city').fillna(np.nan)
        commuters_df['state_name_x'] = commuters_df['state_name_x'].where(pd.notnull, commuters_df['state_name_y'])
        commuters_df = commuters_df.drop(['state_name_y'], axis=1).rename(columns = {"state_name_x": "state_name"})
    
        # Adjust city names to match format
        commuters_df.replace(to_replace='New York City', value='New York', inplace=True)
        commuters_df.replace(to_replace='D.C.', value='District of Columbia', inplace=True)
        commuters_df.replace(to_replace='Arlington County', value='Arlington', inplace=True)
        
        # Skip entry that is not in US Data
        commuters_df = commuters_df.drop(commuters_df[commuters_df['city']=='Edison'].index)
    
        # Merge data from Wikipedia with US Data
        commuters_df = pd.merge(commuters_df,us_data[['city','state_name','lat','lng','population','density']],how='left',on=['city','state_name']).fillna(0)
    
        commuters_df['total percentage'] = commuters_df['bicycle percentage'] + commuters_df['pedestrian percentage'] + commuters_df['public_transit percentage']
        commuters_df['bike and pedestrian percentage'] = commuters_df['bicycle percentage'] + commuters_df['pedestrian percentage']
    
    else:
        commuters_df = pd.read_csv('https://raw.githubusercontent.com/bauhofer/data/master/commuters_clean.csv', sep=';')
    
    # OPTIONAL: Save data to csv
#    commuters_df.to_csv(path_or_buf='../us-commuters-data/commuters_clean.csv', sep=';')
    

    # _________________________
    #
    # ----- CHOROPLETH MAP

    # Presentation
    options = st.multiselect('Commuters types:',('Bicyclists', 'Pedestrians', 'Public Transport'))
    
    # Figure
    fig = go.Figure(
            layout=dict(
                    geo_scope='usa',
                    geo_landcolor="lightgray"
                    )
            )
    
    # Reference marker
    fig.add_trace(go.Scattergeo(
        lon = [-85],
        lat = [51.2],
        name = 'reference marker',
        text = 'Reference marker: 5%',
        mode = 'markers+text',
        textposition = 'middle right',
        showlegend = False,
        marker = dict(
            size=10,
            color=colors[3],
            line_width=0)
    ))

    # Scatter Markers
    if 'Public Transport' in options:
        choro_trace(percentage='public_transit percentage',
                    legend_name='Public transportation commuters',
                    selected_color=0)
    if 'Pedestrians' in options:
        choro_trace(percentage='pedestrian percentage',
                    legend_name='Pedestrian commuters',
                    selected_color=1)
    if 'Bicyclists' in options:
        choro_trace(percentage='bicycle percentage',
                    legend_name='Bicycle commuters',
                    selected_color=2)
    if not options:
        choro_trace(percentage='total percentage',
                    legend_name='Total non-car commuters',
                    selected_color=3)
    
    # Layout
    fig.update_layout(
            margin=dict(l=0, r=0, t=25, b=40),
    )

    st.plotly_chart(fig, height=290)
    
    
    # _________________________
    #
    # ----- BAR PLOT

    # Presentation
    st.markdown("In the following bar plot, the cities are sorted with respect to the total number of non-car commuters.\
                Adjust the number of compared cities with the following field.")
    picks = st.number_input('Number of compared cities:',
                                            min_value=0, max_value=commuters_df.shape[0], value=15)

    # Sort data
    commuters_df = commuters_df.sort_values(by=['total percentage'], ascending=False)
    
    # Plot data
#    picks = 15
    pos = np.arange(picks)
    plt.figure(figsize=(12.4,7))
    bars1 = plt.bar(pos, commuters_df['public_transit percentage'][:picks], capsize=5, align='center'\
                   , color=colors[0], alpha=0.7, edgecolor='black', linewidth=0, label='public transit commuters')
    bars2 = plt.bar(pos, commuters_df['pedestrian percentage'][:picks], capsize=5, align='center'\
                   , bottom=list(commuters_df['public_transit percentage'][:picks])\
                   , color=colors[1], alpha=0.7, edgecolor='black', linewidth=0, label='pedestrian commuters')
    bars3 = plt.bar(pos, commuters_df['bicycle percentage'][:picks], capsize=5, align='center'\
                   , bottom=list(commuters_df['pedestrian percentage'][:picks] + commuters_df['public_transit percentage'][:picks])\
                   , color=colors[2], alpha=0.7, edgecolor='black', linewidth=0, label='bicycle commuters')
    
    # Remove frame, labels and ticks
    plt.tick_params(top=False, bottom=False, left=False, right=False, labelleft=False, labelbottom=True)
    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    
    # Label bars
    for b1, b2, b3 in zip(bars1, bars2, bars3):
        h1 = b1.get_height()
        h2 = b2.get_height()
        h3 = b3.get_height()
        if float(h1) > 0:
            plt.gca().text(b1.get_x() + b1.get_width()/2, h1 - 2.2\
                       , str(float(round(h1, 1))) + '%', ha='center', color=colors[3], fontsize=11)
        if float(h2) > 0:
            plt.gca().text(b1.get_x() + b1.get_width()/2, h1+h2 - 2.2\
                       , str(float(round(h2, 1))) + '%', ha='center', color=colors[3], fontsize=11)
        if float(h3) > 0:
            plt.gca().text(b3.get_x() + b3.get_width()/2, h1+h2+h3 - 2.2\
                       , str(float(round(h3, 1))) + '%', ha='center', color=colors[3], fontsize=11)
    
    # Include Title, ticks and legend
    plt.legend(fontsize=12)
    plt.xticks(pos, commuters_df['city'][:picks], rotation=45, ha='right', fontsize=12)
    plt.title('US cities with the highest total percentage of non-motorized commuters'\
              , fontsize=15, fontweight='bold')
    plt.tight_layout()
    
    st.pyplot()
    

    # _________________________
    #
    # ----- DATAFRAME

    if st.checkbox("Show data in tabular form", value=False, key=None):
        st.write(commuters_df.drop(columns=["Unnamed: 0","lat","lng","bike and pedestrian percentage"]).
                 rename(columns = {'city': 'City',
                                   'state_name': 'State',
                                   'bicycle percentage': 'Bicycles [%]',
                                   'pedestrian percentage': 'Pedestrians [%]',
                                   'public_transit percentage': 'Public Transport [%]',
                                   'population': 'Population',
                                   'density': 'Density',
                                   'total percentage': 'Total [%]'}).sort_values(by=['Total [%]'], ascending=False).reset_index(drop=True))
    
    
    # _________________________
    #
    # ----- CORRELATIONS
    
    st.subheader("Correlations")
    
    st.markdown("In order to find indicators for the presence of certain commuter types, \
                correlations between different factors are considered.")

    if st.checkbox("Show correlation of all factors", value=False, key=None):  
        plt.figure(figsize=(10,8), dpi= 80)
        sns.pairplot(commuters_df[['pedestrian percentage', 'bicycle percentage', 
                                   'public_transit percentage', 'density', 
                                   'population']], kind="scatter", 
                plot_kws=dict(s=80, edgecolor="black", linewidth=1))
        st.pyplot()

    st.markdown("From the given factors, only the population density gives a slight indication for the percentage of people commuting via public transport.")
    
#    # Plot
    sns.set(style="white", font_scale=1.2)
    plt.figure(figsize=(10,8), dpi= 80)
    ax = sns.lmplot(x="density", y="public_transit percentage",
               data=commuters_df.loc[commuters_df['public_transit percentage'] != 0],
               height=7, aspect=1.6, robust=True, palette='tab10',
               scatter_kws=dict(s=60, linewidths=.7, edgecolors='black'))
    ax.set(xlabel="Density [People per km^2]", ylabel="Public Transport [%]")
    st.pyplot()
    
    
    # _________________________
    #
    # ----- FEATURE ENGINEERING
    # ----- IN PROGRESS !!!
    
    # Find indicators
    # Local
#    us_colleges = pd.read_csv('../us-commuters-data/us-colleges-and-universities.csv', sep=';')
    # Global
#    us_colleges = pd.read_csv('https://raw.githubusercontent.com/bauhofer/data/master/us-colleges-and-universities.csv', sep=';')

#    st.write(us_colleges)
    # Number of colleges in cities
    # Number of students and lecturers in cities
    
    
if __name__ == '__main__':
    main()