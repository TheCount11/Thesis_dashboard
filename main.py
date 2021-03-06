# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 14:50:35 2021

@author: sagnik_mukherjee
"""

import numpy as np
import pandas as pd
import pydeck as pdk
import altair as alt
import seaborn as sns
import streamlit as st
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

file_main = Path(__file__).parents[0]/ 'data/german2.csv'
df = pd.read_csv(file_main)

def clean_emoji(x):
    if x == '{}':
       return ''
    else:
        return x[1:-1]

def generate_wordcloud(time,userdf):

    newlist =userdf['hashtags'].loc[time]
    foo = []
    for item in newlist:
        foo.append(item.lower().split(','))

    flat_list = [item for sublist in foo for item in sublist]
    text = " ".join(word for word in flat_list)
    stopwords = set(STOPWORDS)

    wordcloud =WordCloud(stopwords=stopwords,
               background_color="gray",
               width=1600,
               height=800,
               contour_width=1,
               contour_color='black',
               collocations = False).generate(text)

    return wordcloud

def typicality(tag, results_subset):

    results_total = Counter()
    df['hashtags'].str.lower().str.split(',').apply(results_total.update)

    freq_total = (results_total[f'{tag}']/sum(results_total.values()))*100
    freq_subset = (results_subset[f'{tag}']/sum(results_subset.values()))*100
    typ =  (freq_subset-freq_total)/freq_total

    return typ




df['hashtags'] = df['hashtags'].apply(lambda x: x[1:-1])
df['emoji'] = df['emoji'].str.lower().apply(lambda x : clean_emoji(x))


st.set_page_config(layout="wide") 

st.title("The EU Migration Crisis on Twitter")
file_ap = Path(__file__).parents[0]/ 'data' / '54875226_403.jpg'
st.image(str(file_ap))
st.markdown("*Refugees fleeing as Moria burns in September, 2020. Photo credits to Associated Press Photos/Petros Giannakouris*")
"""On 2nd Septermber, 2015 the body of a three-year-old Syrian boy washed up near Bodrum, Turkey. This incident is largely held to be the beginning of the Migration Crisis in EU. Recently, Angela Merkel considered this crisis to be one of the most difficult for her to deal with during her 16 year tenure. 

This crisis has put some of the best and worst attributes of human society at the forefront. Not only, do we see this on newspapers and televisions, but now more so on Twitter. Ever since the Arab Spring movement, Twitter has been the social network for socio-political issues to be expressed. Official announcement from heads of states and CEO's are covered on Twitter which are in turn covered by journalists and newspapers. However, also ordinary people increasingly take to Twitter to express their opinions. This is why, tweets have been chosen to get a feel for the public perception during the EU Migration Crisis.  
"""  
with st.beta_expander('Note'):
    st.write("The spatial facet involves using latitude, longitude data to make visualizations. Hence, it might seem strange to users to see the 'select a language' selection within the spatial facet. This has been done because of two reasons. The first reason involves the image below")
    file_path = Path(__file__).parents[0]/ 'data' / 'lang-loc-uk.jpeg'
    st.image(str(file_path))
    st.write("""The image shows the number of tweets throught the 5 years of the datset when they are filtered based on language (post_language) and country (post_location) for English and the UK. 41% of all tweets is in English. Clearly, there is very little difference between using language or country to filter the data. In other words, people tweeting in Italian are confined (largely) to Italy. 

