import os
import requests
import webvtt
from constants import logger


def download_captions(
    captions, download_folder_path, title_of_output_mp4, captions_list, convert_to_srt
):
    filtered_captions = [
        caption for caption in captions if caption["locale_id"] in captions_list
    ]

    for caption in filtered_captions:
        if caption["file_name"].endswith(".vtt"):
            caption_name = f"{title_of_output_mp4} - {caption['video_label']}.vtt"
            vtt_path = os.path.join(download_folder_path, caption_name)
            srt_name = caption_name.replace(".vtt", ".srt")
            srt_path = os.path.join(download_folder_path, srt_name)

            # Skip if the final caption file already exists
            if (
                convert_to_srt
                and os.path.isfile(srt_path)
                and os.path.getsize(srt_path) > 0
            ):
                logger.info(f"Skipped caption (already exists): {srt_name}")
                continue
            if (
                not convert_to_srt
                and os.path.isfile(vtt_path)
                and os.path.getsize(vtt_path) > 0
            ):
                logger.info(f"Skipped caption (already exists): {caption_name}")
                continue

            try:
                response = requests.get(caption["url"])
                response.raise_for_status()
                with open(vtt_path, "wb") as file:
                    file.write(response.content)

                if convert_to_srt:
                    srt_content = webvtt.read(vtt_path)
                    srt_content.save_as_srt(srt_path)

                    # Remove VTT file
                    os.remove(vtt_path)
            except Exception as e:
                logger.error(f"Error downloading caption '{caption_name}': {e}")

        else:
            print(
                "Only VTT captions are supported. Please create a github issue if you'd like to add support for other formats."
            )
