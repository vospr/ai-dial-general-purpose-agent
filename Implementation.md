# Task 13: General Purpose Agent - Complete Implementation Guide

## 📋 Overview

This guide provides step-by-step instructions for implementing a comprehensive General Purpose AI Agent with 6 major capabilities:

1. ✅ Core Agent with GPT-4o
2. ✅ File Content Extraction
3. ✅ RAG Search + Image Generation
4. ✅ Web Search (DuckDuckGo MCP)
5. ✅ Python Code Interpreter (MCP)
6. ✅ Multi-Model Support (Claude Sonnet)

**Time Estimate:** 8-12 hours for complete implementation  
**Complexity:** Advanced (⭐⭐⭐⭐⭐)

---

## 🚀 WSL Commands - Complete Setup

### Prerequisites

- Docker Desktop running
- DIAL API Key from EPAM
- EPAM VPN connected
- WSL2 with Ubuntu
- Python 3.11+

---

## Step-by-Step Implementation

### STEP 1: Core Agent Setup

#### 1.1: Navigate to Project

```bash
cd /mnt/c/Users/AndreyPopov/ai-dial-general-purpose-agent
```

#### 1.2: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Expected dependencies:
- `aidial-sdk` - DIAL application framework
- `aidial-client` - DIAL API client
- `langchain-openai` - LangChain OpenAI integration
- `langchain-community` - LangChain tools
- `faiss-cpu` - Vector store for RAG
- `aiohttp` - Async HTTP client

#### 1.3: Review File Structure

```bash
tree -L 3 task/
```

Expected output:
```
task/
├── agent.py                 # TODO: Agent orchestration logic
├── app.py                   # TODO: FastAPI application
├── prompts.py               # TODO: System prompt
├── tools/
│   ├── base.py              # TODO: BaseTool abstract class
│   ├── files/
│   │   └── file_content_extraction_tool.py
│   ├── rag/
│   │   └── rag_tool.py
│   ├── deployment/
│   │   ├── base.py
│   │   └── image_generation_tool.py
│   └── mcp/
│       ├── mcp_client.py
│       └── mcp_tool.py
└── utils/
    ├── constants.py
    ├── dial_file_content_extractor.py
    ├── history.py
    └── stage.py
```

#### 1.4: Configure DIAL Core

```bash
# Edit core/config.json
nano core/config.json
```

Add to `applications`:
```json
"general-purpose-agent": {
  "displayName": "General Purpose Agent",
  "description": "General Purpose Agent. Equipped with: WEB search (DuckDuckGo via MCP), RAG search (supports PDF, TXT, CSV files), Python Code Interpreter (via MCP), Image Generation (model).",
  "endpoint": "http://host.docker.internal:5030/openai/deployments/general-purpose-agent/chat/completions",
  "inputAttachmentTypes": ["image/png", "image/jpeg"],
  "forwardAuthToken": true
}
```

Add to `models`:
```json
"gpt-4o": {
  "displayName": "GPT 4o",
  "endpoint": "http://adapter-dial:5000/openai/deployments/gpt-4o/chat/completions",
  "iconUrl": "http://localhost:3001/gpt4.svg",
  "type": "chat",
  "upstreams": [
    {
      "endpoint": "https://ai-proxy.lab.epam.com/openai/deployments/gpt-4o/chat/completions",
      "key": "{YOUR_DIAL_API_KEY}"
    }
  ]
}
```

**⚠️ Replace `{YOUR_DIAL_API_KEY}` with your actual API key!**

#### 1.5: Start Docker Services

```bash
# Start DIAL infrastructure
docker compose up -d

# Wait for services
sleep 15

# Check services
docker compose ps -a
```

Expected services:
- `chat` (port 3000)
- `core` (port 8080)
- `themes` (port 3001)
- `redis` (port 6379)
- `adapter-dial`

#### 1.6: Implement Core Files

**Checklist:**
- [ ] `task/agent.py` - Implement `GeneralPurposeAgent` class
- [ ] `task/app.py` - Implement FastAPI application
- [ ] `task/prompts.py` - Create system prompt
- [ ] `task/tools/base.py` - Implement `BaseTool` abstract class

**Key Implementation:**

```python
# task/prompts.py
SYSTEM_PROMPT = """You are a General Purpose AI Agent with advanced capabilities.

**Available Tools:**
[Will be populated as tools are added]

**Instructions:**
- Use appropriate tools for each task
- Be concise and helpful
- Explain your reasoning
"""
```

