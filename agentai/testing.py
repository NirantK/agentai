from api import chat_complete
from conversation import Conversation
from vectordb import ChromaDB, Query
from annotations import tool, ToolRegistry


GPT_MODEL = "gpt3.5-turbo"
# From SQLite Document Code
# agentai_functions = [json.loads(func.json_info) for func in [get_best_documents]]


agent_system_message = """You are ChinookGPT, a helpful assistant who gets answers to user questions from the Chinook Vector Database.
Be as precise as possible to your users
Begin!"""

search_docs_registry = ToolRegistry()

db = ChromaDB.doc_loader("layout-parser-paper.pdf")


@tool(registry=search_docs_registry)
def get_docs(query: Query):
    return db.get_docs(query)


doc_conversation = Conversation()
doc_conversation.add_message(role="system", content=agent_system_message)
doc_conversation.add_message("user", "Hi, what are the top 3 features of layoutparser?")
assistant_message = chat_complete(
    conversation=doc_conversation,
    model=GPT_MODEL,
    callable_function=get_docs,
)

doc_conversation.display_conversation(detailed=True)
