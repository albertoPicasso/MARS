from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
import os


class Utils: 

    #Utils
    def build_LLM(self): 
        
        api_key = self.get_api_key_from_file()
         
        if (not (api_key == None)):
            llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18",
                            api_key=api_key)
            return llm
        
        
    def build_web_search_tool(self): 
        api_key = self.get_api_key_from_file("generationAgent/configFiles/tavilyAPI.txt")
        
        if (not (api_key == None)):
            os.environ["TAVILY_API_KEY"] = api_key
            return  TavilySearchResults()
        
        
    def get_api_key_from_file(self, file="generationAgent/configFiles/openAIAPI.txt"):
        try:
            with open(file, "r") as f:
                api_key = f.read().strip()
            return api_key
        except Exception as e:
            return None

    #Prompts utils 
        
    def get_context_promt_template(self) : 
        rag_prompt_template = PromptTemplate(
        template="""
        Contesta a la pregunta en base al contexto proporcionado y el historial de la conversación.

        Historial de conversación:
        {history}

        Contexto relevante:
        ```
        {context}
        ```

        Pregunta: {question}
        
        Al citar, incluye el título y la página de los mensajes de los que obtuviste la información. 
        Si no es necesario citar, puedes omitirlo. Evita parafrasear de manera que se pierda la flexibilidad del texto original. 
        Traduce el contexto si es necesario antes de leerlo.
        """,
        input_variables=["history", "context", "question"],
        )

        return rag_prompt_template
        
        
    def get_knowledge_prompt_template(self):
        
        knowledge_prompt_template = PromptTemplate(
            template="""
            Responde a la siguiente pregunta basándote únicamente en tu conocimiento general:

            Pregunta: {question}

            Proporcione una respuesta clara y concisa. Si es necesario, incluya ejemplos relevantes o explicaciones adicionales.
            """,
            input_variables=["question"],
        )
        
        return knowledge_prompt_template
    
    
    def get_web_search_prompt_template(self):
        web_search_prompt_template = PromptTemplate(
            template=""" 
            Utiliza la información proporcionada en el contexto de la búsqueda para responder a la siguiente pregunta de manera clara y precisa:

            Contexto: {context}

            Pregunta: {question}

            Respuesta: Asegúrate de que tu respuesta esté bien fundamentada y, si es necesario, incluye ejemplos relevantes o explicaciones adicionales basadas en el contexto proporcionado.
            """,
            input_variables=["question", "context"],
        )
        
        return web_search_prompt_template
    
    
    #Zero - shot - classifier
    def get_zsc_template(self):
        zero_shot_template = PromptTemplate(
        template="""
                Given the following context and message history, classify the user's question into one of the following categories:
                - "context": If the answer can be derived directly from the context or message history.
                - "knowledge": If the answer is available from your internal knowledge.
                - "search": If the answer cannot be derived from either and requires external information.

                Context: {context}
                Message History: {history}
                Question: {question}

                Classify the question as "context", "knowledge", or "search".
                Only return the class name
                If Class name is "search" return also a optimized and contextfull web_query with this format 
                search*optimized_query
                """,
        input_variables=["context", "history", "question"]
        )
        
        return zero_shot_template
    
    
    
    
    
    def format_context(self,context):
        """
        Formatea el contexto a partir del contenido de las páginas y los metadatos.
        
        Args:
        - context (list): Lista de diccionarios con `page_content` y `metadata`.
        
        Returns:
        - str: El contexto formateado como una cadena de texto.
        """
        formatted_context = []
        for doc in context:
            page_content = doc["page_content"]
            file_name = doc["metadata"]["file"]
            page_number = doc["metadata"]["page_number"]
            
            formatted_context.append(f"Archivo: {file_name} (Página {page_number})\n{page_content}")
        
        return "\n\n".join(formatted_context)


    def format_history(self,messages):
        """
        Formatea el historial de la conversación en una cadena de texto.
        
        Args:
        - messages (list): Lista de diccionarios con el historial de la conversación.
        
        Returns:
        - str: El historial formateado como una cadena de texto.
        """
        formatted_messages = []
        for message in messages:
            if message["type"] == "HumanMessage":
                role = "Usuario"
            elif message["type"] == "AIMessage":
                role = "IA"
            else:
                role = "Desconocido" 
            formatted_messages.append(f"{role}: {message['text']}")
        
        return "\n".join(formatted_messages)
        
        
