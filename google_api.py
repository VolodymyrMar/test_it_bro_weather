import os.path
from googleapiclient.discovery import build
from google.oauth2 import service_account


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SAMPLE_SPREADSHEET_ID = '1U7EdNXXZ0wIkY65VaFsGOyhLseXx_Gn65iLWYSegokw'
SAMPLE_RANGE_NAME = 'Sheet_1'


def make_weather_record(column, city, precipitation):
    credentials = service_account.Credentials.from_service_account_file(
        filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'credentials.json'
        ),
        scopes=SCOPES,
    )

    service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()

    service.get(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=SAMPLE_RANGE_NAME,
    ).execute()

    # data_from_sheet = result.get('values', [])
    service.update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=f'{SAMPLE_RANGE_NAME}!A{column}:C{column}',
        valueInputOption='USER_ENTERED',
        body={'values': [[city, precipitation, '2']]},
    ).execute()
