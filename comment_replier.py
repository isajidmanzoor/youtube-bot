import pickle
import requests
from googleapiclient.discovery import build

def get_youtube_service():
    with open('youtube_token.pickle', 'rb') as f:
        creds = pickle.load(f)
    return build('youtube', 'v3', credentials=creds)

def get_unanswered_comments(video_id, max_results=10):
    youtube = get_youtube_service()
    own_id = None
    try:
        own_id = youtube.channels().list(part='id', mine=True).execute()['items'][0]['id']
    except Exception:
        pass
    try:
        response = youtube.commentThreads().list(
            part='snippet,replies',
            videoId=video_id,
            maxResults=max_results,
            order='time'
        ).execute()
        unanswered = []
        for item in response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']
            reply_count = item['snippet']['totalReplyCount']
            author_channel = comment.get('authorChannelId', {}).get('value')
            if own_id and author_channel == own_id:
                continue
            if reply_count == 0:
                unanswered.append({
                    'id': item['snippet']['topLevelComment']['id'],
                    'text': comment['textDisplay'],
                    'author': comment['authorDisplayName']
                })
        return unanswered
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_reply(comment_text, author, topic):
    from config import GROQ_API_KEY, GROQ_MODEL
    prompt = f"You are a friendly crypto YouTuber. Reply to this comment on your video about {topic}. Comment from {author}: {comment_text}. Write SHORT friendly 1-2 sentence reply only."
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": GROQ_MODEL, "reasoning_effort": "low", "messages": [{"role": "user", "content": prompt}], "max_tokens": 80, "temperature": 0.8}
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=15)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Reply gen failed: {e}")
    return "Thanks for watching! Subscribe for more crypto tips!"

def post_reply(comment_id, reply_text):
    youtube = get_youtube_service()
    try:
        youtube.comments().insert(part='snippet', body={'snippet': {'parentId': comment_id, 'textOriginal': reply_text}}).execute()
        return True
    except Exception as e:
        print(f"Post reply failed: {e}")
        return False

def reply_to_comments(video_id, topic, max_replies=5):
    comments = get_unanswered_comments(video_id, max_results=max_replies)
    replied = 0
    for comment in comments:
        reply = generate_reply(comment['text'], comment['author'], topic)
        if post_reply(comment['id'], reply):
            print(f"Replied to {comment['author']}: {reply[:50]}...")
            replied += 1
    print(f"Total replies: {replied}")
    return replied