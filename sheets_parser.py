import gspread
from oauth2client.service_account import ServiceAccountCredentials


def parse_sheets_links(sheet_key, credentials_file):
    try:
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_file, scope)
        client = gspread.authorize(credentials)

        sheet = client.open_by_key(sheet_key).sheet1

        range_to_clear = sheet.range("B2:E100")

        for cell in range_to_clear:
            cell.value = ''

        sheet.update_cells(range_to_clear)

        links = sheet.col_values(1)[1:]

        result = [[i + 2, link] for i, link in enumerate(links)]

        return result

    except Exception as e:
        print(f"Error parsing Google Sheets links: {e}")
        return None
