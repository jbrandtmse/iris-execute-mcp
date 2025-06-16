# IRIS Terminal MCP Server Project Charter

## Overview

We propose a **Model Context Protocol (MCP) server for InterSystems IRIS** that replicates the behavior of
the IRIS terminal in a programmatic environment. This server will enable an AI agent or other client to
execute ObjectScript commands and SQL queries in an IRIS session – much like the functionality of the IRIS
WebTerminal – but exposed through the standardized MCP interface. The solution consists of two parts: an
IRIS-side ObjectScript backend that handles command execution, and a client-side component (in Python or
Node.js) that interfaces with IRIS and communicates via MCP. The design emphasizes configurability (IRIS
host, port, namespace, credentials), session persistence, and secure authentication, all without requiring
containerization.

## Architecture and Components

**1. IRIS ObjectScript Backend:**
On the IRIS server, we implement a backend class (or set of classes) in ObjectScript responsible for
maintaining an interactive terminal session. This backend closely follows the pattern of the IRIS
WebTerminal's core engine. In WebTerminal, a background IRIS job is launched for each terminal session,
which executes incoming commands and captures their output. We will adopt a similar approach: -
**Terminal Session Class:** Create a class (e.g., Terminal.Session) that can be JOBed to run an interactive
loop. This class will extend relevant system classes (as WebTerminal does by extending %CSP.WebSocket
and %Library.Routine) to utilize IRIS’s I/O redirection mechanisms. It will manage one IRIS
session, maintaining state (variables, default namespace, etc.) across multiple commands.
- **I/O Redirection and Capture:** The session class will open a pseudo-terminal device (using IRIS’s _X3._
ANSI terminal handling) and enable I/O redirection for that device. By calling
    ##class(%Device).ReDirectIO($$$YES), the class can intercept all output writes and reads. We will
override the low-level write routines (similar to WebTerminal’s wstr, wchr, etc.) so that any text sent to
the terminal device is captured and not actually printed to a console. Instead, output chunks will be
collected and sent back to the client. This means when ObjectScript code executed in the session writes to
the “terminal,” our overrides will package the output into a message rather than writing to a screen.
- **Command Execution Loop:** The session job will run a loop waiting for input commands and executing
them. It uses an inter-process communication mechanism to receive commands from the MCP client. In
WebTerminal, the child process calls a WaitCommand() method that blocks until a new command arrives
from the parent (the web socket process), then returns that command for execution. We will
implement a similar WaitForCommand() routine using a global or other signaling method (e.g., a named
global or a semaphore). Each iteration will: (a) enable output redirection (to capture any text the command
produces), (b) execute the next command (via the ObjectScript XECUTE command or invoking a routine),
and (c) disable redirection once done. After execution, an end-of-execution signal is generated,
including the current namespace and any error status. This lets the client know the command finished
and can also provide error text if an exception occurred.

```
1 2
```
```
3 4
```
```
5
```
```
4 6
```
```
1 2
```
```
7
7
```

**2. MCP Client Interface (Python/Node.js):**
On the client side, we provide a lightweight program that acts as the MCP server front-end. This component
can be implemented in **Python** (leveraging the InterSystems IRIS Native API) or **Node.js** (using the IRIS
Native SDK for Node.js). Its responsibilities:
- **Connection to IRIS:** On startup, the client reads configuration (environment variables or parameters) for
    IRIS_HOSTNAME, IRIS_PORT, IRIS_NAMESPACE, IRIS_USERNAME, and IRIS_PASSWORD. It
uses these to establish a connection to the IRIS instance. In Python, for example, we would use
    irisnative.Connection() to connect to the IRIS super-server (the standard 1972 port) with the given
credentials. In Node.js, the intersystems-iris-native module provides similar connectivity.
Successful authentication is required to proceed – the IRIS backend will thus run in the context of the
specified IRIS user, ensuring all permissions and data access adhere to IRIS’s security.
- **Launching IRIS Session:** Once connected, the client initializes the IRIS terminal session. This can happen
in one of two ways: (a) by explicitly launching the ObjectScript session loop via a class method (e.g., calling
    Terminal.Session.Start() which JOBs a new process on the IRIS server), or (b) by relying on the
