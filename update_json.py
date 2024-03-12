import json
import re
import requests

# Fetch all release information from GitHub
def fetch_all_releases(repo_url):
    api_url = f"https://api.github.com/repos/{repo_url}/releases"
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(api_url, headers=headers)
    releases = response.json()
    sorted_releases = sorted(
        releases, key=lambda x: x["published_at"], reverse=False)

    return sorted_releases

# Fetch the latest release information from GitHub
def fetch_latest_release(repo_url):
    api_url = f"https://api.github.com/repos/{repo_url}/releases"
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(api_url, headers=headers)
    releases = response.json()
    sorted_releases = sorted(
        releases, key=lambda x: x["published_at"], reverse=True)

    if sorted_releases:
        return sorted_releases[0]

    raise ValueError("No release found.")

# Update the JSON file with the fetched data
def remove_tags(text):
    text = re.sub('<[^<]+?>', '', text)  # Remove HTML tags
    text = re.sub(r'#{1,6}\s?', '', text)  # Remove markdown header tags
    return text

def get_ipa_url(assets):
    for asset in assets:
            return asset['browser_download_url']
    return None
    
def update_json_file(json_file, fetched_data_all, fetched_data_latest):
    with open(json_file, "r") as file:
        data = json.load(file)

    app = data["apps"][0]

    # Ensure 'versions' key exists in app
    if "versions" not in app:
        app["versions"] = []

    for release in fetched_data_all:
        full_version = fetched_data_latest["tag_name"].lstrip('v')
        tag = release["tag_name"]
        version = re.search(r"^(\d+\.\d+\.\d+)", full_version).group(1)
        versionDate = release["published_at"]
        description = release["body"]
        description = remove_tags(description)
        description = re.sub(r'\*{2}', '', description)
        description = re.sub(r'-', '•', description)
        description = re.sub(r'`', '"', description)

        downloadURL = get_ipa_url(release["assets"])
        size = next((asset["size"] for asset in release["assets"] if asset['browser_download_url'] == downloadURL), None)

        version_entry = {
            "version": version,
            "date": versionDate,
            "localizedDescription": description,
            "downloadURL": downloadURL,
            "size": size
        }

             # Check if the version entry already exists based on version
        version_entry_exists = [item for item in app["versions"] if item["version"] == version]

        # If the version entry exists, remove it
        if version_entry_exists:
            app["versions"].remove(version_entry_exists[0])

        # Add the new version entry (whether or not it existed before) only if downloadURL is not None
        if downloadURL is not None:
            # Insert the version entry at the first position
            app["versions"].insert(0, version_entry)

    # Now handle the latest release data (from the second script)
    full_version = fetched_data_latest["tag_name"].lstrip('v')
    tag = fetched_data_latest["tag_name"]
    version = re.search(r"^(\d+\.\d+\.\d+)", full_version).group(1)
    app["version"] = version
    app["versionDate"] = fetched_data_latest["published_at"]

    description = fetched_data_latest["body"]
    description = remove_tags(description)
    description = re.sub(r'\*{2}', '', description)
    description = re.sub(r'-', '•', description)
    description = re.sub(r'`', '"', description)

    app["versionDescription"] = description
    app["downloadURL"] = get_ipa_url(fetched_data_latest["assets"])
    app["size"] = next((asset["size"] for asset in fetched_data_latest["assets"] if asset['browser_download_url'] == app["downloadURL"]), None)

    # Ensure 'news' key exists in data
    if "news" not in data:
        data["news"] = []

    # Add news entry if there's a new release
    news_identifier = f"release-{full_version}"
    news_entry = {
        "title": f"{full_version} - Winston for Reddit",
        "identifier": news_identifier,
        "caption": f"Update of Winston just got released!",
        "date": fetched_data_latest["published_at"],
        "tintColor": "#000000",
        "imageURL": "https://raw.githubusercontent.com/Balackburn/Winston/main/images/news/news_2.png",
        "notify": True,
        "url": f"https://github.com/lo-cafe/winston/releases/tag/{tag}"
    }

    # Check if the news entry already exists
    news_entry_exists = any(item["identifier"] ==
                            news_identifier for item in data["news"])

    # Add the news entry if it doesn't exist
    if not news_entry_exists:
        data["news"].append(news_entry)

    with open(json_file, "w") as file:
        json.dump(data, file, indent=2)

# Main function
def main():
    repo_url = "lo-cafe/winston"
    json_file = "apps.json"

    fetched_data_all = fetch_all_releases(repo_url)
    fetched_data_latest = fetch_latest_release(repo_url)
    update_json_file(json_file, fetched_data_all, fetched_data_latest)

if __name__ == "__main__":
    main()
