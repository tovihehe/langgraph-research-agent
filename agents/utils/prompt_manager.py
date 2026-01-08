import json
from typing import Dict

class PromptManager:
    def __init__(self, config):
        self.config = config
        self.prompts_data = self.load_prompts()

    def load_prompts(self) -> Dict[str, str]:
        """
        Create and return a dictionary where:
        - The key is the name of the prompt (e.g. "examples", "is_sql_prompt"...)
        - The value is the content of the file.
        """
        prompts = {}
        for prompt_name, prompt_path in self.config.prompt_paths.items():
            with open(prompt_path, 'r', encoding='utf-8') as file:
                if prompt_name == "examples":
                    prompts[prompt_name] = json.load(file)
                else:
                    prompts[prompt_name] = file.read()
        return prompts

    def get_prompt(self, prompt_name) -> str:
        if prompt_name in self.prompts_data:
            return self.prompts_data[prompt_name]
        else:
            return None
