
from flask import Flask, request, jsonify
import os
from twilio.twiml.messaging_response import MessagingResponse
from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationSummaryBufferM