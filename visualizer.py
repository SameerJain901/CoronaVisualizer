import streamlit as st
import os
import os.path
import sys
import time
import pandas as pd
import numpy as np
import re
import requests as rq
from bs4 import BeautifulSoup

import json
import datetime
import logging 
import plotly.graph_objects as go
import plotly.io as pio
import SessionState
from plotly.subplots import make_subplots
import geojson_rewind
import plotly.express as px
import loader
import streamlit.components.v1 as components
import pickle as pk
import plotly.colors as co
##########################################################Definitions
os.chmod('.streamlit/config.toml',755)
 
	
def prepare_mapviz(cdata,india_states):
    state_id_map = {}
    for feature in india_states["features"]:
        feature["id"] = feature["properties"]["state_code"]
        state_id_map[feature["properties"]["st_nm"]] = feature["id"]
    cdata['State'] = cdata['State'].apply(lambda x: x.replace("Delhi",'NCT of Delhi'))
    cdata['State'] = cdata['State'].apply(lambda x: x.replace("Arunachal Pradesh",'Arunanchal Pradesh'))
    cdata['State'] = cdata['State'].apply(lambda x: x.replace("Ladakh",'Jammu & Kashmir'))
    cdata['State'] = cdata['State'].apply(lambda x: x.replace("Jammu and Kashmir",'Jammu & Kashmir'))
    cdata['State'] = cdata['State'].apply(lambda x: x.replace("Dadra and Nagar Haveli and Daman and Diu",'Dadara & Nagar Havelli'))
    cdata['State'] = cdata['State'].apply(lambda x: x.replace("Andaman and Nicobar Islands",'Andaman & Nicobar Island'))
    cdata["GeoID"] = cdata["State"].apply(lambda x: 'StateUnassigned' if x=='State Unassigned' else state_id_map[x])
    return cdata



##########################################################Prepare_data
loader.initialize()
session_state = SessionState.get(IS_scrapped=False)
india_states = json.load(open("out2.json"))
india_states=geojson_rewind.rewind(india_states, rfc7946=False)

final_data=pd.read_csv("final_data.csv")
cdata=prepare_mapviz(final_data.copy(),india_states)


##########################################################

#-------------------------------------------------------------------------------------------------------- Styles
quietlight='''<div class="lds-hourglass"></div>
            <style type='text/css'>
            .lds-hourglass {
            display: inline-block;
            position: relative;
            width: 80px;
            height: 80px;
            }
            .lds-hourglass:after {
            content: " ";
            display: block;
            border-radius: 50%;
            width: 0;
            height: 0;
            margin: 8px;
            box-sizing: border-box;
            border: 32px solid #262730;
            border-color: #262730 transparent #262730 transparent;
            animation: lds-hourglass 1.2s infinite;
            }
            @keyframes lds-hourglass {
            0% {
                transform: rotate(0);
                animation-timing-function: cubic-bezier(0.55, 0.055, 0.675, 0.19);
            }
            50% {
                transform: rotate(900deg);
                animation-timing-function: cubic-bezier(0.215, 0.61, 0.355, 1);
            }
            100% {
                transform: rotate(1800deg);
            }
            }
            </style>

            '''

dark=''' 
              <div class="lds-hourglass"></div>
            <style type='text/css'>
            .lds-hourglass {
            display: inline-block;
            position: relative;
            width: 80px;
            height: 80px;
            }
            .lds-hourglass:after {
            content: " ";
            display: block;
            border-radius: 50%;
            width: 0;
            height: 0;
            margin: 8px;
            box-sizing: border-box;
            border: 32px solid #fafafa;
            border-color: #fafafa transparent #fafafa transparent;
            animation: lds-hourglass 1.2s infinite;
            }
            @keyframes lds-hourglass {
            0% {
                transform: rotate(0);
                animation-timing-function: cubic-bezier(0.55, 0.055, 0.675, 0.19);
            }
            50% {
                transform: rotate(900deg);
                animation-timing-function: cubic-bezier(0.215, 0.61, 0.355, 1);
            }
            100% {
                transform: rotate(1800deg);
            }
            }
            </style>
            
            '''
