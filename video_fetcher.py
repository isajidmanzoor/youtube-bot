# ============================================================
#   VIDEO_FETCHER.PY — Pexels se stock videos download karo
# ============================================================

import requests
import os
import time
import random
from config import PEXELS_API_KEY


def fetch_pexels_videos(search_query: str, num_clips: int = 5, output_dir: str = "output/videos/clips") -> list[str]:
    """
    Pexels API se stock video clips download karo.
    Returns: list of downloaded file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    downloaded = []

    headers = {"Authorization": PEXELS_API_KEY}

    try:
        params = {
            "query": search_query,
            "per_page": min(num_clips * 2, 20),  # extra fetch in case some fail
            "orientation": "landscape",
            "size": "medium",
            "page": random.randint(1, 10),
        }

        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        videos = data.get("videos", [])
        if not videos:
            print(f"⚠️  Pexels: No results for '{search_query}', trying fallback...")
            return fetch_pexels_videos("technology office", num_clips, output_dir)

        for i, video in enumerate(videos):
            if len(downloaded) >= num_clips:
                break

            # Best quality HD file prefer karo
            video_files = sorted(
                video.get("video_files", []),
                key=lambda x: x.get("width", 0),
                reverse=True,
            )

            # 1920 ya closest resolution lo
            chosen = None
            for vf in video_files:
                if vf.get("file_type") == "video/mp4":
                    chosen = vf
                    break

            if not chosen:
                continue

            url = chosen["link"]
            filename = os.path.join(output_dir, f"clip_{i:03d}.mp4")

            try:
                dl = requests.get(url, timeout=60, stream=True)
                dl.raise_for_status()
                with open(filename, "wb") as f:
                    for chunk in dl.iter_content(chunk_size=8192):
                        f.write(chunk)

                if os.path.getsize(filename) > 10_000:  # at least 10KB
                    downloaded.append(filename)
                    print(f"✅ Downloaded clip {len(downloaded)}: {filename}")
                else:
                    os.remove(filename)

            except Exception as e:
                print(f"⚠️  Clip {i} download failed: {e}")
                time.sleep(1)

        print(f"✅ Total clips downloaded: {len(downloaded)}")
        return downloaded

    except requests.exceptions.RequestException as e:
        print(f"❌ Pexels API error: {e}")
        return []
    except Exception as e:
        print(f"❌ fetch_pexels_videos error: {e}")
        return []
