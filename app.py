import pandas as pd
import numpy as np
import streamlit as st

# import glob
# import yaml
from pathlib import Path
from collections import defaultdict

import os, time
import random
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
                try:
                    flag = check_valid_value(query, s2, exact_flag=exact_flag)
                    if flag: break
                except Exception as e: # s can be ['None']
                    flag=False
        else:
            flag = check_valid_value(query, s, exact_flag=exact_flag)

        
        ok_flag_list.append(flag)
    
    assert len(ok_flag_list) == len(df)
    return np.array(ok_flag_list)

def display_image(url, scale=0.5, enable_flag = False):
    from urllib.request import urlopen
    from PIL import Image

    enable_flag = False if display_img_flag != 'Yes' else True # adhoc code, should send this variable properly
    
    if enable_flag: # default to False as imgur server seems to refuse our request and cause permanent error
        # image = Image.open(urlopen(url))
        # st.image(image.resize(( int(image.width * scale), int(image.height * scale))))

        
        #The problem occur because imgur remove file extension e.g. 'jpg', 
        #so either url is wrong with urlopen or Image.open does not know image type if use requests/urllib3
        st.image(url)

def display_heroes_from_df(df,display_cols=display_cols, show_df=True):
    vtob = "is" if len(df)<=1 else "are"
    st.write(f'There {vtob} {len(df)} heroes in the filtered list')

    if show_df:
        st.dataframe(df[display_cols],
                 column_config={
                         "image": st.column_config.ImageColumn("Avatar", help="",
                                                              # width="medium", # width alone doesnt matter and there is no height option
                                                              )},
                 use_container_width=True,
                 # height=128, # this is height of the whold df, not on each line
                 hide_index=True)

    for i in range(len(df)):
        st.write(" ")
        st.write(f"#########################################")
        st.write(" ")
        
        url = df['image'].values[i]
        display_image(url)
        st.write(f"***{df['name'].values[i]}*** - {df['speed'].values[i]} - {df['class'].values[i]}")
        st.write(f'Attack:{df["attack"].values[i]} -- Defence:{df["defense"].values[i]} -- Health:{df["health"].values[i]}')
        st.write(f"***{df['skill'].values[i]}***" )
        st.write("\n**Special Skills**")
        st.write(df['effects'].values[i])

        if df['passives'].values[i] != 0 and df['passives'].values[i] != '0':
            st.write("\n**Passives**")
            st.write(df['passives'].values[i])

        if df['family_bonus'].values[i] != 0 and df['passives'].values[i] != '0':
            st.write("\n**Family Bonus**")
            st.write(df['family_bonus'].values[i])

#########################################
## Helper function for LB/CB stat analysis
def return_costume_list(df0, hero_name):
    assert hero_name in df0.name.values

    if hero_name[-2:] == "C3":
        return ['None', 'CB1', 'CB2', 'CB3']
    if hero_name[-2:] == "C2":
        hero_name2 = hero_name[:-1] + "3"
        if hero_name2 in df0.name.values: # if this hero has C3
            return ['None', 'CB1', 'CB2', 'CB3']
        else:
            return ['None', 'CB1', 'CB2']
    elif hero_name[-2:] == " C":
        hero_name2 = hero_name + "2"
        hero_name3 = hero_name + "3"
        if hero_name3 in df0.name.values: # if this hero has C2
            return ['None', 'CB1', 'CB2', 'CB3']
        elif hero_name2 in df0.name.values: # if this hero has C2
            return ['None', 'CB1', 'CB2']
        else:
            return ['None', 'CB1']
    else:
        hero_name1 = hero_name + " C"
        hero_name2 = hero_name + " C2"
        hero_name3 = hero_name + " C3"
        if hero_name3 in df0.name.values: # if this hero has C2
            return ['None', 'CB1', 'CB2', 'CB3']
        elif hero_name2 in df0.name.values: # if this hero has C2
            return ['None', 'CB1', 'CB2']
        elif hero_name1 in df0.name.values: # if this hero has C2
            return ['None', 'CB1']
        else:
            return ['None']