#--------------------------------------------------------------------------------------------------------- 
# Theming 
def update_theme(primaryColor,backgroundColor,secondaryBackgroundColor,textColor,font):
    # Theme Base
    theme_data=['[theme]\n\n','primaryColor=\"%s\"\n'%(primaryColor),
    'backgroundColor=\"%s\"\n'%(backgroundColor),
    'secondaryBackgroundColor=\"%s\"\n'%(secondaryBackgroundColor),
    'textColor=\"%s\"\n'%(textColor),
    'font=\"%s\"\n'%(font)]
    os.remove('.streamlit/config.toml')
    theme_file=open('.streamlit/config.toml','w+')
    theme_file.writelines(theme_data)


# Starting with the process

# Side Bar comfiguration
st.set_page_config(  # Alternate names: setup_page, page, layout
	layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	initial_sidebar_state="collapsed",  # Can be "auto", "expanded", "collapsed"
    )
st.sidebar.title('Covid19 Data Visualizer')
pages=['Latest News','Google\'s Mobility Report','Vaccination Reports',
        'Map','Data Reports','Forecast Reports',
]
out=st.sidebar.radio('Page:',pages)

st.sidebar.header('Theme:')
theme=st.sidebar.selectbox('Select your theme:',['Dark','Light','Quiet-Light','Solarized'])
selected_theme=st.sidebar.empty()
# End of side bar configuration


# Theme Configuration
if theme=='Quiet-Light':
    primaryColor="#6eb52f"
    backgroundColor="#f0f0f5"
    secondaryBackgroundColor="#e0e0ef"
    textColor="#262730"
    font="sans serif"
    
elif theme=='Dark':
    primaryColor="#F63366"
    backgroundColor="#0e1117"
    secondaryBackgroundColor="#31333F"
    textColor="#fafafa"
    font="sans serif"
    
elif theme=='Light':
    primaryColor="#f63366"
    backgroundColor="#FFFFFF"
    secondaryBackgroundColor="#f0f2f6"
    textColor="#262730"
    font="sans serif"

else:
    primaryColor="#d33682"
    backgroundColor="#002b36"
    secondaryBackgroundColor="#586e75"
    textColor="#fafafa"
    font="Monospace"

update_theme(primaryColor,backgroundColor,secondaryBackgroundColor,textColor,font)

########################################################################################################################################################################
#################################################################################### Functions #########################################################################
########################################################################################################################################################################
def magnify():
    return [dict(selector="th",
                 props=[("font-size", "7pt")]),
            dict(selector="td",
                 props=[('padding', "4px 4px"),]),
            dict(selector="th:hover",
                 props=[("font-size", "13pt")]),
            dict(selector="tr:hover td:hover",
                 props=[('max-width', '200px'),
                        ('font-size', '14pt'),
                       ('color', '#4f6d7a')])]


def prepare_vtdata():
    df = pd.read_csv("vaccine_doses_statewise.csv",index_col='State')
    df['Total']=df.iloc[:,-2]#df.sum(axis=1)
    df.drop(['Miscellaneous', 'Total'],inplace=True)
    df['Status']='Vaccinated'
    df.reset_index(inplace=True)
    df_vacc=pd.DataFrame(df,columns=['Total','Status','State'])

    dt=pd.read_csv("statewise_tested_numbers_data.csv")
    dt = pd.DataFrame(dt)
    dt['Updated On']=pd.to_datetime(dt['Updated On'],format='%d/%m/%Y')
    df_test=pd.DataFrame(columns=['State',"Status",'Total'])
    dt_grp=dt.groupby(dt['Updated On']).get_group((datetime.datetime.now()-datetime.timedelta(days=1)).strftime("%d"+"/"+"%m"+"/"+"%Y"))
    df_test["Total"]=dt_grp["Total Tested"].fillna(0)
    df_test['Status']='Tested'
    df_test['State']=dt_grp['State'].unique()
    if (dt_grp['State']=='Dadra and Nagar Haveli and Daman and Diu').all()==False:
        df_test.loc[len(df_test.index)] = ['Dadra and Nagar Haveli and Daman and Diu', "Tested", 0] 

    return (df_vacc, df_test)



