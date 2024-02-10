# Bee-AI Chatbot

Bee-AI is a chatbot built using Flask and OpenAI's GPT-3.5 language model, designed to provide assistance through text-based conversations. It utilizes various tools and APIs to offer a range of functionalities, including information extraction, web browsing, and mobile payment integration.

## Features

- **Text-based Conversations**: Users can interact with the chatbot via text messages.
- **Natural Language Processing**: Bee-AI leverages OpenAI's GPT-3.5 model for natural language understanding and response generation.
- **Tool Integration**: It incorporates various tools and APIs to perform tasks such as information extraction, web browsing, and mobile payment processing.
- **Continuous Conversation Loop**: The chatbot maintains a continuous conversation loop, allowing users to engage in multiple exchanges.
- **Customizable System Message**: Users receive a customizable system message outlining the chatbot's capabilities and instructions on usage.

## Tools and APIs Used

- **Google Serper API**: An API for accessing search engine results pages from Google.
- **Safaricom Daraja API**: An API provided by Safaricom for mobile payment integration in Kenya.


## Planned Additions

- **Enhanced Natural Language Understanding**: Implement advanced techniques to improve the chatbot's comprehension of user queries.
- **Additional APIs**: Integrate more APIs to expand the chatbot's capabilities, such as location-based services, weather forecasting, and language translation.
- **User Authentication**: Implement user authentication mechanisms for personalized interactions and data security.
- **Multimedia Support**: Enable support for multimedia content, such as images, videos, and audio files, in conversations.

## Usage

To interact with Bee-AI, follow these steps:

1. Clone the repository: `git clone https://github.com/yourusername/Bee-AI.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the Flask server: `python main.py`
4. Send messages to Bee-AI via HTTP POST requests to `http://localhost:5000/chat`.

## Future Enhancements

In future updates, we plan to add the following features and integrations:

- Integration with Twilio API for handling SMS messages.
- Expansion of toolset to include additional functionality such as language translation and sentiment analysis.

## Contributors



## License
licensed under the [MIT License](LICENSE)