#### 1.7: Test Step 1

```bash
# Terminal 1: Run agent
cd /mnt/c/Users/AndreyPopov/ai-dial-general-purpose-agent
source .venv/bin/activate
python task/app.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:5030
```

**Browser Test:**
1. Open http://localhost:3000/marketplace
2. Verify "General Purpose Agent" appears
3. Verify "GPT 4o" model appears
4. Test GPT-4o: "Hi, what can you do?"
5. Test Agent: "Hi, what can you do?"

---

### STEP 2: File Content Extraction

#### 2.1: Implement File Extraction Tool

```bash
nano task/tools/files/file_content_extraction_tool.py
```

**Key Implementation:**
- Implement `FileContentExtractionTool` extending `BaseTool`
- Use `DIALFileContentExtractor` from utils
- Support pagination

#### 2.2: Update Configuration

Add to `applications["general-purpose-agent"]` in `core/config.json`:
```json
"inputAttachmentTypes": [
  "image/png",
  "image/jpeg",
  "application/pdf",
  "text/html",
  "text/plain",
  "text/csv"
]
```

#### 2.3: Register Tool in app.py

```python
from task.tools.files.file_content_extraction_tool import FileContentExtractionTool

tools = [
    FileContentExtractionTool()
]
```

#### 2.4: Restart Services

```bash
# Restart Docker
docker compose restart core

# Restart agent app (Ctrl+C and rerun)
python task/app.py
```

#### 2.5: Test Step 2

**Test Cases:**
1. "What can you do?" - Should mention file extraction
2. Upload `tests/report.csv` → "What is top sale for category A?"
   - Expected: "1700 on 2025-10-05"
3. Upload `tests/microwave_manual.txt` → "How should I clean the plate?"
   - Should use pagination (2-3 tool calls)

---

### STEP 3: RAG Search + Image Generation

#### 3.1: Implement RAG Tool

```bash
nano task/tools/rag/rag_tool.py
```

**Key Implementation:**
- Document indexing with FAISS
- Conversation-scoped caching
- Semantic search

#### 3.2: Implement Image Generation Tool

```bash
nano task/tools/deployment/base.py
nano task/tools/deployment/image_generation_tool.py
```

**Key Implementation:**
- DIAL deployment-based tool
- Stage API for progress
- Image attachment handling

#### 3.3: Add DALL-E-3 to Configuration

Add to `models` in `core/config.json`:
```json
"dall-e-3": {
  "displayName": "DALL-E-3",
  "endpoint": "http://adapter-dial:5000/openai/deployments/dall-e-3/chat/completions",
  "iconUrl": "http://localhost:3001/gpt3.svg",
  "type": "chat",
  "upstreams": [
    {
      "endpoint": "https://ai-proxy.lab.epam.com/openai/deployments/dall-e-3/chat/completions",
      "key": "{YOUR_DIAL_API_KEY}"
    }
  ]
}
```

#### 3.4: Register Tools

```python
from task.tools.rag.rag_tool import RAGTool
from task.tools.deployment.image_generation_tool import ImageGenerationTool

tools = [
    FileContentExtractionTool(),
    RAGTool(),
    ImageGenerationTool(deployment_name="dall-e-3")
]
```

#### 3.5: Test Step 3

**RAG Test:**
- Upload `tests/microwave_manual.txt` → "How should I clean the plate?"
- Should call RAG tool instead of full extraction

**Image Generation Test:**
- "Generate picture with smiling cat"
- Should show: request → revised prompt → image

---

### STEP 4: MCP Web Search

#### 4.1: Add DuckDuckGo MCP Server to Docker Compose

```bash
nano docker-compose.yml
```

Add service:
```yaml
  ddg-search:
    image: khshanovskyi/ddg-mcp-server:latest
    ports:
      - "8051:8000"
    environment:
      LOG_LEVEL: "INFO"
      MCP_TRANSPORT: "streamable-http"
    restart: unless-stopped
    mem_limit: 512M
    cpus: 0.5
```

#### 4.2: Implement MCP Client

```bash
nano task/tools/mcp/mcp_client.py
nano task/tools/mcp/mcp_tool.py
```

**Key Implementation:**
- HTTP-based MCP client
- Tool discovery from MCP server
- Dynamic tool registration

#### 4.3: Restart Services

```bash
# Restart Docker with new service
docker compose down
docker compose up -d

# Wait for services
sleep 20

# Verify DuckDuckGo service
curl http://localhost:8051/health
```

