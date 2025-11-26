# Task 13: General Purpose Agent with DIAL - Complete Architecture & Planning

## 🎯 Task Overview

**Objective:** Build a comprehensive General Purpose AI Agent equipped with multiple capabilities including web search, file processing, RAG, image generation, and code execution.

**Repository:** ai-dial-general-purpose-agent  
**Complexity:** Advanced (6 major implementation steps)  
**Time Estimate:** 8-12 hours for full implementation

---

## 🧠 Agent Capabilities

### 1. **Web Search** (DuckDuckGo MCP Server)
- Real-time web searches
- Content fetching from URLs
- Free alternative to paid search APIs

### 2. **Python Code Interpreter** (MCP Server)
- Stateful Python execution environment
- Jupyter kernel support
- Chart/data visualization generation
- Mathematical computations

### 3. **Image Generation** (DALL-E-3 via DIAL)
- Text-to-image generation
- Prompt revision and enhancement
- Multiple format support

### 4. **File Content Extractor**
- PDF, TXT, CSV, HTML support
- Pagination for large files
- Attachment handling

### 5. **RAG Search** (Retrieval-Augmented Generation)
- Document indexing and caching
- Semantic search over uploaded files
- Conversation-scoped document memory

---

## 📐 Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│                     USER (Browser)                          │
│                 http://localhost:3000                       │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│              DIAL Chat UI + Core                            │
│              (Marketplace, Routing)                         │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│          General Purpose Agent (port 5030)                  │
│          ┌──────────────────────────────────┐              │
│          │  Agent Orchestrator              │              │
│          │  - Tool selection                │              │
│          │  - Request routing               │              │
│          │  - Response aggregation          │              │
│          └──────────┬───────────────────────┘              │
│                     │                                        │
│          ┌──────────┴───────────────────────┐              │
│          │    Tool Registry                 │              │
│          │  ┌────────────────────────────┐  │              │
│          │  │ 1. File Content Extractor  │  │              │
│          │  │ 2. RAG Search Tool         │  │              │
│          │  │ 3. Image Generation Tool   │  │              │
│          │  │ 4. Web Search (MCP)        │  │              │
│          │  │ 5. Python Interpreter (MCP)│  │              │
│          │  └────────────────────────────┘  │              │
│          └──────────────────────────────────┘              │
└────────────────────────────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┬─────────────┐
         │             │             │             │
         ▼             ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐
│ GPT-4o Model │ │ DALL-E-3 │ │ DuckDuck │ │Python Inter│
│  (via DIAL)  │ │  Model   │ │Go Search │ │preter (MCP)│
│              │ │ (viaegro DIAL)  │ │  (MCP)   │ │ (Docker)   │
└──────────────┘ └──────────┘ └──────────┘ └────────────┘
```

---

## 💭 Key Design Decisions & Reasoning

### Decision 1: Agent Orchestration Pattern

**Challenge:** How to coordinate multiple tools and handle complex multi-step workflows?

**Chosen Approach:** Recursive Orchestrator with Tool Registry

```python
class GeneralPurposeAgent:
    async def handle_request(self, request):
        # 1. Prepare messages with system prompt
        messages = self._prepare_messages(request)
        
        # 2. Call LLM with available tools
        response = await self.llm.create(messages, tools=self.tools)
        
        # 3. If tool calls requested, execute them
        if response.tool_calls:
            tool_results = await self._execute_tools(response.tool_calls)
            
            # 4. Recursively continue with tool results
            return await self.handle_request(updated_request)
        
        # 5. Return final response
        return response
