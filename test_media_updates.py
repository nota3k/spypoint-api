#!/usr/bin/env python3
"""Simple test to verify the updated Media API works correctly."""

import asyncio
from datetime import datetime
from spypointapi.media.media import Media
from spypointapi.media.media_api_response import MediaApiResponse

def test_media_model():
    """Test that the Media model can be created with new fields."""
    media = Media(
        id="test_id",
        camera="test_camera",
        date=datetime.now(),
        large="https://example.com/large.jpg",
        tags=["test"],
        previews=["https://example.com/preview1.jpg"],
        hd_video="https://example.com/video.mp4",
        medium="https://example.com/medium.jpg",
        small="https://example.com/small.jpg",
        origin_date=datetime.now(),
        origin_name="original.jpg",
        origin_size=1024000,
    )
    print("✓ Media model creation successful")
    print(f"  ID: {media.id}")
    print(f"  Camera: {media.camera}")
    print(f"  Large URL: {media.large}")
    print(f"  Medium URL: {media.medium}")
    print(f"  Small URL: {media.small}")
    print(f"  Origin Name: {media.origin_name}")
    print(f"  Origin Size: {media.origin_size}")

def test_media_api_response():
    """Test that MediaApiResponse can parse the new response format."""
    test_response = {
        "cameraId": None,
        "cameraIds": ["cam1", "cam2"],
        "countPhotos": 2,
        "photos": [
            {
                "id": "photo1",
                "camera": "cam1",
                "date": "2025-01-01T12:00:00.000Z",
                "large": {
                    "verb": "GET",
                    "path": "/large.jpg",
                    "host": "cdn.example.com",
                    "headers": []
                },
                "medium": {
                    "verb": "GET",
                    "path": "/medium.jpg",
                    "host": "cdn.example.com",
                    "headers": []
                },
                "small": {
                    "verb": "GET",
                    "path": "/small.jpg",
                    "host": "cdn.example.com",
                    "headers": []
                },
                "tag": ["day"],
                "originDate": "2025-01-01T11:00:00.000Z",
                "originName": "original.jpg",
                "originSize": 2048000
            }
        ]
    }

    media_response = MediaApiResponse.from_json(test_response)
    print("✓ MediaApiResponse parsing successful")
    print(f"  Camera ID: {media_response.camera_id}")
    print(f"  Camera IDs: {media_response.camera_ids}")
    print(f"  Count Photos: {media_response.count_photos}")
    print(f"  Number of Photos: {len(media_response.photos)}")

    if media_response.photos:
        photo = media_response.photos[0]
        print(f"  First Photo ID: {photo.id}")
        print(f"  First Photo Large URL: {photo.large}")
        print(f"  First Photo Medium URL: {photo.medium}")
        print(f"  First Photo Small URL: {photo.small}")
        print(f"  First Photo Origin Name: {photo.origin_name}")
        print(f"  First Photo Origin Size: {photo.origin_size}")

if __name__ == "__main__":
    print("Testing updated Media API...")
    test_media_model()
    print()
    test_media_api_response()
    print("\n✓ All tests passed!")
