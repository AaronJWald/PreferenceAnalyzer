# Preference Analyzer
## A Python tool that allows multiple users to assign scores to items, then process the data for unique insights about the individual and the group.

This project utilizes google sheets to allow users to give a score from 0 to 100 of an item in question. The setup function creates google sheets for each user and emails the individual's sheet to them. Once preference scoring is complete, the aggregation script pulls all of the user data and processes it for analysis. This project is currently configured for a whiskey tasting, but response strings can be edited to fit any type of event.

You will need a google service account (free) with Google Sheets API enabled and an SMTP account to be able to email the results to each participant.

## Features:
 ### Automated Google Sheets Integration
 - Creates a dedicated Google Sheet for each participant.
 - Automatically populates each sheet with whiskey identifiers (either names or blind labels).
 - Assigns a randomized score for testing and prevents API rate limits.

 ### Centralized Data Aggregation
 - Fetches and compiles all participant ratings into a master dataset.
 - Ensures scores are properly formatted (0-100 range).
 - Supports blind testing mode, replacing labels with letters. The correct labels can be pushed from the primary function later.

 ### Personalized and Group Insights
 - Ranking System: Orders whiskeys from best to worst based on average ratings.
 - Personalized Reports: Each participant receives their own customized breakdown via email.
 - Most/Least Polarizing Whiskeys: Identifies controversial bottles based on rating variance.
 - Cost Efficiency Analysis: Highlights whiskeys that provide the best value for their price.
 - Personalized Taste Match: Identifies which individuals you agree and disagree with the most.
 - Biggest Discrepency: Highlights the individual ratings with the highest distance from the group consensus.

 ### Email Reports
 - Their personal rating trends.
 - How their scores compare to the group.
 - Their most loved and hated whiskeys.
 - A ranked list of all whiskeys tasted.

## Installation and configuration
 ### Clone this repository
 ```
 git clone https://github.com/AaronJWald/PreferenceAnalyzer.git
 cd whiskey-weekend
 ```
 ### Install Dependencies
 ```
 pip install -r requirements.txt
 ```
 ### Configure config.ini
 - Path to your google api credentials
 - Input your email address and smtp password
 - Edit your userlist to include all of the people participating

 ### Run setup.py
 - This will create two critical files, contacts.csv and url.csv
  - In contacts.csv, add the email addresses for each user that you would like to email.
 - There is currently a built-in delay to stay within Google's Free Tier rate limits. Anticipated runtime is about 30 seconds per person.
 - After the setup is complete and you have entered the email addresses into contacts.csv, uncomment the email_users function at the bottom and run the script again to share each file with the respective user.

 ### Go through all of the things you are rating

 ### Run Whiskey_Sheet_Aggregation
 
 ### If you did a blind test, go to setup.py and re-comment out email_users and uncomment the reveal() function, and run the script again to reveal items.

