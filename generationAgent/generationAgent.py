from cryptoManager import CryptoManager
from flask import Flask, request,jsonify, abort, make_response
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import json
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableMap
from langchain_core.runnables import RunnableLambda

class GenerationAgent: 
    
    def __init__(self):
        self.app = Flask(__name__)            
        self.setup_routes()
        self.llm = self.build_LLM()

        
    def setup_routes(self):
        self.app.add_url_rule('/generationwithmessagehistory', 'generationwithmessagehistory', self.generationwithmessagehistory, methods=['POST'])
       
       
       
    def generationwithmessagehistory(self):
        #Get data
        encrypted_data = request.get_json()

        if isinstance(encrypted_data, str):
            encrypted_data = json.loads(encrypted_data)

        cipher_text = encrypted_data.get('cipherData')
        decrypted_data = CryptoManager.decrypt_text(cipher_text)
        data = json.loads(decrypted_data)
        
        messages = data["chat"]
        context_data = data["context"]
        context = json.loads(context_data)
        
        #Get question and history
        question = messages.pop(-1) 
        
        #Prepare the promt 
        history_str = self.format_history(messages)
        context_str = self.format_context(context)

        #prompt_template = self.build_rag_prompt(history_str=history_str, context_str=context_str, question=question)
        rag_prompt_template = self.get_promt_template()
    
        
        prompt = rag_prompt_template.invoke({
            "context": context_str,
            "history": history_str,
            "question": question
        }).to_messages()
        
        
        response = self.llm.invoke(prompt)
        generation:str = response.content
        #generation = response
        
        data = {
            "generation" : generation
        }
        
        json_data = json.dumps(data)
        cipher_response = CryptoManager.encrypt_text(json_data)
        return jsonify({"cipher_response": cipher_response}), 200







    #Aux functions
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    def get_promt_template(self) : 
        rag_prompt_template = ChatPromptTemplate.from_template("""
        Contesta a la pregunta en base al contexto proporcionado y el historial de la conversación.

        Historial de conversación:
        {history}

        Contexto relevante:
        ```
        {context}
        ```

        Pregunta: {question}
        """)
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



    def run(self):
        self.app.run(port=5008 , debug=True)

if __name__ == '__main__':
    generationAgent = GenerationAgent()
    generationAgent.run()