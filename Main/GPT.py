import openai
from Main import gpt as gpt_api


class GPT(openai.OpenAI):
    def __init__(self, user:str, user_tweets: list, description: str):
        super().__init__(api_key=gpt_api)
        self.user_tweets = user_tweets
        self.description = description
        self.user = user

    async def get_response(self):
        return self.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user",
                 "content": "Based on the following posts, description, and login, provide a brief summary about this person or group. Include their interests, personality, and any notable traits. Use English language."},
                {"role": "user",
                 "content": f"Posts: '{'. '.join(self.user_tweets)}' Description: '{self.description}', username: f'{self.user}'"}
            ]
        ).choices[0].message.content
