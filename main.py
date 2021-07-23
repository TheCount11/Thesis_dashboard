# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 14:50:35 2021

@author: pool234
"""

import numpy as np
import pandas as pd
import pydeck as pdk
import altair as alt
from PIL import Image
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
    #print(flat_list[:10])
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


st.set_page_config(
     
     layout="wide",
     initial_sidebar_state="expanded",
)


st.title("Visualising twitter data of EU Migration Crisis")
st.sidebar.markdown("# **Quick Reads**")
st.sidebar.markdown("#### **Facets of LBSN**")
st.sidebar.write("")
st.sidebar.write("")
with st.sidebar.beta_expander('Spatial'):
    st.write("The Spatial facet deals with the location information of the tweets.")

with st.sidebar.beta_expander('Temporal'):
    st.write("The Temporal facet deals with the timestamp the tweets.")
    
with st.sidebar.beta_expander('Topical'):
    st.write("The Topical facet deals with the content of the tweets.")

with st.sidebar.beta_expander('Social'):
    st.write("The Social facet deals with the user who tweets.")
with st.sidebar.beta_expander("Learn more"):
    st.write("[Facets - LBSN Structure](https://lbsn.vgiscience.org/structure/facets/)")    
    
st.sidebar.markdown("#### **Data Format**")
st.sidebar.write("")
with st.sidebar.beta_expander('Raw'):
    st.write("Data downloaded from twitter where there is no privacy protection.")
with st.sidebar.beta_expander('HLL'):
    st.write("Privacy aware data format which is based on HyperLogLog algorithm.")  
with st.sidebar.beta_expander('Learn More'):
    st.write("[Privacy Overview](https://lbsn.vgiscience.org/privacy/overview/)")       
    

st.markdown('#### **About the Migration Crisis**')
st.write("")
st.write("""170,000 geotagged tweets filtered with relevant hashtags in six languages. Various types visualisations 
             were used to get a sneak peek into what the data is telling us.""")
             
st.subheader('Take a look at the location of all the tweets collected')
        
st.pydeck_chart(pdk.Deck(
                         
                         width = "100%",
                         initial_view_state=pdk.ViewState(
                             latitude=49.5200,
                             longitude=15.4050,
                             zoom=3,
                             pitch=50,
                             ),
                         layers=[
                             pdk.Layer(
                             "HexagonLayer",
                              df,
                              get_position=["lon", "lat"],
                              auto_highlight=True,
                              elevation_scale=50,
                              pickable=False,
                              elevation_range=[0, 3000],
                              extruded=True,
                              coverage=1,
                         ),
                            
                     ],
                    
                     
                 ))                             
   
with st.beta_expander('Spatial'): 
        
       
    
        col1, col2 = st.beta_columns(2)
        
        with col1:
            lang = st.selectbox('select a language', df["post_language"].unique(), key = "lang")
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
                             data=df[df['post_language'] == lang],
                             opacity =0.3,
                             get_position='[lon, lat]',
                             radius_scale=6,
                             get_fill_color=[255, 140, 0, 100],
                             get_radius=600,
                             pickable = True,
                             extruded = True,
                         ),
                            
                     ],
                    
                     
                 ))
            
            
      
                     
                       
        
with st.beta_expander('Temporal'):
  with st.beta_container():    
        col3, col4 = st.beta_columns(2)
    
        sns.set_theme(style = "darkgrid", font= "serif")
        
        with col3:
                st.write("")
                st.write("")  
                st.write("Tweets were collected between 2016 till January 2021")
                st.write("")  
                st.write("") 
                st.write("Total yearly distribution of tweets")
                fig, ax = plt.subplots() 
                df.years.value_counts(sort = False).plot(kind = "bar", ax = ax)
                ax.xaxis.set_tick_params(rotation=0)
                fig.patch.set_facecolor('gray')
                ax.patch.set_facecolor('gray')
                st.pyplot(fig)
        with col4:        
                st.markdown("take a look at the years in more detail")
                sel = st.selectbox("Select the year", sorted(list(df.years.unique())), key='time')
                fig1,ax1 = plt.subplots()
                df["year-month"][df["years"]==sel].value_counts(sort = False).plot(kind = "bar", ax = ax1)
                ax1.xaxis.set_tick_params(rotation=50)
                fig1.patch.set_facecolor('gray')
                ax1.patch.set_facecolor('gray')
                st.pyplot(fig1)
    
  
with st.beta_expander("Topical"):
 
      
            st.write("""Typicality indicates how typical the measured atrribute is with respect to a subset.
                             Here the subset is time (Years). And the measured attribute is hashtags.""")
            st.write ("""Positive typicality indicates that the hashtag was popular during the year displayed on the x axis.
                      Negative typicality indicates the opposite""")         
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
            
with st.beta_expander("Social : HLL"):   
        st.write("Visualising number of posts vs users all over Europe")
        with st.beta_container():
            file_grid = Path(__file__).parents[0]/ 'data/latlng_to_geohash.csv'	
            grid_data = pd.read_csv(file_grid)
            grid_data.rename(columns = {"latitude_3":"lat", "longitude_3":"lon"},inplace = True)
            grid_data.drop(columns = ["hashtags"],inplace =True)
            
            choice = {'Number of posts' : "postcount",
                      'Number of users' : "usercount"}
            c = st.selectbox('select a metric', list(choice.keys()), key = "c") 
            
            layer = pdk.Layer(
                                "GridLayer",
                                grid_data,
                                pickable=True,
                                extruded=True,
                                cell_size=2000,
                                elevation_scale=150,
                                get_position="[lon,lat]",
                                get_color_weight=choice[c],
                            )
            view_state = pdk.ViewState(latitude=52.5200, longitude=13.4050, zoom=5, bearing=0, pitch=50)
            r = pdk.Deck(layers=[layer], initial_view_state=view_state)
            st.pydeck_chart(r, use_container_width=True)            
            

            
with st.beta_expander('Spatial, Temporal, Topical'):
    
    with st.beta_container(): 
         
        lang_choice = {'English' : 'en',
                       'Spanish' : 'es',
                       'Italian' : 'it',
                       'German' : 'de',
                       'French' : 'fr',
                       'Dutch' : 'nl'}
          
        lan = st.selectbox('select a language', list(lang_choice.keys()), key = "lan")
        peak = st.selectbox('select a peak number between 1 and 6', [1,2,3,4,5,6], key = "peak")
        
        col5, col6, col7 = st.beta_columns(3) 
        
        def dashboard(lan,peak):  
            
         df["year-month"] = pd.to_datetime(df["year-month"]).dt.to_period('M')   
         df.set_index('year-month',inplace =True)   
         userdf = df[df['post_language']== f'{lan}']
        
        
         dates = userdf.groupby(userdf.index)['hashtags'].agg('count')
         dates = dates.sort_values(ascending =False)
         
         
         with col5:
                 st.write(f'Your choice of peak (yyyy-mm) : {dates.index[peak-1]}')
                 
                 sns.set_theme(style = "whitegrid", font= "serif")
                 fig3, ax3 = plt.subplots()
                 userdf.groupby(userdf.index)['hashtags'].agg('count').plot(ax =ax3, color = 'yellow')
                 ax3.plot(dates.index[peak-1],dates[peak-1],'r.',ms =25)   
                 ax3.set_xlabel("")
                 fig3.patch.set_facecolor('gray')
                 ax3.patch.set_facecolor('gray')
                 st.pyplot(fig3)
                 
                 
         with col6:
             
                 st.write("Wordcloud of hashtags used during this time")
                 sns.set_theme(style = "white", font= "serif")
                 fig2, ax2 = plt.subplots()      
                 wordcloud = generate_wordcloud(dates.index[peak-1],userdf)              
                 ax2.imshow(wordcloud)
                 ax2.axis('off')
                 fig2.patch.set_facecolor('gray')
                 ax2.patch.set_facecolor('gray')
                 st.pyplot(fig2)

               
         with col7:
            
            st.write("The 5 most typical hashtags of this peak")
          
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
        
        dashboard(lang_choice[lan],peak)                



with st.beta_expander('P.S.'):
	st.write("The spatial facet does not allow for selection by location, but uses language for the following image")
	file_path = Path(__file__).parents[0]/ 'data' / 'lang-loc-uk.jpeg'
	img = Image.open(file_path) 
	st.image(img)










          
            
            
            
