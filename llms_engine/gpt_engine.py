import os
import openai
from openai import OpenAI

class GPTEngine():
    def __init__(self, gpt_version):
        if os.getenv('OPENAI_API_KEY') is None:
            print("====Plz enter your OPENAI API KEY====")
            self.api_key = input("API KEY : ")

        self.gpt_version=gpt_version
        self.client = OpenAI(
            api_key=self.api_key
        )

    def get_chat_response(self, messages: list, seed: int = 0, temperature=0, max_tokens=1024,  top_p=1, n=1):
        response = self.client.chat.completions.create(
            model=self.gpt_version,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=0,
            presence_penalty=0,
            n=n
        )

        if n > 1:
            all_responses = [response.choices[i].message.content for i in range(len(response.choices))]
            return all_responses

        return response.choices[0].message.content