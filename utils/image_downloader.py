
from urllib.parse import urlparse
from pathlib import Path
import concurrent.futures  # Added missing import
from PIL import Image
import io
import requests
import os
def download_image_from_url(url, destination_path, filename=None, timeout=10):
    """
    Download a single image from URL and save to destination path.
    
    Args:
        url (str): URL of the image to download
        destination_path (str): Directory where image will be saved
        filename (str, optional): Custom filename. If None, uses original filename from URL
        timeout (int): Request timeout in seconds
    
    Returns:
        str: Path to downloaded image if successful, None if failed
    """
    try:
        # Create destination directory if it doesn't exist
        os.makedirs(destination_path, exist_ok=True)
        
        # Get response from URL
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Determine filename
        if filename is None:
            # Extract filename from URL
            parsed_url = urlparse(url)
            url_filename = os.path.basename(parsed_url.path)
            
            # If no proper filename in URL, generate one
            if not url_filename or '.' not in url_filename:
                url_filename = f"image_{hash(url) % 10000:04d}.jpg"
            
            filename = url_filename
        
        # Ensure filename has proper extension
        if '.' not in filename:
            # Try to determine extension from content type
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                filename += '.jpg'
            elif 'png' in content_type:
                filename += '.png'
            elif 'gif' in content_type:
                filename += '.gif'
            else:
                filename += '.jpg'  # default
        
        # Full path for saving
        file_path = os.path.join(destination_path, filename)
        
        # Avoid overwriting existing files
        counter = 1
        original_file_path = file_path
        while os.path.exists(file_path):
            name, ext = os.path.splitext(original_file_path)
            file_path = f"{name}_{counter}{ext}"
            counter += 1
        
        # Save image
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Verify the image is valid
        try:
            with Image.open(file_path) as img:
                img.verify()
            return file_path
        except Exception:
            # Remove invalid image file
            os.remove(file_path)
            return None
            
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return None

def download_multiple_images(urls, destination_path, max_workers=5):
    """
    Download multiple images from URLs concurrently.
    
    Args:
        urls (list): List of image URLs to download
        destination_path (str): Directory where images will be saved
        max_workers (int): Number of concurrent downloads
    
    Returns:
        list: List of successfully downloaded file paths
    """
    print(f"Starting download of {len(urls)} images to {destination_path}...")
    
    successful_downloads = []
    
    # Using ThreadPoolExecutor for concurrent downloads
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create futures for all downloads
        future_to_url = {
            executor.submit(download_image_from_url, url, destination_path): url 
            for url in urls
        }
        
        # Process completed downloads
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                if result:
                    successful_downloads.append(result)
                    print(f"✓ Downloaded: {os.path.basename(result)}")
                else:
                    print(f"✗ Failed: {url}")
            except Exception as e:
                print(f"✗ Error with {url}: {str(e)}")
    
    print(f"Download completed! {len(successful_downloads)}/{len(urls)} images downloaded successfully.")
    return successful_downloads