from cryptoManager import CryptoManager
from flask import Flask, request,jsonify, abort, make_response
import json
from utils import Utils

class GenerationAgent: 
    
    def __init__(self):
        self.app = Flask(__name__)            
        self.setup_routes()
        self.utils = Utils()
        self.llm = self.utils.build_LLM()

        
    def setup_routes(self):
        self.app.add_url_rule('/generationwithmessagehistory', 'generationwithmessagehistory', self.generationwithmessagehistory, methods=['POST'])
       
       
       
    def generationwithmessagehistory(self):
        """
        Generate a response based on message history and provided context.

        This endpoint receives encrypted data in the `cipherData` field, which contains a chat history 
        and additional context to generate a response to the last question. The expected structure of 
        the decrypted JSON is as follows:

        - `chat`: A list of messages in the conversation (array of strings).
        - `context`: Additional context relevant to the conversation (string).

        The function decrypts the `cipherData`, prepares the prompt using the provided message history 
        and context, invokes the language model to generate a response, and returns the encrypted 
        generated response. If any required fields are missing or an error occurs during processing, 
        an appropriate error message is returned.

        ---
        parameters:
        - name: cipherData
            in: body
            required: true
            description: Encrypted JSON string that contains chat history and context.
            schema:
            type: object
            properties:
                cipherData:
                type: string
                description: The encrypted data representing chat history and context.

        responses:
        200:
            description: Response generated successfully.
            schema:
            type: object
            properties:
                cipher_response:
                type: string
                description: The encrypted generated response based on the message history and context.
        400:
            description: Missing required fields in the JSON request.
            schema:
            type: object
            properties:
                error:
                type: string
                example: "Faltan argumentos en el JSON"
        500:
            description: Internal server error occurred during processing.
            schema:
            type: object
            properties:
                message:
                type: string
                example: "Error in RAD Agent"
        """
        #Get data
        try:
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
            history_str = self.utils.format_history(messages)
            context_str = self.utils.format_context(context)

            rag_prompt_template = self.utils.get_promt_template()
        
            
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
        except Exception as e: 
            return jsonify({"message": "Error in RAD Agent"}), 500    





    def run(self):
        self.app.run(port=5008 , debug=True)

if __name__ == '__main__':
    generationAgent = GenerationAgent()
    generationAgent.run()