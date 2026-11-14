"""Jsonplaceholder for the Marketplace application."""

import requests


def get_posts(user_id=None):
    """Get posts using validated application data."""
    params = {} if user_id is None else {"userId": user_id}
    try:
        response = requests.get(
            "https://jsonplaceholder.typicode.com/posts",
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            return []
        return [
            {
                "id": item["id"],
                "title": item["title"],
                "body": item["body"],
                "user_id": item["userId"],
            }
            for item in data
            if isinstance(item, dict)
            and all(key in item for key in ["id", "title", "body", "userId"])
            and (user_id is None or str(item["userId"]) == str(user_id))
        ]
    except (requests.RequestException, ValueError, TypeError):
        return []
