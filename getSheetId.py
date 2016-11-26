from __future__ import print_function
import httplib2
import os

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
# at .credentials
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = '.credentials/client_id.json'
APPLICATION_NAME = 'Sheet ID Getter'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    app_dir = os.path.dirname(os.path.realpath(__file__))
    credential_dir = os.path.join(app_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'user_secret.json')
    
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
    """
    Creates a Sheets API service object
    Queries the file of interest for worksheet ids, and stores it into a dictionary
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1nWhZWZcXNUmzFMGcN7ehcFOZkRF8kgw5GyY-Z6x-0mA'
    result = service.spreadsheets().get(spreadsheetId=spreadsheetId).execute()

    params_dict = {}

    if not result:
        print('GET request failed. Check file_id for correctness.')
    else:
        for sheet in result["sheets"]:
            params_dict[sheet["properties"]["title"]] = str(sheet["properties"]["sheetId"])
    print(params_dict)
    return params_dict

if __name__ == '__main__':
    main()