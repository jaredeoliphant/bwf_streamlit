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
    st.write(f'Number of Unique Household Names: {initial.HeadHouseholdName.nunique()}')
    total_pop = initial.TotalNoPeopleHousehold.sum()
    st.write(f'Total Survey Population: {total_pop:n}')
    st.write(f'Average family size: {initial.TotalNoPeopleHousehold.mean():.2f}')

    childrencolumns = ['NoHouseholdMale0_1Year','NoHouseholdFemale0_1Year',
                       'NoHouseholdMale1_5Year','NoHouseholdFemale1_5Year']
    children5 = initial.loc[:,childrencolumns].sum().sum()
    st.write(f'{100*children5/total_pop:.2f}% less than 5 yrs')
    childrencolumns += ['NoHouseholdMale5_12Year','NoHouseholdFemale5_12Year']
    children12 = initial.loc[:,childrencolumns].sum().sum()
    st.write(f'{100*children12/total_pop:.2f}% less than 12 yrs')
    childrencolumns += ['NoHouseholdMale13_17Year','NoHouseholdFemale13_17Year']
    children18 = initial.loc[:,childrencolumns].sum().sum()
    st.write(f'{100*children18/total_pop:.2f}% less than 18 yrs')

    st.write('\nSources of Drinking Water')
    st.write((initial
           .MainSourceDrinkingWater
           .value_counts(dropna=False,normalize=True)
           .mul(100)
           .round(2)
          ))

    st.write('\nSources of Non-Drinking Water')
    st.write((initial
           .MainSourceOtherPurposeWater
           .value_counts(dropna=False,normalize=True)
           .mul(100)
           .round(2)
          ))

    st.write('\nWater Collection Frequency')
    water_mapping = {
        '2ORMORETIMEPERDAY':'Two or More Times Daily',
        'ONCEDAILY':'Once Daily',
        'EVERYOTHERDAY':'Every Other Day',
        'EVERYTHIRDDAY':'Every Third Day',
        'WEEKLY':'Weekly'
    }
    water_cat = CategoricalDtype(categories=['Two or More Times Daily','Once Daily',
                                          'Every Other Day','Every Third Day','Weekly'], ordered=True)
    water_collection_freq = (initial
            .HouseholdFrequencyAtWaterSource
            .astype('category')
            .map(water_mapping)
            .astype(water_cat)
          )
    water_collection_freq_pct = (water_collection_freq
            .value_counts(dropna=False,normalize=True,sort=False)
            .mul(100)
            .round(2)
          )
    water_collection_freq_count = (water_collection_freq
            .value_counts(dropna=False,sort=False)
          )
    st.write(
        pd.concat([water_collection_freq_pct,water_collection_freq_count],
                  axis=1,
                  keys=('Water Collection Frequency (%)','Water Collection Frequency (count)')
                 )
    )
    fig,ax = plt.subplots()
    water_collection_freq_pct.plot.bar(ax=ax,ylabel='% of Respondents',title='Water Collection Frequency').grid(axis='y')
    ax.set_xticklabels(ax.get_xticklabels(), rotation = 45, ha='right')
    st.pyplot(fig)

    st.write('\nWater Collection Time (Minutes)')
    water_collection_bins = [0]
    for i in range(15):
        water_collection_bins.append(water_collection_bins[-1]+10)
        if water_collection_bins[-1] >= initial.TimeToWaterSourceGetReturn.max():
            water_collection_bins[-1] = initial.TimeToWaterSourceGetReturn.max()
            break
    water_collection_time = (pd.cut(initial.TimeToWaterSourceGetReturn,
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
    who_collects = (initial
           .UsualHouseholdWaterFetcher
           .value_counts(dropna=False,normalize=True)
           .mul(100)
           .round(2)
          )
    who_collects_count = (initial
           .UsualHouseholdWaterFetcher
           .value_counts(dropna=False)
          )
    st.write(
        pd.concat([who_collects,who_collects_count],
                  axis=1,
                  keys=('Usual Household Water Fetcher (%)','Usual Household Water Fetcher (count)')
                 )
    )
    fig,ax = plt.subplots()
    who_collects.plot.bar(ax=ax,ylabel='% of Respondents',title='Who Collects Water?').grid(axis='y')
    ax.set_xticklabels(ax.get_xticklabels(), rotation = 45, ha='right')
    st.pyplot(fig)


    st.write('\nWater Container')
    water_container = (initial
           .ContainerCarryWater
           .value_counts(dropna=False,normalize=True)
           .mul(100)
           .round(2)
          )
    water_container_count = (initial
           .ContainerCarryWater
           .value_counts(dropna=False)
          )
    st.write(
        pd.concat([water_container,water_container_count],
                  axis=1,
                  keys=('Water Container (%)','Water Container (count)')
                 )
    )
    
    
    
    st.write('\n\n ### Head of Household Demographics')
    st.write('\nAverage Age')
    st.write(f'{initial.HeadHouseholdAge.mean():.1f}')

    st.write('\nSex')
    sex = (initial
           .HeadHouseholdSex
           .value_counts(dropna=False,normalize=True)
           .mul(100)
           .round(2)
          )
    sex_count = (initial
           .HeadHouseholdSex
           .value_counts(dropna=False)
          )
    st.write(
        pd.concat([sex,sex_count],
                  axis=1,
                  keys=('Head Household Sex (%)','Head Household Sex (count)')
                 )
    )
    fig, ax = plt.subplots()
    ax.pie(sex.values, labels=sex.index.values,
            autopct='%1.1f%%', shadow=False, startangle=140)
    ax.axis('equal')
    st.pyplot(fig)

    st.write('\nMarital Status')
    marital_status = (initial
           .HeadHouseholdMaritalStatus
           .value_counts(dropna=False,normalize=True)
           .mul(100)
           .round(2)
          )
    marital_status_count = (initial
           .HeadHouseholdMaritalStatus
           .value_counts(dropna=False)
          )
    st.write(
        pd.concat([marital_status,marital_status_count],
                  axis=1,
                  keys=('Head Household Marital Status (%)','Head Household Marital Status (count)')
                 )
    )
    fig,ax = plt.subplots()
    marital_status.plot.bar(ax=ax,ylabel='% of Respondents',title='Head of Household Marital Status').grid(axis='y')
    ax.set_xticklabels(ax.get_xticklabels(), rotation = 45, ha='right')
    st.pyplot(fig)


    st.write('\nEducation')
    ed_mapping = {
        'COMPLETEDJRHIGHSCHOOL':'Completed Jr. High',
        'SOMEJRHIGHSCHOOL':'Completed Primary School',
        'SOMEPRIMARYSCHOOL':'Some or No Primary School',
        'NOFORMALEDUCATION':'Some or No Primary School',
        'COMPLETEDPRIMARYSCHOOL':'Completed Primary School',
        'SOMESRHIGHSCHOOL':'Completed Jr. High',
        'COMPLETEDSRHIGHSCHOOL':'Completed High School',
        'SOMEEDUCATIONBEYONDHIGHSCHOOL':'Some Education Beyond High School'
    }
    ed_cat = CategoricalDtype(categories=['Some or No Primary School','Completed Primary School',
                                          'Completed Jr. High','Completed High School',
                                          'Some Education Beyond High School'], ordered=True)
    education = (initial
           .HeadHouseholdEducation
           .astype('category')
           .map(ed_mapping)
           .astype(ed_cat)
          )
    education_pct = (education
           .value_counts(dropna=False,normalize=True,sort=False)
           .mul(100)
           .round(2)
          )
    education_count = (education
           .value_counts(dropna=False,sort=False)
          )
    st.write(
        pd.concat([education_pct,education_count],
                  axis=1,
                  keys=('Head Household Education (%)','Head Household Education (count)')
                 )
    )
    fig,ax = plt.subplots()
    education_pct.plot.bar(ax=ax,ylabel='% of Respondents',title='Head of Household Education Level').grid(axis='y')
    ax.set_xticklabels(ax.get_xticklabels(), rotation = 45, ha='right')
    st.pyplot(fig)

    st.write('\nOccupation')
    occ_mapping = {
        'FARMER':'Farmer',
        'TRADER':'Trader',
        'OTHER':'Other/None',
        'NONE':'Other/None',
        'CIVILSERVANT':'Civil Servant/Teacher',
        'TEACHER':'Civil Servant/Teacher'
    }
    occupation = (initial
       .HeadHouseholdOccupation
       .astype('category')
       .map(occ_mapping)
      )
    occupation_pct = (occupation
       .value_counts(dropna=False,normalize=True)
       .mul(100)
       .round(2)
      )
    occupation_count = (occupation
       .value_counts(dropna=False)
      )
    st.write(
        pd.concat([occupation_pct,occupation_count],
                  axis=1,
                  keys=('Head Household Occupation (%)','Head Household Occupation (count)')
                 )
    )
    fig,ax = plt.subplots()
    occupation_pct.plot.bar(ax=ax,ylabel='% of Respondents',title='Head of Household Occupation').grid(axis='y')
    ax.set_xticklabels(ax.get_xticklabels(), rotation = 45, ha='right')
    st.pyplot(fig)


image = Image.open('Bright-Water-Foundation-Logo-1.jpg')

st.image(image)
st.write("This application allows users to explore data from Bright Water Foundation's work in Africa.")

df_initial = get_initial_data()
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

    st.write('### selected communities',st.session_state.c_select)

    data_initial = get_community(df_initial,communities)
    
    st.write('---')
    st.write('### Demographic summary')
    demographics(data_initial)