#### 4.4: Register MCP Tools

```python
from task.tools.mcp.mcp_client import MCPClient
from task.tools.mcp.mcp_tool import MCPTool

# Initialize MCP client
mcp_client = MCPClient("http://localhost:8051/mcp")
await mcp_client.connect()

# Get all tools from MCP server
mcp_tools = await mcp_client.list_tools()

# Create MCPTool instances
for mcp_tool_schema in mcp_tools:
    tools.append(MCPTool(mcp_client, mcp_tool_schema))
```

#### 4.5: Test Step 4

**Test Cases:**
1. "Search what is the weather in Kyiv now"
2. "Who is Arkadiy Dobkin?"

---

### STEP 5: Python Code Interpreter

#### 5.1: Add Python Interpreter to Docker Compose

```bash
nano docker-compose.yml
```

Add service:
```yaml
  python-interpreter:
    image: khshanovskyi/python-code-interpreter-mcp-server:latest
    ports:
      - "8050:8000"
    environment:
      LOG_LEVEL: "INFO"
    restart: unless-stopped
    mem_limit: 2G
    cpus: 2.0
```

#### 5.2: Implement Python Interpreter Tool

```bash
nano task/tools/py_interpreter/python_code_interpreter_tool.py
```

**Key Implementation:**
- Jupyter kernel integration
- File output handling
- Chart generation support

#### 5.3: Restart Services

```bash
docker compose down
docker compose up -d
sleep 20
```

#### 5.4: Register Interpreter Tool

```python
from task.tools.py_interpreter.python_code_interpreter_tool import PythonCodeInterpreterTool

# Add Python interpreter MCP tools
py_mcp_client = MCPClient("http://localhost:8050/mcp")
await py_mcp_client.connect()
```

#### 5.5: Test Step 5

**Test Cases:**
1. "What is the sin of 5682936329203?"
   - Should call Python interpreter
2. Upload `tests/report.csv` → "I need chart bar from this data"
   - Should extract content → generate chart → return as attachment

---

### STEP 6: Multi-Model Support

#### 6.1: Add Claude Sonnet to Configuration

Add to `models` in `core/config.json`:
```json
"claude-sonnet-3-7": {
  "displayName": "Claude Sonnet 3.7",
  "endpoint": "http://adapter-dial:5000/openai/deployments/claude-sonnet-3-7/chat/completions",
  "iconUrl": "https://chat.lab.epam.com/themes/anthropic.svg",
  "type": "chat",
  "upstreams": [
    {
      "endpoint": "https://ai-proxy.lab.epam.com/openai/deployments/claude-3-7-sonnet@20250219/chat/completions",
      "key": "{YOUR_DIAL_API_KEY}"
    }
  ]
}
```

#### 6.2: Update Agent Configuration

```python
# task/app.py
# Change orchestration model
ORCHESTRATION_MODEL = "claude-sonnet-3-7"  # Was "gpt-4o"
```

#### 6.3: Test Step 6

Test how Claude Sonnet performs compared to GPT-4o:
- Same queries as before
- Note differences in verbosity and tool selection

---

## 🧪 Complete Test Suite

### Test Matrix

| Test Case | Expected Tool | Expected Result |
|-----------|---------------|-----------------|
| "What can you do?" | None | List capabilities |
| "Hi GPT-4o" (in GPT-4o chat) | None | Model response |
| Upload CSV + "Top sale?" | file_extraction | Specific answer from data |
| Upload TXT + "How to clean?" | rag_search | Answer from document |
| "Generate cat image" | image_generation | Image attachment |
| "Weather in Kyiv?" | web_search | Current weather |
| "Sin of 123456?" | python_interpreter | Calculation result |
| CSV + "Create chart" | file_extraction + python_interpreter | Chart image |

### Validation Script

```bash
# Create test script
cat > test_agent.sh << 'EOF'
#!/bin/bash

echo "Testing General Purpose Agent..."

# Test 1: Check services
echo "1. Checking Docker services..."
docker compose ps -a

# Test 2: Check MCP servers
echo "2. Checking MCP servers..."
curl -s http://localhost:8051/health | jq .
curl -s http://localhost:8050/health | jq .

# Test 3: Check agent
echo "3. Checking agent..."
curl -s http://localhost:5030/health || echo "Agent needs manual start"

# Test 4: Check DIAL
echo "4. Checking DIAL..."
curl -s http://localhost:8080 > /dev/null && echo "✅ DIAL Core" || echo "❌ DIAL Core"
curl -s http://localhost:3000 > /dev/null && echo "✅ DIAL Chat" || echo "❌ DIAL Chat"

echo "All checks complete!"
EOF

chmod +x test_agent.sh
./test_agent.sh
```