def scrape_data():
    card_data={'img_src':[],'link':[],'text':[]}
    with st.spinner('Getting Latest News'):
        
        res=rq.get("https://www.indiatoday.in/coronavirus")
        soup=BeautifulSoup(res.text)
        corona_data=soup.find('div',id='block-views-pollution-coronavirus')
        pollution_left=corona_data.find_all('div',class_='pollution-left')
        pollution_right=corona_data.find_all('div',class_='pollution-right')
        for each_pollution in pollution_left:
            card_data['img_src'].append(each_pollution.a.img.get('src'))
            card_data['link'].append('https://www.indiatoday.in/'+each_pollution.a.get('href'))
        for each_pollution in pollution_right:
            card_data['text'].append(each_pollution.text)

        res=rq.get("https://www.india.com/topic/coronavirus/")
        soup=BeautifulSoup(res.text)
        aside=soup.find('aside',class_="row topic-strlist")
        corona_data=aside.find('ul')
        for each_item in corona_data.find_all('li'):
            card_data['link'].append(each_item.a.get('href'))
            card_data['img_src'].append(each_item.a.img.get('data-lazy-src'))
            card_data['text'].append(each_item.div.h3.a.get_text())
    print('Dumped Data')
    pk.dump(card_data,open('card_data.pkl','wb'))
    

def quick_plot(data,categ,color,img):
    fig=go.Figure()
    fig.add_traces( go.Scatter(x=data.index, y=data[categ],
                               fill='tozeroy',
                               visible=True,
                               marker={'color':color},
                               showlegend=False,
                               name=categ.replace('_',' ').capitalize()
                              )

                )
    fig.add_layout_image(
        dict(
            source='https://image.flaticon.com/icons/png/512/3579/3579748.png',
             xref="paper", yref="paper",
            x=1, y=1.05,
            sizex=0.2, sizey=0.2,
            xanchor="right", yanchor="bottom",
            sizing="contain",
            opacity=0.5,
            layer="below")
        )
    fig.update_layout(title=categ.replace('_',' ').capitalize(),dragmode=False)
    return fig


def getmr_theme(theme):
    if theme=='Light':
        return 'light'
    elif theme=='Dark':
        return 'dark'
    elif theme=='Quiet-Light':
        return 'light'
    else:
        return 'dark'

def get_map_theme(theme):
    if theme=='Light':
        return 'plotly'
    elif theme=='Dark':
        return 'plotly_dark'
    elif theme=='Quiet-Light':
        return 'plotly+quiet_light'
    else:
        return 'plotly_dark+solarized'

def get_color_scale(info):
    if info=='Hospitalized':
        return ['#DB8EE1','#8C2C85']
    elif info=='Recovered':
        return ['#60D0C9','#195942']
    elif info=='Deceased':
        return ['#94B6C7','#4F7592']
    else:
        return ['#C5BDB8','#5B504A']
    
    
def plot_map_all(cdata,date,india_states,info,theme):
    qt=cdata[cdata['Date']==date]
    missed_data={key:[] for key in qt}
    for state in set(cdata.State.unique()).difference(set(cdata[cdata['Date']==date].State)):
              missed_data['Date'].append(date)
              missed_data['State'].append(state)
              missed_data['Deceased'].append(0)
              missed_data['Recovered'].append(0)
              missed_data['Migrated_Other'].append(0)
              missed_data['Hospitalized'].append(0)
              missed_data['GeoID'].append(str(cdata[cdata.State==state].iloc[0]['GeoID']))
    
    qt=qt.append(pd.DataFrame(missed_data))
    state=list(qt['State'])
    vals=list(qt[info])    
    hoverdata=['<b>{}</b>:'.format(se) for se in state]

    for i in range(len(hoverdata)):
        hoverdata[i]=hoverdata[i]+' {}'.format(vals[i])
    fig = px.choropleth(
        qt,
        locations="GeoID",
        geojson= india_states,
        color=info,
        center = {"lat": 22.4797, "lon": 77.8969},
        title="India Corona Stats",
        color_continuous_scale=get_color_scale(info)
    )
    
    
    fig.update_geos(fitbounds="locations", visible=False)
    
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},dragmode=False,template=theme)
    fig.update_traces(hovertemplate=hoverdata)
    return fig