def get_prefix(lb_choice="None", costume_choice="None"):
    prefix_1 = "Max level"

    if lb_choice != 'None':
        prefix_1 = "Limit Break"
    
    prefix_2 = ""
    if costume_choice != "None":
        prefix_2 = f" {costume_choice}" # CB1 or CB2

    prefix_3 = ":"
    if lb_choice == 'LB1':
        prefix_3 = " #1:"
    elif lb_choice == 'LB2':
        prefix_3 = " #2:"

    return prefix_1 + prefix_2 + prefix_3

def return_hero_stat(df0, hero_name, lb_choice="None", costume_choice="None"):
    assert hero_name in df0.name.values
    
    display_cols_0 = ['image', 'name', 'color', 'star', 'class', 'speed',]
    display_cols_1 = [] # ['power', 'attack', 'defense', 'health', ] --> to be select base one LB/Costume choice
    display_cols_2 = ['AetherPower', 'source', 'family', 'types', 'skill', 'effects', 'passives', 'family_bonus'] # 'Aether Power' name is changed in June 2024

    prefix = get_prefix(lb_choice, costume_choice)

    display_cols_1.append(f'{prefix} Power')
    display_cols_1.append(f'{prefix} Attack')
    display_cols_1.append(f'{prefix} Defense')
    display_cols_1.append(f'{prefix} Health')
    
    display_cols_all = display_cols_0 + display_cols_1 + display_cols_2
    df_ret = df0[df0.name == hero_name][display_cols_all]

    df_ret = df_ret.rename(columns={f'{prefix} Power':'power',
                    f'{prefix} Attack':'attack',
                    f'{prefix} Defense':'defense',
                    f'{prefix} Health':'health'})
    return df_ret

    
def return_talent_choice(key="default_key"):
    talent_list = ['None', 'Sword+20', 'Shield+20', 'Health+20', 'Sword+25', 'Shield+25', 'Health+20 Shield+5','Sword+20 Shield+5','Shield+20 Sword+5']
    
    talent_choice = st.selectbox(label='Approx. Talent (stat are all cruded approximated. Visit heroplan.io for exact calculation.) :', 
                                 options=talent_list, 
                                 index=0, 
                                 key=key)
    
    talent_tp, talent_attack, talent_defense, talent_health = 0, 0, 0, 0
    if talent_choice == 'Sword+20':
        talent_tp, talent_attack, talent_defense, talent_health = 100, 150, 50, 100
    elif talent_choice == 'Shield+20':
        talent_tp, talent_attack, talent_defense, talent_health = 100, 50, 150, 100
    elif talent_choice == 'Health+20':
        talent_tp, talent_attack, talent_defense, talent_health = 100, 75, 75, 200
    if talent_choice == 'Sword+25':
        talent_tp, talent_attack, talent_defense, talent_health = 125, 300, 50, 200
    elif talent_choice == 'Shield+25':
        talent_tp, talent_attack, talent_defense, talent_health = 125, 50, 330, 200
    elif talent_choice == 'Health+20 Shield+5': # choose shield-path on 5 master nodes
        talent_tp, talent_attack, talent_defense, talent_health = 125, 75, 255, 300
    elif talent_choice == 'Sword+20 Shield+5':
        talent_tp, talent_attack, talent_defense, talent_health = 125, 150, 230, 200
    elif talent_choice == 'Shield+20 Sword+5':
        talent_tp, talent_attack, talent_defense, talent_health = 125, 200, 150, 200
    return talent_tp, talent_attack, talent_defense, talent_health

def choose_hero(key="Hero1", default_index=0):
    name_choice = st.selectbox(label='Hero Name:', options=all_name_extra, index=default_index, key=key+"_name")
    costume_list = return_costume_list(df_extra, name_choice)
    costume_choice = st.selectbox(label='Costume:', options=costume_list, index=0, key=key+"_costume")
    lb_list = ['None', 'LB1', 'LB2']
    lb_choice = st.selectbox(label='Limit Break:', options=lb_list, index=0, key=key+"_lb")

    talent_tp, talent_attack, talent_defense, talent_health = return_talent_choice(key=key+"_talent")
        
    df_ret = return_hero_stat(df_extra, name_choice, lb_choice=lb_choice, costume_choice=costume_choice)
    df_ret.power.values[0] += talent_tp
    df_ret.attack.values[0] += talent_attack
    df_ret.defense.values[0] += talent_defense
    df_ret.health.values[0] += talent_health
        
    return df_ret

