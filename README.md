# us-commuters
For interactive demonstration visit
https://us-commuters.herokuapp.com/

Interactive visualisation of non-motorised commuter types in US cities.
Code outline:

Three Wikipedia pages are scraped and parsed.
- https://en.wikipedia.org/wiki/List_of_U.S._cities_with_most_bicycle_commuters
- https://en.wikipedia.org/wiki/List_of_U.S._cities_with_most_pedestrian_commuters
- https://en.wikipedia.org/wiki/List_of_U.S._cities_with_high_transit_ridership
- Libraries and tools: Beautifulsoup, Regular expressions, urllib, Streamlit

Data is cleaned and merged with geographical data provided by simplemaps.com.
- Geographical locations are required for visualisation
- missing data is filled, different naming conventions are corrected
- cleaned data is stored to improve speed in future use
- Libraries and tools: Pandas

Data is visualised in interactive choropleth map.
- Choropleth map of US is initialised with reference marker
- Scatter markers are added for commuter types given by user input
- Libraries and tools: Plotly

Data is visualised in stacked bar plot.
- appearance and annotations are customised
- Libraries and tools: Matplotlib

Data is shown in tabular form

Correlation of data is shown
- Libraries and tools: Seaborn

Interactive features are added with Streamlit

Code is deployed with Heroku