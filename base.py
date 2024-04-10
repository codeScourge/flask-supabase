from supabase.client import Client, ClientOptions
from gotrue import SyncSupportedStorage
from werkzeug.local import LocalProxy
from flask import session, g
import os


# --- setup ---
# We tell the Supabase Client to save the JWT token inside the Flasks session
class FlaskSessionStorage(SyncSupportedStorage):
    def __init__(self):
        self.storage = session

    def get_item(self, key: str) -> str | None:
        if key in self.storage:
            return self.storage[key]

    def set_item(self, key: str, value: str) -> None:
        self.storage[key] = value

    def remove_item(self, key: str) -> None:
        if key in self.storage:
            self.storage.pop(key, None)


# Set the flow_type to "pkce" (the backend one)
def get_supabase_anon() -> Client:
    if "supabase_anon" not in g:
        g.supabase_anon = Client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_KEY_ANON"),
            options=ClientOptions(
                storage=FlaskSessionStorage(),
                flow_type="pkce"
            ),
        )
    return g.supabase_anon

supabase_client: Client = LocalProxy(get_supabase_anon)
