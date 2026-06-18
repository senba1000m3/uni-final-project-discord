import asyncio
import discord
from discord.ext import commands
from services.supabase_db import SupabaseService
from services.llm_service import LLMService

class MemoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = SupabaseService()
        self.llm = LLMService()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.content.startswith('!'):
            return

        game_id = self.db.get_game_id_by_discord(str(message.author.id))

        if game_id:
            try:
                # 1. 儲存玩家訊息
                self.db.save_memory(game_id, message.content, sender="player")

                # 加上正在輸入中的狀態，讓玩家知道 Koori 正在思考
                async with message.channel.typing():
                    # 2. 獲取對話歷史 (此時已包含剛剛玩家送出的訊息)
                    history = self.db.get_recent_memories(game_id, limit=8)

                    # 3. 呼叫 Groq 產生回應
                    reply_text = self.llm.generate_response(history)

                    # 4. 儲存 Koori 的回應 (is_processed 預設會是 True)
                    self.db.save_memory(game_id, reply_text, sender="koori")

                # 5. 一句一句回傳給玩家 (改用 send 直接發送到頻道，模擬人類對話)
                # 依照換行符號分割，並過濾掉空字串
                lines = [line.strip() for line in reply_text.split('\n') if line.strip()]
                for line in lines:
                    async with message.channel.typing():
                        # 依據字串長度模擬打字延遲時間 (每字約 0.15 秒，最多延遲 1.5 秒)
                        delay = min(len(line) * 0.15, 1.5)
                        await asyncio.sleep(delay)
                    await message.channel.send(line)

            except Exception as e:
                print(f"❌ 記憶同步或回覆失敗: {e}")

async def setup(bot):
    await bot.add_cog(MemoryCog(bot))