```

**Why This Works:**
- ✅ Flexible: Can handle any number of tool calls
- ✅ Composable: Tools can trigger other tools
- ✅ Traceable: Full history of tool calls
- ✅ State Management: Conversation-scoped caching

---

### Decision 2: Tool Abstraction Layer

**Challenge:** Different tool types (local, MCP, DIAL deployments) need unified interface

**Solution:** BaseTool Abstract Class

```python
class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool identifier"""
        
    @property
    @abstractmethod
    def schema(self) -> dict:
        """OpenAI function calling schema"""
        
    @abstractmethod
    async def execute(self, arguments: dict) -> str:
        """Tool execution logic"""
```

**Three Tool Categories:**

1. **Local Tools** (File/RAG)
```python
class FileContentExtractionTool(BaseTool):
    async def execute(self, arguments):
        # Direct file processing
        content = await self.file_extractor.extract(file_id)
        return content
```

2. **Deployment Tools** (Image Generation)
```python
class ImageGenerationTool(DeploymentBasedTool):
    async def execute(self, arguments):
        # Call DIAL model deployment
        response = await self.dial_client.generate(prompt)
        return response
```

3. **MCP Tools** (Web Search, Code Interpreter)
```python
class MCPTool(BaseTool):
    async def execute(self, arguments):
        # Call MCP server
        result = await self.mcp_client.call_tool(self.tool_name, arguments)
        return result
```

---

### Decision 3: MCP Integration Strategy

**Challenge:** Multiple MCP servers (DuckDuckGo, Python Interpreter) with different capabilities

**Solution:** MCP Client Abstraction

```python
class MCPClient:
    async def connect(self, server_url: str):
        # Initialize MCP connection
        self.session = await self._http_session.post(
            f"{server_url}/initialize"
        )
    
    async def list_tools(self) -> list[dict]:
        # Discover available tools
        response = await self._http_session.post(
            f"{self.server_url}/tools/list"
        )
        return response['tools']
    
    async def call_tool(self, tool_name: str, arguments: dict):
        # Execute tool
        response = await self._http_session.post(
            f"{self.server_url}/tools/call",
            json={"name": tool_name, "arguments": arguments}
        )
        return response['result']
```

**Benefits:**
- ✅ Dynamic tool discovery
- ✅ Multiple MCP servers support
- ✅ Automatic tool schema parsing
- ✅ Consistent error handling

---

### Decision 4: RAG Implementation with Conversation Caching

**Challenge:** Files uploaded in conversation should be searchable without re-indexing

**Solution:** Conversation-Scoped Document Cache

```python
class DocumentCache:
    def __init__(self):
        self.caches: dict[str, VectorStore] = {}
    
    def get_or_create(self, conversation_id: str) -> VectorStore:
        if conversation_id not in self.caches:
            self.caches[conversation_id] = FAISS(embeddings)
        return self.caches[conversation_id]
    
    def add_documents(self, conversation_id: str, docs: list[Document]):
        cache = self.get_or_create(conversation_id)
        cache.add_documents(docs)
    
    def search(self, conversation_id: str, query: str) -> list[Document]:
        cache = self.caches.get(conversation_id)
        if not cache:
            return []
        return cache.similarity_search(query)
```

**Why Conversation-Scoped?**
- ✅ Privacy: Documents isolated per conversation
- ✅ Performance: No need to search irrelevant docs
- ✅ Memory: Automatic cleanup when conversation ends
- ✅ Context: Agent remembers all uploaded files in conversation

---

### Decision 5: File Processing Strategy

**Challenge:** Large files (manuals, reports) can't fit in single LLM request

**Options:**
1. **Full Extraction:** Load entire file (fails for large files)
2. **Fixed Chunking:** Split into pages (loses context)
3. **Hybrid: Pagination + RAG** ✅

**Hybrid Approach:**

```python
# Step 1: Try pagination for small files
if file_size < THRESHOLD:
    content = await extract_file_content(
        file_id=file_id,
        page_number=1,
        page_size=2000
    )
    return content

# Step 2: For large files, use RAG
else:
    # Index file
    await rag_tool.index_file(file_id, conversation_id)
    
    # Search specific content
    results = await rag_tool.search(query, conversation_id)
    return results
```

**Decision Flow:**
- Small file → Pagination (faster, preserves structure)
- Large file → RAG (semantic search, more accurate)
- Agent decides based on pagination response ("more pages available")

---

### Decision 6: Image Generation with Stage Support

**Challenge:** Image generation requires showing progress and intermediate results

**Solution:** DIAL Stage API

```python
async def generate_image(self, prompt: str, choice: Choice):
    # Stage 1: Show generation request
    with StageProcessor(choice, "image_generation") as stage:
        stage.add_custom_content(
            "request",
            json.dumps({"prompt": prompt})
        )
        
        # Stage 2: Generate image
        response = await self.dial_client.generate(prompt)
        
        # Stage 3: Show revised prompt
        stage.add_custom_content(
            "revised_prompt",
            response.revised_prompt
        )
        
        # Stage 4: Return image
        return response.image_url
```

**User Experience:**
1. User sees "Generating image..." with original prompt
2. User sees revised/enhanced prompt
3. User sees generated image
4. Image is attached to response

---

### Decision 7: Python Code Interpreter Integration

**Challenge:** LLMs can't do math accurately. Need real code execution.

**Solution:** Stateful Jupyter Kernel via MCP

**Flow:**
```
User: "What is sin(5682936329203)?"
  ↓
Agent: [Realizes needs computation]
  ↓
Tool Call: python_interpreter.execute_code(
    code="import math\nresult = math.sin(5682936329203)\nprint(result)"
)
  ↓
MCP Server: [Runs code in Jupyter kernel]
  ↓
Tool Result: "0.8623..."
  ↓
Agent: "The sine of 5682936329203 is approximately 0.8623"
```

**Key Features:**
- **Stateful:** Variables persist across tool calls
- **Safe:** Sandboxed Docker environment
- **Rich:** Can generate plots, charts, files
- **Async:** Non-blocking execution

---

## 🛠️ Implementation Patterns

### Pattern 1: Tool Registration and Discovery

```python
class ToolRegistry:
    def __init__(self):
        self.tools: list[BaseTool] = []
    
    def register(self, tool: BaseTool):
        self.tools.append(tool)
    
    def get_schemas(self) -> list[dict]:
        return [tool.schema for tool in self.tools]
    
    async def execute(self, tool_name: str, arguments: dict) -> str:
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        return await tool.execute(arguments)
```

---

### Pattern 2: Async Tool Execution

```python
async def _execute_tools(self, tool_calls: list[ToolCall]) -> list[Message]:
    # Execute tools in parallel
    tasks = [
        self._execute_single_tool(tool_call)
        for tool_call in tool_calls
    ]
    results = await asyncio.gather(*tasks)
    
    # Convert results to tool messages
    return [
        Message(
            role=Role.TOOL,
            tool_call_id=tool_call.id,
            content=result
        )
        for tool_call, result in zip(tool_calls, results)
    ]
```

---

### Pattern 3: System Prompt Engineering

```python
SYSTEM_PROMPT = """You are a General Purpose AI Agent with advanced capabilities.

