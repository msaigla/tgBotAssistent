import os
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from gspread_formatting import set_column_width
import os
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from gspread_formatting import set_column_width

load_dotenv()
scopes = [
    'https://www.googleapis.com/auth/spreadsheets'
]
creds = Credentials.from_service_account_file("GoogleSheetApi.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = os.getenv('ID_SHEET')
workbook = client.open_by_key(sheet_id)

worksheet_list = map(lambda x: x.title, workbook.worksheets())
worksheet_name = os.getenv('SHEET_NAME')

if worksheet_name in worksheet_list:
    sheet = workbook.worksheet(worksheet_name)
else:
    values_title = [
        "id чата",
        "Имя",
        "Пол",
        "Город/Область",
        "Где практикует массаж?",
        "Были клиенты?",
        "Техника массажа",
        "Уверенность в соцсетях",
        "Уверенность"
    ]

    sheet = workbook.add_worksheet(worksheet_name, 3, len(values_title))
    sheet.append_row(values_title)
    sheet.format("A1:J1", {"textFormat": {"bold": True}})
    set_column_width(sheet, 'A:J', 200)


async def add_new_user(values: list):
    return sheet.append_row(values)['updates']['updatedRange'].split(':')[0].replace("'Клиенты'!", '')


async def delete_user_from_sheet(chat_id):
    try:
        cell = sheet.find(str(chat_id), in_column=1)
        sheet.delete_rows(int(cell.row), int(cell.row))
    except:
        pass


async def new_many_clients_user(chat_id, clients: str):
    cell = sheet.find(str(chat_id), in_column=1)
    sheet.update_cell(int(cell.row), 6, clients)


async def new_fell_user(chat_id, fell: str):
    cell = sheet.find(str(chat_id), in_column=1)
    sheet.update_cell(int(cell.row), 9, fell)