def offset_signal(signal, marker_offset):
    if abs(signal) <= marker_offset:
        return 0
    return signal - marker_offset if signal > 0 else signal + marker_offset

def forecast_india(daywise,n_days,theme=get_map_theme(theme)):
    
    cdata=pd.read_csv('forecasts.csv')
    cdata.set_index('date',inplace=True)
    state='India'
    x_date=cdata.index
    fig_data=[]
    fig_layouts=[]
    titles=['Hospitalized in %s'%(state),'Recovered in %s'%(state),
            'Deceased in %s'%(state),'Migrated_Other in %s'%(state)]
    fig = make_subplots(rows=4,cols=1,shared_xaxes=True,vertical_spacing=0.05,subplot_titles=titles,)
    cc=1
    color={'Hospitalized':['#eb3758','#eb3a37'],'Recovered':['#36eb58','#36eba0'],
          'Deceased':['#767f7b','#848685'],'Migrated_Other':['#974cc9','#b04cc9']}
    for status in ['Hospitalized','Recovered','Deceased','Migrated_Other']:
        
        y_status=list(cdata[status])[-n_days:]
        
        fig.add_trace(go.Scatter(
            x=x_date,
            y=y_status,
            mode='markers',
            marker=dict(color=color[status][0])
        ),row=cc,col=1)

        xref,yref=None,None
        if cc==1:
            xref='x'
            yref='y'
        else:
            xref='x'+str(cc)
            yref='y'+str(cc)
        fig_layouts.extend([dict(
            type='line',
            xref=xref,
            yref=yref,
            x0=x_date[i],
            y0=0,
            x1=x_date[i],
            y1=offset_signal(y_status[i], marker_offset=0.04),
            line=dict(
                color=color[status][1],
                width=1
            )
        ) for i in range(len(y_status))])
        cc+=1

    fig.update_layout(showlegend=False,template=theme,
                      shapes=fig_layouts,height=900,
                     )
    # fig.show()
    return fig


def daywise_india(daywise,n_days,theme=get_map_theme(theme)):
    
    cdata=daywise
    cdata.set_index('date',inplace=True)
    state='India'
    x_date=cdata.index
    fig_data=[]
    fig_layouts=[]
    titles=['Hospitalized in %s'%(state),'Recovered in %s'%(state),
            'Deceased in %s'%(state),'Migrated_Other in %s'%(state)]
    fig = make_subplots(rows=4,cols=1,shared_xaxes=True,vertical_spacing=0.05,subplot_titles=titles,)
    cc=1
    color={'Hospitalized':['#eb3758','#eb3a37'],'Recovered':['#36eb58','#36eba0'],
          'Deceased':['#767f7b','#848685'],'Migrated_Other':['#974cc9','#b04cc9']}
    for status in ['Hospitalized','Recovered','Deceased','Migrated_Other']:
        
        y_status=list(cdata[status])[-n_days:]
        
        fig.add_trace(go.Scatter(
            x=x_date,
            y=y_status,
            mode='markers',
            marker=dict(color=color[status][0])
        ),row=cc,col=1)

        xref,yref=None,None
        if cc==1:
            xref='x'
            yref='y'
        else:
            xref='x'+str(cc)
            yref='y'+str(cc)
        fig_layouts.extend([dict(
            type='line',
            xref=xref,
            yref=yref,
            x0=x_date[i],
            y0=0,
            x1=x_date[i],
            y1=offset_signal(y_status[i], marker_offset=0.04),
            line=dict(
                color=color[status][1],
                width=1
            )
        ) for i in range(len(y_status))])
        cc+=1

    fig.update_layout(showlegend=False,template=theme,
                      shapes=fig_layouts,height=900,
                     )
    # fig.show()
    return fig

