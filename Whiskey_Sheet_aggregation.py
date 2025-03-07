import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import datetime as dt
import time
import os
from whiskey_bottles import bottles_with_keys
from whiskey_bottles import price_dict
import Email_Python

os.chdir(os.path.dirname(os.path.abspath(__file__)))
creds = 'Path_to_your_google_api_cred_file_here'
folder_path = "path_to_where_you_want_to_save_data"
data = pd.read_csv('C:/Path/To/Whiskey_urls.csv')
contacts =  pd.read_csv('Path_to_contact_file_here.csv')
# Path to the file

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(creds, scope)
client = gspread.authorize(creds)

df = pd.DataFrame()
dataframe = []

for x,y in zip(data['User'], data['URL']):
    spreadsheet = client.open_by_url(y)
    worksheet = spreadsheet.sheet1
    data = worksheet.get_all_values()
    sheet_df = pd.DataFrame(data[1:], columns=data[0])
    sheet_df = sheet_df.iloc[:, :2]
    sheet_df['User'] = x
    dataframe.append(sheet_df)
    df = pd.concat(dataframe, ignore_index=True)

#If you use a blind test, uncomment the line below to replace all the letters with their respective bottle, otherwise, leave as is.
#df['Whiskey'] = df['Whiskey'].replace(bottles_with_keys)


#makes sure all ratings folllow expectations
df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
df['Score'] = df['Score'].clip(upper=100, lower= 0)
average = df.groupby(by='Whiskey', as_index= False).mean(numeric_only=True)
average_ranked = df.groupby(by='Whiskey', as_index= False).mean(numeric_only=True).sort_values(by='Score', ascending=False)
critic_ranked = df.groupby(by='User', as_index= False).mean(numeric_only=True).sort_values(by='Score', ascending=True)

#does some additional configuration to improve user readability by appending price to the bottle title for later use.
average_ranked['Prices'] = average_ranked['Whiskey'].map(price_dict) 
average_ranked['Combined'] = average_ranked['Whiskey'] + ' ($' + average_ranked['Prices'].astype(str) + ')'
average_ranked['Efficiency'] = average_ranked['Score'] / average_ranked['Prices']


#Below this point is all of the data processing. Each function returns one or more statements. These statements are combined at the end to create an email for each
#user. These were organized by the order I wanted them in the email.

#Creates a ranked list by average rating, or by personal rating if a user argument is passed.
#Users end up getting two lists.
def best_bottles(user = 'All'):
    
    statement = f"This definitive order of bottles, best to worst: {''.join([x + ', ' for x in average_ranked['Whiskey'].iloc[:-1]])}and last and most certainly least, {average_ranked['Whiskey'].iloc[-1]}. Let's break it into tiers though:\n\n"
    if user != 'All':
        statement = "For your reference, here is your personal tier list of whiskeys from this weekend.\n\n"
    def param_setting(hinum, lonum):
        hinum = int(hinum)
        lonum = int(lonum)
        considered = average_ranked['Combined'].loc[((average_ranked['Score'] <= hinum) & (average_ranked['Score'] > lonum))]
        if user != 'All':
            user_considered = df.loc[df['User'] == user]
            user_considered['Prices'] = user_considered['Whiskey'].map(price_dict)
            user_considered['Combined'] = user_considered['Whiskey'] + ' ($' + user_considered['Prices'].astype(str) + ')'
            considered = user_considered['Combined'].loc[((user_considered['Score'] <= hinum) & (user_considered['Score'] > lonum))]
        if len(considered) > 1:
            bottles = f"{''.join([x + ', ' for x in considered.iloc[:-1]])}{considered.iloc[-1]}"
        if len(considered) == 1:
            bottles = f"{considered.iloc[-1]}"
        if len(considered) == 0:
            return 'None'
        return bottles
    tier1 = f'Gift-Worthy (Consensus score over 92): {param_setting(100,92)}\n\n'
    tier2 = f'Top Shelf (Consensus score between 85 and 92): {param_setting(92,85)}\n\n'
    tier3 = f'Daily Sipper (Consensus score between 70 and 85): {param_setting(85,70)}\n\n'
    tier4 = f'Passable (Consensus score between 50 and 70): {param_setting(70,50)}\n\n'
    tier5 = f'Rough (Consensus score between 30 and 50): {param_setting(50,30)}\n\n'
    tier6 = f'Awful (Consensus score below 30): {param_setting(30,0)}\n\n'
    if user != 'All':
        tier1 = f'Gift-Worthy (Score over 92): {param_setting(100,92)}\n\n'
        tier2 = f'Top Shelf (Score between 85 and 92): {param_setting(92,85)}\n\n'
        tier3 = f'Daily Sipper (Score between 70 and 85): {param_setting(85,70)}\n\n'
        tier4 = f'Passable (Score between 50 and 70): {param_setting(70,50)}\n\n'
        tier5 = f'Rough (Score between 30 and 50): {param_setting(50,30)}\n\n'
        tier6 = f'Awful (Score below 30): {param_setting(30,0)}\n\n'
    tiered =tier1+tier2+tier3+tier4+tier5+tier6
    return statement, tiered


