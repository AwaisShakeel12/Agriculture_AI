
import os 
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI


from langgraph.graph.state import  CompiledStateGraph 
from langgraph.graph import  StateGraph, START, END
from IPython.display import display, Image

from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph.message import  add_messages
from typing import  Annotated, Sequence
from langgraph.graph import  MessagesState
from langgraph.prebuilt import  ToolNode, tools_condition
from typing_extensions import TypedDict
from typing import Literal
from dataclasses import dataclass
from pydantic import BaseModel, field_validator, ValidationError
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver


import operator
from langchain_core.messages import BaseMessage
from langchain_core.messages import RemoveMessage
from langchain_core.messages import trim_messages
from langchain_core.runnables import RunnableConfig

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

api_key

genai.configure(api_key=api_key)

llm_gemini =  ChatGoogleGenerativeAI(model='gemini-1.5-flash', api_key=api_key)
from langchain_groq import ChatGroq
groq_api_key = ''

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_api_key)
from langchain_community.utilities import OpenWeatherMapAPIWrapper

os.environ["OPENWEATHERMAP_API_KEY"] = ""

weather = OpenWeatherMapAPIWrapper()
from tavily import TavilyClient
import os 

client = TavilyClient(api_key='')

# response = client.search(query='what is bitcoin price today')

def weather_fun(location: str):
    """ 
    Search Weather of location
    
    Args:
        location (str): The location to get the weather for.
    
    Returns:
        str: The weather data.
    """
    weather = OpenWeatherMapAPIWrapper()
    weather_data = weather.run(location)
    print(weather_data)
    return weather_data



from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
web_search = TavilySearchResults(max_results=2)
tools: list[tool] = [web_search, weather_fun]

llm_with_tools = llm.bind_tools(tools)
sys_msg = SystemMessage(content="""You are ASAI, Follow these guidelines:
      
   
      
      you are a experienced agriculture  advisor  experience in farmer and agriculture with more then 10 years of experince,
      your job is to answer user  based {messages},
      answerr user query from your own knowledge  or  tool  web search,
      
      2- for example user have a quetion tell me about some spacific plant , so answer from your own knowledge or use web searcg
      to answeer,
      
      3 if user question is like we want to grow some crop ,  so you first need to know the location of user ,
        when you get the answer  use tool weather_fun  for checking the weather. , 
        use tool to get weather report so you recommend user a batter crops after knowing the condtion.
    
      
      """
      "Provide a general support response to the following query : {messages}"
      
                        
    )
def Agent(state: MessagesState)-> MessagesState:
   
    return {'messages':[llm_with_tools.invoke([sys_msg] + state['messages'])]}

builder: StateGraph= StateGraph(MessagesState)

builder.add_node('Agent',Agent)
builder.add_node('tools', ToolNode(tools))

builder.add_edge(START, 'Agent')
builder.add_conditional_edges('Agent', tools_condition)
builder.add_edge('tools', 'Agent')


memory: MemorySaver = MemorySaver()
graph: CompiledStateGraph= builder.compile( checkpointer=memory)

display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

