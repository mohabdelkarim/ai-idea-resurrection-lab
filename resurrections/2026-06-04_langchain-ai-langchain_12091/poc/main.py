import os
import json

class MemGPT:
    def __init__(self, model_name="basic"):
        self.model_name = model_name
        self.memory = {}

    def add_memory(self, key, value):
        self.memory[key] = value

    def get_memory(self, key):
        return self.memory.get(key)

class LangChain:
    def __init__(self):
        self.memgpt = MemGPT()

    def process_query(self, query):
        try:
            # Simulate processing query
            result = f"Processed query: {query}"
            return result
        except Exception as e:
            return f"Error processing query: {str(e)}"

    def add_memory(self, key, value):
        self.memgpt.add_memory(key, value)

    def get_memory(self, key):
        return self.memgpt.get_memory(key)

def main():
    langchain = LangChain()

    while True:
        print("1. Process Query")
        print("2. Add Memory")
        print("3. Get Memory")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            query = input("Enter your query: ")
            result = langchain.process_query(query)
            print(result)
        elif choice == "2":
            key = input("Enter key: ")
            value = input("Enter value: ")
            langchain.add_memory(key, value)
            print("Memory added successfully")
        elif choice == "3":
            key = input("Enter key: ")
            value = langchain.get_memory(key)
            if value:
                print(f"Value for key '{key}': {value}")
            else:
                print(f"No value found for key '{key}'")
        elif choice == "4":
            break
        else:
            print("Invalid option. Please choose a valid option.")

if __name__ == "__main__":
    main()