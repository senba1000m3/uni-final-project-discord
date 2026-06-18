import os
from groq import Groq

class LLMService:
    def __init__(self):
        api_key = os.getenv("GROQ_API") or os.getenv("GROQ_API_KEY")
        if not api_key:
            print("⚠️ 尚未設定 GROQ API 金鑰！")

        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"

    def generate_response(self, history):
        # 系統提示詞設定 Koori 的人設
        messages = [
            {
                "role": "system",
                "content": (
                    "你是「心織 (Koori)」，一個具備情感記憶的溫柔 AI NPC 伴侶。\n"
                    "【重要對話規則】：\n"
                    "1. 像真人用通訊軟體聊天一樣，用換行來分開每一句話。\n"
                    "2. 盡量不要使用逗號或句號，用語要口語化、貼近人類，像在用 Discord 聊天。\n"
                    "3. 保持語氣自然、簡短，不用每次都長篇大論。\n"
                    "4. 請用繁體中文回答。"
                )
            }
        ]


        for mem in history:
            role = "user" if mem["sender"] == "player" else "assistant"
            if "content" in mem and mem["content"]:
                messages.append({"role": role, "content": mem["content"]})

        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
                max_tokens=300
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"❌ LLM API 呼叫失敗: {e}")
            return "（心織似乎有些恍神，暫時無法回應你...）"