def best_rater():
    #returns statements that contains average deviation from consensus. Since this df is sorted, slot 0 will be the person who most accurately rated, the last will be least accurate
    average = df.groupby(by='Whiskey', as_index= False).mean(numeric_only=True)
    df_com = pd.merge(df,average, on = 'Whiskey')
    df_com['Score_z'] = abs(df_com['Score_x'] - df_com['Score_y'])
    average_dif = df_com[['User','Score_z']]
    scores = average_dif.groupby(by='User', as_index= False).mean(numeric_only=True).sort_values(by = 'Score_z', ascending = True)
    statement1 = f"The person who's rating best represented the group was {scores['User'].iloc[0]}\n"
    statement2 = f"The person who disagreed with the group the most was {scores['User'].iloc[-1]}\n\n"
    return statement1, statement2

def harshest_critic():
    biggest_hater = f"The biggest hater was {critic_ranked['User'].iloc[0]} with an average rating of {round(critic_ranked['Score'].iloc[0],0)}\n"
    happy_to_be_here = f"The person with the highest average rating was {critic_ranked['User'].iloc[-1]}. His average score was {round(critic_ranked['Score'].iloc[-1],0)}\n"
    list = f"Here is how we rank from most to least critical: {''.join([x + ', ' for x in critic_ranked['User'].iloc[:-1]])}and {critic_ranked['User'].iloc[-1]}.\n\n"
    statement = biggest_hater+happy_to_be_here+list
    return statement

def preference(user):
    user_data = df.loc[df['User'] == user]
    dif = pd.merge(user_data,average, on='Whiskey')
    dif['Score_z'] = abs(dif['Score_x'] - dif['Score_y'])
    big_dif = dif.loc[dif['Score_z'] == dif['Score_z'].max()]
    small_dif = dif.loc[dif['Score_z'] == dif['Score_z'].min()]
    if big_dif['Score_x'].iloc[0] > big_dif['Score_y'].iloc[0]:
        statement1 = f"Your hottest take was that {big_dif['Whiskey'].iloc[0]} was better than people gave it credit for. You gave it a {big_dif['Score_x'].iloc[0]} compared to the average of {big_dif['Score_y'].iloc[0]}.\n"
    else:
        statement1 = f"Your hottest take was that {big_dif['Whiskey'].iloc[0]} was worse than everyone else thought. You gave it a {big_dif['Score_x'].iloc[0]} compared to the average of {big_dif['Score_y'].iloc[0]}.\n"

    statement2 = f"You were spot on with your rating of {small_dif['Whiskey'].iloc[0]}. You gave it a {small_dif['Score_x'].iloc[0]} compared to the average of {small_dif['Score_y'].iloc[0]}.\n\n"

    return statement1, statement2

def favorite_and_least(user):
    #returns list of bottles that scored over 90 and lower than 40
    user_data = df.loc[df['User'] == user]

    best = user_data['Whiskey'].loc[user_data['Score'] >= 90]
    worst = user_data['Whiskey'].loc[user_data['Score'] <= 40]

    if len(best) >= 3:
        output1 = f"{''.join([x + ', ' for x in best.iloc[:-1]])}and {best.iloc[-1]} were your favorite bottles. They scored over 90.\n"
    elif len(best) == 2:
        output1 = f"{''.join([x + ' ' for x in best.iloc[:-1]])}and {best.iloc[-1]} were your favorite bottles. They both scored over 90.\n"
    elif len(best) == 1:
        output1 = f"{best.iloc[-1]} was your favorite bottle. It was the only one to score over 90.\n"
    else:
        output1 =  'You did not find a bottle that you loved this weekend, better luck next year.\n'


    if len(worst) >= 3:
        output2 = f"You didn't care for {''.join([x + ', ' for x in worst.iloc[:-1]])}and {worst.iloc[-1]}. They scored below 40.\n\n"
    elif len(worst) == 2:
        output2 = f"You didn't care for {''.join([x + ' ' for x in worst.iloc[:-1]])}and {worst.iloc[-1]}. They both scored below 40.\n\n"
    elif len(worst) == 1:
        output2 = f"You didn't care for {worst.iloc[-1]}. It was the only one to score below 40.\n\n"
    else:
        output2 =  "You did not find a bottle you truly hated. That's good!\n\n"
    return output1, output2

