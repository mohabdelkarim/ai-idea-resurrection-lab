import json
import requests
from typing import Dict, Any

class ResponseFormat:
    def __init__(self, type: str, schema: Dict[str, Any] = None):
        self.type = type
        self.schema = schema

    def to_dict(self):
        response_format = {"type": self.type}
        if self.schema:
            response_format["schema"] = self.schema
        return response_format

class OpenAIConnector:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    def generate_text(self, prompt: str, response_format: ResponseFormat = None):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "prompt": prompt
        }
        if response_format:
            data["response_format"] = response_format.to_dict()

        try:
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, data=json.dumps(data))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

def main():
    api_key = "YOUR_API_KEY"
    model = "gpt-4"
    connector = OpenAIConnector(api_key, model)

    prompt = "Generate a JSON object with a name and age"
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name", "age"]
    }
    response_format = ResponseFormat("json_schema", schema)

    result = connector.generate_text(prompt, response_format)
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()