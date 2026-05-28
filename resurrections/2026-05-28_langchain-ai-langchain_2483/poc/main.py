import sys
class Agent:
    def __init__(self):
        self.response = ""
    def stream_final_response(self, response):
        self.response = response
        yield self.response
    def get_final_response(self):
        return self.response
class Observer:
    def __init__(self, agent):
        self.agent = agent
    def update(self, response):
        print(f"Received response: {response}")
def main():
    try:
        agent = Agent()
        observer = Observer(agent)
        response = "This is the final response"
        for final_response in agent.stream_final_response(response):
            observer.update(final_response)
        print(f"Final response: {agent.get_final_response()}")
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
if __name__ == "__main__":
    main()