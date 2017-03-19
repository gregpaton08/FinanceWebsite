#!/usr/bin/env python

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import base64   # used to decode base64url encoded email body
import string   # used to remove punctuation from date string
import datetime # used to parse bill due date


def get_subject_for_message(message):
    return next((header for header in message['payload']['headers'] if header.get('name', '') == 'Subject'), {} ).get('value', 'email has not subject')

def get_body_for_message(message):
    body_data = message['payload']['body'].get('data', '')
    return base64.urlsafe_b64decode(body_data.encode('ascii'))

def parse_pseg_message(message_body):
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
                due_date = line[line.find(due_date_search_token) + len(due_date_search_token):]
                due_date = due_date.translate(None, string.punctuation)
            break
    
    # parse the date into a datetime object and decrement the month to get the correct billing cycle
    billing_cycle_date = datetime.datetime.strptime(due_date, '%B %d %Y').date().replace(day=1) + datetime.timedelta(days=-1)

    return {
        'account' : 'PSE&G',
        'balance' : balance,
        'due_date' : due_date,
        'billing_cycle' : billing_cycle_date,
        'paid_date' : None
    }



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

    subject = get_subject_for_message(message)

    body_text = get_body_for_message(message)
    
    bill_info = parse_pseg_message(body_text)
    

    print(subject)
    print('Balance: ' + bill_info['balance'])
    print('Billing cycle: ' + bill_info['billing_cycle'].strftime('%d %B %Y'))
    print('Due date: ' + bill_info['due_date'])
