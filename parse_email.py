#!/usr/bin/env python

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import base64   # used to decode base64url encoded email body
import string   # used to remove punctuation from date string
import datetime # used to parse bill due date


def get_subject_for_message(message):
    return next((header for header in message['payload']['headers'] if header.get('name', '') == 'Subject'), {} ).get('value', 'email has not subject')

# def get_body_for_message(message):
#     body_data = message


SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET = 'client_id.json'

store = file.Storage('storage.json')
credentials = store.get()
if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET, SCOPES)
    credentials = tools.run_flow(flow, store)

GMAIL = build('gmail', 'v1', http=credentials.authorize(Http()))

query_terms = {
    'from:' : 'myaccount@pseg.com'
}

query = ''
for key, val in query_terms.iteritems():
    query += key + val + ' '

# todo: update query to only check for emails with a date after the last time the script was called
# Get a list of the message IDs using the list() method. Still need to get the message using the get() method and passing the ID.
message_ids = GMAIL.users().messages().list(userId='me', q=query).execute().get('messages', [])
for message_id in message_ids:
    message = GMAIL.users().messages().get(userId='me', id=message_id['id']).execute()

    print(get_subject_for_message(message))

    # print the body of the email
    body_data = message['payload']['body'].get('data', None)
    if body_data:
        body_text = base64.urlsafe_b64decode(body_data.encode('ascii'))
        
        balance = ''
        balance_search_token = 'current balance of $'
        due_date = None
        due_date_search_token = 'is due on '
        body_lines = body_text.split('<br />')
        for line in body_lines:
            if balance_search_token in line:
                balance = line[line.find(balance_search_token) + len(balance_search_token):]
                balance = balance[:balance.find(' ')]
                if due_date_search_token in line:
                    date = line[line.find(due_date_search_token) + len(due_date_search_token):]
                    date = date.translate(None, string.punctuation)
                break
        
        # parse the date into a datetime object and decrement the month to get the correct billing cycle
        billing_cycle_date = datetime.datetime.strptime(date, '%B %d %Y').date().replace(day=1) + datetime.timedelta(days=-1)
        
        print('Balance: ' + balance)
        print(billing_cycle_date)
