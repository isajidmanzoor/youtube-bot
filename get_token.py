
import os, pickle, base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl", "https://www.googleapis.com/auth/youtube"]

def main():
    if not os.path.exists("client_secret.json"):
        print("client_secret.json not found!")
        return
    creds = None
    if os.path.exists("youtube_token.pickle"):
        with open("youtube_token.pickle", "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=8080, open_browser=True)
        with open("youtube_token.pickle", "wb") as f:
            pickle.dump(creds, f)
    print("Token saved!")
    with open("youtube_token.pickle", "rb") as f:
        token_b64 = base64.b64encode(f.read()).decode()
    with open("client_secret.json") as f:
        secret_json = f.read().strip()
    with open("GITHUB_SECRETS.txt", "w") as f:
        f.write("YOUTUBE_TOKEN_B64:\n" + token_b64 + "\n\nYOUTUBE_CLIENT_SECRET_JSON:\n" + secret_json)
    print("Done! Check GITHUB_SECRETS.txt")

main()
