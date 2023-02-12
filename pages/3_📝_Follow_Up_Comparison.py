import streamlit as st
from PIL import Image
from Home import get_initial_data, get_followup_data, get_community
from pandas.api.types import CategoricalDtype
import matplotlib.pyplot as plt
import pandas as pd




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
    data_followup = get_community(df_followup,communities)

    st.write(f'''
        There are
        {data_initial.query('~completed').completed.count()}
        records that are marked as "incomplete",
        do you want to remove them?
        ''')
    remove_incomplete = st.checkbox(label='Remove incomplete records',value=True)
    if remove_incomplete:
        data_initial = data_initial.query('completed')


    # st.write('##')
    st.write('---')
    st.write('How much money was spent by members of this household for medical treatment for these illnesses in the last four (4) weeks? (in local currency)')
    fig1,ax1 = plt.subplots()
    (data_initial
    .medical_cost_four_weeks_local
    .plot.hist(ax=ax1,title='Initial Survey Medical Costs')
    )
    ax1.grid(axis='y')
    ax1.set_xlabel('Medical Costs Previous 4 Weeks (Local Currency)')

    fig2,ax2 = plt.subplots()
    (data_followup
    .medical_cost_four_weeks_local
    .plot.hist(ax=ax2,title='Follow Up Survey Medical Costs')
    )
    ax2.grid(axis='y')
    ax2.set_xlabel('Medical Costs Previous 4 Weeks (Local Currency)')

    col1, col2 = st.columns(2)
    col1.pyplot(fig1)
    col2.pyplot(fig2)
    # st.pyplot(fig)


    st.write('In the last two weeks, how many days have you personally been unable to do work due to your own stomach pain/diarrhea illness?')
    # st.write('---')
    col1, col2 = st.columns(2)
    col1.write('#### Initial Survey')
    col1.write(data_initial.two_weeks_days_work_missed.value_counts(normalize=True).mul(100).round(2))
    col1.write('sum of work days missed')
    col1.write(data_initial.two_weeks_days_work_missed.sum())

    col2.write('#### Follow Up Survey')
    col2.write(data_followup.two_weeks_days_work_missed.value_counts(normalize=True).mul(100).round(2))
    col2.write('sum of work days missed')
    col2.write(data_followup.two_weeks_days_work_missed.sum())


    st.write('In the last two weeks, how many total days have other members of your family been unable to do work due to stomach pain/diarrhea illness?')
    col1, col2 = st.columns(2)
    col1.write('#### Initial Survey')
    col1.write(data_initial.two_weeks_days_hh_work_missed.value_counts(normalize=True).mul(100).round(2))
    col1.write('sum of work days missed household')
    col1.write(data_initial.two_weeks_days_hh_work_missed.sum())

    col2.write('#### Follow Up Survey')
    col2.write(data_followup.two_weeks_days_hh_work_missed.value_counts(normalize=True).mul(100).round(2))
    col2.write('sum of work days missed household')
    col2.write(data_followup.two_weeks_days_hh_work_missed.sum())


    st.write('In the last two weeks, how many total school days have school-age children in this household missed due to illness? (No. of days)')
    col1, col2 = st.columns(2)
    col1.write('#### Initial Survey')
    col1.write(data_initial.two_weeks_children_school_days.value_counts(normalize=True).mul(100).round(2))
    col1.write('sum of school days missed')
    col1.write(data_initial.two_weeks_children_school_days.sum())

    col2.write('#### Follow Up Survey')
    col2.write(data_followup.two_weeks_children_school_days.value_counts(normalize=True).mul(100).round(2))
    col2.write('sum of school days missed')
    col2.write(data_followup.two_weeks_children_school_days.sum())



    st.write('Do you treat your water in any way to make it safer to drink?')
    col1, col2 = st.columns(2)
    col1.write('#### Initial Survey')
    col1.write(data_initial.treat_water.value_counts(normalize=True,dropna=False).mul(100).round(2))

    col2.write('#### Follow Up Survey')
    col2.write(data_followup.treat_water.value_counts(normalize=True,dropna=False).mul(100).round(2))



    st.write('How often do you treat your water to make it safe?')
    col1, col2 = st.columns(2)
    col1.write('#### Initial Survey')
    col1.write(data_initial.treat_water_freq.value_counts(normalize=True,dropna=False).mul(100).round(2))

    col2.write('#### Follow Up Survey')
    col2.write(data_followup.treat_water_freq.value_counts(normalize=True,dropna=False).mul(100).round(2))



    st.write('When was the last time you treated your household drinking water with chlorine?')
    col1, col2 = st.columns(2)
    col1.write('#### Initial Survey')
    col1.write(data_initial.treat_water_last_chlorine.value_counts(normalize=True,dropna=False).mul(100).round(2))

    col2.write('#### Follow Up Survey')
    col2.write(data_followup.treat_water_last_chlorine.value_counts(normalize=True,dropna=False).mul(100).round(2))