#-----------------------------------------------------------------------------------------------------------------------------
if out=='Map':
    st.header('Map')
    Dates=pd.to_datetime(cdata.Date,dayfirst=True)

    date=st.date_input('Select Day',min_value=Dates.min(),max_value=Dates.max())
    # state=st.selectbox('Select State',list(loader.get_cdata().State.unique()))
    info=st.selectbox('Select Information Type',['Hospitalized','Recovered','Migrated_Other','Deceased'])
    date=pd.to_datetime(date,dayfirst=True)
    config = dict({'scrollZoom': False,
    'displayModeBar': False,
    'editable': False})


    with st.spinner('Preparing Map'):
        st.plotly_chart(
            plot_map_all(cdata,date.strftime('%d/%m/%Y'),india_states,info,get_map_theme(theme)),
                             use_container_width=False,**{'config':config})

if out=='Latest News':
    if session_state.IS_scrapped:
        print('Skipping Scraping')
    else:
        scrape_data()
        session_state.IS_scrapped=True
    st.header('Latest News')
    card_data=pk.load(open('card_data.pkl','rb'))
    my_card='\n'.join(open('card.html','r').readlines())
    my_card=my_card.replace('st_backgroundColor',backgroundColor)
    my_card=my_card.replace('st_textColor',textColor)
    my_card=my_card.replace('st_secondaryBackgroundColor',secondaryBackgroundColor)
    rows=int(len(card_data['img_src'])/3)
    if rows*3>len(card_data['img_src']):
        rows-=1
    ind=0
    for i in range(rows):
        new_card=my_card
        for i in range(1,4):
            new_card=new_card.replace('st_link_'+str(i),card_data['link'][ind])
            new_card=new_card.replace('st_text_'+str(i),card_data['text'][ind])
            new_card=new_card.replace('st_img_src_'+str(i),card_data['img_src'][ind])
            ind+=1
        components.html(new_card,height=400,width=1200)

