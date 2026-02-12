import os
from urllib.parse import urlparse
from constants import LINK_ASSET_URL, FILE_ASSET_URL, logger


def download_supplementary_assets(
    udemy, assets, download_folder_path, course_id, lecture_id
):
    for asset in assets:
        match asset["asset_type"]:
            case "File" | "SourceCode":
                process_files(udemy, asset, course_id, lecture_id, download_folder_path)
            case "ExternalLink":
                process_external_links(
                    udemy, asset, course_id, lecture_id, download_folder_path
                )
            case _:
                logger.warning(
                    f"Unsupported asset type '{asset['asset_type']}' for asset '{asset.get('filename', 'unknown')}'. Skipping."
                )


def process_files(udemy, asset, course_id, lecture_id, download_folder_path):
    assets_folder = os.path.join(download_folder_path, "assets")
    if not os.path.exists(assets_folder):
        os.makedirs(assets_folder)

    asset_file_path = os.path.join(assets_folder, asset["filename"])

    # Skip if file already exists and is non-empty
    if os.path.isfile(asset_file_path) and os.path.getsize(asset_file_path) > 0:
        logger.info(f"Skipped asset (already exists): {asset['filename']}")
        return

    asset_type = asset["asset_type"]
    try:
        info_response = udemy.request(
            FILE_ASSET_URL.format(
                course_id=course_id, lecture_id=lecture_id, asset_id=asset["id"]
            )
        )
        if info_response is None:
            logger.error(
                f"Failed to fetch asset info for '{asset['filename']}' (network error)"
            )
            return

        asset_info = info_response.json()

        download_urls = asset_info.get("download_urls", {})
        # The download URL key matches the asset_type (e.g., "File", "SourceCode")
        url_list = download_urls.get(asset_type) or download_urls.get("File")
        if not url_list:
            logger.error(
                f"No download URL found for asset '{asset['filename']}' (type: {asset_type})"
            )
            return

        file_response = udemy.request(url_list[0]["file"])
        if file_response is None:
            logger.error(
                f"Failed to download asset '{asset['filename']}' (network error)"
            )
            return

        file_response.raise_for_status()

        with open(asset_file_path, "wb") as file:
            for chunk in file_response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
    except Exception as e:
        logger.error(f"Error downloading asset '{asset['filename']}': {e}")


def process_external_links(udemy, asset, course_id, lecture_id, download_folder_path):
    external_links_folder = os.path.join(download_folder_path, "external-links")
    if not os.path.exists(external_links_folder):
        os.makedirs(external_links_folder)

    asset_filename = f"{asset['filename']}.url"
    asset_file_path = os.path.join(external_links_folder, asset_filename)

    # Skip if link file already exists
    if os.path.isfile(asset_file_path) and os.path.getsize(asset_file_path) > 0:
        logger.info(f"Skipped external link (already exists): {asset_filename}")
        return

    try:
        resp = udemy.request(
            LINK_ASSET_URL.format(
                course_id=course_id, lecture_id=lecture_id, asset_id=asset["id"]
            )
        )
        if resp is None:
            logger.error(
                f"Failed to fetch external link for '{asset_filename}' (network error)"
            )
            return

        response = resp.json()

        asset_url = response["external_url"]

        with open(asset_file_path, "w") as file:
            file.write(f"[InternetShortcut]\nURL={asset_url}\n")
    except Exception as e:
        logger.error(f"Error downloading external link '{asset_filename}': {e}")