persistent connection’s process as the session (in IRIS, a connected process can itself execute commands
sequentially). The design leans toward the first approach for full fidelity – we invoke a class method that
creates a new background process for the session. The MCP client will receive a session identifier or simply
use the connection’s context to reference this new job.
- **MCP Protocol Handling:** The client side implements the MCP protocol, which standardizes how an AI
agent invokes tools. We will support **two modes** of MCP communication:
- **Standard I/O (STDIO) mode:** The MCP server can run as a standalone process (for example, launched by
an AI agent locally). In this mode, the Python/Node program reads MCP requests (likely JSON or a similar
structured format) from STDIN and writes responses to STDOUT. Each request will contain the IRIS
command to execute (and possibly a session ID if multiple sessions are handled), and the response will
contain the command’s output and status.
- **HTTP mode:** Alternatively, the MCP server can be run as a lightweight HTTP server (for example, using
FastAPI with Uvicorn in Python). In this mode, the AI agent calls a REST endpoint (specified by a full URL) to
issue commands. The design allows specifying a base URL for the server if using HTTP integration. A single
HTTP endpoint (e.g. /execute) will accept POST requests containing a command (and session token if
applicable) and will respond with JSON containing the execution results. This gives flexibility to deploy the
MCP server on a network and have the AI connect over HTTP (with optional TLS for security). The **full URL** of
the MCP service can thus be configured when integrating via HTTP.

```
Command Dispatch and Response: Upon receiving a command via MCP (from STDIN or HTTP), the
client component will forward it to the IRIS backend session and wait for the result. If we have
launched a background IRIS job, the client could set the command into a known global or queue that
the IRIS session’s WaitForCommand() is polling. For example, the client might do:
^TerminalQueue(sessionId) = $lb("m", "<command text>") and signal the session (e.g.,
by releasing a semaphore or setting an event). The IRIS session then picks up the command,
executes it, and produces output. The output and any errors will be captured by our ObjectScript
hooks and stored (perhaps in another global or in the connection’s memory) as chunks. The client
then retrieves that output. In practice, the WebTerminal uses a SendChunk($ZPARENT, ...) call
in the child process to push output chunks to the parent. In our design, since the MCP client
actively awaits the result, it can simply gather all output text from the session once execution is
done. For instance, the IRIS class could accumulate the output in a global
^TerminalOutput(sessionId) or return it via a dedicated method. The MCP client will format
this into the MCP response structure.
```
```
8
```
### •

```
6 9
```

```
Maintaining Session State: The same IRIS session process remains active for sequential
commands, so state persists. If a user sets a variable or changes namespace in one command, later
commands in that session will reflect those changes (just as in an interactive IRIS Terminal). This
behavior matches a real terminal session. The IRIS backend can also explicitly include the current
namespace or prompt in the output if needed (WebTerminal, for example, sends an updated
namespace prompt after each command via the "end" message ). We can include the namespace
in the MCP response to inform the agent of the context (useful if the agent needs to be aware of
namespace changes).
```
**3. Multi-Session Support (Optional):**
By default, the design pairs each MCP client (each AI or user process) with a single IRIS session. However, it
is feasible to support multiple concurrent sessions if needed. In an HTTP deployment, for example, the
server could handle requests from multiple agents by including a session identifier in requests. We would
maintain a pool or map of IRIS session jobs keyed by session ID. Each new session request spawns a fresh
IRIS background job (or opens a new IRIS connection) and stores it. Subsequent commands with that
session ID are routed to the correct IRIS process. This approach ensures isolation between sessions. The
WebTerminal architecture itself is inherently multi-session (one background job per web client) and we can
mirror that structure here. Proper cleanup (job termination) would be done when a session is closed or
after a period of inactivity. (If multi-session proves complex to implement initially, the server can start with a
single-session-per-process design, which is acceptable for one-to-one AI agent use and then be extended
later.)

