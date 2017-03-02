#!/usr/bin/env python

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import base64

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
    body = data['payload']['body']
    body_data = body.get('data', None)
    if body_data:
        print(base64.urlsafe_b64decode(body_data.encode('ascii') + '==='))