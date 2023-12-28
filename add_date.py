import gspread
from oauth2client.service_account import ServiceAccountCredentials


def write_date_to_sheets(sheet_key, date, row):
    try:
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json", scope)
        client = gspread.authorize(credentials)

        sheet = client.open_by_key(sheet_key).sheet1

        for i, item in enumerate(date):
            try:
                sheet.update_cell(row, i + 2, item)
            except Exception as update_error:
                print(f"Error updating Google Sheets cell: {update_error}")

    except Exception as e:
        print(f"Error writing links to Google Sheets: {e}")