if out=='Google\'s Mobility Report':

    mr_2020=pd.read_csv('2020_IN_Region_Mobility_Report.csv')
    mr_2021=pd.read_csv('2021_IN_Region_Mobility_Report.csv')
    IN20=mr_2020[mr_2020.sub_region_1.isna()]
    mr_2020.drop(IN20.index,axis=0,inplace=True)
    IN21=mr_2021[mr_2021.sub_region_1.isna()]
    mr_2021.drop(IN21.index,axis=0,inplace=True)
    IN20.index=IN20.date
    IN21.index=IN21.date



    mrdt_links={
        'bus':['transit_stations_percent_change_from_baseline','#d01884','https://www.dropbox.com/s/c687b5muzd2lqrx/bus.svg?raw=1'],
        'home':['residential_percent_change_from_baseline','#8430ce','https://www.dropbox.com/s/05ifsbhl84fze3c/home.svg?raw=1'],
        'hospital':['grocery_and_pharmacy_percent_change_from_baseline','#129eaf','https://www.dropbox.com/s/l6spsoxatmme6ca/hospital.svg?raw=1'],
        'office':['workplaces_percent_change_from_baseline','#d56e0c','https://www.dropbox.com/s/8uws8tb8kpi88eh/office.svg?raw=1'],
        'park':['parks_percent_change_from_baseline','#188038','https://www.dropbox.com/s/cwiz5g67a9wh681/park.svg?raw=1'],
        'cart':['retail_and_recreation_percent_change_from_baseline','#1967d2','https://www.dropbox.com/s/afnvdw1zn6q5kne/trolley.svg?raw=1']
    }

    kachra={
                'cart':'''Mobility trends for places such as
        restaurants, cafés, shopping centres,
        theme parks, museums, libraries and
        cinemas.''',
                'hospital':'''Mobility trends for places such as
        supermarkets, food warehouses,
        farmers markets, specialty food
        shops and pharmacies.''',
                'park':'''Mobility trends for places like
        national parks, public beaches,
        marinas, dog parks, plazas and public
        gardens.''',
                'bus':'''Mobility trends for places that are public
        transport hubs, such as underground, bus and
        train stations.''',
                'office':'''Mobility trends for places of work''',
                'home':'''Mobility trends for places of residence.''',
    }


    simp='''
            <style type='text/css'>
            .shadow {
                transition: .5s ease;
                background-color: st_back;
                color: st_tc;
                }
                
                .shadow:hover{
                
                box-shadow:
                1px 1px #373737,
                2px 2px #373737,
                3px 3px #373737,
                4px 4px #373737,
                5px 5px #373737,
                6px 6px #373737;
                -webkit-transform: translateX(-3px);
                transform: translateX(-3px);
                transition: .5s ease;
                }
                </style>
                <div class=shadow>
                st_text
                </div>

        '''
    my_card='\n'.join(open('html_test.html','r').readlines())
    header=st.empty()

    header.header('Google\'s Mobility Report 2021')
    with st.spinner('loading..'):
        components.html(my_card.replace('theme17',getmr_theme(theme)))



    st.write("The data shows how visits to places, such as corner shops and parks, are changing in each geographic region")
    year=st.selectbox('Select the year for which you want to view the data: ',['2021','2020'])
    if year=='2020':
        header.header('Google\'s Mobility Report 2020')
    else:
        header.header('Google\'s Mobility Report 2021')




    categ=st.selectbox('Select data type to view:',[x.capitalize() for x in list(mrdt_links.keys())])

    sel_categ=mrdt_links[categ.lower()]
    if year=='2021':
        data=IN21
    else:
        data=IN20
    c1,c2=st.beta_columns(2)
    c1.plotly_chart(quick_plot(data,sel_categ[0],sel_categ[1],sel_categ[2]))
    card_2=simp.replace('st_back',primaryColor)
    card_2=simp.replace('st_tc',textColor)
    card_2=card_2.replace('st_text',kachra[categ.lower()])
    avg=data[sel_categ[0]].mean()
    c2.markdown('''### {} compared to the baseline
    '''.format(str(avg)))
    components.html(card_2)


    st.header('State Level Mobility Reports')

    ST20=mr_2020[mr_2020.sub_region_2.isna()]
    ST21=mr_2021[mr_2021.sub_region_2.isna()]
    if year=='2021':
        ST=ST21
    else:
        ST=ST20

    states=ST.sub_region_1.unique()
    state=st.selectbox('Select State for state level view:',states)
    c1,c2=st.beta_columns(2)
    c1.plotly_chart(quick_plot(ST[ST['sub_region_1']==state],sel_categ[0],sel_categ[1],sel_categ[2]))
    avg=ST[ST['sub_region_1']==state][sel_categ[0]].mean()
    c2.markdown('''### {} compared to the baseline
    '''.format(str(avg)))
    components.html(card_2)

