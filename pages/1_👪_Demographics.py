import streamlit as st
from PIL import Image
from Home import get_initial_data, get_community
from pandas.api.types import CategoricalDtype
import matplotlib.pyplot as plt
import pandas as pd


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
    water_collection_bins = [0]
    for i in range(15):
        water_collection_bins.append(water_collection_bins[-1]+10)
        if water_collection_bins[-1] >= initial.minutes_fetch_water.max():
            water_collection_bins[-1] = initial.minutes_fetch_water.max()
            break
    water_collection_time = (pd.cut(initial.minutes_fetch_water,
                                    water_collection_bins,
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

    st.write('\n\n ### Head of Household Demographics')
    st.write('\nAverage Age')
    st.write(f'{initial.hh_age.mean():.1f}')

    st.write('\nSex')
    sex = (initial
           .hh_sex
           .value_counts(dropna=False,normalize=True)
           .mul(100)
           .round(2)
          )
    st.write(sex)
    fig, ax = plt.subplots()
    ax.pie(sex.values, labels=sex.index.values,
            autopct='%1.1f%%', shadow=False, startangle=140)
    ax.axis('equal')
    st.pyplot(fig)

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


image = Image.open('Bright-Water-Foundation-Logo-1.jpg')

st.image(image)
st.write("This application allows users to explore data from Bright Water Foundation's work in Africa.")

df_initial = get_initial_data()
commuity_selection_options = ['Sankebunase project (Sankebunase, Nkurakan, Amonom, Mampong, Wekpeti)',
                                'Ekorso project (Ekorso, Akwadum, Akwadusu)'] \
                                + list(df_initial.community.dropna().unique())
if 'c_select' not in st.session_state:
    st.session_state.c_select = []
# st.write(st.session_state)
# st.write(commuity_selection_options)
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

    # st.session_state.c_select = communities
    st.write('### selected communities',st.session_state.c_select)

    data_initial = get_community(df_initial,communities)
    # data_followup = get_community(df_followup,communities)
    # st.write('### Initial Survey Data',data_initial)
    st.write(f'''
        There are
        {data_initial.query('~completed').completed.count()}
        records that are marked as "incomplete",
        do you want to remove them?
        ''')
    remove_incomplete = st.checkbox(label='Remove incomplete records',value=True)
    if remove_incomplete:
        data_initial = data_initial.query('completed')
        # st.write('### Initial Survey Data with removed incomplete records',data_initial)


    # weekday_graph(data_initial)

    # st.write('---')
    # st.write('### Number of Surveys conducted per Safe Water Educator',data_initial.SWE_name.value_counts())

    # dup_name = data_initial.hh_name.value_counts().loc[lambda x: x > 1]
    # if dup_name.any():
    #     st.write('---')
    #     st.write('#### These household names are duplicated in this dataset',dup_name)
    # else:
    #     st.write('---')
    #     st.write('#### There are no duplicate household names in this dataset')

    st.write('---')
    st.write('### Demographic summary')
    demographics(data_initial)
