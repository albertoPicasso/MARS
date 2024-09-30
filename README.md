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

<h2>MARS architecture</h2>
<td><img src="images/architecture.png" alt="Architecture" width="500"></td>

<h3>View Agent</h3>
<p>It is responsible for providing a user interface, managing the conversation history, and accessing the selected knowledge base. In this case, the agent is designed for a <b> single user</b>.</p>

<h3>Control Agent</h3>
<p>It is responsible for user authentication as well as controlling which databases they own (up to a maximum of 3). It also manages the system's logic, deciding which agent to call and determining the format of the information sent to them in order to fulfill the tasks requested by the user. The agent is designed for a <b> multi user</b>.</p>

<h3>Retrieval and Database Agent</h3>
<p>It is responsible for creating databases as well as monitoring their status. It handles direct interaction with them, including creating, deleting, and retrieving context from the databases. The agent is designed for a <b> multi user</b>.</p>

<h3>Generation Agent</h3>
  
