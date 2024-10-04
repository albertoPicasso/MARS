<table  border="0">
  <tr>
    <td><img src="images/logo.png" alt="Logo" width="150"></td>
    <td>
      <h1>MARS</h1>
      <p><i>(Multi-Agent RAG System)</i></p>
    </td>
  </tr>
</table>

<h2>What is MARS? </h2>
<p>MARS is an intuitive platform designed for the rapid and effortless creation of RAG systems using your own PDF files. It offers a comprehensive suite of tools for seamless document interaction, encompassing everything from an  user interface to  database management and response generation.</p>
<p>Additionally, MARS allows each user in the system to have up to three different knowledge bases from which context can be retrieved.</p>

<h2>MARS architecture</h2>
<td><img src="images/architecture.png" alt="Architecture" width="500"></td>

<h3>View Agent</h3>
<p>It is responsible for providing a user interface, managing the conversation history, and accessing the selected knowledge base. In this case, the agent is designed for a <b> single user</b>.</p>

<h3>Control Agent</h3>
<p>It is responsible for user authentication as well as controlling which databases they own (up to a maximum of 3). It also manages the system's logic, deciding which agent to call and determining the format of the information sent to them in order to fulfill the tasks requested by the user. The agent is designed for a <b> multi user</b>.</p>

<h3>Retrieval and Database Agent</h3>
<p>It is responsible for creating databases as well as monitoring their status. It handles direct interaction with them, including creating, deleting, and retrieving context from the databases. The agent is designed for a <b> multi user</b>.</p>

<h3>Generation Agent</h3>
<p>It is responsible for interacting with the language model to generate responses. The agent is designed for a <b> multi user</b>.</p></p>

<h2>How to use MARS? </h2>
<ol>
  <li>Set up your virtual environment in python 3.10 and install the required libraries listed in the requirements.txt file.  
   </li>
    <p><pre><code>
    pip install requirements.txt</i></p></code></pre>
  <p> </p>
  
  <p> </p>
  
  <li>Configure the port and network interface for each agent.</li>
  <p>Flask is used as the server, so modifying the line where these parameters are configured will be sufficient.</p>
  <p><pre><code>
    def run(self):
        self.app.run(port=5005, debug=False)</i></p></code></pre>
  <p> </p>
  
  <li>Configure each agent to enable communication with the other agents.</li>
  <p>To do this, you must fill in the fields of the information files with the appropriate data. These files are located in the <i>configFiles</i> folder, with one in the <i>View Agent</i> and another in the <i>Control Agent</i>. Only the required information should be changed; do not alter the field names. These files are used to populate the configuration classes.</p>
<p> </p>
<td><img src="images/configFiles.png" alt="configFiles" width="150"></td>
  
  <li>Provide the OpenAI key</li>
  <p>In the <i>Generation Agent</i>, create a file named <i>apiFile.txt</i>, which should contain the OpenAI API key necessary for using the LLM.</p>
</ol>
<p> </p>
<p> </p>

<em>Notice</em>
<p>In order for a user to interact with the Control Agent, they must have their username and password stored in the database. Currently, only the provided example user is entered. If you want to modify, add a different user, or create an automated system for adding users, this should be done in the insert_users function of the file <i>controlAgent/databaseManager.py</i>.

The current implementation looks like this: 

<pre><code>def insert_users(self):
    user_id = self.add_user('al', 'veryDifficultPass')
    if user_id:
        self.add_databases(user_id)</code></pre>
</p>

<h2>How does encryption work in MARS?</h2>
<p>Due to the use of the HTTP protocol instead of HTTPS, all messages containing sensitive content are sent encrypted manually in a message with the following format: </p><p><i>{'cipherData': CipherJson}</i></p>
<p></p>
<p>All messages use the same function found in the <i>cryptoManager.py</i> file, but with different keys. Whenever a message is sent to an agent, it is encrypted with the recipient's key, and when a response is expected, it is decrypted using the same key that was used for encryption.</p>

<h2>Demo</h2>
<a href="https://youtu.be/inJnUh2JDbo" target="_blank">
    <img src="https://img.youtube.com/vi/inJnUh2JDbo/0.jpg" alt="Mira mi video" style="max-width: 100%; height: auto;">
</a>
<p> </p>
<p>    The test file contains notes on how Linux works.</p>

<h2>Known issues</h2>
<ul>
  <li>When a new database is created in an already used slot, the internal process works fine, but the previous message history is not cleared, and it is recommended to refresh the webpage.<p> </p></li>
  <li>There are some issues when deleting databases and content in the RAG Agent. This is due to background processes that do not complete execution when creating embeddings or accessing the database. Therefore, although the system updates its tables correctly, the vector databases and temporary files need to be deleted manually for now.<p> </p></li>
</ul>


<h2>Next steps</h2>
<p>Create a better way to receive data via JSON by defining schemas for the required data structure using Pydantic, and manage all related data encapsulated within a class instead of using individual variables.</p><p> </p>

<p>Enhance error handling and traceability by utilizing bitacoring.</p><p> </p>

<pEnhance the generation agent to enable internet search capabilities. </p><p> </p>

<h2>Technologies used</h2>
<ul>
  <li>Flask as server</li>
  <li>GPT 4o mini as llm</li>
  <li>Chroma as Vector Database</li>
</ul>
