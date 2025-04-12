import os
import subprocess

REPO_URL = "https://github.com/mistralai/platform-docs-public.git"
CLONE_DIR = "./git"
DOCS_DIR = os.path.join(CLONE_DIR, "docs")

def clone_repo(url=REPO_URL, clone_dir=CLONE_DIR):
    """
    Clone the GitHub repository to a local directory.

    Args:
        url (str): The URL of the GitHub repository.
        clone_dir (str): The local directory to clone the repository into.
    """
    if not os.path.exists(clone_dir):
        os.makedirs(clone_dir, exist_ok=True)
        subprocess.run(["git", "clone", url, clone_dir], check=True)
    else:
        if os.path.exists(os.path.join(clone_dir, ".git")):
            subprocess.run(["git", "-C", clone_dir, "pull"], check=True)
        else:
            print(f"{clone_dir} is not a git repository.")

def scrape_docs():
    """
    Clone the repository and ensure the docs are up-to-date.
    """
    clone_repo()