def write_short_description(df_hero):
    url = df_hero['image'].values[0]
    display_image(url)
    st.write(f'Power: {df_hero["power"].values[0]}')
    st.write(f'Attack: {df_hero["attack"].values[0]}')
    st.write(f'Defense: {df_hero["defense"].values[0]}')
    st.write(f'Health: {df_hero["health"].values[0]}')
    st.write(f'Speed: {df_hero["speed"].values[0]}')
    st.write(f'Class: {df_hero["class"].values[0]}')
    st.write(f'Types: {df_hero["types"].values[0]}')


def generate_hero_description(df_hero):
    txt =  f"""

{df_hero.name.values[0]} Description:
Element: {df_hero.color.values[0]}
Star: {df_hero.star.values[0]}
Power: {df_hero.power.values[0]}
Attack: {df_hero.attack.values[0]}
Defense: {df_hero.defense.values[0]}
Health: {df_hero.health.values[0]}
Speed: {df_hero.speed.values[0]}
Class: {df_hero['class'].values[0]}

Special Skills:
{df_hero['effects'].values[0]}
Passives:
{df_hero['passives'].values[0]}

"""

    return txt

def generate_end_prompt(df0, hero1, hero2, df1=None, df2=None):

    end_txt = """
Now please begin with
********************
# Head to Head Analysis
********************
"""

    txt =  f"""
{hero1} vs. {hero2}

"""
    if df1 is None:
        df1 = return_hero_stat(df0, hero1)
    if df2 is None:
        df2 = return_hero_stat(df0, hero2)
    txt_hero1 = generate_hero_description(df1)
    txt_hero2 = generate_hero_description(df2)

    txt += txt_hero1 + txt_hero2 + end_txt

    return txt

#########################################
## Load the main file (TODO: caching)=
st.set_page_config(layout="wide")
st.header(f'HeroPlan Explorer')
st.write('Powered by Heroplan.io : Thanks E&P community for continually update hero data.')

df = pd.read_csv('heroes_ep.csv')
st.write(f'### Updated: {time.ctime(os.path.getmtime("heroes_ep.csv"))} -- Total heroes in HeroPlan database = {len(df)}')

df_extra = pd.read_csv("heroes_ep_extra.csv")
all_name_extra = sorted(list(df_extra['name'].values))

#########################################

class_values = ['None'] + list(df['class'].unique()) 
star_values = ['None'] + list(df['star'].unique())
color_values = ['None'] + list(df['color'].unique())
speed_values = ['None'] + list(df['speed'].unique())
family_values = ['None'] + list(df['family'].unique())
source_values = ['None'] + list(df['source'].unique()) # Contain lot of typo bugs from HeroPlan

#########################################
## Select Main Program

from streamlit_option_menu import option_menu

with st.sidebar:
    genre = option_menu("Choose how to explore heroes",
            ["Heroes Explorer", 
             "Team Simulation", 
             "Hero Comparison by Gemini-Flash-2.0 AI",
             # "Hero Comparison by Gemini AI (text)", # Obsolete
             "LB CB Hero Stat"],
                icons=['clipboard-data', 'microsoft-teams','code', 'cast'], 
            default_index=0
    )
    
    # genre = st.selectbox(label="Choose how to explore heroes",
    #         options=["Heroes Explorer", 
    #          "Team Simulation", 
    #          "Hero Comparison by Gemini AI",
    #          "LB CB Hero Stat"],
    #          index=0
    # )
    
    # genre = st.radio(
    # "Choose how to explore heroes",
    # ["Heroes Explorer", 
    #  "Team Simulation", 
    #  "Hero Comparison by Gemini AI",
    #  "LB CB Hero Stat"],
    # captions = ["Filter only heroes with certain properties", "Co-powered by Elioty33's DataVault"])

    display_img_flag = "Yes"
    # display_img_flag = st.radio(
    #     "Display Avatar in Description",
    #     ["Yes", "No"],
    #     captions = ["Default", "If problem occur, set to 'no'"]
    # )
    
