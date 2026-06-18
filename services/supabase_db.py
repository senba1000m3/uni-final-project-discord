import os
from supabase import create_client, Client

class SupabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(url, key)

    def bind_user(self, game_id, discord_id):
        return self.client.table("user_profiles").update({
            "discord_id": discord_id
        }).eq("game_id", game_id).execute()

    def get_user_profile(self, discord_id):
        res = self.client.table("user_profiles").select("*").eq("discord_id", discord_id).execute()
        return res.data[0] if res.data else None

    def get_game_id_by_discord(self, discord_id):
        profile = self.get_user_profile(discord_id)
        return profile['game_id'] if profile else None

    def get_npc_relation(self, game_id):
        res = self.client.table("npc_relations").select("*").eq("game_id", game_id).execute()
        return res.data[0] if res.data else None

    def get_chat_stats(self, game_id):
        res = self.client.table("chat_memories").select("platform, sender").eq("game_id", game_id).execute()
        stats = {
            "discord_player": 0,
            "discord_koori": 0,
            "unity_player": 0,
            "unity_koori": 0
        }
        if res.data:
            for row in res.data:
                key = f"{row.get('platform')}_{row.get('sender')}"
                if key in stats:
                    stats[key] += 1
        return stats

    def save_memory(self, game_id, content, sender="player"):
        valid_senders = ["player", "koori"]
        if sender not in valid_senders:
            raise ValueError(f"Invalid sender: {sender}. Must be one of {valid_senders}")

        data = {
            "game_id": game_id,
            "platform": "discord",
            "sender": sender,
            "action_type": "chat",
            "content": content,
            "is_processed": False
        }
        return self.client.table("chat_memories").insert(data).execute()

    def get_recent_memories(self, game_id, limit=8):
        res = self.client.table("chat_memories")\
            .select("sender, content, created_at")\
            .eq("game_id", game_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()

        return list(reversed(res.data)) if res.data else []
