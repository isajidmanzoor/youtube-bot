# ============================================================
#   VIDEO_FETCHER.PY — Pexels se stock videos download karo
# ============================================================

import requests
import os
import time
import random
from config import PEXELS_API_KEY


def fetch_pexels_videos(search_query: str, num_clips: int = 5, output_dir: str = "output/videos/clips", exclude_ids: set = None) -> list[str]:
    """
    Pexels API se stock video clips download karo.
    Clips used in any past video (or in exclude_ids) are skipped.
    Files are named pexels_<id>.mp4 so ids can be remembered after upload.
    Returns: list of downloaded file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    downloaded = []
    try:
        from brain.uniqueness import seen
        used_ids = {str(x) for x in seen("clip_id")}
    except Exception:
        used_ids = set()
    used_ids |= {str(x) for x in (exclude_ids or set())}

    headers = {"Authorization": PEXELS_API_KEY}

    try:
        params = {
            "query": search_query,
            "per_page": min(num_clips * 3, 40),  # extra fetch: some fail, some were used before
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
            return fetch_pexels_videos("technology office", num_clips, output_dir, exclude_ids)

        # Clips from past videos are skipped, so look at more pages when this one is mostly used
        tried = {params["page"]}
        while sum(1 for v in videos if str(v.get("id")) not in used_ids) < num_clips and len(tried) < 4:
            params["page"] = random.choice([p for p in range(1, 21) if p not in tried])
            tried.add(params["page"])
            more = requests.get(
                "https://api.pexels.com/videos/search",
                headers=headers,
                params=params,
                timeout=30,
            )
            if more.status_code == 200:
                videos += more.json().get("videos", [])

        for i, video in enumerate(videos):
            vid_id = str(video.get("id", f"x{i}"))
            if vid_id in used_ids:
                continue
            if len(downloaded) >= num_clips:
                break

            # Best quality HD file prefer karo
            video_files = sorted(
                video.get("video_files", []),
                key=lambda x: x.get("width", 0),
                reverse=True,
            )

            # 1920 ya closest resolution lo (4K files are huge and get scaled down anyway)
            mp4s = [vf for vf in video_files if vf.get("file_type") == "video/mp4"]
            chosen = next((vf for vf in mp4s if 0 < vf.get("width", 0) <= 1920), mp4s[0] if mp4s else None)

            if not chosen:
                continue

            url = chosen["link"]
            filename = os.path.join(output_dir, f"pexels_{vid_id}.mp4")

            try:
                dl = requests.get(url, timeout=60, stream=True)
                dl.raise_for_status()
                with open(filename, "wb") as f:
                    for chunk in dl.iter_content(chunk_size=8192):
                        f.write(chunk)

                if os.path.getsize(filename) > 10_000:  # at least 10KB
                    downloaded.append(filename)
                    used_ids.add(vid_id)
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
