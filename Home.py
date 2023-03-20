import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from pandas.api.types import CategoricalDtype
from PIL import Image
import jwt
import requests
import typing


@st.cache_data(ttl=3600)  # 1 hour
def get_api_token() -> typing.Union[str, None]:
    """returns API token (str) based on environment variables. Returns None
    if API call fails"""
    server_name = os.environ["API_SERVER_URL"]
    cert_key = os.environ["CERT_NAME"]
    encoded = os.environ["ENCODED_CERT"]
    resp = requests.get(
        f"{server_name}/auth", headers={"mykey": cert_key, "test": encoded,},
    )
    if resp.status_code != 200:
        st.error(f"status_code={resp.status_code}, {data['msg']}")
        return None

    data = resp.json()
    return data["access_token"]


def decrypt_api_response(encryted_data: str) -> pd.DataFrame:
    """Decrypts the api query response data using jwt and returns a pandas
    DataFrame"""
    server_public_key = os.environ["PUBLIC_KEY"]
    query_results = jwt.decode(encryted_data, server_public_key, ["RS256"])
    data = query_results["data"]
    return pd.DataFrame(data)


def query_api(
    token: str, query_data: dict, table: str
) -> typing.Union[pd.DataFrame, None]:
    """runs a query on the API according to the following inputs:
    token=Authorization token retreived previously
    query_data=dictionary with all query parameters
    table=name of table to query from
    returns a pandas DataFrame or None if the API request fails"""
    server_name = os.environ["API_SERVER_URL"]
    server_public_key = os.environ["PUBLIC_KEY"]
    resp = requests.post(
        f"{server_name}/query/{table}",
        data=query_data,
        headers={"Authorization": f"Bearer {token}",},
    )

    if resp.status_code != 200:
        st.error(f"status_code={resp.status_code}, {resp.json()}")
        return None
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


@st.cache_data(ttl=3600 * 24)  # 24 hrs
def get_data(tableName: str) -> typing.Union[pd.DataFrame, None]:
    """returns pandas DataFrame of all {tableName} data from Ghana where
    completed == 1 and disabled != True.
    returns None if API request (query_api()) fails"""
    query_data = {
        "query": str(
            {
                "$and": [
                    {"Country": "Ghana"},
                    {"Completed": 1},
                    {"disabled": {"$ne": True}},
                ]
            }
        ),
        "extra": str({"sort": [("date", 1)]}),
    }
    token = get_api_token()
    df = query_api(token, query_data, tableName)
    return df


def add_since_earliest(df: pd.DataFrame) -> pd.DataFrame:
    """adds a column to the inputted DataFrame that contains the earliest
    date"""
    return df.assign(
        since_earliest=lambda df_: df_.date - df_.groupby(by="a").date.transform(min)
    )


def tweak_initial(df: pd.DataFrame) -> pd.DataFrame:
    """data wrangling function for initial survey DataFrame. Strips whitespace on free input
    questions"""
    # name and phone are the only true free response questions
    return df.assign(
        HeadHouseholdName=lambda df_: df_.HeadHouseholdName.str.strip(),
        HeadHouseholdPhoneNumber=lambda df_: df_.HeadHouseholdPhoneNumber.str.strip(),
        nameBwe=lambda df_: df_.nameBwe.str.strip(),
    )


def tweak_followup(df: pd.DataFrame) -> pd.DataFrame:
    """data wrangling function for followup survey DataFrame. Strips whitespace on free input 
    questions"""
    return df.assign(
        HeadHouseholdName=lambda df_: df_.HeadHouseholdName.str.strip(),
        nameBwe=lambda df_: df_.nameBwe.str.strip(),
    )


def get_community(df: pd.DataFrame, communities: List[str]) -> pd.DataFrame:
    """query the DataFrame to only return the records with the selected communities"""
    return df.query("Community.isin(@communities).values")


def weekday_graph(data: pd.DataFrame) -> None:
    """produce a bar graph of number of surveys conducted on each day of the week"""
    mapdict = {
        "0": "Mon",
        "1": "Tues",
        "2": "Wed",
        "3": "Thur",
        "4": "Fr",
        "5": "Sat",
        "6": "Sun",
    }
    fig, ax = plt.subplots()
    datedata = pd.to_datetime(data.date)
    datedata.dt.day_of_week.value_counts().sort_index().plot.bar(
        ylabel="Initial Surveys Conducted",
        title="Day of Week Initial Survey was conducted",
        ax=ax,
    )
    newlabels = [mapdict[tck.get_text()] for tck in ax.get_xticklabels()]
    ax.set_xticklabels(newlabels)
    ax.grid(axis="y")
    add_labels(ax, pct=False)
    st.pyplot(fig)


