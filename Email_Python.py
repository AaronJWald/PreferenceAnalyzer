import matplotlib.pyplot as plt
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email import encoders
from os.path import basename
import configparser

# Replace with the path to your JSON credentials file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Path to the config.ini file
config_path = os.path.join(current_dir, 'config.ini')
config = configparser.ConfigParser()
config.read('config.ini')
email_address = config['Data']['default_email']

#This import list is a bit heavier duty than you need for this program. Much of this functionality is
#used in my other projects.
def send_email(subject, body, to_email, filename = None):
    # Your email and password (use an app password if using Gmail)
    email_address = config['Data']['default_email']
    email_password = config['Data']['email_pass']

    # Set up the MIME
    message = MIMEMultipart()
    message['From'] = email_address
    message['To'] = to_email
    message['Subject'] = subject

    # Attach the body of the email
    message.attach(MIMEText(body, 'plain'))

    #This is for adding a graph if you would like to email one out.
    if filename != None:    
        with open(filename, "rb") as attachment:
    # MIMEImage object for the PNG image
            part = MIMEImage(attachment.read(), name="graph.png")
            part.add_header("Content-Disposition", "attachment", filename="Performance.png")
            message.attach(part)

    # Connect to the SMTP server (in this case, Gmail's SMTP server)
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        # Start the TLS encryption
        server.starttls()

        # Login to the email account
        server.login(email_address, email_password)

        # Send the email
        server.sendmail(email_address, to_email, message.as_string())

# Example usage
if __name__ == "__main__":
    subject = 'Your automated email!'
    body = 'Well Done!'
    to_email = email_address

    send_email(subject, body, to_email)