#########################################
## Program 1
if genre == 'Heroes Explorer':
    
    col1, col2 = st.columns(2)
    with col1:
        st.header("Standard Filters:")
        st.markdown("*Tips:* filter costume by typing **' C'** **'C2'** or **'C3'** in the Name box.")
        st.markdown("*SpecialSkill Category:* try **defense debuff**, **hit all**. See **types** column to learn more on SpecialSkill Category")
        with st.expander("Filter Options"):
            name_option = st.text_input(label="Name:", value="")
            star_option = st.selectbox(label='Star:', options=star_values, index=0)
            color_option = st.selectbox(label='Color:', options=color_values, index=0)
            speed_option = st.selectbox(label='Speed:', options=speed_values, index=0)
            class_option = st.selectbox(label='Class:', options=class_values, index=0)
            family_option = st.selectbox(label='Family:', options=family_values, index=0)
            source_option = st.selectbox(label='Origin:', options=source_values, index=0)
    
            special_type_option = st.text_input(label="SpecialSkill Category", value="Hit 3")
            special_text_option = st.text_input(label="SpecialSkill Text", value="Dispel")
            passive_text_option = st.text_input(label="Passive Text", value="")
    with col2:
        st.header("Stat Filters")
        st.markdown("*Tips:* put the **minimum** att/def/hp stat you want to filter heroes, e.g. put 1100 in **Power**")
        with st.expander("Stat Options"):   
            power_option = st.text_input(label="Power:", value="0")
            defense_option = st.text_input(label="Defense:", value="0")
            attack_option = st.text_input(label="Attack:", value="0")
            health_option = st.text_input(label="Health:", value="0")

            max_percent_option = st.text_input(label="Max % in Special Skill:", value="0")
            
            total_dot_option = st.text_input(label="Total DoT Damage:", value="0")
            dot_per_turn_option = st.text_input(label="DoT Damage Per Turn:", value="0")
    # with col3:
    #     st.header("Sorted By")
    #     st.write("Tips: you can also directly click at the column name to sort")
    #     sort_option = st.selectbox(label='Sort by', options=display_cols[1:], index=5) # default is power
    sort_option = "power"
    
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

    if family_option != 'None':
        idx_all.append(filter_by_1col(df, 'family', family_option, exact_flag=False))

    if power_option != "0":
        power_option = int(power_option)
        idx_all.append(filter_by_1col_num(df, 'power', power_option, oper_flag="ge"))
    
    if defense_option != "0":
        defense_option = int(defense_option)
        idx_all.append(filter_by_1col_num(df, 'defense', defense_option, oper_flag="ge"))   

    if attack_option != "0":
        attack_option = int(attack_option)
        idx_all.append(filter_by_1col_num(df, 'attack', attack_option, oper_flag="ge"))   

    if health_option != "0":
        health_option = int(health_option)
        idx_all.append(filter_by_1col_num(df, 'health', health_option, oper_flag="ge"))

    if total_dot_option != "0":
        total_dot_option = int(total_dot_option)
        idx_all.append(filter_by_1col_num(df, 'total_dot_damage', total_dot_option, oper_flag="ge"))

    if dot_per_turn_option != "0":
        dot_per_turn_option = int(dot_per_turn_option)
        idx_all.append(filter_by_1col_num(df, 'dot_damage_per_turn', dot_per_turn_option, oper_flag="ge"))

    if max_percent_option != "0":
        max_percent_option = int(max_percent_option)
        idx_all.append(filter_by_1col_num(df, 'max_special_percent', max_percent_option, oper_flag="ge"))
    
    if special_type_option  != '':
        idx_all.append(filter_by_1col(df, 'types', special_type_option, exact_flag=False))    

    if special_text_option != '':
        idx_all.append(filter_by_1col(df, 'effects', special_text_option, exact_flag=False))    

    if passive_text_option != '':
        idx_all.append(filter_by_1col(df, 'passives', passive_text_option, exact_flag=False))    
    
    #########################################

    df2 = df[np.all(idx_all,axis=0)]

    display_heroes_from_df(df2.sort_values(sort_option, ascending=False))
