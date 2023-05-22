from concurrent.futures import ThreadPoolExecutor, wait

from langchain import LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import LlamaCpp

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
# Verbose is required to pass to the callback manager

# Make sure the model path is correct for your system!
llm = LlamaCpp(
    model_path="./models/ggml-vic13b-uncensored-q4_0.bin", callback_manager=callback_manager, verbose=True
)

template = """
{history}
Human: {human_input}
Assistant:"""

prompt = PromptTemplate(
    input_variables=["history", "human_input"],
    template=template
)



executor = ThreadPoolExecutor(max_workers=1)

user_chats = {}

async def chat(userid: str, message: str):
    if not userid in user_chats:
        user_chats[userid] = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=True,
            memory=ConversationBufferWindowMemory(k=2),
        )
    chat_chain = user_chats[userid]

    return chat_chain.predict(human_input=message)
