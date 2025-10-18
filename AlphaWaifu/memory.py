# Runtime memory (shared across modules)
CURRENT_DROPS: dict = {}   # {chat_id: {...}}

# Drop interval (default = 50 msgs, sudo can change)
DROP_INTERVAL: int = 50

# Optional helper to get user info
def get_user_info(user):
    """
    Return a dict with firstname and username from a Telegram user object.
    """
    return {
        "firstname": getattr(user, "first_name", None),
        "username": getattr(user, "username", None),
    }