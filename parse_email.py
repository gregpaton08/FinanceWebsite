#!/usr/bin/env python

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import base64   # used to decode base64url encoded email body
import string   # used to remove punctuation from date string
import datetime # used to parse bill due date
from lxml import html


def get_credentials():
    SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
    CLIENT_SECRET = 'client_id.json'

    # Retrieve credential from file.
    store = file.Storage('storage.json')
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET, SCOPES)
        credentials = tools.run_flow(flow, store)
    return credentials

def get_gmail_service(credentials=None):
    if not credentials:
        credentials = get_credentials()
    return build('gmail', 'v1', http=credentials.authorize(Http()))

def get_subject_for_message(message):
    return next((header for header in message['payload']['headers'] if header.get('name', '') == 'Subject'), {} ).get('value', 'email has not subject')

def get_body_for_message(message):
    body_data = message['payload']['body'].get('data', '')
    if len(body_data) == 0:
        # If the body is empty the email may have been sent in parts: html, plain text, etc.
        parts = message['payload']['parts']
        # Try to get the HTML part if available.
        part = next((part for part in parts if part['mimeType'] == 'text/html'), None)
        # Otherwise just take the first part
        if not part:
            part = parts[0]

        body_data = part.get('body', {}).get('data', '')
    return base64.urlsafe_b64decode(body_data.encode('utf-8'))

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
    
    due_date = datetime.datetime.strptime(due_date, '%B %d %Y').date()
    # parse the date into a datetime object and decrement the month to get the correct billing cycle
    billing_cycle_date = due_date.replace(day=1) + datetime.timedelta(days=-1)

    return {
        'account' : 'PSE&G',
        'balance' : balance,
        'due_date' : due_date,
        'billing_cycle' : billing_cycle_date,
        'paid_date' : None
    }

def parse_citi_message(message_body):
    # print(message_body)
    # Verify that this email contains statement information.
    body_search_term = 'statement'
    if not body_search_term in message_body.lower():
        return None

    tree = html.fromstring(message_body)

    query = '//td[text()[contains(., "Statement Date")]]/child::node()[contains(., "Statement Date")]/following-sibling::node()[1]'
    # query = '//td[text()[contains(., "Statement Date")]]/text()[2]/following-sibling::text()[1]'
    # query = '//child::text()[contains(., "Statement Date")]/'
    # query = '//*[text()[contains(., "Statement")]]/child::text()[contains(., "Statement")]'
    # query = '//td[contains(text(), "Statement")]'
    # query = '//td[text()[contains(., "Statement Date")]]/text()'
    # query = '//td[text()[contains(., "Statement Date")]]'
    # query = '//td/text()[contains(., "Statement Date")]'
    # query = '//[text()[contains(., "Statement Date")]]/text()'
    # query = '//td/b[contains(text(), "Double Cash Card")]/../child::text()'
    # query = '//td/*[contains(text(), "State")]/text()'
    # query = '//td[contains(text(), "lease")]/text()'
    # query = '//td[contains(text(), "Statement Balance:")]/text()'
    # result = tree.xpath(query)[0].encode('ascii', 'ignore')
    # print(result)
    results = tree.xpath(query)
    print(len(results))
    for result in results:
        print('===============')
        print(type(result))
        # print(result.encode('ascii', 'ignore'))
        print(result.text_content())
        # print(result)

    # body_text.replace('<br />', '\n')

    # body_lines = body_text.split('\n')

    # print(len(body_lines))

    # balance = 0.0
    # for line in body_lines:
    #     if 'Statement Balance: ' in line:
    #         balance = line[line.rfind('$') + 1:]
    #         balance = balance[:balance.find('<')]
    #         print(balance)

    # billing_cycle = None
    # for line in body_lines:
    #     print(line)
    #     if 'Statement' in line:
    #         print(line)

    return None

def print_bill_info(bill_info):
    print('Account:       ' + bill_info['account'])
    print('Balance:       ' + bill_info['balance'])
    print('Billing cycle: ' + bill_info['billing_cycle'].strftime('%B %Y'))
    print('Due date:      ' + bill_info['due_date'].strftime('%d %B %Y'))


# gmail_service = get_gmail_service()

query_terms = {
    'from:' : 'alerts@citibank.com'
    # 'from:' : 'myaccount@pseg.com'
}

query = ''
for key, val in query_terms.iteritems():
    query += key + val + ' '

# todo: update query to only check for emails with a date after the last time the script was called
# Get a list of the message IDs using the list() method. Still need to get the message using the get() method and passing the ID.
message_ids = [0]#gmail_service.users().messages().list(userId='me', q=query).execute().get('messages', [])
for message_id in message_ids:
    # message = gmail_service.users().messages().get(userId='me', id=message_id['id']).execute()

    # subject = get_subject_for_message(message)

    body_text = ''#get_body_for_message(message)
    with open('citi.html', 'r') as file:
        body_text = file.read();
    # with open('citi.html', 'w') as file:
    #     file.write(body_text)
    # print(body_text)

    bill_info = parse_citi_message(body_text)
    
    # bill_info = parse_pseg_message(body_text)
    # print_bill_info(bill_info)
