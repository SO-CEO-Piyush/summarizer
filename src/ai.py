import os

import openai


class AiSummarizer:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def create_system_prompt(self, custom_instructions: str):
        prompt = """
        You have to summarize the following content concisely in few sentences
        """
        if custom_instructions:
            prompt += f"\n{custom_instructions}"
        return prompt

    def summarize(self, text: str, custom_instructions: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": self.create_system_prompt(custom_instructions),
                },
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content
