import os
import requests
from git import Repo

class GitHubScraper:
    def __init__(self, repo_url, clone_dir='cloned_repo'):
        self.repo_url = repo_url
        self.clone_dir = clone_dir

    def clone_repo(self):
        try:
            if not os.path.exists(self.clone_dir):
                print(f"Cloning repository from {self.repo_url} to {self.clone_dir}")
                Repo.clone_from(self.repo_url, self.clone_dir)
            else:
                print(f"Directory {self.clone_dir} already exists. Continuing with existing directory.")
        except Exception as e:
            print(f"Error cloning repository: {e}")

    def search_code(self, search_term):
        self.clone_repo()
        results = []

        # Check for README in the root path
        readme_path = os.path.join(self.clone_dir, 'README.md')
        if os.path.exists(readme_path):
            with open(readme_path, 'r', errors='ignore') as f:
                content = f.read()
                if search_term in content:
                    results.append({'path': readme_path, 'content': content})

        # Search other files
        for root, _, files in os.walk(self.clone_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path != readme_path:
                    try:
                        with open(file_path, 'r', errors='ignore') as f:
                            content = f.read()
                            if search_term in content:
                                results.append({'path': file_path, 'content': content})
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")

        return results

    def search_raw(self, search_term):
        try:
            # Construct the raw URL for the README.md file in the main branch
            raw_url = self.repo_url.replace('github.com', 'raw.githubusercontent.com').replace('/tree/', '/') + '/main/README.md'
            print(f"Searching raw content at {raw_url}")
            response = requests.get(raw_url)
            if response.status_code == 200:
                content = response.text
                if search_term in content:
                    return raw_url
        except Exception as e:
            print(f"Error searching raw content: {e}")
        return None

    def get_raw_file_content(self, raw_url):
        try:
            print(f"Fetching raw content from {raw_url}")
            response = requests.get(raw_url)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to fetch raw content. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error fetching raw content: {e}")
        return None