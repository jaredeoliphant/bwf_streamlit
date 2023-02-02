import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from pandas.api.types import CategoricalDtype

@st.cache
def get_initial_data():
    df = pd.read_excel('InitialSurvey.xlsx').iloc[:-1,:]
    return tweak_bwf_initial(df)

@st.cache
def get_followup_data():
    df = pd.read_excel('FollowUpSurvey.xlsx').iloc[:-1,:]
    return tweak_bwf_followup(df)

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


def remove_test_records(df):
    # st.write(f'removed household names:')
    # st.write(df[df.hh_name.str.contains('test',case=False).fillna(False)].hh_name.unique())
    return df[~df.hh_name.str.contains('test',case=False).fillna(False)]


def tweak_bwf_initial(df):
    return (
        df
        .rename(columns=initial_rename_func())
        .assign(hh_name = lambda df_: df_.hh_name.str.strip(),   # name and phone are the only true free response questions
                hh_phone = lambda df_: df_.hh_phone.str.strip(),
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

def demographics(initial):
    """Generate and st.write demographic data from initial survey data"""
    st.write('Systematic Survey Sample:\n')

    st.write(f'Number of Survey Entries (Families): {initial.id.size}')
    st.write(f'Number of Unique Household Names: {initial.hh_name.nunique()}')
    total_pop = initial.hh_size.sum()
    st.write(f'Total Survey Population: {total_pop:n}')
    st.write(f'Average family size: {initial.hh_size.mean():.2f}')

    children5 = initial.loc[:,'males_0_1_yr':'females_1_5_yr'].sum().sum()
    st.write(f'{100*children5/total_pop:.2f}% less than 5 yrs')
    children12 = initial.loc[:,'males_0_1_yr':'females_5_12_yr'].sum().sum()
    st.write(f'{100*children12/total_pop:.2f}% less than 12 yrs')
    children18 = initial.loc[:,'males_0_1_yr':'females_12_17_yr'].sum().sum()
    st.write(f'{100*children18/total_pop:.2f}% less than 18 yrs')

    # st.write(initial.child_fatalities.value_counts())

    st.write('\nSources of Drinking Water')
    st.write((initial
           .drinking_water_source
           .value_counts(dropna=False,normalize=True)
           .mul(100)
           .round(2)
          ))

    st.write('\nSources of Non-Drinking Water')
    st.write((initial
           .nondrinking_water_source
           .value_counts(dropna=False,normalize=True)
           .mul(100)
           .round(2)
          ))

    st.write('\nWater Collection Frequency')
    water_mapping = {
        '2 or more times per day':'Two or More Times Daily',
        'Once daily':'Once Daily',
        'Every other day':'Every Other Day',
        'Every 3rd day':'Every Third Day',
        'Weekly':'Weekly'
    }
    water_cat = CategoricalDtype(categories=['Two or More Times Daily','Once Daily',
                                          'Every Other Day','Every Third Day','Weekly'], ordered=True)
    water_collection_freq = (initial
            .freq_fetch_water
            .astype('category')
            .map(water_mapping)
            .astype(water_cat)
            .value_counts(dropna=False,normalize=True,sort=False)
            .mul(100)
            .round(2)
          )
    st.write(water_collection_freq)
    fig,ax = plt.subplots()
    water_collection_freq.plot.bar(ax=ax,ylabel='% of Respondents',title='Water Collection Frequency').grid(axis='y')
    ax.set_xticklabels(ax.get_xticklabels(), rotation = 45, ha='right')
    st.pyplot(fig)

    st.write('\nWater Collection Time (Minutes)')
    water_collection_time = (pd.cut(initial.minutes_fetch_water,
                                    [0,10,15,20,30,45,initial.minutes_fetch_water.max()],
                                    right=True,include_lowest=True)
                                    .value_counts(normalize=True,sort=False)
                                    .mul(100)
                                    .round(2)
                                    )
    st.write(water_collection_time)
    fig,ax = plt.subplots()
    (water_collection_time
    .plot.bar(ax=ax,ylabel='% of Respondents',title='Water Collection Time (Minutes)')
    )
    ax.grid(axis='y')
    newlabels = [tck.get_text() for tck in ax.get_xticklabels()]
    newlabels[0] = '[0.0,10.0]'
    ax.set_xticklabels(newlabels, rotation = 45, ha = 'right')
    st.pyplot(fig)

    st.write('\nWho Collects Water')
    who_collects = (initial.
           who_fetch_water
           .value_counts(dropna=False,normalize=True)
           .mul(100)
           .round(2)
          )
    st.write(who_collects)
    fig,ax = plt.subplots()
    who_collects.plot.bar(ax=ax,ylabel='% of Respondents',title='Who Collects Water?').grid(axis='y')
    ax.set_xticklabels(ax.get_xticklabels(), rotation = 45, ha='right')
    st.pyplot(fig)


    st.write('\nWater Container')
    st.write((initial
           .fetch_water_container
           .value_counts(dropna=False,normalize=True)
           .mul(100)
           .round(2)
          ))

    st.write('\n\nHead of Household Demographics')
    st.write('\nAverage Age')
    st.write(f'{initial.hh_age.mean():.1f}')

    st.write('\nSex')
    st.write((initial
           .hh_sex
           .value_counts(dropna=False,normalize=True)
           .mul(100)
           .round(2)
          ))
    st.write('\nMarital Status')
    marital_status = (initial
           .hh_marital
           .value_counts(dropna=False,normalize=True)
           .mul(100)
           .round(2)
          )
    st.write(marital_status)
    fig,ax = plt.subplots()
    marital_status.plot.bar(ax=ax,ylabel='% of Respondents',title='Head of Household Marital Status').grid(axis='y')
    ax.set_xticklabels(ax.get_xticklabels(), rotation = 45, ha='right')
    st.pyplot(fig)


    st.write('\nEducation')
    ed_mapping = {
        'Completed Jr. High school':'Completed Jr. High',
        'Some Jr. High school':'Completed Primary School',
        'Some primary school':'Some or No Primary School',
        'No formal education':'Some or No Primary School',
        'Completed primary school':'Completed Primary School',
        'Some Sr. High School':'Completed Jr. High',
        'Completed Sr. High School':'Completed High School',
        'Some education beyond High School':'Some Education Beyond High School'
    }
    ed_cat = CategoricalDtype(categories=['Some or No Primary School','Completed Primary School',
                                          'Completed Jr. High','Completed High School',
                                          'Some Education Beyond High School'], ordered=True)
    education = (initial
           .hh_education
           .astype('category')
           .map(ed_mapping)
           .astype(ed_cat)
           .value_counts(dropna=False,normalize=True,sort=False)
           .mul(100)
           .round(2)
          )
    st.write(education)
    fig,ax = plt.subplots()
    education.plot.bar(ax=ax,ylabel='% of Respondents',title='Head of Household Education Level').grid(axis='y')
    ax.set_xticklabels(ax.get_xticklabels(), rotation = 45, ha='right')
    st.pyplot(fig)

    st.write('\nOccupation')
    occ_mapping = {
        'Farmer':'Farmer',
        'Trader':'Trader',
        'Other':'Other/None',
        'None':'Other/None',
        'civil servant (works for government)':'Civil Servant/Teacher',
        'Teacher':'Civil Servant/Teacher'
    }
    occupation = (initial
       .hh_occupation
       .astype('category')
       .map(occ_mapping)
       .value_counts(dropna=False,normalize=True)
       .mul(100)
       .round(2)
      )
    st.write(occupation)
    fig,ax = plt.subplots()
    occupation.plot.bar(ax=ax,ylabel='% of Respondents',title='Head of Household Occupation').grid(axis='y')
    ax.set_xticklabels(ax.get_xticklabels(), rotation = 45, ha='right')
    st.pyplot(fig)


df_initial = get_initial_data()
df_followup = get_followup_data()
commuity_selection_options = ['Sankebunase project (Sankebunase, Nkurakan, Amonom, Mampong, Wekpeti)',
                                'Ekorso project (Ekorso, Adkwadum, Akwaduuso)'] \
                                + list(df_initial.community.dropna().unique())
communities = st.multiselect(
    "Choose communities", commuity_selection_options)
if not communities:
    st.error("Please select at least one community.")
else:
    if commuity_selection_options[0] in communities:
        group_communities = ['Sankebunase (Nkurakan/Amonon)', 'Sankubenase', 'Nkurakan', 'Amonom', 'Mampong', 'Wekpeti/Abresu']
        communities.remove(commuity_selection_options[0])
        communities += group_communities
    if commuity_selection_options[1] in communities:
        group_communities = ['Ekorso', 'Akwadum','Akwadusu']
        communities.remove(commuity_selection_options[1])
        communities += group_communities
    communities = list(set(communities))
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

    st.write('---')
    st.write('### Demographic summary')
    demographics(data_initial)
