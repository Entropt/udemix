import os
import shutil
from urllib.parse import urlparse
from constants import ARTICLE_URL, logger


def download_article(
    udemy, article, download_folder_path, title_of_output_article, task_id, progress
):
    progress.update(
        task_id,
        description=f"Downloading Article {title_of_output_article}",
        completed=0,
    )

    article_filename = f"{title_of_output_article}.html"

    try:
        resp = udemy.request(ARTICLE_URL.format(article_id=article["id"]))
        if resp is None:
            logger.error(
                f"Failed to fetch article '{title_of_output_article}' (network error)"
            )
            return

        article_response = resp.json()

        with open(
            os.path.join(os.path.dirname(download_folder_path), article_filename),
            "w",
            encoding="utf-8",
            errors="replace",
        ) as file:
            file.write(article_response["body"])

        progress.console.log(f"[green]Downloaded {title_of_output_article}[/green] ✓")
    except Exception as e:
        logger.error(f"Error downloading article '{title_of_output_article}': {e}")
    finally:
        try:
            progress.remove_task(task_id)
        except KeyError:
            pass
        if os.path.isdir(download_folder_path):
            shutil.rmtree(download_folder_path)
