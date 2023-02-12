import streamlit as st
from PIL import Image
from Home import get_initial_data, get_community, tweak_communitywater, get_communitywater_data
from pandas.api.types import CategoricalDtype
import matplotlib.pyplot as plt
import pandas as pd

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


    communitywater_df = get_communitywater_data()
    communitywater = get_community(tweak_communitywater(communitywater_df),communities)
    st.write('##')
    st.write('---')

    st.write('### Community Water Tests',communitywater)
    colilert_test_result = (communitywater['Colilert Test Result']
                .value_counts(dropna=False,normalize=True)
                .mul(100)
                .round(2)
                )
    st.write(colilert_test_result)

    fig,ax = plt.subplots()
    colilert_test_result.plot.bar(ax=ax,
                                ylabel='% of Tests',
                                title='Colilert Test Results')
    ax.grid(axis='y')
    ax.set_xticklabels(ax.get_xticklabels(), rotation = 45, ha='right')
    st.pyplot(fig)

    petrifilm_test_result = (communitywater['Petrifilm Test Result']
                .value_counts(dropna=False,normalize=True)
                .mul(100)
                .round(2)
                )
    st.write(petrifilm_test_result)

    fig,ax = plt.subplots()
    petrifilm_test_result.plot.bar(ax=ax,
                                ylabel='% of Tests',
                                title='Petrifilm Test Results')
    ax.grid(axis='y')
    ax.set_xticklabels(ax.get_xticklabels(), rotation = 45, ha='right')
    st.pyplot(fig)
