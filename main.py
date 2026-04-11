# Example of Error Handling:
# try:
#     response = client.messages.create(...)  # API call that might fail
#     print(response.content)
# except anthropic.APIConnectionError as e:
#     print(f"No internet connection: {e}")
# except anthropic.AuthenticationError:
#     print("Bad API key — check your .env file")
# except Exception as e:
#     print(f"Unexpected error: {e}")  # catch-all


def main(self):
    print(f'Hello World!')

if __name__ == '__main__':
    main('PyCharm')