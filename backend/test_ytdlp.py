"""
Quick test script to diagnose yt-dlp video info extraction
"""
import yt_dlp

# Test URL - replace with your actual URL
test_url = "https://www.twitch.tv/videos/2303502238"

print("Testing yt-dlp video info extraction...")
print(f"URL: {test_url}\n")

ydl_opts = {
    'quiet': False,
    'no_warnings': False,
    'extract_flat': False,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print("Extracting info...")
        info = ydl.extract_info(test_url, download=False)
        
        print("\n=== EXTRACTED INFO ===")
        print(f"ID: {info.get('id', 'N/A')}")
        print(f"Title: {info.get('title', 'N/A')}")
        print(f"Duration: {info.get('duration', 'N/A')} seconds")
        print(f"Uploader: {info.get('uploader', 'N/A')}")
        print(f"Thumbnail: {info.get('thumbnail', 'N/A')[:100]}...")
        print(f"View count: {info.get('view_count', 'N/A')}")
        print(f"Upload date: {info.get('upload_date', 'N/A')}")
        print("\n=== SUCCESS ===")
        
except Exception as e:
    print(f"\n=== ERROR ===")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print("\nThis might mean:")
    print("1. The URL requires authentication")
    print("2. The video is private or deleted")
    print("3. yt-dlp needs to be updated")
    print("4. Network/firewall issue")
