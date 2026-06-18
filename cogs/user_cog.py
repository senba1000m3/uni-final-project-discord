import discord
from discord.ext import commands
from discord import app_commands
from services.supabase_db import SupabaseService

class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = SupabaseService()

    @app_commands.command(name="bind", description="將你的 Discord 帳號與心織遊戲序號綁定")
    @app_commands.describe(game_id="請輸入遊戲內生成的 10 位數序號")
    async def bind(self, interaction: discord.Interaction, game_id: str):

        if len(game_id) != 10:
            await interaction.response.send_message("❌ 格式錯誤！序號應為 10 位數。", ephemeral=True)
            return

        discord_id = str(interaction.user.id)

        try:
            res = self.db.bind_user(game_id, discord_id)
            if res.data:
                await interaction.response.send_message(f"✅ 綁定成功！心織現在認得你了。", ephemeral=True)
            else:
                await interaction.response.send_message("❌ 找不到序號，請確認輸入是否正確。", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("⚠️ 綁定失敗：可能該帳號已被綁定。", ephemeral=True)

    @app_commands.command(name="status", description="詳細查詢玩家資訊、心織目前的狀態及各平台對話數據")
    async def status(self, interaction: discord.Interaction):
        await interaction.response.defer() # 避免讀取資料庫過久導致超時

        discord_id = str(interaction.user.id)
        profile = self.db.get_user_profile(discord_id)

        if not profile or not profile.get('game_id'):
            await interaction.followup.send("❌ 你還沒有綁定心織序號喔！請先使用 `/bind` 指令。", ephemeral=True)
            return

        game_id = profile['game_id']
        player_name = profile.get('player_name') or "未設定"
        player_birthday = profile.get('player_birthday') or "未設定"
        player_summary = profile.get('player_summary') or "無"

        relation = self.db.get_npc_relation(game_id)
        stats = self.db.get_chat_stats(game_id)

        # 狀態防呆
        favorability = relation.get('favorability', 0) if relation else 0
        current_mood = relation.get('current_mood', '平靜') if relation else '平靜'
        long_term_summary = relation.get('long_term_summary') or "尚無紀錄"

        # 計算總量
        total_dc = stats['discord_player'] + stats['discord_koori']
        total_unity = stats['unity_player'] + stats['unity_koori']
        total_all = total_dc + total_unity

        embed = discord.Embed(title="📊 玩家與心織狀態面板", color=0xADD8E6)

        # 玩家資訊區塊
        embed.add_field(name="👤 玩家名稱", value=f"`{player_name}`", inline=True)
        embed.add_field(name="🎂 生日", value=f"`{player_birthday}`", inline=True)
        embed.add_field(name="🔗 遊戲序號", value=f"`{game_id}`", inline=True)
        if player_summary != "無":
            embed.add_field(name="📝 玩家特徵/摘要", value=player_summary, inline=False)

        # 心織狀態區塊
        embed.add_field(name="💖 Koori 好感度", value=f"**{favorability}**", inline=True)
        embed.add_field(name="💭 Koori 心情", value=f"**{current_mood}**", inline=True)
        embed.add_field(name="📖 長期記憶摘要", value=long_term_summary, inline=False)

        # 對話數據區塊
        embed.add_field(name="💬 總對話量", value=f"共 **{total_all}** 則訊息", inline=False)

        dc_text = f"玩家: {stats['discord_player']} 則\nKoori: {stats['discord_koori']} 則"
        embed.add_field(name="📱 Discord 對話", value=dc_text, inline=True)

        unity_text = f"玩家: {stats['unity_player']} 則\nKoori: {stats['unity_koori']} 則"
        embed.add_field(name="🎮 Unity 對話", value=unity_text, inline=True)

        embed.set_footer(text="數據為跨平台即時同步！")

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserCog(bot))