if out=='Vaccination Reports':
    st.header('Vaccination and Testing status accross india')
    vacc_data, test_data = prepare_vtdata()
    
    color_vacc=['#B12F95','#ECACD3']
    color_test=['#ADABED','#2E7FDC']
    config={
    'scrollZoom': False,
    'displayModeBar': False,
    'editable': False,
    }
    vacc_data.sort_values(by='Total',inplace=True)
    test_data.sort_values(by='Total',inplace=True)
    v_col=co.n_colors(co.hex_to_rgb(color_vacc[0]),co.hex_to_rgb(color_vacc[1]),len(vacc_data.Total))
    t_col=co.n_colors(co.hex_to_rgb(color_test[0]),co.hex_to_rgb(color_test[1]),len(vacc_data.Total))
    fig_bar = go.Figure()
    fig_bar.add_trace(
        go.Bar(
            x = vacc_data.Total,
            y = vacc_data.State,
            visible=True,showlegend=False,orientation='h',marker=dict(color=['rgb'+str(x) for x in v_col]),
        )
    )

    fig_bar.add_trace(
            go.Bar(
                x = test_data.Total,
                y = test_data.State,
                orientation='h',marker=dict(color=['rgb'+str(x) for x in t_col]),
                visible=False,
                showlegend=False,
            )
        )  

    fig_bar.update_layout(dragmode=False,showlegend=False,template=get_map_theme(theme),width=1200,height=1000,
        updatemenus=[go.layout.Updatemenu(
            active=0,
            buttons=list(
                [dict(label = 'Vaccinated',
                    method = 'update',
                    args = [{'visible': [True, False]},
                            {'title': 'Vaccinated',
                            'showlegend':True}]),
                dict(label = 'Tested',
                    method = 'update',
                    args = [{'visible': [False, True]},
                            {'title': 'Tested',
                            'showlegend':True}]),
                ]),
                pad={"r": 10, "t": 2},
                showactive=True,
                x=1.0,
                xanchor="right",
                y=1.3,
                yanchor="top"
            )
        ]
        )
    


    

    fig=px.bar_polar(vacc_data.sort_values(by='Total')[-15:], 
                    title='Top 15 states in vaccination',
                    theta="State",r='Total',
                    color='Total',template=get_map_theme(theme),barmode='relative',
                    color_continuous_scale= color_vacc)
    fig.update_layout(dragmode=False)
    fig1,fig2=st.beta_columns([1,1])
    fig1.plotly_chart(fig,**{'config':config})
    
    fig=px.bar_polar(test_data.sort_values(by='Total')[-15:],
                    title='Top 15 states in testing',
                     theta="State",r='Total',
                    color='Total',template=get_map_theme(theme),barmode='relative',
                    color_continuous_scale= color_test)
    fig.update_layout(dragmode=False)
    fig2.plotly_chart(fig,**{'config':config})
    st.plotly_chart(fig_bar,**{'config':config})

if out=='Forecast Reports':
    st.header('Forecast Reports')
    with st.spinner('Loading Data'):
        mata=pd.read_csv('final_data.csv')
        mata.Date=pd.to_datetime(mata.Date,dayfirst=True)
        daywise=mata.groupby('Date').agg(sum)
        daywise.sort_index(ascending=True,inplace=True)
    days=st.slider(label='Number of days to forecast',
                    min_value=1,max_value=100,step=1)
    if st.button('Forecast'):
        with st.spinner('Please wait... Model are working with numbers'):
            st.plotly_chart(forecast_india(daywise,days))

if out=='Data Reports':
    
    data=pd.read_csv('final_data.csv')
    data.set_index(data.Date)
    data.sort_index(inplace=True)
    state=st.selectbox('Select the state for state related data: ',list(data.State.unique()))
    
    data=data[data.State==state]
    styled_data=data.style
    styles = [
        dict(selector="tr:hover",props=[("background-color", "#eccbd9")]),
        dict(selector="th:hover",props=[("background-color", "#eccbd9")]),
        dict(selector="th", props=[('background-color','{}'.format(secondaryBackgroundColor)),
                                ("font-size", "120%"),
                                ("text-align", "center"),
                                ('color', '#ffffff'),
                                ('border','1px solid #dbe9ee')]),
        dict(selector='tbody', props=[('color', '{}'.format(secondaryBackgroundColor)),]),
        dict(selector='tr', props=[('background-color','{}'.format(secondaryBackgroundColor)),
                                    ('color', '{}'.format(textColor)),
                                    ('font-family','Helvetica')]),
        dict(selector='td',props=[('border','1px solid {}'.format(textColor))])]

    styles.extend(magnify())
    df=styled_data.set_table_styles(styles)
    components.html(df.render(),width=600,height=800,scrolling =True)


