
import httplib2
import os
import datetime
import base64
from email.mime.text import MIMEText

from apiclient import discovery, errors
import oauth2client
from oauth2client import client
from oauth2client import tools

SCOPES = 'https://www.googleapis.com/auth/gmail.compose'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'

service = None

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_gmail_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    return service

def get_mails_with_query(gmail_service, mail_query):
    
    try:
        response = service.users().messages().list(userId = 'me', q = mail_query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId = 'me', q = mail_query, pageToken=page_token).execute()
            messages.extend(response['messages'])
        
        return messages
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
        
def get_attachment_from_mail(gmail_service, mail_id):
    try:
        message = gmail_service.users().messages().get(userId='me', id=mail_id).execute()
        for part in message['payload']['parts']:
            if part['filename']:
                if 'data' in part['body']:
                    data = part['body']['data']
                else:
                    att_id=part['body']['attachmentId']
                    att=service.users().messages().attachments().get(userId='me', messageId=mail_id,id=att_id).execute()
                    data=att['data']
                    
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
        
def create_email(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_string())}

def send_email(formatted_message_text):
    try:
        message = (service.users().messages().send(userId='me', body=formatted_message_text).execute())
        print 'Message Id: %s' % message['id']
        return message
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
    
        

if __name__ == '__main__':
#     today_string = datetime.date.today().strftime("%Y/%m/%d")
    service = get_gmail_service()
#     query = 'label:report from:(android.testing@shadowfax.in) after:2016/1/29 before:2016/2/1'
#     messages_list = get_mails_with_query(service, query)
#     for messages in messages_list:
#         get_attachment_from_mail(service, messages['id'])

    message_text = create_email('varnan.k@shadowfax.in', 'varnan.k.nair@gmail.com', 'Reaching Late', 'Hi Team HR! As usual, I will reach after 11 :PM')
    send_email(message_text)
    