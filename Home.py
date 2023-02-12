import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from pandas.api.types import CategoricalDtype
from PIL import Image

@st.cache
def get_initial_data():
    df = pd.read_excel('InitialSurvey_anon.xlsx')#.iloc[:-1,:]
    return tweak_bwf_initial(df)

@st.cache
def get_followup_data():
    df = pd.read_excel('FollowUpSurvey_anon.xlsx')#.iloc[:-1,:]
    return tweak_bwf_followup(df)

@st.cache
def get_communitywater_data():
    df = pd.read_excel('CommunityWaterTest_anon.xlsx')#.iloc[:-1,:]
    return df

@st.cache
def followup_rename_func():
    followup_mapping = pd.read_csv('followup_questions_mapping.csv')
    followup_rename = followup_mapping.set_index('0').to_dict()['1']
    return followup_rename

@st.cache
def initial_rename_func():
    initial_mapping = pd.read_csv('initial_questions_mapping.csv')
    initial_rename = initial_mapping.set_index('0').to_dict()['1']
    return initial_rename

def add_since_earliest(df):
    return (df.assign(since_earliest = lambda df_:
                      df_.date - df_.groupby(by='a')
                                    .date
                                    .transform(min)
                     )
           )

def remove_test_records(df):
    # st.write(f'removed household names:')
    # st.write(df[df.hh_name.str.contains('test',case=False).fillna(False)].hh_name.unique())
    return df[~df.hh_name.str.contains('test',case=False).fillna(False)]

def tweak_bwf_initial(df):
    return (
        df
        .rename(columns=initial_rename_func())
        .assign(hh_name = lambda df_: df_.hh_name.str.strip(),   # name and phone are the only true free response questions
                # hh_phone = lambda df_: df_.hh_phone.str.strip(),
                SWE_name = lambda df_: df_.SWE_name.str.strip()
               )
        .query('country != "Test Country" and community != "Test Village"')
        .pipe(remove_test_records)
        .astype({'completed':'bool'})
        .astype({a:'category' for a in ['hh_sex','hh_marital','hh_occupation','hh_education','interviewee','freq_fetch_water','who_fetch_water','fetch_water_container','treat_water',
                                        'treat_water_method','treat_water_freq','treat_water_last_chlorine','chlorine_source','chlorine_difficulty','hh_retrieve_water_method',
                                        'hh_defecate','youngest_stool_dispose','wash_hands_24hr','wash_hands_24hr_when','wash_hands_method','children_hospital','ill_child_breastfeed',
                                        'child_hospital_outcome','yearly_health_change','yearly_hh_health_change']
                }
               )
        .astype({a:'int' for a in ['hh_age','males_0_1_yr','females_0_1_yr','males_1_5_yr','females_1_5_yr','males_5_12_yr','females_5_12_yr','males_12_17_yr','females_12_17_yr',
                                   'males_18_yr','females_18_yr','hh_size','minutes_fetch_water','chlorine_cost_weekly','two_weeks_school_children_diarrhea',
                                   'two_weeks_children_school_days', 'one_week_children_diarrhea','two_weeks_days_work_missed','two_weeks_days_hh_work_missed',
                                   'medical_cost_four_weeks_local']
                }
               )
        # .pipe(duplicate_names)
    )

def tweak_bwf_followup(df):
    return (
        df
        .rename(columns=followup_rename_func())
        .assign(hh_name = lambda df_: df_.hh_name.str.strip(),
                SWE_name = lambda df_: df_.SWE_name.str.strip()
               )
        .query('country != "Test Country" and community != "Test Village"')
        .pipe(remove_test_records)
        .astype({'completed':'bool'})
        .astype({a:'category' for a in ['interviewee','treat_water','treat_water_method','treat_water_freq','treat_water_last_chlorine','chlorine_source','chlorine_difficulty',
                                        'hh_retrieve_water_method','wash_hands_24hr_when','wash_hands_method','children_hospital','ill_child_breastfeed','child_hospital_outcome',
                                        'yearly_health_change','yearly_hh_health_change','level_of_benefit']
                }
               )
        .astype({a:'int' for a in ['chlorine_cost_weekly','two_weeks_school_children_diarrhea','two_weeks_children_school_days','one_week_children_diarrhea',
                                   'two_weeks_days_work_missed','two_weeks_days_hh_work_missed','medical_cost_four_weeks_local']
                }
               )
    )

