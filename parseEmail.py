#!/usr/bin/env python

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import base64
import string

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET = 'client_id.json'

store = file.Storage('storage.json')
credentials = store.get()
if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET, SCOPES)
    credentials = tools.run_flow(flow, store)

GMAIL = build('gmail', 'v1', http=credentials.authorize(Http()))

messages = GMAIL.users().messages().list(userId='me', q='from:myaccount@pseg.com').execute().get('messages', [])
for message in messages:
    data = GMAIL.users().messages().get(userId='me', id=message['id']).execute()
    
    # print the subject of the email
    for header in data['payload']['headers']:
        if header['name'] == 'Subject':
            print(header['value'])
            
    # print the body of the email
    body_data = data['payload']['body'].get('data', None)
    if body_data:
        body_text = base64.urlsafe_b64decode(body_data.encode('ascii'))
        
        # save as html file
        with open('temp.html', 'w') as html_file:
            html_file.write(body_text)
        
        balance = ''
        date = None
        balance_search_token = 'current balance of $'
        date_search_token = 'is due on '
        body_lines = body_text.split('<br />')
        for line in body_lines:
            if balance_search_token in line:
                balance = line[line.find(balance_search_token) + len(balance_search_token):]
                balance = balance[:balance.find(' ')]
                if date_search_token in line:
                    date = line[line.find(date_search_token) + len(date_search_token):]
                    date = date.translate(None, string.punctuation)
                break
        
        print('Balance: ' + balance)
        print('Date:    ' + date)
