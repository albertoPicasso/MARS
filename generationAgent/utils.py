from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, AIMessagePromptTemplate
from langchain_openai import ChatOpenAI

class Utils: 
        
    def get_promt_template(self) : 
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


    def build_LLM(self): 
        
        api_key = self.get_api_key_from_file()
        
        if (not (api_key == None)):
            llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18",
                            api_key=api_key)
            return llm
        
    def get_api_key_from_file(self, file="generationAgent/apiFile.txt"):
        try:
            with open(file, "r") as f:
                api_key = f.read().strip()
            return api_key
        except Exception as e:
            return None
        
        
