import pandas as pd
import numpy as np
import streamlit as st

# import glob
# import yaml
from pathlib import Path
from collections import defaultdict

#########################################
# Helpers Functions

display_cols = ['image','name', 'color', 'star', 'class', 'speed', 'power', 'attack', 'defense', 'health', 'types', 'source', 'family']

def filter_by_1col_num(df, col_name, query, oper_flag="eq"):
    ok_flag_list = []
    assert col_name in df.columns, "col_name must be valid"

    for i, val in enumerate(df[col_name]):
        if oper_flag == 'ge':
            flag = True if val >= query else False
        elif oper_flag == 'le':
            flag = True if val <= query else False
        else: # default = eq
            flag = True if val == query else False

        ok_flag_list.append(flag)
    
    assert len(ok_flag_list) == len(df)
    return np.array(ok_flag_list)

def filter_by_1col(df, col_name, query, exact_flag=False):

    def check_valid_value(query, string, exact_flag=False):
        if exact_flag:
            if query.lower() == string.lower():
                return True

        elif query.lower() in string.lower():
            return True
        
        return False

    ok_flag_list = []
    assert col_name in df.columns, "col_name must be valid"

    for i, s in enumerate(df[col_name]):

        if isinstance(s, list):
            for s2 in s:
                flag = check_valid_value(query, s2, exact_flag=exact_flag)
                if flag: break
        else:
            flag = check_valid_value(query, s, exact_flag=exact_flag)

        
        ok_flag_list.append(flag)
    
    assert len(ok_flag_list) == len(df)
    return np.array(ok_flag_list)

def display_image(url, scale=0.5):
    from urllib.request import urlopen
    from PIL import Image

    image = Image.open(urlopen(url))
    st.image(image.resize(( int(image.width * scale), int(image.height * scale))))

def display_heroes_from_df(df):
    st.dataframe(df[display_cols],
                 column_config={
                         "image": st.column_config.ImageColumn("Avatar", help="")},
                 use_container_width=True,
                 hide_index=True)

    for i in range(len(df)):
        url = df['image'].values[i]
        display_image(url)
        st.write(f"{df['name'].values[i]} - {df['speed'].values[i]} - {df['class'].values[i]}")
        st.write(f'Attack:{df["attack"].values[i]} -- Defence:{df["defense"].values[i]} -- Health:{df["health"].values[i]}')
        st.write(df['skill'].values[i])
        st.write(df['effects'].values[i])
        # for sp in df['effects'].values[i]:
        #     st.write(sp)

#########################################
## Load the main file (TODO: caching)=
st.set_page_config(layout="wide")
st.header(f'HeroPlan Explorer')
st.write('Powered by Heroplan.io : Thanks E&P community for continually update hero data.')

df = pd.read_csv('heroes_ep.csv')
class_values = ['None'] + list(df['class'].unique()) 
star_values = ['None'] + list(df['star'].unique())
color_values = ['None'] + list(df['color'].unique())
speed_values = ['None'] + list(df['speed'].unique())
source_values = ['None'] + list(df['source'].unique())

# defense_values = ['None'] + list(df['defense'].unique())
# attack_values = ['None'] + list(df['attack'].unique())
# health_values = ['None'] + list(df['health'].unique())

#########################################
## Select Main Program

with st.sidebar:
    genre = st.radio(
    "Choose how to explore heroes",
    [":rainbow[Heroes Explorer]", "***LB/CB Hero Stat*** :movie_camera:"],
    captions = ["Filter only heroes with certain properties", "Co-powered by Elioty33's DataVault"])

#########################################
## Program 1
if genre == ':rainbow[Heroes Explorer]':
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Standard Filters:")
        st.write("Tips: filter costume by typing ' C' or 'C2' in the Name box")
        with st.expander("Filter Options"):
            name_option = st.text_input(label="Name:", value="")
            star_option = st.selectbox(label='Star:', options=star_values, index=0)
            color_option = st.selectbox(label='Color:', options=color_values, index=0)
            speed_option = st.selectbox(label='Speed:', options=speed_values, index=0)
            class_option = st.selectbox(label='Class:', options=class_values, index=0)
            source_option = st.selectbox(label='Origin:', options=source_values, index=0)
    
            special_type_option = st.text_input(label="SpecialSkill Category", value="Hit 3")
            special_text_option = st.text_input(label="SpecialSkill Text", value="Dispel")
    with col2:
        st.header("Stat Filters")
        with st.expander("Stat Options"):   
            defense_option = st.text_input(label="Defense:", value="0")
            attack_option = st.text_input(label="Attack:", value="0")
            health_option = st.text_input(label="Health:", value="0")
    with col3:
        st.header("Sorted By (or directly click at the column name)")
        sort_option = st.selectbox(label='Sort by', options=display_cols[1:], index=5) # default is power
    
    idx_all = []

    if name_option != '':
        idx_all.append(filter_by_1col(df, 'name', name_option, exact_flag=False)) 

    if star_option != 'None':
        idx_all.append(filter_by_1col_num(df, 'star', star_option, oper_flag="eq"))    

    if speed_option != 'None':
        idx_all.append(filter_by_1col(df, 'speed', speed_option, exact_flag=True))    

    if color_option != 'None':
        idx_all.append(filter_by_1col(df, 'color', color_option, exact_flag=False))    

    if class_option != 'None':
        idx_all.append(filter_by_1col(df, 'class', class_option, exact_flag=False))    

    if source_option != 'None':
        idx_all.append(filter_by_1col(df, 'source', source_option, exact_flag=False))    

    if defense_option != "0":
        defense_option = int(defense_option)
        idx_all.append(filter_by_1col_num(df, 'defense', defense_option, oper_flag="ge"))   

    if attack_option != "0":
        attack_option = int(attack_option)
        idx_all.append(filter_by_1col_num(df, 'attack', attack_option, oper_flag="ge"))   

    if health_option != "0":
        health_option = int(health_option)
        idx_all.append(filter_by_1col_num(df, 'health', health_option, oper_flag="ge"))   

    if special_type_option  != '':
        idx_all.append(filter_by_1col(df, 'types', special_type_option, exact_flag=False))    

    if special_text_option != '':
        idx_all.append(filter_by_1col(df, 'effects', special_text_option, exact_flag=False))    
    
    #########################################
    st.header(f'Updated: Oct 23, 2023 -- Total heroes = {len(df)}')

    df2 = df[np.all(idx_all,axis=0)]

    display_heroes_from_df(df2.sort_values(sort_option, ascending=False))
#########################################
## Program 2
else:
    st.write(" Work in progress")