The second reason for using languages is due to the fact that there would be more tweets in absolute number if the data is filtered with languages instead of countries. This is because of erroneous longitude and latitude coordinates, which sometimes does not fall within the border of any country but are otherwise fine for the purpose of data analysis. Hence, to keep tweets (around 16,000) of them, the Spatial facet uses languages and not countries for filtering and analysing the data. 
   """)


with st.beta_expander('Explore the Facets'):

        with st.beta_container(): 
           
           st.write("""Twitter data is incredibly multi-faceted. This means that the raw data comes with many kinds of information and to make sense of them, we have to look at the various facets both singularly and simultaneously. So let's begin by looking at some of the facets signularly.""") 
           st.subheader("Spatial")	
           st.write("""The spatial distribution of the tweets can be visualized on a map to see where the tweets come from.""")
           st.write("Hover over the points for more information")       
           options = np.insert(df['post_language'].unique(),0,'all')
           lang = st.selectbox('select a language', options, key = "lang")
           if lang == 'all':
           	data = df
           else:
             data = df[df['post_language'] == lang]	
           st.write("""The language codes used are the [ISO 639-1 alpha codes] (https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)""")  
           st.pydeck_chart(pdk.Deck(
                         tooltip = {"text": "Hashtags used : {hashtags}\n Year posted : {years}"},
                         width = "100%",
                         initial_view_state=pdk.ViewState(
                             latitude=49.5200,
                             longitude=15.4050,
                             zoom=3,
                             pitch=50,
                             ),
                         layers=[
                             pdk.Layer(
                             'ScatterplotLayer',
                             data=data,
                             opacity =0.3,
                             get_position='[lon, lat]',
                             radius_scale=6,
                             get_fill_color=[255, 140, 0, 100],
                             get_radius=600,
                             pickable = True,
                             extruded = True,
                         ),

                     ],


                 ),use_container_width = True)

        with st.beta_container():
            st.subheader("Temporal")      
            st.write("""As the name suggests, the temporal facet is about using the timestamps associated with tweets and exploring their patterns. Here the distribution of tweets over the years and also the sub-distribution within each year is shown with the bar charts. 
            
Hover the mouse pointer over the charts for exact counts""")
            col3, col4 = st.beta_columns(2)
            

            with col3:
                    
                    st.write("Total yearly distribution of tweets")
                    plot_years = df.years.value_counts().rename_axis('years').reset_index(name='tweet_count')
                    plot_years['years'] = plot_years.astype({'years': 'str'})
                    c1 = alt.Chart(plot_years).mark_bar().encode(
                                              x= alt.X('years:O', axis=alt.Axis(labelAngle =0)),
                                              y='tweet_count',
                                              tooltip = ['tweet_count']
                                              ).properties(width =500)
                    st.altair_chart(c1)

            with col4:
                    
                    st.markdown("Take a look at the tweet distribution of each year in further detail")
                    sel = st.selectbox("Select the year", sorted(list(df.years.unique())), key='time')
                    plot_years2 = df['year-month'][df['years']== sel].value_counts().rename_axis('months').reset_index(name='tweet_count')
                    plot_years2.sort_values(by=['months'],inplace =True)
                    plot_years2['months'] = plot_years2['months'].apply(lambda x: pd.to_datetime(x).strftime('%b'))
                    c2 = alt.Chart(plot_years2).mark_bar().encode(
                                              x= alt.X('months:N', axis=alt.Axis(labelAngle =0), sort =None),
                                              y='tweet_count',
                                              tooltip = ['tweet_count']
                                              ).properties(width =500)
                    st.altair_chart(c2)
                   
            st.subheader("Topical") 
            st.write("")
            st.write("This facet deals with the 'what' of the tweets. For our dataset, the broader topic would be the migration crisis. But even there, one can find distinct topics being raised on Twitter. Hashtags are a great indicator of topics, and here we are using hashtags with a novel metric : typicality.")
            
            st.write("""Typicality indicates how typical the measured attribute is with respect to a subset derived from the entire dataset.
                                 Here the subset is time (Years). And the measured attribute is hashtag(s).""")
            st.write ("""Positive typicality indicates that the hashtag was popular during the year displayed on the x axis.
                          Negative typicality indicates the opposite""")
            st.write("The chart is a stacked bar chart. You can hover over the columns for exact values for each hashtag.")              
            file_typ = Path(__file__).parents[0]/ 'data/typicality-30.csv'
            typ_df = pd.read_csv(file_typ)


            columns = st.multiselect('Select Hashtags (You can select more than one)', list(typ_df.columns)[:-1])
            columns.append("Years")

            plot = typ_df[columns]
            plot.set_index("Years", inplace = True)
            p = plot.melt(ignore_index = False).reset_index()

            c = alt.Chart(p).mark_bar().encode(

            x= alt.X('Years:O', axis=alt.Axis(labelAngle =0)),
                            y=alt.Y('value:Q'),
                            color=alt.Color('variable:N'),
                            tooltip=['variable', 'value', 'Years'])

            st.altair_chart(c, use_container_width=True)