#########################################
## Program 2 "Team Simulation"
elif genre == "Team Simulation":
    note_flag = st.checkbox("Displayt Notepad", value=False)
    
    nheroes_choice_list = [2,3,4,5]
    nheroes_choice = st.selectbox(label='Number of Heroes:', options=nheroes_choice_list, index=len(nheroes_choice_list)-1)

    additional_col = 0
    if note_flag:
        additional_col = 1
        
    col_list = st.columns(nheroes_choice+additional_col)
    df_hero_list = []
    total_power = 0
    for ii in range(nheroes_choice):
        with col_list[ii]:
            df_hero_list.append(choose_hero(key=f"Hero{ii+1}", default_index=ii)) # 'key' in st.selectbox to differentiate widgets
            write_short_description(df_hero_list[-1])
        total_power += df_hero_list[ii]['power'].values[0]

    if note_flag:
        with col_list[-1]:
            txt = st.text_area("Write your note about team synergy", max_chars=1000, height = 480)

    df_hero_all5 = pd.concat(df_hero_list)
        
    st.write(f'======================')
    st.write(f'### Total power = {total_power}')
    st.write(f'======================')
    
    display_heroes_from_df(df_hero_all5, display_cols=df_hero_all5.columns[:-2], show_df=True) # display all except special-skill text

# 
#########################################
## Program 4.1 "Hero Comparison by Gemini AI (table-style)"
elif genre == "Hero Comparison by Gemini-Flash-2.0 AI":
    nheroes_choice = 2

    ############
    # showcase

    showcase_choice = st.radio(
    "Choose showcase example",
    ["Option 1", 
     "Option 2", 
     "Option 3",
    ],
    captions = ["Eliane vs. Black Caesar", "Eliane vs. Azlar C3 (you have to manually set up his CB)", "Willow vs. Bennu C"])
    if showcase_choice == "Option 1":
        hero1_name = "Eliane"
        hero2_name = "Black Caesar"
    elif showcase_choice == "Option 2":
        hero1_name = "Eliane"
        hero2_name = "Azlar C3"
    else:
        hero1_name = "Willow"
        hero2_name = "Bennu C"
    
    hero_showcase = []
    # list cannot use numpy index
    h1 = int(np.where(np.array(all_name_extra) == hero1_name)[0][0])
    h2 = int(np.where(np.array(all_name_extra) == hero2_name)[0][0])
    hero_showcase.append(h1)
    hero_showcase.append(h2)
    assert type(hero_showcase[0]) is int and type(hero_showcase[1]) is int
    
    col_list = st.columns(nheroes_choice)
    df_hero_list = []
    total_power = 0
    for ii in range(nheroes_choice):
        with col_list[ii]:
            df_hero_list.append(choose_hero(key=f"Hero{ii+1}", default_index=hero_showcase[ii])) # 'key' in st.selectbox to differentiate widgets
            write_short_description(df_hero_list[-1])
        total_power += df_hero_list[ii]['power'].values[0]

    df_hero_all5 = pd.concat(df_hero_list)

    ### BEGIN Gemini API
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    import google.generativeai as genai
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')

    with open('prompts/hero_compare_prompt_table_style.txt', 'r') as f:
        prompt = f.read()

    hero1 = df_hero_list[0]['name'].values[0]
    hero2 = df_hero_list[1]['name'].values[0]
    end_prompt = generate_end_prompt(df_extra, hero1, hero2, df1=df_hero_list[0] , df2=df_hero_list[1] )

    current_prompt = prompt+end_prompt
    response = model.generate_content(current_prompt)
    st.write(response.text)

    display_heroes_from_df(df_hero_all5, display_cols=df_hero_all5.columns[:-2], show_df=True) # display all except special-skill text

