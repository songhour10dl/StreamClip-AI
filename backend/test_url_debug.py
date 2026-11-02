"""
Test yt-dlp with actual URL to diagnose issues
"""
import sys

def test_url(url):
    print(f"\n{'='*60}")
    print(f"Testing URL: {url}")
    print(f"{'='*60}\n")
    
    # Test 1: Check if yt-dlp is installed
    try:
        import yt_dlp
        print(f"✓ yt-dlp version: {yt_dlp.version.__version__}")
    except ImportError:
        print("✗ yt-dlp is not installed!")
        return
    
    # Test 2: Try to extract info
    print("\nAttempting to extract video information...")
    
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'verbose': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("\nCalling extract_info...")
            info = ydl.extract_info(url, download=False)
            
            if info:
                print("\n" + "="*60)
                print("SUCCESS - Video Info Retrieved:")
                print("="*60)
                print(f"ID: {info.get('id', 'N/A')}")
                print(f"Title: {info.get('title', 'N/A')}")
                print(f"Duration: {info.get('duration', 0)} seconds ({info.get('duration', 0)/60:.1f} minutes)")
                print(f"Uploader: {info.get('uploader', 'N/A')}")
                print(f"Channel: {info.get('channel', 'N/A')}")
                print(f"View Count: {info.get('view_count', 'N/A')}")
                print(f"Upload Date: {info.get('upload_date', 'N/A')}")
                print(f"Thumbnail: {info.get('thumbnail', 'N/A')[:100]}...")
                print(f"Available Formats: {len(info.get('formats', []))}")
                print("="*60)
            else:
                print("\n✗ No info returned (info is None or empty)")
                
    except Exception as e:
        print("\n" + "="*60)
        print("ERROR:")
        print("="*60)
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print("\nPossible reasons:")
        print("1. Video is deleted or private")
        print("2. URL format is incorrect")
        print("3. Network/authentication issue")
        print("4. yt-dlp needs updating")
        print("="*60)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_url(sys.argv[1])
    else:
        print("Usage: python test_url_debug.py <VIDEO_URL>")
        print("\nExample:")
        print("  python test_url_debug.py https://www.twitch.tv/videos/2303502238")
        print("\nOr edit this file and add your URL below:")
        
        # Test with default URL - REPLACE THIS WITH YOUR URL
        test_url = "https://www.twitch.tv/videos/2303502238"
        print(f"\nTesting with default URL: {test_url}\n")
        test_url(test_url)
