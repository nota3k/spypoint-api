import asyncio
from aiohttp import ClientSession
from spypointapi import SpypointApi

USERNAME = "svomak@gmail.com"
PASSWORD = "prow-winkle-record"

async def main():
    async with ClientSession() as session:
        api = SpypointApi(USERNAME, PASSWORD, session)
        await api.async_authenticate()

        # Get cameras first to get camera IDs
        cameras = await api.async_get_cameras()
        print("Cameras:", cameras)

        if cameras:
            camera_ids = [camera.id for camera in cameras]

            # Example parameters for the new API
            media = await api.async_get_media(
                camera=camera_ids,  # Use all camera IDs
                date_end="2025-12-31",  # Example end date
                limit=10,  # Limit to 10 results
                media_types=["photo"],  # Filter by photo media type
                species=[],  # Empty array for all species
                time_of_day=["day", "night"],  # Both day and night
                custom_tags=[],  # Empty array for no custom tags
            )
            print("Media:", media)
        else:
            print("No cameras found.")

if __name__ == "__main__":
    asyncio.run(main())
