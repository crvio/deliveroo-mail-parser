
from __future__ import print_function
import httplib2
import os
import base64
import string
import re
import json
import datetime

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


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

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    search_label = 'Label_15' # entrega-deliveroo
    citycode = {'Berlin':8}

    #results = service.users().labels().list(userId='me').execute()
    #results = service.users().messages().list(userId='me',labelIds=search_label).execute()
    results = service.users().threads().list(userId='me',labelIds=search_label).execute()
    hilos = results.get('threads', [])

    while 'nextPageToken' in results:
        page_token = results['nextPageToken']
        results = service.users().threads().list(userId='me',labelIds=search_label, pageToken=page_token).execute()
        hilos.extend(results.get('threads', []))

    #print(type(threads))
    #print(type(threads[0]))
    #print(threads[0].keys())
    #print(type(threads[0]['id']))
    #print(type(threads[0]['threadId']))
    nres=0
    mail_strings=[]

    if not hilos:
        print('No threads found.')
    else:
      print('Messages:')
      for hilo in hilos:
        #print(message['id'],message['threadId'])
        thread = service.users().threads().get(userId='me', id=hilo['id'], format='full').execute()
        mail_strings.append(str(base64.decodebytes(thread['messages'][0]['payload']['body']['data'].encode())))
        #mail_strings.append(base64.decodestring(thread['messages'][0]['payload']['body']['data'])) # this works in python 2.7
        nres=nres+1
    print(nres)

    f = open('deliveries.json', 'w')

    transl = {'Geliefert um':'date', 'Lieferzeit':'deltime', 'Restaurant':'restaurant', 'Restaurantadresse':'r_address', 'Restaurant Telefon':'r_tel', 'Trinkgeld (Kreditkarte)':'tip_cc'}
    deliveries = []

    for mail_string in mail_strings:
        #f.write(mail_string)
        ms_lines=mail_string.split('\\r\\n')
        #ms_lines=string.split(mail_string,'\r\n') # this works in python 2.7
        delivery_info = {}
        for ms_line in ms_lines:
            match_field = re.search('([^:]*): (.*)',ms_line)
            match_nr = re.search('Bestellung #([0-9]+) geliefert',ms_line)
            if match_field:
                delivery_info[transl[match_field.group(1)]]=match_field.group(2)
            elif match_nr:
                delivery_info['daily_id']=match_nr.group(1)
        deliveries.append(delivery_info)

    for delivery in deliveries:
        delivery['deltime_s']=minsec2sec(delivery['deltime'])
        deldate=datetime.datetime.strptime(delivery['date'],'%Y-%m-%d %H:%M:%S')
        delivery['id']= int(delivery['daily_id'])+10000*deldate.hour+1000000*deldate.day+100000000*deldate.month+10000000000*(deldate.year%100)+1000000000000*citycode['Berlin']

    json.dump(deliveries,f)
    f.close()

def minsec2sec(s):
    """ Parsea un string con minutos y segundos y devuelve el numero
        de segundos correspondiente
        s: es un string describiendo el tiempo con formato 'MMm SSs'
    """
    match = re.search('([0-9]+)m ([0-9]+)s',s)
    if match:
        return int(match.group(1))*60 + int(match.group(2))
    else:
        return -1

if __name__ == '__main__':
    main()
