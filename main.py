from flask import Flask, request, jsonify

import os

from twilio.twiml.messaging_response import MessagingResponse

from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_models import ChatOpenAI
# from langchain_mistralai.chat_models import ChatMistralAI
from langchain.schema import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationSummaryBufferMemory

from Agent_Tools.tools import ExtractTillInformationTool, ExtractQrCodeInformationTool

from Functions.Browsing.functions import SearchTool
# from Functions.Apify.functions import CrawlWebsiteTool
from Functions.Mpesa.till.functions import PaymentTillTool
from Functions.Mpesa.paybill.functions import PaymentPaybillTool
from Functions.Mpesa.qr_code.functions import QrCodeTool

# from Agent_Tools.Voice.tools import record_and_transcribe, chatgpt, print_colored, text_to_speech

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")

system_message = SystemMessage(content="""
    " You are Bee, a helpful Assistant!",
    " As a wordlclass helpful assistant with more than 40 years of experience, you make sure users have a seamless conversation with you.",
    " Your will be helping users using the tools available for you, the tools include:",
                               
    "- ExtractInformationTool() -> Use this when extracting the required information from users query",
    "- PaymentTillTool() -> Use this to initiate payments to till accounts",
    "- PaymentPaybillTool()-> Use this to initiate payments to paybill accounts"
    "- ExtractQrCodeInformationTool() -> Use this to extract qrcode informations
    "- QrCodeTool() -> use this to generate qrcode" 
    "- SearchTool() -> Use this to do a search on the web using googleserper",
    "- CrawlWebsiteTool, -> Use this to crawl websites"
    " Your goal is to interpret user input, understand their intentions, and categorize them to streamline a smooth conversation",
    " You are capable of browsing the web using the search tool and making payments .",
    " Use the  search to add Emojis in your conversation"
    " Respond with the language the user uses. If the uses texts in 'English' respond in 'English, If the user texts in 'Sheng' respond in 'Sheng', if the user texts in 'Swahili' respond in 'Swahili'."
    " Don't make things up"
    " Keep your answers as short as possible"
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