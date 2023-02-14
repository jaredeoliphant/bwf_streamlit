import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from pandas.api.types import CategoricalDtype
from PIL import Image
import jwt
import requests


@st.cache(ttl=3600) #1 hour
def get_api_token() -> str:
    server_name = os.environ['API_SERVER_URL']
    cert_key = os.environ['CERT_NAME']
    encoded = os.environ['ENCODED_CERT']
    resp = requests.get(
        f"{server_name}/auth",
        headers={
            'mykey': cert_key,
            'test': encoded,
        }
    )
    if resp.status_code != 200:
        st.error(f"status_code={resp.status_code}, {data['msg']}")
        return None

    data = resp.json()
    return data['access_token']


def decrypt_api_response(encryted_data: str) -> pd.DataFrame:
    server_public_key = os.environ['PUBLIC_KEY']
    query_results = jwt.decode(encryted_data, server_public_key, ["RS256"])
    data = query_results["data"]
    return pd.DataFrame(data)



def query_api(token: str, query_data: dict, table: str) -> pd.DataFrame:
    server_name = os.environ['API_SERVER_URL']
    server_public_key = os.environ['PUBLIC_KEY']
    resp = requests.post(
        f"{server_name}/query/{table}",
        data=query_data,
        headers={
            "Authorization": f"Bearer {token}",
        }
    )

    if resp.status_code != 200:
        st.error(f"status_code={resp.status_code}, {resp.json()}")
        return False
        # query data will be encrypted with server cert
    query_results = resp.json()
    # load server public cert
    # server_public_key = open('certs/server/2023-02-10.pub', 'rb').read()
    # decrypt query results with server public cert
    return decrypt_api_response(query_results)


# table names
# CommunityWater
# CommunityWaterTest
# FollowUpSurvey
# HealthCheckSurvey
# HouseholdAttendingMeeting
# HouseholdWaterTest
# InitialSurvey
# Meeting
# SWEMonthlyClinicSummary
# SWEMonthlySchoolSummary
# SWEMonthlySummary
# SWEMonthlyTotalSummary
# Volunteer
# VolunteerHousehold
# VolunteerHouseholdWaterTest
# VolunteerMonthlySummary
# VolunteerMonthlyTotalSummary

@st.cache(ttl=3600*24) # 24 hrs
def get_initial_data():
    query_data = {
            "query": str({
                "$and": [
                    {"Country": "Ghana"},
                    {"Completed": 1},
                    {"disabled": {"$ne": True}},
                ]
            }),
            "extra": str({
                "sort": [
                    ("date", 1)
                ]
            }),
        }
    # df = pd.read_excel('InitialSurvey_anon.xlsx')#.iloc[:-1,:]
    token = get_api_token()
    table = 'InitialSurvey'
    df = query_api(token, query_data, table)
    return df

@st.cache(ttl=3600*24) # 24 hrs
def get_followup_data():
    query_data = {
            "query": str({
                "$and": [
                    {"Country": "Ghana"},
                    {"Completed": 1},
                    {"disabled": {"$ne": True}},
                ]
            }),
            "extra": str({
                "sort": [
                    ("date", 1)
                ]
            }),
        }
    # df = pd.read_excel('InitialSurvey_anon.xlsx')#.iloc[:-1,:]
    token = get_api_token()
    table = 'FollowUpSurvey'
    df = query_api(token, query_data, table)
    return df

@st.cache(ttl=3600*24) # 24 hrs
def get_communitywater_data():
    query_data = {
            "query": str({
                "$and": [
                    {"Country": "Ghana"},
                    {"Completed": 1},
                    {"disabled": {"$ne": True}},
                ]
            }),
            "extra": str({
                "sort": [
                    ("date", 1)
                ]
            }),
        }
    # df = pd.read_excel('InitialSurvey_anon.xlsx')#.iloc[:-1,:]
    token = get_api_token()
    table = 'CommunityWaterTest'
    # table = 'CommunityWater'
    df = query_api(token, query_data, table)
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
    return df.query('Community.isin(@communities).values')

def weekday_graph(data):
    mapdict = {'0':'Mon','1':'Tues','2':'Wed','3':'Thur','4':'Fr','5':'Sat','6':'Sun'}
    fig, ax = plt.subplots()
    datedata = pd.to_datetime(data.date)
    datedata.dt.day_of_week.value_counts().sort_index().plot.bar(ylabel='Initial Surveys Conducted',title='Day of Week Initial Survey was conducted',ax=ax)
    newlabels = [mapdict[tck.get_text()] for tck in ax.get_xticklabels()]
    ax.set_xticklabels(newlabels)
    ax.grid(axis='y')
    st.pyplot(fig)

def date_graph(data_i,data_f):
    data_i = data_i.assign(date = pd.to_datetime(data_i.date))
    data_f = data_f.assign(date = pd.to_datetime(data_f.date))
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
                                    + list(df_initial.Community.dropna().unique())
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
        
        st.write('### Initial Survey Data',data_initial.drop(columns=['HeadHouseholdPhoneNumber','Namebwe']))

        st.write('---')
        st.write('### Follow up Survey Data',data_followup.drop(columns=['Namebwe']))
        date_graph(data_initial,data_followup)

        weekday_graph(data_initial)

        st.write('---')
        # st.write('### Number of Surveys conducted per Safe Water Educator',data_initial.Namebwe.value_counts())

        dup_name = data_initial.HeadHouseholdName.value_counts().loc[lambda x: x > 1]
        if dup_name.any():
            st.write('---')
            st.write('#### These household names are duplicated in this dataset',dup_name)
        else:
            st.write('---')
            st.write('#### There are no duplicate household names in this dataset')


if __name__ == '__main__':
    main()
