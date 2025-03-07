import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime as dt
import pandas as pd
import random as rd
import os
from whiskey_bottles import bottles_key
from whiskey_bottles import letters
import time

# Replace with the path to your JSON credentials file
creds_path = 'Path_to_your_google_api_cred_file_here'
Whiskey_locations = pd.DataFrame(columns=['User','URL'])
New_Whiskey_locations = pd.DataFrame(columns=['User','URL'])

# Replace with your Google Sheets document name and sheet name
document_name = "Whiskey Weekend"
sheet_name = 'Sheet1'

# Replace with the list of users
#This allows more dynamic control if this is used through multiple weekends
user_list = ['list','of','user','names']

# Use credentials to create a gspread authorized client
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(credentials)

#This file should hold name as well as the url to the google sheet they use to rate. This file gets generated by
#the script, but this method allows me to check if a file exists or not without generating a new one each time
file_path = 'C:/Path/To/Whiskey_urls.csv'

contacts = pd.read_csv('C:/Path/To/contacts.csv')


def remove_elements_from_list_a(list_a, list_b):
    return [x for x in list_a if x not in list_b]

def mainsetup():
    if os.path.exists(file_path):
        print("The file exists!")
        
        existing_sheet = pd.read_csv(file_path)
        existing_sheet.reset_index(drop=True)
        existing_user = existing_sheet['User'].to_list()
        print(f"{existing_user} already exist!")
        user_list_new = remove_elements_from_list_a(user_list,existing_user)
        for user in user_list_new:
            # Create a new worksheet for the user
            spreadsheet = client.create(f"{user}'s Whiskey Ratings")
            user_worksheet = spreadsheet.sheet1
            user_worksheet.update_title(f'{user}')

            # Set up the headers in the new worksheet
            user_worksheet.update_cell(1, 1, "Whiskey")
            user_worksheet.update_cell(1, 2, "Score")

            #Important! My friends wanted to do a blind taste test, and so I incorporated this method which filled the google sheets with letters instead of
            #names, you can replace this with bottles_key in the event you'd rather just have the bottle names in front of you.
            #
            for x in range(len(letters)): 
                user_worksheet.update_cell((x+2), 1, letters[x])
                user_worksheet.update_cell((x+2), 2, rd.randint(1,100))
            #I use the sleep function here to prevent running into rate limits from Google's api
            time.sleep(60)
            # Set the formula in cell A2
            spreadsheet.share('yourEmail@email.com', perm_type='user', role='writer')
            
            #Appends the newly created url to the whiskey url sheet
            New_Whiskey_locations.loc[len(New_Whiskey_locations)] = [user, spreadsheet.url]
            New_Whiskey_locations.reset_index(drop=True)

        combined = pd.concat([existing_sheet,New_Whiskey_locations], ignore_index=True)
        combined.to_csv('C:/Users/Aaron/OneDrive/Documents/Fiverr_projects/Whiskey_Project/Whiskey_urls.csv')
    else:
        print("The file doesn't exist! Main setup starting")
        for user in user_list:
            # Create a new worksheet for the user
            spreadsheet = client.create(f"{user}'s Whiskey Ratings")
            user_worksheet = spreadsheet.sheet1
            user_worksheet.update_title(f'{user}')

            # Set up the headers in the new worksheet
            user_worksheet.update_cell(1, 1, "Whiskey")
            user_worksheet.update_cell(1, 2, "Score")


            for x in range(len(letters)): 
                user_worksheet.update_cell((x+2), 1, letters[x])
                user_worksheet.update_cell((x+2), 2, rd.randint(1,100))
            time.sleep(60)
            # Set the formula in cell A2
            spreadsheet.share('yourEmail@email.com', perm_type='user', role='writer')
            
        Whiskey_locations.loc[len(New_Whiskey_locations)] = [user, spreadsheet.url]
        Whiskey_locations.to_csv(file_path)

#In the event there are late adds, this function will go through all existing sheets and append the new bottles to them. New bottles should be a list, even if only one
#is added. If this were going into production, I would definitely raise an exception here, but for now, I will settle for knowing it should be a list.
def additional_bottles(new_bottles, user = 'All'):
    existing_sheet = pd.read_csv(file_path)
    if user == 'All':
        users = existing_sheet['User'].to_list()
    
        for user in users:
            spreadsheet = client.open_by_url(existing_sheet['URL'].loc[existing_sheet['User'] == user])
            worksheet = spreadsheet.sheet1
            last_row = len(worksheet.get_all_values())

# Append new bottles to the "Whiskey" column
            for bottle in new_bottles:
                worksheet.update_cell(last_row + 1, 1, bottle)
                last_row += 1
    else:
        spreadsheet = client.open_by_url(existing_sheet['URL'].loc[existing_sheet['User'] == user])
        worksheet = spreadsheet.sheet1
        last_row = len(worksheet.get_all_values())

# Append new bottles to the "Whiskey" column
        for bottle in new_bottles:
            worksheet.update_cell(last_row + 1, 1, bottle)
            last_row += 1
pass

#running mainsetup() should create the files for you to modify.
mainsetup()
#additional_bottles()