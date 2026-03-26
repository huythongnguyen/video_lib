---
name: resona-tts
description: Generate Vietnamese AI speech audio using the Resona TTS API (resona.live). Covers authentication, voice IDs, submitting async jobs, polling, and downloading audio files.
---

# Resona TTS Skill

[Resona](https://resona.live) is a Vietnamese AI Text-to-Speech platform. This skill covers everything needed to call its API from a Python script to generate high-quality Vietnamese audio.

---

## API Basics

- **Base URL**: `https://resona.live`
- **Auth**: Bearer token in the `Authorization` header
- **API Key format**: `rsk_...`

```
Authorization: Bearer rsk_YOUR_KEY_HERE
```

### ⚠️ Cloudflare Protection
The API is behind Cloudflare and will return **HTTP 403 error code 1010** if called with default Python `urllib` headers. You **must** include browser-like headers:

```python
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://resona.live",
    "Referer": "https://resona.live/",
}
```

---

## Speech Generation Flow (Async)

Speech generation is a **3-step async process**:

```
POST /api/v1/generate-speech   →  get request_id
GET  /api/v1/generate-speech/:request_id/status  →  poll until "completed"
GET  /api/v1/generate-speech/:request_id         →  get audio_urls
```

### Step 1: Submit Job

```http
POST /api/v1/generate-speech
Content-Type: application/json
Authorization: Bearer YOUR_KEY

{
  "text": "Speaker 1: Your Vietnamese text here.",
  "voice_ids": ["VOICE_ID_HERE"]
}
```

**Response:**
```json
{
  "request_id": "ee3a9ff9-a907-4a60-9c61-d6a2b882799f",
  "status": "processing",
  "message": "Speech generation job submitted successfully",
  "usage": { "charCount": 8 }
}
```

**Note**: The text must be prefixed with `Speaker 1: ` (for single-speaker).

### Step 2: Poll Status

```http
GET /api/v1/generate-speech/:request_id/status
```

**Response:**
```json
{ "request_id": "...", "status": "processing" }
```

Possible `status` values: `processing` | `completed` | `failed`

Poll every **3 seconds**. Typical completion time: 12–18 seconds per job.

### Step 3: Get Result

```http
GET /api/v1/generate-speech/:request_id
```

**Response:**
```json
{
  "request_id": "...",
  "status": "completed",
  "audio_urls": ["https://storage.googleapis.com/.../audio.mp3"],
  "created_at": "2024-12-28T10:00:00Z"
}
```

Download the audio from `audio_urls[0]`. Files are `.mp3` (sometimes `.wav`).

---

## Complete Python Implementation

See `generate_tts.py` for the full working script. Key helper function:

```python
import urllib.request, json, time, os

API_KEY = "rsk_YOUR_KEY_HERE"
BASE_URL = "https://resona.live"

def api_request(method, path, data=None):
    url = BASE_URL + path
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://resona.live",
        "Referer": "https://resona.live/",
    }
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def generate_speech(text, voice_id, max_wait=180):
    """Full pipeline: submit → poll → return audio URLs"""
    # Submit
    result = api_request("POST", "/api/v1/generate-speech", {
        "text": f"Speaker 1: {text}",
        "voice_ids": [voice_id]
    })
    request_id = result["request_id"]

    # Poll
    deadline = time.time() + max_wait
    while time.time() < deadline:
        status = api_request("GET", f"/api/v1/generate-speech/{request_id}/status")
        if status["status"] == "completed":
            break
        elif status["status"] == "failed":
            raise Exception(f"Job {request_id} failed")
        time.sleep(3)

    # Get result
    result = api_request("GET", f"/api/v1/generate-speech/{request_id}")
    return result["audio_urls"]
```

---

## Available Vietnamese Voices

All voices are high quality (`Cao`). Retrieved from https://resona.live/vi/voices.

### Recommended for Buddhist/Calm Content
| Voice Name | Voice ID | Gender | Region |
|---|---|---|---|
| **Thanh Nhã** | `ES9XihN1RcFVpypacTTh` | Nữ (Female) | Miền Bắc |
| **Tuệ An** | `0phiCO46biYtwYYP0DIR` | Nữ (Female) | Miền Nam |
| **Vân Anh** | `ODDT6PXH9Eb43SpMXZda` | Nữ (Female) | Miền Bắc |
| **Thuỷ Nguyên** | `CBeyUXIIbS2pfymElCps` | Nữ (Female) | Miền Bắc |
| **Suối Chậm Chạp** | `gRtmTcLs6zegO7JihCbL` | Nữ (Female) | Miền Nam |

### All Available Voices
| Voice Name | Voice ID | Gender | Region |
|---|---|---|---|
| Ngộ Không | `Hw8RCKYahvuS5uT8Z4Ye` | Nam | Miền Bắc |
| Bát Giới | `R1CqN2exQZPOvXdMYFnq` | Nam | Miền Bắc |
| Thanh Nhã | `ES9XihN1RcFVpypacTTh` | Nữ | Miền Bắc |
| Trung Kiên | `qRMFIUAS0vaFeZI5abu8` | Nam | Miền Bắc |
| Việt Trung | `GmlanOjlAHIuPeJ86ipB` | Nam | Miền Bắc |
| Tuệ An | `0phiCO46biYtwYYP0DIR` | Nữ | Miền Nam |
| Minh Tuấn | `KPQJS4asbzfvJwN9fEsb` | Nam | Miền Bắc |
| Vân Anh | `ODDT6PXH9Eb43SpMXZda` | Nữ | Miền Bắc |
| Mai Thương | `uoPJ9UARkvMsZ8x0Zoaj` | Nữ | Miền Bắc |
| Ong Ấm Áp | `W6vqCkz7l7n0GxNaKzyG` | Nữ | Miền Bắc |
| Hổ Cứng Rắn | `tak3IN3asjyDvk2dC3iR` | Nam | Miền Bắc |
| Thuỷ Nguyên | `CBeyUXIIbS2pfymElCps` | Nữ | Miền Bắc |
| Tiền Nhanh Nhẹn | `USYTYBI33ONlIoLQwm6d` | Nam | Miền Bắc |
| Hổ Mịn Màng | `dwK3JbXXe2LLisf6Tfx6` | Nam | Miền Bắc |
| Núi Cam Cháy | `KZxq3ccG4XmAVq9ExnJE` | Nam | Miền Nam |
| Hiệp Thức | `QCWGCSBcDBqmvoWXuvCW` | Nam | Miền Bắc |
| Bướm Nóng Bỏng | `5psvYObKYOvb6zRpYUeB` | Nữ | Miền Bắc |
| Suối Chậm Chạp | `gRtmTcLs6zegO7JihCbL` | Nữ | Miền Nam |
| Phở Độc Đáo | `HMSLcMlUWQAxu1Vd1NO4` | Nữ | Miền Bắc |
| Ghế Nhanh Nhẹn | `HEhDjGxPNpHaJcNjQvsH` | Nữ | Miền Bắc |
| Bão Tối Đen | `KYaeDi6NjskLfXfT5P1r` | Nam | Miền Bắc |
| Gà Xanh Lá | `5dNRyrnMGdbHO5ypPIPc` | Nữ | Miền Bắc |
| Thỏ Cao Ráo | `ygSDr73sJKhkSgERsiCB` | Nữ | Miền Bắc |
| Kệ Lạnh Buốt | `DZeZtsmjaG0rWIbQ6B8V` | Nam | Miền Bắc |
| Rắn Vàng Óng | `sqfAqIMRd7QvQTjYQGX3` | Nữ | Miền Bắc |
| Mèo Khô Ráo | `d9iNLHJpr7r10IAjhvtI` | Nữ | Miền Bắc |
| Trời To Lớn | `r3yLcbkngGdZdT2hE4Va` | Nam | Miền Bắc |
| Giấy Tối Đen | `JY46W80vwCMm3nf6ez4q` | Nam | Miền Bắc |
| Kính Hồng Phấn | `urTltTMVMviGIngBif76` | Nữ | Miền Bắc |
| Lá Hồng Phấn | `PvC9LUTn1aVnx2k2ex8C` | Nữ | Miền Bắc |
| Sách Vàng Óng | `NKsNW8ppA9lzNlLjdXaJ` | Nam | Miền Bắc |
| Sàn Khôn Ngoan | `Ql3fzSgaRnot6aSfYnAh` | Nam | Miền Bắc |
| Mũ Nón Nhỏ Bé | `EeNF9QA6WD46ytC7aPXd` | Nữ | Miền Bắc |
| Mèo Mạnh Mẽ | `5YOCevpLRnJNQOUFey8O` | Nữ | Miền Bắc |
| Trần Xuất Sắc | `Wg7u9eoTOJf0b4996smf` | Nam | Miền Bắc |
| Giò Hạnh Phúc | `3KE0nSREA3z8pB2fj7YD` | Nam | Miền Bắc |
| Cây Khôn Ngoan | `JE9f7AhmbmI347tVXEtc` | Nam | Miền Nam |
| Bàn Ngắn Gọn | `2oHQU9InI5ndjhOMQPOM` | Nam | Miền Nam |
| Giày Thanh Tao | `wlRJZJhdTgmD0LHPUeay` | Nữ | Miền Bắc |
| Kiến Dịu Dàng | `pb2N2cyodd3N8VPVPedQ` | Nữ | Miền Bắc |
| Giày Hay Ho | `C98DukJu88lWXoMkxndM` | Nam | Miền Bắc |
| Tuyết Hẹp Hòi | `YnhPX6VhjR5w9ziWQ7bB` | Nam | Miền Bắc |
| Trà Quý Phái | `DU6CsX1T7dMQj28Z9lnp` | Nam | Miền Bắc |
| Heo Tối Đen | `0sGlBW3tXu3ePvf2rP7L` | Nam | Miền Nam |
| Tuyết Nhẹ Nhàng | `C3tEh3RaFrM9GXzy3lGJ` | Nam | Miền Bắc |
| Kẹo Xanh Lá | `0Fy1bweLldClcIxNdPCw` | Nữ | Miền Nam |
| Nước Nóng Bỏng | `nVUYb9R86xapPz0stjTw` | Nam | Miền Nam |
| Kiến Mềm Mại | `eJ89HkCfsUzbONodEne8` | Nữ | Miền Nam |
| Suối Nhanh Nhẹn | `CngjyCLnd6wlvDjXggjq` | Nữ | Miền Nam |
| Mèo Hay Ho | `YTV4sGvY5YuVVapAwGo0` | Nữ | Miền Nam |
| Túi Chậm Chạp | `WKDlzjoN2GtJYxIHRIyA` | Nữ | Miền Nam |
| Bút Lấp Lánh | `8yyyJnoFM6MMvUdo3o9R` | Nữ | Miền Bắc |
| Bún Đặc Biệt | `IheQnRUN5p6gVveNaPkv` | Nam | Miền Bắc |
| Suối Mát Mẻ | `ayLREiin0y8yGJD1ThxB` | Nữ | Miền Bắc |
| Giường Ngọt Ngào | `FtU7ctG0gsfoKSYznFQr` | Nữ | Miền Nam |

---

## Usage Tips

- **Single speaker**: Prefix text with `Speaker 1: `
- **No external dependencies**: Uses only Python stdlib (`urllib.request`, `json`, `time`, `os`)
- **Rate limiting**: No known rate limits observed; process jobs sequentially to be safe
- **Polling interval**: 3 seconds works well; typical job duration is 12–18 seconds
- **Audio format**: Downloads as `.mp3` (check URL for `.wav` if needed)
- **Docs URL**: https://resona.live/vi/docs/api-reference