with st.beta_expander('Explore Events with the Facets'):
            with st.beta_container():
             st.subheader("Using the facets for event detection") 
             st.write("""Tweets are not made in vacuum. They are quite related to things happening around us. The facets independently can only give us a part of the full picture. When facets are combined, by selecting specific timeframes, locations and topics : events are brought in focus. Events on twitter give us a link and allow us to explore the differences and similarities between society and social media. For example, the default event (the one shown before you choose anything) being shown is the Muslim Ban brought into force by Donald Trump. Note how all the facets explored individually are combined for event detection. """)
             
             lang_choice = {'English' : 'en',
                           'Spanish' : 'es',
                           'Italian' : 'it',
                           'German' : 'de',
                           'French' : 'fr',
                           'Dutch' : 'nl'}

            lan = st.selectbox('select a language', list(lang_choice.keys()), key = "lan")
            peak = st.selectbox('select a peak number between 1 (most number of tweets) and 6 (lesser number of tweets than 1, but not the least number of tweets)', [1,2,3,4,5,6], key = "peak")

            col5, col6 = st.beta_columns(2)
            col7, col8 = st.beta_columns(2)

            def dashboard(lan,peak):

             df["year-month"] = pd.to_datetime(df["year-month"]).dt.to_period('M')
             df.set_index('year-month',inplace =True)
             userdf = df[df['post_language']== f'{lan}']


             dates = userdf.groupby(userdf.index)['hashtags'].agg('count')
             dates = dates.sort_values(ascending =False)


             with col5:
                     st.write(f'Your choice of peak (yyyy-mm) : {dates.index[peak-1]} (Temporal)')

                     sns.set_theme(style = "whitegrid", font= "serif")
                     fig3, ax3 = plt.subplots()
                     userdf.groupby(userdf.index)['hashtags'].agg('count').plot(ax =ax3, color = 'yellow')
                     ax3.plot(dates.index[peak-1],dates[peak-1],'r.',ms =25)
                     ax3.set_xlabel("")
                     fig3.patch.set_facecolor('gray')
                     ax3.patch.set_facecolor('gray')
                     st.pyplot(fig3)


             with col6:

                     st.write("Wordcloud of hashtags based on their frequency of use used during this peak (Topical)")
                     sns.set_theme(style = "white", font= "serif")
                     fig2, ax2 = plt.subplots()
                     wordcloud = generate_wordcloud(dates.index[peak-1],userdf)
                     ax2.imshow(wordcloud)
                     ax2.axis('off')
                     fig2.patch.set_facecolor('gray')
                     ax2.patch.set_facecolor('gray')
                     st.pyplot(fig2)


             with col7:

                st.write("The 5 most typical hashtags of this peak (Topical)")

                subset_df = df.where((df['post_language'] == f'{lan}') & (df.index == dates.index[peak-1] ))
                subset_df.dropna(inplace =True)
                results_subset = Counter()
                subset_df['hashtags'].str.lower().str.split(',').apply(results_subset.update)
                foo = {item : typicality(item,results_subset) for item,_ in results_subset.most_common(5)}
                plot=pd.DataFrame.from_dict(foo,orient='index').reset_index().rename(columns = {'index':'hashtag', 0:'typicality'})

                sns.set_theme(style = "whitegrid", font= "serif")
                fig4,ax4 = plt.subplots()
                plot.plot(kind = "bar", ax = ax4, legend = False)

                ax4.xaxis.set_tick_params(rotation=50)
                fig4.patch.set_facecolor('gray')
                ax4.patch.set_facecolor('gray')
                ax4.set_xticklabels(list(plot['hashtag']))
                st.pyplot(fig4, use_container_width = True)

             with col8:

                   st.write('These were the places where the tweets were tweeted from (Spatial) ')
                   layer = pdk.Layer(
                                    "HexagonLayer",
                                    subset_df,
                                    pickable=False,
                                    extruded=True,
                                    elevation_range = [0,3000],
                                    elevation_scale=150,
                                    get_position="[lon,lat]",
                                    coverage = 1,
                                    )
                   view_state = pdk.ViewState(latitude=52.5200, longitude=13.4050,
                                  zoom=3,
                                  bearing=0,
                                  pitch=50)
                   r = pdk.Deck(layers=[layer], initial_view_state=view_state)
                   st.pydeck_chart(r, use_container_width=True)



            dashboard(lang_choice[lan],peak)
            st.write("### **Some of the significant events captured on Twitter in German**")
            st.empty() 
            st.empty()
            event_german_path = Path(__file__).parents[0]/ 'data' / 'german_tweets.jpeg'
            st.image(str(event_german_path))

            st.write("### **Some of the significant events captured on Twitter in English**")
            st.empty() 
            st.empty()
            event_english_path = Path(__file__).parents[0]/ 'data' / 'english_tweets.jpeg'
            st.image(str(event_english_path))

            
with st.beta_expander("Learn more"):
    st.write("To get a better idea of the facets presented here and of Location Based Social Networks in general feel free to check this link. ")	
    st.write("[Facets - LBSN Structure](https://lbsn.vgiscience.org/structure/facets/)")
    st.write("Publication on [Typicality](https://www.mdpi.com/2220-9964/10/6/407)")
    st.write("Publication on [Facets](https://www.tandfonline.com/doi/full/10.1080/13658816.2018.1546390)")
    st.markdown("*Created by Sagnik Mukherjee for his Master's Thesis in Cartography, 2021*")
	    












