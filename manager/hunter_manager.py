from dotenv import load_dotenv
import os
import requests

load_dotenv()


class HunterManager:
    """
    Responsible for managing multiple Hunter API keys.
    """

    ACCOUNT_URL = "https://api.hunter.io/v2/account"

    def __init__(self):
        self.api_keys = self._load_keys()

    def _load_keys(self) -> list[str]:
        """
        Load Hunter API keys from .env
        """

        keys = os.getenv("HUNTER_KEYS", "")

        return [
            key.strip()
            for key in keys.split(",")
            if key.strip()
        ]

    def _check_key(self, api_key: str) -> dict | None:
        """
        Validate a single API key.

        Returns:
            {
                "api_key": "...",
                "remaining": 36,
                "used": 14,
                "reset_date": "...",
                "email": "..."
            }

            or None
        """

        try:

            response = requests.get(
                self.ACCOUNT_URL,
                params={"api_key": api_key},
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()["data"]

            return {
                "api_key": api_key,
                "remaining": int(
                    data["requests"]["credits"]["remaining"]
                ),
                "used": int(
                    data["requests"]["credits"]["used"]
                ),
                "reset_date": data["reset_date"],
                "email": data["email"],
            }

        except Exception as e:

            print(f"Invalid Hunter key : {e}")

            return None

    def get_available_key(self, min_remaining: int = 20) -> str | None:
        """
        Return the Hunter API key having at least
        `min_remaining` credits left.
        """

        available_keys = []

        for key in self.api_keys:

            info = self._check_key(key)

            if info is None:
                continue

            # Skip exhausted or low-credit keys
            if info["remaining"] < min_remaining:
                continue

            available_keys.append(info)

        if not available_keys:
            print(f"No Hunter API key has at least {min_remaining} credits remaining.")
            return None

        available_keys.sort(
            key=lambda x: x["remaining"],
            reverse=True,
        )

        best = available_keys[0]

        print(
            f"Using Hunter Account: {best['email']}",
            f"({best['remaining']} credits left)"
        )

        return best["api_key"]