def taste_profile(user):
    user_data = df.loc[df['User'] == user]
    other_users = df.loc[df['User'] != user]
    dif = pd.merge(user_data,other_users, on='Whiskey')
    dif['Score_z'] = abs(dif['Score_x'] - dif['Score_y'])
    average_dif = dif.groupby(by='User_y', as_index= False).mean(numeric_only=True).sort_values(by='Score_z', ascending=True)
    #print(average_dif)
    ranked = average_dif['User_y'].to_list()
    statement = f"This is the list of participants based on how closely your taste aligns with theirs, from closest to furthest: {''.join([x + ', ' for x in average_dif['User_y'].iloc[:-1]])}and {average_dif['User_y'].iloc[-1]}.\n\n"
    return statement

def polarizing():
    std_devs = df.groupby('Whiskey')['Score'].std().reset_index()
    # Rename the column for clarity
    std_devs.rename(columns={'Score': 'std_dev'}, inplace=True)
    # Sort by standard deviation to compare
    std_devs = std_devs.sort_values(by='std_dev', ascending=False)

    most_polarizing = std_devs.iloc[:3]
    least_polarizing = std_devs.iloc[-3:]

    statement = f"The most polarizing bottles were {''.join([x + ', ' for x in most_polarizing['Whiskey'].iloc[:-1]])}and {most_polarizing['Whiskey'].iloc[-1]}\n"
    statement2 = f"The least polarizing bottles were {''.join([x + ', ' for x in least_polarizing['Whiskey'].iloc[:-1]])}and {least_polarizing['Whiskey'].iloc[-1]}\n\n"

    return statement, statement2

def discussion():
    average = df.groupby(by='Whiskey', as_index= False).mean(numeric_only=True)
    df_com = pd.merge(df,average, on = 'Whiskey')
    df_com['Score_z'] = df_com['Score_x'] - df_com['Score_y']
    Biggest_fan = df_com.loc[df_com['Score_z'] == df_com['Score_z'].max()]
    Biggest_hater = df_com.loc[df_com['Score_z'] == df_com['Score_z'].min()]
    statement = f"We need {Biggest_fan['User'].iloc[0]} to defend his take of {Biggest_fan['Whiskey'].iloc[0]}. This was the most disproportionately high rating of the night. He rated it {Biggest_fan['Score_x'].iloc[0]} vs. the average score of {Biggest_fan['Score_y'].iloc[0]}\n"
    statement2 = f"Also, we need {Biggest_hater['User'].iloc[0]} to defend his take of {Biggest_hater['Whiskey'].iloc[0]}. This was the most disproportionately low rating of the night. He rated it {Biggest_hater['Score_x'].iloc[0]} vs. the average score of {Biggest_hater['Score_y'].iloc[0]}\n\n"
    return statement,statement2

def efficency():
    efficient = average_ranked.sort_values(by = 'Efficiency', ascending= False)
    efficient = efficient.loc[efficient['Prices'] != 1]
    statement = f"For those who are looking for the best bang for their buck, here is the list ordered by cost efficiency (average score divided by cost):\n\n{''.join([x + ', ' for x in efficient['Combined'].iloc[:-1]])}and least efficient, {efficient['Combined'].iloc[-1]}."
    return statement


users = ['Aaron']
for x in users:
    contact = contacts['email'].loc[contacts['User'] == x].item()
    subject = f"{x}'s Whiskey Weekend Results"
    total_statement = best_bottles()[0] + best_bottles()[1] + best_rater()[0] + best_rater()[1] + harshest_critic() +  polarizing()[0] + polarizing()[1] + discussion()[0] + discussion()[1] + "Let's dive into your preferences specifcally\n\n" + favorite_and_least(x)[0] + favorite_and_least(x)[1] + taste_profile(x) + preference(x)[0] + preference(x)[1] + best_bottles(user = x)[0] + best_bottles(user = x)[1] + efficency()
    print(total_statement)
    print(contact)
    Email_Python.send_email(subject=subject, body=total_statement, to_email=contact)
    