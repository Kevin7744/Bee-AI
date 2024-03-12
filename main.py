from flask import Flask, request, jsonify

import os

from twilio.twiml.messaging_response import MessagingResponse

from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_models import ChatOpenAI
# from langchain_mistralai.chat_models import ChatMistralAI
from langchain.schema import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationSummaryBufferMemory

from agent_functions.functions import ExtractTillInformationTool, ExtractQrCodeInformationTool

from agent_tools.Browsing.tools import SearchTool
# from agent_tools.Apify.tools import CrawlWebsiteTool
from agent_tools.Mpesa.till.tools import PaymentTillTool
from agent_tools.Mpesa.paybill.tools import PaymentPaybillTool
from agent_tools.Mpesa.qr_code.tools import QrCodeTool

# from Agent_Tools.Voice.tools import record_and_transcribe, chatgpt, print_colored, text_to_speech

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")

system_message = SystemMessage(content="""
You are Bee, a world-class assistant with extensive experience in facilitating seamless interactions for users. Your expertise lies in accurately interpreting user inputs and leveraging a suite of specialized tools to meet their needs effectively. Your toolkit includes:

ExtractInformationTool(): Deploy this tool to parse and understand the nuances of user queries.
PaymentTillTool(): Utilize this tool for initiating transactions to till accounts.
PaymentPaybillTool(): Employ this tool for making payments to paybill accounts.
ExtractQrCodeInformationTool(): Use this to decipher information from QR codes.
QrCodeTool(): This tool allows you to generate QR codes as needed.
SearchTool(): Leverage this for conducting web searches, employing Google's search capabilities.
CrawlWebsiteTool(): This tool is designed for web crawling, enabling you to extract information from various websites.
                               
Your primary objective is to understand the intent behind user queries and classify them effectively to ensure a smooth and efficient conversation flow. In addition to your core responsibilities, you are equipped with web browsing capabilities through the SearchTool, allowing you to enrich conversations with emojis and relevant web content.

Adaptability is key in your interactions. Match the user's language to ensure a personalized and relatable conversation. Whether the user communicates in English, Sheng, or Swahili, respond in kind.

Remember to uphold the principles of accuracy and brevity in your responses. Do not fabricate information and strive to keep your replies concise and to the point
Remember to keep you responses as short as possible.
""")


tools = [
    ExtractTillInformationTool(), 
    PaymentTillTool(),
    PaymentPaybillTool(), 
    ExtractQrCodeInformationTool(), 
    QrCodeTool(),
    SearchTool(),
    # CrawlWebsiteTool(),
]

agent_kwargs = {
    "extra_prompt_message": [MessagesPlaceholder(variable_name="memory")],
    "system_message": system_message,
}

memory = ConversationSummaryBufferMemory(memory_key="memory",
                                         return_messages=True,
                                         llm=llm,
                                         max_token_limit=250)


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
        return jsonify({"error": str(e)}), 400  
    if user_input.lower() == "end":
        return jsonify({
            "message": "Have a good day!"
        })

    agent_response = agent({"input": user_input})
    print("Agent Response:", agent_response)  

    assistant_message_content = agent_response.get(
        "output", "No response from the assistant.")

    twilio_resp = MessagingResponse()
    twilio_resp.message(assistant_message_content)

    return str(twilio_resp)


# while True:
#     user_message = record_and_transcribe()
#     response = chatgpt(api_key, conversation1, chatbot1, user_message)
#     print_colored("Julie:", f"{response}\n\n")
#     user_message_without_generate_image = re.sub(r'(Response:|Narration:|Image: generate_image:.*|)', '', response).strip()
#     text_to_speech(user_message_without_generate_image, voice_id1, elapikey)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)