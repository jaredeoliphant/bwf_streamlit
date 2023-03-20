import streamlit as st
from PIL import Image
from Home import (
    get_data,
    get_community,
    header_info,
    selection_sidebar,
    add_labels
)
from pandas.api.types import CategoricalDtype
import matplotlib.pyplot as plt
import pandas as pd

## start of main script
##----------------------------
header_info()

df_initial = get_data(tableName='InitialSurvey')
if type(df_initial) != pd.DataFrame:
    st.error("API failed to return data")
else:
    communities = selection_sidebar(df_initial)

    if communities:
        communitywater_df = get_data(tableName='CommunityWaterTest')
        communitywater = get_community(communitywater_df, communities)
        st.write("##")
        st.write("---")

        st.write("### Community Water Tests", communitywater)
        colilert_test_result = (
            communitywater.ColilertTestResult.value_counts(dropna=False, normalize=True)
            .mul(100)
            .round(2)
        )
        st.write(colilert_test_result)

        fig, ax = plt.subplots()
        colilert_test_result.plot.bar(
            ax=ax, ylabel="% of Tests", title="Colilert Test Results"
        )
        ax.grid(axis="y")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        add_labels(ax)
        st.pyplot(fig)

        petrifilm_test_result = (
            communitywater.PetrifilmTestResult.value_counts(
                dropna=False, normalize=True
            )
            .mul(100)
            .round(2)
        )
        st.write(petrifilm_test_result)

        fig, ax = plt.subplots()
        petrifilm_test_result.plot.bar(
            ax=ax, ylabel="% of Tests", title="Petrifilm Test Results"
        )
        ax.grid(axis="y")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        add_labels(ax)
        st.pyplot(fig)
