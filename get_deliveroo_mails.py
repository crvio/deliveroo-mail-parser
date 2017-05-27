
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

import argparse
parser = argparse.ArgumentParser(parents=[tools.argparser], description='Descarga la información de entregas enviada vía correo por deliveroo')
parser.add_argument('-f','--jsonfile', help='El archivo json a escribir con la información de los correos. Default is "deliveries.json"', default='deliveries.json', required=False)
parser.add_argument('-l','--label', help='La etiqueta usada para identificar los correos de deliveroo. Defaults to "entrega-deliveroo"', default='entrega-deliveroo', required=False)
flags = vars(parser.parse_args())


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

    all_labels = service.users().labels().list(userId='me').execute()

    search_label = next(x['id'] for x in all_labels['labels'] if x['name'] == flags['label'])
    #search_label = 'Label_15' # entrega-deliveroo
    citycode = {'Berlin':8}

    results = service.users().threads().list(userId='me',labelIds=search_label).execute()
    hilos = results.get('threads', [])

    while 'nextPageToken' in results:
        page_token = results['nextPageToken']
        results = service.users().threads().list(userId='me',labelIds=search_label, pageToken=page_token).execute()
        hilos.extend(results.get('threads', []))

    if os.path.isfile(flags['jsonfile']):
        f = open(flags['jsonfile'], 'r')
        deliveries = json.load(f)
        f.close()
    else:
        deliveries = []

    nres = 0
    nres_new = 0

    transl = {'Geliefert um': 'date', 'Lieferzeit': 'deltime', 'Restaurant': 'restaurant', 'Restaurantadresse': 'r_address', 'Restaurant Telefon': 'r_tel', 'Trinkgeld (Kreditkarte)': 'tip_cc'}

    if not hilos:
        print('No threads found.')
    else:
        print('Messages:')
        thread_ids = [delivery['thread_id'] for delivery in deliveries]
        for hilo in hilos:
            if not hilo['id'] in thread_ids:
                thread = service.users().threads().get(userId='me', id=hilo['id'], format='full').execute()
                mail_string = str(base64.urlsafe_b64decode(thread['messages'][0]['payload']['body']['data'].encode('UTF8')))
                ms_lines = mail_string.split('\\r\\n')
                delivery_info = {}
                delivery_info['thread_id'] = hilo['id']
                for ms_line in ms_lines:
                    match_field = re.search('([^:]*): (.*)',ms_line)
                    match_nr = re.search('Bestellung #([0-9]+) geliefert',ms_line)
                    if match_field:
                        delivery_info[transl[match_field.group(1)]]=match_field.group(2)
                    elif match_nr:
                        delivery_info['daily_id']=match_nr.group(1)
                delivery_info['deltime_s'] = minsec2sec(delivery_info['deltime'])
                deldate=datetime.datetime.strptime(delivery_info['date'],'%Y-%m-%d %H:%M:%S')
                delivery_info['id']= int(delivery_info['daily_id'])+10000*deldate.hour+1000000*deldate.day+100000000*deldate.month+10000000000*(deldate.year%100)+1000000000000*citycode['Berlin']
                deliveries.append(delivery_info)
                nres_new=nres_new+1
            nres=nres+1
    print(nres)
    print("%d of them are new." % nres_new)

    f = open(flags['jsonfile'], 'w')
    json.dump(deliveries, f)
    f.close()


def minsec2sec(s):
    """ Parsea un string con minutos y segundos y devuelve el numero
        de segundos correspondiente
        s: es un string describiendo el tiempo con formato 'MMm SSs'
    """
    match = re.search('([0-9]+)m ([0-9]+)s', s)
    if match:
        return int(match.group(1)) * 60 + int(match.group(2))
    else:
        return -1

if __name__ == '__main__':
    main()
