import pandas as pd

df = pd.read_excel('InitialSurvey.xlsx').iloc[:-1,:]
df = df.drop(columns=['Email SWE','Head Household Phone Number'])
df.to_excel('InitialSurvey_anon.xlsx',index=False)

df = pd.read_excel('FollowUpSurvey.xlsx').iloc[:-1,:]
df = df.drop(columns=['Email BWE'])
df.to_excel('FollowUpSurvey_anon.xlsx',index=False)

df = pd.read_excel('CommunityWaterTest.xlsx').iloc[:-1,:]
df = df.drop(columns=['Email BWE'])
df.to_excel('CommunityWaterTest_anon.xlsx',index=False)

df = pd.read_excel('HouseholdWaterTestSWE.xlsx').iloc[:-1,:]
df = df.drop(columns=['Email BWE'])
df.to_excel('HouseholdWaterTestSWE_anon.xlsx',index=False)

df = pd.read_excel('HouseholdWaterTestVolunteers.xlsx').iloc[:-1,:]
df = df.drop(columns=['Email BWE','Email Volunteer'])
df.to_excel('HouseholdWaterTestVolunteers_anon.xlsx',index=False)
