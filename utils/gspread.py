import gspread
from google.oauth2.service_account import Credentials

def setup_gspread():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_file("g-auth.json", scopes=scopes)
    client = gspread.authorize(credentials)
    return client