**Available Tools:**
1. **file_content_extraction** - Extract content from uploaded files (PDF, TXT, CSV)
   - Use for small files or when you need full content
   - Supports pagination for large files

2. **rag_search** - Semantic search over uploaded documents
   - Use for large files or when searching for specific information
   - More efficient than full extraction for targeted queries

3. **web_search** - Search the web for current information
   - Use for real-time data, news, weather
   - Returns search results with URLs

4. **python_interpreter** - Execute Python code
   - Use for calculations, data analysis, chart generation
   - Stateful: variables persist across calls

5. **image_generation** - Generate images from text descriptions
   - Use for creating visualizations, illustrations
   - Returns image URL and revised prompt

**Decision Making:**
- For uploaded files: Try pagination first, switch to RAG if file is large
- For calculations: Always use python_interpreter (don't estimate)
- For current events: Use web_search
- For creative tasks: Use image_generation

**Response Format:**
- Be concise and helpful
- Explain which tools you're using and why
- Show intermediate steps when relevant
"""
```

---

## 📊 Implementation Steps

### Step 1: Core Agent Setup
**Files:** agent.py, app.py, prompts.py, core/config.json

**Key Implementation:**
- Agent orchestration loop
- Message preparation
- Tool call handling
- DIAL Core configuration

---

### Step 2: File Content Extraction
**Files:** tools/base.py, tools/files/file_content_extraction_tool.py

**Key Implementation:**
- Base tool abstraction
- File content fetching
- Pagination support
- MIME type handling

---

### Step 3: RAG + Image Generation
**Files:** tools/rag/rag_tool.py, tools/deployment/image_generation_tool.py

**Key Implementation:**
- Document indexing with FAISS
- Semantic search
- Image generation via DIAL
- Stage API for progress

---

### Step 4: MCP Web Search
**Files:** tools/mcp/mcp_client.py, tools/mcp/mcp_tool.py

**Key Implementation:**
- MCP HTTP client
- Tool discovery
- Dynamic tool registration
- DuckDuckGo integration

---

### Step 5: Python Code Interpreter
**Files:** tools/py_interpreter/python_code_interpreter_tool.py

**Key Implementation:**
- Jupyter kernel integration
- Code execution sandboxing
- File output handling
- Chart/plot generation

---

### Step 6: Multi-Model Support
**Files:** app.py, core/config.json

**Key Implementation:**
- Claude Sonnet 3.7 configuration
- Model switching
- Performance comparison

---

## 🔐 Security Considerations

### 1. Code Execution Safety
- Docker isolation
- Resource limits (CPU, memory)
- No network access from interpreter
- Automatic cleanup

### 2. File Processing
- Virus scanning (not implemented)
- Size limits
- Allowed MIME types only
- Conversation-scoped access

### 3. API Key Management
- Environment variables
- No hardcoding in config
- Separate keys.json file
- .gitignore protection

---

## 📈 Performance Optimizations

### 1. Parallel Tool Execution
```python
# Execute multiple tools simultaneously
results = await asyncio.gather(*tool_tasks)
```

### 2. Conversation Caching
- Vector stores cached per conversation
- No re-indexing on each query
- Automatic cleanup on conversation end

### 3. Streaming Responses
- Real-time content delivery
- Lower perceived latency
- Better user experience

---

## 🎓 Key Learnings

**Before This Task:**
- Built simple agents with single tools
- Used basic function calling
- No multi-step workflows

**After This Task:**
- Understand agent orchestration patterns
- Can integrate multiple tool types
- Know MCP protocol implementation
- Understand RAG for agent memory
- Can build production-grade agents

---

## 🚀 Production Readiness

### Current Implementation (Development):
- ❌ No authentication beyond DIAL
- ❌ No rate limiting per user
- ❌ No monitoring/observability
- ❌ No tool execution timeout
- ❌ In-memory caching only

### Production Requirements:
- ✅ User authentication and authorization
- ✅ Rate limiting and quotas
- ✅ Comprehensive logging (structured)
- ✅ Metrics (Prometheus)
- ✅ Distributed caching (Redis)
- ✅ Tool execution timeouts
- ✅ Error recovery and retries
- ✅ Load balancing

---

## 🎯 Conclusion

This General Purpose Agent demonstrates:

1. **Advanced Orchestration:** Recursive tool calling with state management
2. **Tool Composition:** Multiple tool types working together
3. **MCP Integration:** Dynamic tool discovery and execution
4. **RAG Implementation:** Conversation-scoped document memory
5. **Multi-Modal:** Text, images, code, web content

**Key Achievement:** Built a production-quality foundation for general-purpose AI agents that can handle complex, multi-step tasks with various tools.

**Complexity Rating:** ⭐⭐⭐⭐⭐ (5/5) - Most complex task in the series

This represents the culmination of all previous tasks:
- RAG from Task 5/6
- Tool calling from Task 8
- MCP from Task 9/10
- DIAL integration from Task 11

A truly comprehensive AI agent implementation! 🎉

