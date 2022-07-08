#According to Ian's code on streamlit dashboard
import streamlit as st

import pandas as pd
pd.options.display.max_columns = None
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from matplotlib import pyplot as plt
import itertools

from sqlalchemy import create_engine, inspect, Table, MetaData
metadata = MetaData()
from sqlalchemy.engine.base import Engine
from sqlalchemy.sql import select
from sqlalchemy.orm import scoped_session, sessionmaker, base
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer 


st.set_page_config(page_title='Results Dashboard', page_icon=('favicon.ico'), initial_sidebar_state='expanded', layout='wide')
#st.sidebar.image('olblack.png', width=140)
st.sidebar.title('Results Dashboard')


# streamlit cache decorator https://docs.streamlit.io/library/advanced-features/experimental-cache-primitives
# for Mike's code for connecting to the database
#----------------------------------------------------------#
# @st.experimental_singleton
# def connect_db( 
#             db = "datarepo",
#             dbschema = "openlabcdr",
#             user = "postgres", 
#             pwd = "postgres", 
#             addy = "localhost", # Team Remote
#             port = "5433", #Team remote          
#         ):

#     uri = "postgresql://{user}:{pwd}@{addy}:{port}/{db}".format(
#             db = db,
#             user = user, 
#             pwd = pwd, 
#             addy = addy,
#             port = port)
    
#     print("Connecting to: {}".format(uri))

#     engine = create_engine(uri)
#     db = scoped_session(sessionmaker(bind=engine))
#     db.execute("SET search_path TO {}".format(dbschema))

#     inspector = inspect(engine)

#     result_set = db.execute("SELECT current_database();")  
#     for r in result_set:  
#         print("current database: {}".format(r))

#     result_set = db.execute("SELECT current_schema();")  
#     for r in result_set:  
#         print("current schema: {}".format(r))

#     return (engine, db, inspector)

# engine, db, inspector = connect_db(
#     db = "datarepo",
#     dbschema = "openlabcdr",
#     pwd = "postgres", 
#     addy = "localhost", # Team Remote
#     port = "5433", #Team remote
# )


# # streamlit cache for DB query
# @st.experimental_memo
# def query_db(sql, _engine):
#     return pd.read_sql_query(sql, engine)

# # query
# sql = ( "SELECT mv_peaks.peak_retentiontime, mv_peaks.peak_area, mv_peaks.peak_area_unit, mv_peaks.peak_symmetry, mv_peaks.peak_tailingfactor, mv_peaks.resultset_name, mv_injcompounds.injcompound_name, mv_injections.instrument_name, mv_injections.injection_acquireddate, mv_injections.injection_datafilename "
#         "FROM openlabcdr.mv_injections "
#         "LEFT JOIN openlabcdr.mv_peaks "
#         "ON mv_injections.injection_id = mv_peaks.injection_id "
#         "LEFT JOIN openlabcdr.mv_injcompounds "
#         "ON mv_peaks.object_id = mv_injcompounds.mainpeak_object_id "
#         "WHERE mv_peaks.resultsetrevision_iscurrent = TRUE;")


# # query the database
# raw_results_df = query_db(sql, engine)
# # drop NaN and Null values, need to address this a better way
# results_df = raw_results_df.dropna()
#----------------------------------------------------------------------------------------------#

#Data from OMS (excel files)
df_5 = pd.read_excel(r'Excel from OMS/sequence and detail.xls.xlsx', skiprows=1)

#only keep the 'Sample' injection, get rid of "calibration", 'Blank'
df_5_sample = df_5.loc[df_5['sample_type'] == 'Sample']

#List all repeated results/sample names
df_5_sample_inj = df_5_sample.query('sample_injections_count > 1')
results_df = df_5_sample_inj[['sample_name','project_name','sample_injections_count']].groupby(['sample_name','project_name'],as_index=False).sum(['sample_injections_count']).fillna(0)



# multiselection for project_name
with st.sidebar.expander('Select Project Name(s)', expanded=True):
    rs_filter = st.text_input('Filter on:', key='rs_filter')
    filtered_results_df = results_df[results_df['project_name'].str.contains(rs_filter)]
    result_options = filtered_results_df.project_name.unique()
    container = st.container()
    all_results = st.checkbox("Select all projects", value=True)
    # reload results, not sure if this works
    # if st.button('Reload results'):
    #     raw_results_df = query_db(sql, engine)
    #     results_df = raw_results_df.dropna()

if all_results:
    selected_results = container.multiselect("", result_options, result_options, key='results')
else:
    selected_results = container.multiselect("", result_options, key='results')

# selected results dataframe
selected_results_df = results_df[results_df.project_name.isin(selected_results)]

# multiselection for injection compound
with st.sidebar.expander('Select Sample(s)', expanded=True):
    c_filter = st.text_input('Filter on:', key='c_filter')
    filtered_compounds_df = selected_results_df[selected_results_df['sample_name'].str.contains(c_filter)]
    compound_options = filtered_compounds_df.sample_name.unique()
    container = st.container()
    all_compounds = st.checkbox("Select all samples", value=True)

if all_compounds:
    compounds_filtered = container.multiselect("", compound_options, compound_options, key='compounds')
else:
    compounds_filtered = container.multiselect("", compound_options, key='compounds')

# selected results + selected compounds dataframe
compounds_filtered_df = selected_results_df[selected_results_df.sample_name.isin(compounds_filtered)]


table1 = go.Figure(data=[go.Table(header=dict(values=['<b>Sample Name</b>', '<b>Project Name</b>', '<b>Sample Injection Counts</b>']),
                                cells=dict(values=[compounds_filtered_df["sample_name"], compounds_filtered_df['project_name'], compounds_filtered_df['sample_injections_count']]))
                                    ])
st.plotly_chart(table1)



fig3 = px.bar(compounds_filtered_df, x="sample_name", y="sample_injections_count", title="Samples with Multiple Injections", color="project_name")
#fig3.update_traces(quartilemethod="linear", jitter=0.3)
st.plotly_chart(fig3)



