from flask import Flask, request, jsonify
import os
from twilio.twiml.messaging_response import MessagingResponse
from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationSummaryBufferMemory
from Agent_Tools.tools import ExtractTillInformationTool, ExtractQrCodeInformationTool
from Functions.Browsing.functions import SearchTool
from Functions.Mpesa.functions import PaymentTillTool, QrCodeTool
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

# Initialize ChatOpenAI with the specified model
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")

# Define the system message
system_message = SystemMessage(content="""
    "You are an helpful Assistant!",
    "As a wordlclass helpful assistant with more than 40 years of experience, you make sure users have a seamless conversation.",
    "Your will be helping users using the tools available, the tools include:",
                               
    "- ExtractInformationTool() -> Use this when extracting the required information from users query",
    "- PaymentTillTool() -> Use this to initiate payments with the response from ExtractInforomationTool(). ",
    "- ExtractQrCodeInformationTool(), 
    "-  QrCodeTool(),"
    "-  SearchTool(),",
    "Your goal is to interpret user input, understand their intentions, and categorize them to streamline a smooth conversation process.",
    "You are capable of browsing the web using the search tool and making payments .",
    "For instance, if a user inputs: 'pay 1000 shillings to 174379',"
    "Use the  search to add Emojis in your conversation"
    """)

# Define the tools and agent settings
tools = [
    ExtractTillInformationTool(), 
    PaymentTillTool(), 
    ExtractQrCodeInformationTool(), 
    QrCodeTool(),
    SearchTool(),
]

agent_kwargs = {
    "extra_prompt_message": [MessagesPlaceholder(variable_name="memory")],
    "system_message": system_message,
}

memory = ConversationSummaryBufferMemory(memory_key="memory",
                                         return_messages=True,
                                         llm=llm,
                                         max_token_limit=250)

# Create the agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    agent_kwargs=agent_kwargs,
    memory=memory,
    user_input_key="input"
)

# Continuous conversation loop
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.form["Body"]
    except Exception as e:
        return jsonify({"error": str(e)}), 400  # Bad Request for missing or invalid Body

    if user_input.lower() == "end":
        return jsonify({
            "message": "Have a good day!"
        })

    # Input the user message into the agent
    agent_response = agent({"input": user_input})
    print("Agent Response:", agent_response)  # Print for debugging

    # Access the assistant's response content from the output field
    assistant_message_content = agent_response.get(
        "output", "No response from the assistant.")

    # Prepare Twilio response
    twilio_resp = MessagingResponse()
    twilio_resp.message(assistant_message_content)

    # Return Twilio response
    return str(twilio_resp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)