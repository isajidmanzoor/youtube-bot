# ============================================================
#   YOUTUBE_UPLOADER.PY — YouTube Data API v3 se upload karo
# ============================================================

import os
import time
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import (
    YOUTUBE_CLIENT_SECRET,
    VIDEO_LANGUAGE,
    VIDEO_CATEGORY_ID,
    VIDEO_PRIVACY,
)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "youtube_token.pickle"


def _get_authenticated_service():
    """OAuth2 credentials lo, cached token use karo."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(YOUTUBE_CLIENT_SECRET):
                raise FileNotFoundError(
                    f"❌ '{YOUTUBE_CLIENT_SECRET}' not found!\n"
                    "Google Cloud Console se download karo:\n"
                    "  APIs & Services → Credentials → OAuth 2.0 Client IDs → Download JSON\n"
                    f"  Aur '{YOUTUBE_CLIENT_SECRET}' naam se is folder mein rakh do."
                )
            flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=8080, open_browser=True)

        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
        print("✅ YouTube auth token saved")

    return build("youtube", "v3", credentials=creds)


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    thumbnail_path: str = None,
    privacy: str = None,
    max_retries: int = 3,
) -> str | None:
    """
    YouTube pe video upload karo.
    Returns: YouTube video ID or None on error
    """
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return None

    privacy = privacy or VIDEO_PRIVACY

    # Title 100 chars max, description 5000 chars max
    title = title[:100]
    description = description[:5000]

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags[:500],  # YouTube tag limit
            "categoryId": VIDEO_CATEGORY_ID,
            "defaultLanguage": VIDEO_LANGUAGE,
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    for attempt in range(1, max_retries + 1):
        try:
            service = _get_authenticated_service()

            media = MediaFileUpload(
                video_path,
                mimetype="video/mp4",
                resumable=True,
                chunksize=4 * 1024 * 1024,  # 4MB chunks
            )

            request = service.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    pct = int(status.progress() * 100)
                    print(f"  ⬆️  Uploading... {pct}%", end="\r")

            video_id = response["id"]
            print(f"\n✅ Uploaded! https://youtube.com/watch?v={video_id}")

            # Set thumbnail if provided
            if thumbnail_path and os.path.exists(thumbnail_path):
                try:
                    service.thumbnails().set(
                        videoId=video_id,
                        media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg"),
                    ).execute()
                    print(f"✅ Thumbnail set for {video_id}")
                except Exception as te:
                    print(f"⚠️  Thumbnail upload failed: {te}")

            return video_id

        except Exception as e:
            print(f"❌ Upload attempt {attempt} failed: {e}")
            if attempt < max_retries:
                wait = 30 * attempt
                print(f"   Retrying in {wait}s...")
                time.sleep(wait)

    print("❌ All upload attempts failed")
    return None