## Connection, Configuration, and Security

**Configuration Parameters:** The MCP server should be flexible to point at any IRIS instance. The following
parameters will be supported, via environment variables, config files, or command-line options: - **IRIS
Hostname/IP and Port:** Network location of the IRIS server. For a local IRIS, this might be localhost and
the default superserver port 1972. These correspond to IRIS_HOSTNAME and IRIS_PORT. If
connecting over HTTP (to an IRIS web gateway), a full URL can be specified instead (e.g. [http://iris-](http://iris-)
server:52773/csp/sys/...), though the preferred approach is using the native superserver protocol for
full terminal functionality. - **Namespace:** The IRIS namespace in which to start the session. The client
will pass this to the IRIS backend (our Terminal.Session class will ZNAMESPACE to that context upon
start). If the user of the MCP server does not specify one, a default (like USER) will be assumed. -
**Credentials:** IRIS username and password for authentication. These are required to open the IRIS
connection or to JOB the session with the proper user. Only users with legitimate IRIS accounts and
sufficient privileges will be able to execute commands. (For example, using the IRIS-managed _SYSTEM
account for administrative tasks, or a limited user account for restricted operations.) - **MCP Endpoint
Config:** If using STDIO mode, no additional config is needed beyond launching the process. If using HTTP
mode, the server may allow specifying the listen port (e.g., default 8000) or full URL path. This way, an AI
agent can be configured with something like a target URL [http://localhost:8000/](http://localhost:8000/) if it’s using HTTP. In
Claude’s Desktop integration example, the configuration under "mcpServers" shows how an
environment can specify the command to run or the env variables for MCP servers – our server will
fit into such a scheme.

**Authentication Flow:** The client component will handle authentication at two levels: - **IRIS Login:** As
described, it uses the provided IRIS credentials to connect. If the login fails, the MCP server will return an
error and abort the session start. (In an HTTP scenario, the endpoint could respond with an HTTP 401 if

### •

```
7
```
```
8
```
```
10
```
```
11
```
```
12 13
```

credentials are bad, or include an error in the JSON response.) All executed commands run under this IRIS
account’s context, so IRIS’s role-based access control is in effect. This prevents unauthorized actions – e.g., if
using a non-privileged account, system-sensitive commands or global access will be denied by IRIS.

- **MCP Access Control:** If needed, an API key or token can be configured for the MCP HTTP mode to prevent
arbitrary outside use. Since the MCP server might be interfacing with an AI, this may not be exposed
publicly, but for completeness, one can include a simple auth (like a shared secret the AI client knows). In
STDIO mode, this is not applicable (the process is directly started by the agent).

**Security Considerations:** Executing arbitrary commands on IRIS is powerful, so we must ensure that only
intended clients can interact. By using IRIS’s own authentication, we rely on IRIS to vet permissions.
Additionally, the MCP server will _not_ permit OS-level command execution by default (i.e., the special IRIS
terminal syntax !command or $command will either be disabled or treated carefully). (Notably, a
community contribution to WebTerminal demonstrated adding support for OS commands by intercepting
input that begins with!. In our design, we may initially exclude this for security, or include it as an
optional feature behind a setting. If enabled, it would use a similar approach: detect a leading! in the
command and use the ObjectScript OPEN command with the "Q" option to run an OS shell command
, capturing its output, as was done in that WebTerminal hack. This must be restricted to trusted users.)

Because we aim to avoid containerization, the server will run directly on the host environment. That means
it inherits the security context of the machine and the IRIS instance. Standard best practices should be
followed: e.g., do not hardcode credentials, use TLS if connecting to IRIS over a network, and possibly log or
audit the commands run for traceability. IRIS’s audit log can capture Terminal commands if configured,
which might be useful when an AI is issuing commands.

## Command Execution and Output Handling

**Execution Sequence:** For each command issued by the client (AI): 1. **Receive Command:** The MCP front-
end (Python/Node) receives a request (from STDIN or HTTP) containing the command text. For example, the
AI might send: { "action": "execute", "code": "WRITE ##class(Example.Util).Hello()" }.

2. **Send to IRIS Session:** The client then injects this command into the IRIS session. If using our background
job model, the client can call a method or set a global that the waiting IRIS process will pick up. In
WebTerminal’s design, the parent process uses a global or inter-process queue to hand the command to the
child, which is exactly what our WaitForCommand will retrieve. For instance, we might implement
    Terminal.Common.SendCommand(sessionId, cmd) that places the command into
    ^TerminalQueue(sessionId) and signals the session.
3. **Execution in IRIS:** The Terminal.Session process, which has been blocked in WaitForCommand(),
now obtains the command. It then executes it in the IRIS context via XECUTE (or if the command is
actually a structured request, it might call other class methods – but simplest is to treat the text as an
ObjectScript line). We wrap this execution in an error trap to catch any runtime exceptions – $ZERROR is
captured. Also, output is being redirected at this time. All standard output (from writes, prints, or the
implicit output of a command) will _not_ go to a real terminal; instead our overridden write routines will
collect the output into a buffer. For example, our wstr(str) method will receive each chunk of text that
would have been printed, and we implement it to append str to an output variable and also possibly
update $X/$Y (cursor position) appropriately. Control characters (like newline, form feed) are handled by
specialized routines (as shown in WebTerminal’s wnl , wff , etc.) which we also implement to capture
those as text (e.g., convert to "\r\n" for newline). By the end of the command’s execution, we

```
14 15
```
```
16
```
```
1
```
```
6
```
```
17 18
```

have an **output buffer** containing everything that would have appeared in a traditional IRIS terminal for
that command. If the command invoked a **READ** (waiting for user input), our rstr/rchr hooks would
kick in – these send a message back to the client indicating input is needed. (In our MCP scenario,
handling interactive READs may be beyond scope, but the mechanism exists to prompt the AI for input if
necessary.)

4. **Return Results:** After execution, the IRIS session signals completion. In WebTerminal, an "end"
message with the namespace and error status is sent. For MCP, the client can now retrieve the output
buffer and error info. The Python/Node client assembles the response to the AI. For STDIO, this could be a
JSON object like: { "output": "<captured output text>", "error": null, "namespace":
"USER" }. If using HTTP, the response body would contain the same JSON. The output text will exactly
mirror what the IRIS Terminal would have shown if the user ran that command manually. For example, if
the command was WRITE 2+2, the output would be 4. If the command changed the namespace ( ZN
"SAMPLES"), the next prompt’s namespace would be different – we include that in the response so the
agent knows the context changed. Any error thrown (e.g., a reference to an undefined variable) would be
caught; the error text ($ZERROR) can be returned in an "error" field and the output might include IRIS’s
error message as well.

```
Prompting (if needed): In an interactive human terminal, after each command IRIS prints a new
prompt (USER>). In the MCP server context, we do not necessarily need to send a prompt each
time – the AI likely doesn’t need a visual prompt. However, we do maintain the notion of the current
prompt internally. If the AI queries it or if it’s useful for debugging, we could provide it. The
WebTerminal ensures the prompt is on a new line by outputting a newline (write !!) before
sending the end signal. We might replicate a similar behavior so that if someone were to view
the output, it’s nicely formatted. But primarily, the MCP response will contain the final accumulated
output.
```
**Example:** Suppose the AI requests to execute two commands in sequence: - First command: SET X=
WRITE "X is ",X. The MCP server forwards this to IRIS. The IRIS session sets the variable and writes the
text. The output captured would be: X is 5. This is sent back as output. The AI sees {output: "X is
5", error: null}.

- Second command: WRITE X*2. The IRIS session still has X in memory from the previous command
(since it’s the same session). So it computes X*2 = 10 and writes 10. The output 10 is captured and
returned. This demonstrates that state was preserved across calls, just like a real terminal (where you would
get 10 as output without needing to set X again).

**Leveraging WebTerminal Code:** Our design is heavily informed by the WebTerminal project. In fact, we can
reuse portions of its logic to reduce implementation effort: - The ObjectScript class for the session can
incorporate code from **WebTerminal.Core**. WebTerminal.Core already implements the redirection hooks
(wstr, wnl , etc.) and the command loop, as shown in its source. We can trim or adapt this for
MCP (e.g., remove browser-specific commands like autocompletion unless needed). The license of
WebTerminal is MIT, so reuse is permitted. - We do not need the CSP.WebSocket part of
WebTerminal.Engine, since our client replaces the web socket. Instead, our Python/Node client will fulfill the
role of routing messages. But the **communication protocol** (the format of messages between the front-
end and IRIS session) can be simpler here. For example, WebTerminal used $LISTBUILD with flags like
"o" , "e" , "r" to denote output, end, and read requests. We can similarly define that internally.
However, externally to the AI we will present a clean JSON or text interface (hiding these flags). - By
mimicking WebTerminal’s approach, we ensure even complex terminal interactions (like running %SYSTEM

```
19
```
```
7
```
### 1.

```
20
```
```
4 6
```
```
21
```
```
22
```

routines, which produce paged output or ANSI text) are handled correctly. For instance, terminal control
sequences or multi-line output are already managed by the X3.64 device and our capture hooks. This is a
robust solution tested in WebTerminal. Nikita Savchenko (WebTerminal’s author) noted that using
%CSP.WebSocket and _“mixing globals and/or interprocess communication you can achieve pretty much any
result”_ – our design takes the same philosophy by mixing IRIS globals for comms and IRIS device control
for capturing I/O.

## Deployment and Usage

**IRIS Side Installation:** We will package the ObjectScript classes as an InterSystems package (could be
delivered via ZPM or an importable XML). It will include classes like Terminal.Session,
Terminal.Common, etc., analogous to WebTerminal’s classes. After importing, a user might need to
grant permissions (e.g., the %Developer role if using system routines) to the service account. No special
web application is required on IRIS (unless HTTP mode is desired and we choose to implement the IRIS side
as a CSP service – but our plan is to handle HTTP in the external program, not in IRIS).

**Client Side Setup:** The Python or Node.js MCP server will be provided as a script or module (for instance, a
PyPI package mcp-server-iris exists and we align with its approach ). Users will run this program,
supplying configuration either via environment or command-line. For example:

```
Using Python: Install the package and run
iris_mcp_server.py --hostname localhost --port 1972 --namespace USER --
username _SYSTEM --password SYS. This will start listening for MCP commands (either opening
a JSON-RPC over STDIN or starting a web server).
```
```
Using Node.js: A similar CLI could be provided, or integrated into a Node-based agent system.
```
In an AI platform like Claude or others that support MCP, the configuration block would point to this server.
For instance, in Claude’s desktop config one would add an entry for the IRIS MCP server with the command
to run it and the environment variables. The example given on Open Exchange for a similar tool shows
how these are set. We will document usage for both modes (STDIO and HTTP).

**Operation:** Once running, the MCP server awaits requests. If the AI is integrated correctly, it will send an
initial handshake (some MCP implementations ask the tool to describe itself or list available functions). We
can handle a basic **“describe”** query by returning something like: _Tool name: "IRIS Terminal"; description:
"Executes InterSystems IRIS ObjectScript commands in a terminal session"; inputs: "ObjectScript command string";
outputs: "Command output text"._ After that, actual execute requests will be processed as detailed. The user
(or AI developer) can test the server by sending a known command. For example, issuing a command to
retrieve the IRIS version: WRITE $ZVERSION. The server should respond with the version string of IRIS
(e.g., _"IRIS for Windows (x86-64) 2023.1 (Build 215)"_ ). This confirms the session is live and using the correct
namespace/user context.

**No Container Needed:** This design avoids requiring a Docker container by running everything in the host
OS. As long as the host has an IRIS instance (which could itself be containerized or not, but the MCP server
just treats it as a host:port endpoint), and the host has the programming environment for the client side,
we’re set. We assume the IRIS Native API libraries are available (for Python, this is achieved by installing the

```
3
```
```
23
```
```
24
```
### •

### •

```
12
12
```
```
25
```

intersystems-iris Python package, which includes the necessary client libraries; for Node, the
intersystems-iris-native NPM package would be used). The absence of a container means the
deployment is simpler in many cases – it can run on a developer’s machine or a server where IRIS is
installed, with minimal overhead. (If one did want containerization, it’s still possible to dockerize this MCP
server along with an IRIS instance, but that remains optional.)

## Conclusion

In summary, the IRIS Terminal MCP server is designed to act as a powerful bridge between AI agents and
the InterSystems IRIS data platform. It allows execution of arbitrary IRIS commands in a controlled session,
echoing the capabilities of the proven WebTerminal application in a non-GUI context. By combining
ObjectScript on the server (to leverage IRIS’s internal mechanics for terminal I/O) with a modern client-side
MCP adapter (in Python or Node.js), we achieve an integration that is both **feature-rich** and
**straightforward to use**.

Key features of the design include:

```
Persistent IRIS Sessions per client, maintaining state and context just like an interactive IRIS
Terminal.
Full Command Support , from simple expressions to class method calls, and even interactive
behaviors (reads or multistep operations), thanks to the use of IRIS’s terminal control routines
.
Configurable Connectivity , allowing specification of IRIS host, port, namespace, and user
credentials at runtime. Authentication is enforced to protect data and operations.
Flexible MCP Exposure , supporting direct process integration (STDIO) or deployment as a
microservice (HTTP REST API) depending on the AI platform’s needs. In either case, the payloads are
structured (JSON-based), and multiple sessions can be handled if needed by scaling background
jobs.
No Container Requirement , making it easy to run in existing environments (e.g., on a developer’s
IRIS instance or a test server) – install the ObjectScript classes and the client package, then launch
the MCP server process.
```
By following this design, developers can **programmatically drive IRIS as if at a terminal** , enabling use
cases like AI-assisted database queries, schema exploration, system management, and more, all through
natural language instructions mediated by an intelligent agent. This specification draws upon the robust
architecture of IRIS WebTerminal and adapts it to the modern MCP tool ecosystem, ensuring that our
solution is both reliable and deeply integrated with IRIS’s capabilities.

**Sources:**

```
InterSystems WebTerminal project (open-source) – provided insight into capturing terminal I/O in
IRIS and handling communication between processes.
Dmitry Maslennikov’s IRIS MCP Server (CaretDev) – configuration example for IRIS connection
parameters.
InterSystems Developer Community articles – confirmation of WebTerminal’s use of
%CSP.WebSocket and interprocess globals , and examples of extending WebTerminal for OS
commands.
```
### • • 4 6 • 8 • • 3 •

```
1 4 2 6
```
-
    8
-
    3
14 15


Caché WebTerminal v4 Release | InterSystems Developer
Community |
https://community.intersystems.com/post/cach%C3%A9-webterminal-v4-release

Web Sockets | InterSystems Developer Community | Java|Frontend|Caché
https://community.intersystems.com/post/web-sockets

GitHub - caretdev/mcp-server-iris: InterSystems IRIS MCP server
https://github.com/caretdev/mcp-server-iris

Package
https://openexchange.intersystems.com/package/mcp-server-iris

Add OS command execution to WebTerminal | InterSystems Developer Community
https://community.intersystems.com/post/add-os-command-execution-webterminal

GitHub - intersystems-community/webterminal: The first and the most powerful web-based terminal for
InterSystems IRIS®, InterSystems Caché®, Ensemble®, HealthShare®, TrakCare® and other products built
on top of InterSystems Data Platforms.
https://github.com/intersystems-community/webterminal

I can't get to work WebTerminal in IRIS Health Connect 2023.1 |
https://community.intersystems.com/post/i-cant-get-work-webterminal-iris-health-connect-

Package
https://openexchange.intersystems.com/package/bg-iris-agent

```
1 2 4 5 6 7 9 17 18 19 20 22
```
```
3
```
```
8 10 11
```
```
12 13 24
```
```
14 15 16
```
```
21
```
```
23
```
```
25
```