#########################################
## Program 4.2 "Hero Comparison by Gemini AI (old-style text blah blah analysis)!!"
elif genre == "Hero Comparison by Gemini AI (text)":
    story_flag = st.checkbox("Imagine Exciting (or boring) Fighting Between The Two", value=False)
    nheroes_choice = 2

    #################
    # FUN Idea
    # COULDN'T do this even on init, since when user specified, df_extra must be used instead of df_init_rand
    # rand_power_threshold = 850 # will randomly show heroes which power above threshold
    # idx = filter_by_1col_num(df_extra, 'power', rand_power_threshold, oper_flag="ge")
    # df_init_rand = df_extra[idx]

    ############
    # showcase
    hero_showcase = []
    # list cannot use numpy index
    h1 = int(np.where(np.array(all_name_extra) == 'Voidstar')[0][0])
    h2 = int(np.where(np.array(all_name_extra) == 'Rochefort')[0][0])
    hero_showcase.append(h1)
    hero_showcase.append(h2)
    assert type(hero_showcase[0]) is int and type(hero_showcase[1]) is int
    
    col_list = st.columns(nheroes_choice)
    df_hero_list = []
    total_power = 0
    for ii in range(nheroes_choice):
        rand_ii = random.randint(0, len(df_extra))
        with col_list[ii]:
            # UNFORTUNATELY, couldn't use rand_ii as default_index as program always refresh
            df_hero_list.append(choose_hero(key=f"Hero{ii+1}", default_index=hero_showcase[ii])) # 'key' in st.selectbox to differentiate widgets
            write_short_description(df_hero_list[-1])
        total_power += df_hero_list[ii]['power'].values[0]

    df_hero_all5 = pd.concat(df_hero_list)

    ### BEGIN Gemini API
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    import google.generativeai as genai
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')

    with open('prompts/hero_compare_prompt.txt', 'r') as f:
        prompt = f.read()

    hero1 = df_hero_list[0]['name'].values[0]
    hero2 = df_hero_list[1]['name'].values[0]
    end_prompt = generate_end_prompt(df_extra, hero1, hero2, df1=df_hero_list[0] , df2=df_hero_list[1] )

    current_prompt = prompt+end_prompt
    response = model.generate_content(current_prompt)
    st.write(response.text)

    display_heroes_from_df(df_hero_all5, display_cols=df_hero_all5.columns[:-2], show_df=True) # display all except special-skill text

    ### Generate FUN story
    if story_flag:
        txt_hero1 = generate_hero_description(df_hero_list[0])
        txt_hero2 = generate_hero_description(df_hero_list[1])

        
        
        story_prompt = f"Generate a fun, fighting story of two heroes based on the following {hero1} vs. {hero2} information:\n\n" + txt_hero1 + txt_hero2 + response.text
        story_response = model.generate_content(story_prompt)
        st.write("## FIGHTING STORY")
        st.write(story_response.text)

#########################################
## Program 3 "Individual Stat"
else:
    
    
    st.header("Analyze Hero LB/CB Stat (without Emblem)")
    st.write("HeroPlan and DataVault are combined here. Thanks ***@Elioty33*** for his DataVault contribution")
    st.write(f"Currently, there are {len(df_extra)} heroes having both data on HeroPlan and DataVault.")
    st.write(f"We don't have emblem calculator here, you can go heroplan.io to do the job.")
    st.write(f"***Heuristically*** Choose Sword-path can increase att 100-150, def 50-100, hp ~100 (reverse att-def for shield path)")
    st.write(f"Choose HP-path can increase att 50-100, def 50-100, hp ~200")
    

    name_values = sorted(list(df_extra['name'].values))
    name_choice = st.selectbox(label='Hero Name:', options=name_values, index=0)

    costume_list = return_costume_list(df_extra, name_choice)
    costume_choice = st.selectbox(label='Costume:', options=costume_list, index=0)
    
    lb_list = ['None', 'LB1', 'LB2']
    lb_choice = st.selectbox(label='Limit Break:', options=lb_list, index=0)
        
    talent_tp, talent_attack, talent_defense, talent_health = return_talent_choice()
    df_ret = return_hero_stat(df_extra, name_choice, lb_choice=lb_choice, costume_choice=costume_choice)
    
    df_ret.power.values[0] += talent_tp
    df_ret.attack.values[0] += talent_attack
    df_ret.defense.values[0] += talent_defense
    df_ret.health.values[0] += talent_health
    
    display_heroes_from_df(df_ret,display_cols=df_ret.columns[:-2]) # display all except special-skill text