def date_graph(data_i: pd.DataFrame, data_f: pd.DataFrame) -> None:
    """produce a graph showing the number of surveys conducted on each day of the year"""
    data_i = data_i.assign(date=pd.to_datetime(data_i.date))
    data_f = data_f.assign(date=pd.to_datetime(data_f.date))
    weekly = data_f.groupby(pd.Grouper(key="date", freq="W")).id.count()
    fig, ax = plt.subplots()
    weekly.plot.area(
        ax=ax, title="Initial and Follow up survey date", label="Follow up"
    )

    weekly = data_i.groupby(pd.Grouper(key="date", freq="W")).id.count()
    weekly.plot.area(ax=ax, label="Initial").grid(axis="y")
    ax.legend()
    st.pyplot(fig)


def add_labels(ax: plt.Axes, pct: bool = True) -> None:
    """add value labels to all bars in a given axis. For absolute counts, set pct=False"""
    for p in ax.patches:
        if not pd.isna(p.get_height()):
            if pct:
                s = f"{p.get_height():.1f}" + "%"
            else:
                s = f"{p.get_height():.0f}"
            ax.annotate(
                s,
                (p.get_x() + p.get_width() / 2, p.get_height()),
                ha="center",
                va="bottom",
            )


def header_info() -> None:
    """display header information that will be on nearly every page of streamlit app"""
    image = Image.open("Bright-Water-Foundation-Logo-1.jpg")

    st.image(image)
    st.write(
        "This application allows users to explore data from Bright Water Foundation's work in Africa."
    )


def selection_sidebar(df_initial: pd.DataFrame) -> typing.List[str]:
    """interactive multiselect on the sidebar. Whatever selection the user makes on
    one page will be carried over to the other pages"""
    commuity_selection_options = [
        "Sankebunase project (Sankebunase, Nkurakan, Amonom, Mampong, Wekpeti)",
        "Ekorso project (Ekorso, Akwadum, Akwadusu)",
    ] + list(df_initial.Community.dropna().unique())
    if "c_select" not in st.session_state:
        st.session_state.c_select = []
    communities = st.sidebar.multiselect(
        "Choose communities",
        commuity_selection_options,
        default=st.session_state.c_select,
    )
    if not communities:
        st.sidebar.error("Please select at least one community.")
        st.session_state.c_select = []
    else:
        if commuity_selection_options[0] in communities:
            group_communities = [
                "Sankebunase (Nkurakan/Amonon)",
                "Sankebunase",
                "Nkurakan",
                "Amonom",
                "Mampong",
                "Wekpeti/Abresu",
            ]
            communities.remove(commuity_selection_options[0])
            communities += group_communities
        if commuity_selection_options[1] in communities:
            group_communities = ["Ekorso", "Akwadum", "Akwadusu"]
            communities.remove(commuity_selection_options[1])
            communities += group_communities
        communities = list(set(communities))
        st.session_state.c_select = communities
        st.write("### selected communities", communities)

    return communities


def main() -> None:
    """main function"""
    header_info()

    df_initial = get_data(tableName="InitialSurvey")
    df_followup = get_data(tableName="FollowUpSurvey")
    if (type(df_initial) != pd.DataFrame) or (type(df_followup) != pd.DataFrame):
        st.error("API failed to return data")
        # return

    communities = selection_sidebar(df_initial)

    if communities:
        data_initial = get_community(df_initial, communities)
        data_followup = get_community(df_followup, communities)

        st.write(
            "### Initial Survey Data",
            data_initial.drop(columns=["HeadHouseholdPhoneNumber", "Namebwe"]),
        )

        st.write("---")
        st.write("### Follow up Survey Data", data_followup.drop(columns=["Namebwe"]))
        date_graph(data_initial, data_followup)

        weekday_graph(data_initial)

        st.write("---")
        # st.write('### Number of Surveys conducted per Safe Water Educator',data_initial.Namebwe.value_counts())

        dup_name = data_initial.HeadHouseholdName.value_counts().loc[lambda x: x > 1]
        if dup_name.any():
            st.write("---")
            st.write(
                "#### These household names are duplicated in this dataset", dup_name
            )
        else:
            st.write("---")
            st.write("#### There are no duplicate household names in this dataset")


if __name__ == "__main__":
    main()