---

## 🔧 Troubleshooting

### Issue 1: MCP Server Not Starting

```bash
# Check logs
docker compose logs ddg-search
docker compose logs python-interpreter

# Verify ports
netstat -ano | findstr "8050 8051"

# Restart specific service
docker compose restart ddg-search
```

### Issue 2: Tool Not Being Called

**Possible Causes:**
1. Tool schema not properly formatted
2. Tool description unclear
3. System prompt doesn't mention tool

**Fix:**
```python
# Improve tool description
@property
def schema(self) -> dict:
    return {
        "type": "function",
        "function": {
            "name": self.name,
            "description": "VERY SPECIFIC description of when to use this tool",
            "parameters": {...}
        }
    }
```

### Issue 3: Agent Taking Too Long

**Check:**
- Multiple recursive tool calls
- Large file processing
- MCP server performance

**Fix:**
```python
# Add timeout to tool execution
async def execute(self, arguments):
    try:
        result = await asyncio.wait_for(
            self._execute_impl(arguments),
            timeout=30.0
        )
        return result
    except asyncio.TimeoutError:
        return "Tool execution timed out"
```

---

## 📊 Service URLs Reference

| Service | URL | Purpose |
|---------|-----|---------|
| **DIAL Chat** | http://localhost:3000 | User interface |
| **DIAL Core** | http://localhost:8080 | API gateway |
| **Agent** | http://localhost:5030 | General Purpose Agent |
| **DuckDuckGo MCP** | http://localhost:8051 | Web search |
| **Python Interpreter MCP** | http://localhost:8050 | Code execution |

---

## 🎯 Implementation Checklist

### Step 1: Core Agent ✅
- [ ] `agent.py` implemented
- [ ] `app.py` implemented
- [ ] `prompts.py` created
- [ ] `tools/base.py` implemented
- [ ] DIAL config updated
- [ ] Services running
- [ ] Basic tests pass

### Step 2: File Extraction ✅
- [ ] `file_content_extraction_tool.py` implemented
- [ ] Registered in app.py
- [ ] Config updated with file types
- [ ] CSV test passes
- [ ] TXT pagination test passes

### Step 3: RAG + Images ✅
- [ ] `rag_tool.py` implemented
- [ ] `image_generation_tool.py` implemented
- [ ] DALL-E-3 added to config
- [ ] RAG test passes
- [ ] Image generation test passes

### Step 4: Web Search ✅
- [ ] DuckDuckGo service added
- [ ] `mcp_client.py` implemented
- [ ] `mcp_tool.py` implemented
- [ ] MCP tools registered
- [ ] Web search tests pass

### Step 5: Code Interpreter ✅
- [ ] Python interpreter service added
- [ ] `python_code_interpreter_tool.py` implemented
- [ ] Tool registered
- [ ] Math test passes
- [ ] Chart generation test passes

### Step 6: Multi-Model ✅
- [ ] Claude Sonnet added to config
- [ ] Orchestration model changed
- [ ] Performance comparison done

---

## 🚀 Final Commands

### Start Everything

```bash
# Terminal 1: Docker services
cd /mnt/c/Users/AndreyPopov/ai-dial-general-purpose-agent
docker compose up -d

# Terminal 2: Agent
source .venv/bin/activate
python task/app.py
```

### Stop Everything

```bash
# Stop agent (Ctrl+C in Terminal 2)

# Stop Docker
docker compose down
```

### View Logs

```bash
# Agent logs (in Terminal 2)

# Docker logs
docker compose logs -f

# Specific service
docker compose logs -f ddg-search
docker compose logs -f python-interpreter
```

---

## 🎓 What You'll Learn

By completing this task, you'll master:

1. **Agent Orchestration:** Complex multi-step workflows
2. **Tool Composition:** Multiple tool types working together
3. **MCP Protocol:** Dynamic tool discovery and execution
4. **RAG Implementation:** Document indexing and search
5. **Multi-Modal AI:** Text, images, code, web content

**Estimated Time:** 8-12 hours for full implementation

**Difficulty:** ⭐⭐⭐⭐⭐ (Expert Level)

Good luck! This is the culmination of all previous tasks! 🎉