def tweak_communitywater(df):
    return (
        df
        .rename(columns={'Country':'country','Community':'community','Completed':'completed'})
        .query('country != "Test Country" and community != "Test Village"')
        .astype({'completed':'bool'})
    )

def get_community(df,communities):
    return df.query('community.isin(@communities).values')

def weekday_graph(data):
    mapdict = {'0':'Mon','1':'Tues','2':'Wed','3':'Thur','4':'Fr','5':'Sat','6':'Sun'}
    fig, ax = plt.subplots()
    data.date.dt.day_of_week.value_counts().sort_index().plot.bar(ylabel='Initial Surveys Conducted',title='Day of Week Initial Survey was conducted',ax=ax)
    newlabels = [mapdict[tck.get_text()] for tck in ax.get_xticklabels()]
    ax.set_xticklabels(newlabels)
    ax.grid(axis='y')
    st.pyplot(fig)

def date_graph(data_i,data_f):
    weekly = data_f.groupby(pd.Grouper(key='date',freq='W')).id.count()
    fig,ax = plt.subplots()
    weekly.plot.area(ax=ax,title='Initial and Follow up survey date',label='Follow up')

    weekly = data_i.groupby(pd.Grouper(key='date',freq='W')).id.count()
    weekly.plot.area(ax=ax,label='Initial').grid(axis='y')
    ax.legend()
    st.pyplot(fig)


def main():
    image = Image.open('Bright-Water-Foundation-Logo-1.jpg')

    st.image(image)
    st.write("This application allows users to explore data from Bright Water Foundation's work in Africa.")

    df_initial = get_initial_data()
    df_followup = get_followup_data()
    commuity_selection_options = ['Sankebunase project (Sankebunase, Nkurakan, Amonom, Mampong, Wekpeti)',
                                    'Ekorso project (Ekorso, Akwadum, Akwadusu)'] \
                                    + list(df_initial.community.dropna().unique())
    if 'c_select' not in st.session_state:
        st.session_state.c_select = []
    communities = st.sidebar.multiselect(
        "Choose communities", commuity_selection_options,
        default = st.session_state.c_select)
    if not communities:
        st.sidebar.error("Please select at least one community.")
        st.session_state.c_select = []
    else:
        if commuity_selection_options[0] in communities:
            group_communities = ['Sankebunase (Nkurakan/Amonon)', 'Sankebunase', 'Nkurakan', 'Amonom', 'Mampong', 'Wekpeti/Abresu']
            communities.remove(commuity_selection_options[0])
            communities += group_communities
        if commuity_selection_options[1] in communities:
            group_communities = ['Ekorso', 'Akwadum','Akwadusu']
            communities.remove(commuity_selection_options[1])
            communities += group_communities
        communities = list(set(communities))
        st.session_state.c_select = communities
        st.write('### selected communities',communities)

        data_initial = get_community(df_initial,communities)
        data_followup = get_community(df_followup,communities)
        st.write('### Initial Survey Data',data_initial)
        st.write(f'''
            There are
            {data_initial.query('~completed').completed.count()}
            records that are marked as "incomplete",
            do you want to remove them?
            ''')
        remove_incomplete = st.checkbox(label='Remove incomplete records',value=True)
        if remove_incomplete:
            data_initial = data_initial.query('completed')
            st.write('### Initial Survey Data with removed incomplete records',data_initial)


        st.write('---')
        st.write('### Follow up Survey Data',data_followup)
        date_graph(data_initial,data_followup)

        split_date = st.date_input('Split Date Between 3 months and 6 months')
        st.write(split_date)

        weekday_graph(data_initial)

        st.write('---')
        st.write('### Number of Surveys conducted per Safe Water Educator',data_initial.SWE_name.value_counts())

        dup_name = data_initial.hh_name.value_counts().loc[lambda x: x > 1]
        if dup_name.any():
            st.write('---')
            st.write('#### These household names are duplicated in this dataset',dup_name)
        else:
            st.write('---')
            st.write('#### There are no duplicate household names in this dataset')


if __name__ == '__main__':
    main()
