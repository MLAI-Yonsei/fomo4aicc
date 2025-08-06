import os
import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM

class LlamaEngine():
    def __init__(self, llama_version):
        model_path = f"../models/models--{llama_version.replace('/','--')}"
        os.environ['TRANSFORMERS_CACHE'] = model_path

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path, use_auth_token=True)
            self.model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.bfloat16, device_map="auto", use_auth_token=True)
        except OSError:
            self.tokenizer = AutoTokenizer.from_pretrained(llama_version, cache_dir=model_path, use_auth_token=True)
            self.model = AutoModelForCausalLM.from_pretrained(llama_version, cache_dir=model_path, torch_dtype=torch.bfloat16, device_map="auto", use_auth_token=True)

    def get_chat_response(self, messages: list, seed: int = 0, max_tokens=1024):
        pipeline = transformers.pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
        )

        prompt = pipeline.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )

        terminators = [
            pipeline.tokenizer.eos_token_id,
            pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        outputs = pipeline(
            prompt,
            max_new_tokens=max_tokens,
            eos_token_id=terminators,
            do_sample=False,
            temperature=0.0,
            top_p=1.0,
        )

        response = outputs[0]["generated_text"][len(prompt):]
        return response