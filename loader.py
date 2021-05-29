import pandas as pd
import numpy as np
import json
import datetime
import geojson_rewind
import plotly.graph_objects as go
import plotly.io as pio

cdata=pd.read_csv('cdata.csv')
fdata=pd.read_csv('forecasts.csv')
final_data=pd.read_csv("final_data.csv")
map_json = json.load(open("out2.json"))

def prepare_mapviz(cdata):
    state_id_map = {}
    india_states = geojson_rewind.rewind(map_json, rfc7946=False)
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


def initialize():
        pio.templates["solarized"] = go.layout.Template({
                'layout': {'geo': {'bgcolor': 'rgb(0,43,54)',
                                        'lakecolor': 'rgb(0,43,54)',
                                        'landcolor': 'rgb(0,43,54)',
                                        'showlakes': True,
                                        'showland': True,
                                        'subunitcolor': '#506784'},
                                'polar':{'angularaxis': {'gridcolor': '#506784', 
                                        'linecolor': '#506784', 'ticks': ''},
                                        'bgcolor': 'rgb(0,43,54)',
                                'radialaxis': {'gridcolor': '#506784', 
                                        'linecolor': '#506784', 'ticks': ''}},

                                'paper_bgcolor': 'rgb(0,43,54)',
                                'plot_bgcolor': 'rgb(0,43,54)'
                                
                                }}
                )

        pio.templates["quiet_light"] = go.layout.Template({
                'layout': {'geo': {'bgcolor': 'rgb(240,240,245)',
                                        'lakecolor': 'rgb(240,240,245)',
                                        'landcolor': 'rgb(240,240,245)',
                                        'showlakes': True,
                                        'showland': True,
                                        'subunitcolor': '#506784'},
                                
                                'polar':{'angularaxis': {'gridcolor': '#506784', 
                                        'linecolor': '#506784', 'ticks': ''},
                                        'bgcolor': 'rgb(240,240,245)',
                                'radialaxis': {'gridcolor': '#506784', 
                                        'linecolor': '#506784', 'ticks': ''}},
                                
                                'paper_bgcolor': 'rgb(240,240,245)',
                                'plot_bgcolor': 'rgb(240,240,245)'
                                
                                }}
                )




