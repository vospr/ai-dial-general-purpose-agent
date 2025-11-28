#!/usr/bin/env python3
"""
Integration Tests for General Purpose Agent
Based on test scenarios from README.md
"""
import sys
import os
import requests
import time
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Test configuration
DIAL_CORE_URL = "http://localhost:8080"
CHAT_URL = "http://localhost:3000"
AGENT_URL = "http://localhost:5030"
DIAL_API_KEY = "dial_api_key"  # Default key from docker-compose

def print_test_header(test_name):
    """Print formatted test header"""
    print("\n" + "="*80)
    print(f"TEST: {test_name}")
    print("="*80)

def print_result(success, message):
    """Print test result"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def test_service_health():
    """Test Step 0: Verify all services are running"""
    print_test_header("Service Health Check")
    
    services = {
        "DIAL Core": f"{DIAL_CORE_URL}/health",
        "Chat UI": f"{CHAT_URL}",
        "Agent": f"{AGENT_URL}/health" if AGENT_URL else None,
    }
    
    all_healthy = True
    for name, url in services.items():
        if url is None:
            print_result(False, f"{name}: Not configured")
            all_healthy = False
            continue
            
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 302, 404]:
                print_result(True, f"{name}: Running")
            else:
                print_result(False, f"{name}: Status {response.status_code}")
                all_healthy = False
        except Exception as e:
            print_result(False, f"{name}: {str(e)}")
            all_healthy = False
    
    return all_healthy

def test_step1_basic_functionality():
    """Test Step 1: Basic Agent Functionality"""
    print_test_header("Step 1: Basic Agent Functionality")
    
    # Test 1: Check if agent can be imported and instantiated
    try:
        from task.app import app, GeneralPurposeAgentApplication
        agent_app = GeneralPurposeAgentApplication()
        print_result(True, "Agent application can be instantiated")
    except Exception as e:
        print_result(False, f"Agent instantiation failed: {e}")
        return False
    
    # Test 2: Check if agent starts (if running)
    try:
        response = requests.get(f"{AGENT_URL}/health", timeout=2)
        if response.status_code == 200:
            print_result(True, "Agent service is running")
        else:
            print_result(False, f"Agent service returned {response.status_code}")
    except:
        print_result(False, "Agent service not running (start with: python task/app.py)")
        print("   Note: This is expected if agent is not started yet")
    
    # Test 3: Verify tools can be created
    try:
        import asyncio
        from task.app import GeneralPurposeAgentApplication
        
        async def test_tools():
            agent_app = GeneralPurposeAgentApplication()
            # This will fail if tools can't be created
            # We'll catch the error to see what's missing
            try:
                tools = await agent_app._create_tools()
                print_result(True, f"Tools created successfully ({len(tools)} tools)")
                for tool in tools:
                    print(f"   - {tool.name}")
                return True
            except Exception as e:
                print_result(False, f"Tool creation failed: {e}")
                return False
        
        return asyncio.run(test_tools())
    except Exception as e:
        print_result(False, f"Tool creation test failed: {e}")
        return False

def test_step2_file_extraction():
    """Test Step 2: File Content Extraction"""
    print_test_header("Step 2: File Content Extraction Tool")
    
    try:
        from task.tools.files.file_content_extraction_tool import FileContentExtractionTool
        tool = FileContentExtractionTool(endpoint=DIAL_CORE_URL)
        
        # Check tool properties
        checks = {
            "Tool name": tool.name is not None,
            "Tool description": tool.description is not None,
            "Tool schema": tool.schema is not None,
            "Show in stage": isinstance(tool.show_in_stage, bool),
        }
        
        all_pass = True
        for check_name, result in checks.items():
            print_result(result, f"{check_name}: {'OK' if result else 'Missing'}")
            if not result:
                all_pass = False
        
        return all_pass
    except Exception as e:
        print_result(False, f"File extraction tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step3_rag_tool():
    """Test Step 3: RAG Search Tool"""
    print_test_header("Step 3: RAG Search Tool")
    
    try:
        from task.tools.rag.rag_tool import RagTool
        from task.tools.rag.document_cache import DocumentCache
        
        cache = DocumentCache.create()
        tool = RagTool(
            endpoint=DIAL_CORE_URL,
            deployment_name="gpt-4o",
            document_cache=cache
        )
        
        checks = {
            "Tool name": tool.name is not None,
            "Tool description": tool.description is not None,
            "Tool schema": tool.schema is not None,
            "Document cache": cache is not None,
        }
        
        all_pass = True
        for check_name, result in checks.items():
            print_result(result, f"{check_name}: {'OK' if result else 'Missing'}")
            if not result:
                all_pass = False
        
        return all_pass
    except Exception as e:
        print_result(False, f"RAG tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step4_image_generation():
    """Test Step 4: Image Generation Tool"""
    print_test_header("Step 4: Image Generation Tool")
    
    try:
        from task.tools.deployment.image_generation_tool import ImageGenerationTool
        tool = ImageGenerationTool(endpoint=DIAL_CORE_URL)
        
        checks = {
            "Tool name": tool.name is not None,
            "Tool description": tool.description is not None,
            "Tool schema": tool.schema is not None,
        }
        
        all_pass = True
        for check_name, result in checks.items():
            print_result(result, f"{check_name}: {'OK' if result else 'Missing'}")
            if not result:
                all_pass = False
        
        return all_pass
    except Exception as e:
        print_result(False, f"Image generation tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step5_web_search():
    """Test Step 5: Web Search (DuckDuckGo MCP)"""
    print_test_header("Step 5: Web Search (DuckDuckGo MCP)")
    
    # Test MCP server connectivity
    try:
        response = requests.get("http://localhost:8051/health", timeout=5)
        if response.status_code == 200:
            print_result(True, "DuckDuckGo MCP server is running")
        else:
            print_result(False, f"DuckDuckGo MCP server returned {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"DuckDuckGo MCP server not accessible: {e}")
        return False
    
    # Test MCP client and tools
    try:
        import asyncio
        from task.tools.mcp.mcp_client import MCPClient
        
        async def test_mcp():
            try:
                client = await MCPClient.create("http://localhost:8051/mcp")
                tools = await client.get_tools()
                print_result(True, f"MCP client connected, found {len(tools)} tools")
                for tool in tools:
                    print(f"   - {tool.name}")
                return True
            except Exception as e:
                print_result(False, f"MCP client test failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        return asyncio.run(test_mcp())
    except Exception as e:
        print_result(False, f"Web search test failed: {e}")
        return False

def test_step6_python_interpreter():
    """Test Step 6: Python Code Interpreter"""
    print_test_header("Step 6: Python Code Interpreter")
    
    # Test MCP server connectivity
    try:
        response = requests.get("http://localhost:8050/health", timeout=5)
        if response.status_code == 200:
            print_result(True, "Python Interpreter MCP server is running")
        else:
            print_result(False, f"Python Interpreter MCP server returned {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Python Interpreter MCP server not accessible: {e}")
        return False
    
    # Test Python interpreter tool
    try:
        from task.tools.py_interpreter.python_code_interpreter_tool import PythonCodeInterpreterTool
        import asyncio
        
        async def test_interpreter():
            try:
                tool = await PythonCodeInterpreterTool.create(
                    mcp_url="http://localhost:8050/mcp",
                    tool_name="execute_code",
                    dial_endpoint=DIAL_CORE_URL
                )
                print_result(True, f"Python interpreter tool created: {tool.name}")
                return True
            except Exception as e:
                print_result(False, f"Python interpreter tool creation failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        return asyncio.run(test_interpreter())
    except Exception as e:
        print_result(False, f"Python interpreter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step7_multi_model():
    """Test Step 7: Multi-Model Support"""
    print_test_header("Step 7: Multi-Model Support (Claude Sonnet)")
    
    try:
        import json
        config_path = project_root / "core" / "config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        # Check if Claude Sonnet is configured
        models = config.get("models", {})
        if "claude-sonnet-3-7" in models:
            print_result(True, "Claude Sonnet 3.7 model is configured")
            model_config = models["claude-sonnet-3-7"]
            checks = {
                "Display name": "displayName" in model_config,
                "Endpoint": "endpoint" in model_config,
                "Upstreams": "upstreams" in model_config and len(model_config["upstreams"]) > 0,
            }
            
            all_pass = True
            for check_name, result in checks.items():
                print_result(result, f"{check_name}: {'OK' if result else 'Missing'}")
                if not result:
                    all_pass = False
            
            return all_pass
        else:
            print_result(False, "Claude Sonnet 3.7 model not found in config")
            return False
    except Exception as e:
        print_result(False, f"Multi-model test failed: {e}")
        return False

def test_configuration():
    """Test Configuration Completeness"""
    print_test_header("Configuration Check")
    
    try:
        import json
        config_path = project_root / "core" / "config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        # Check application
        apps = config.get("applications", {})
        if "general-purpose-agent" in apps:
            app_config = apps["general-purpose-agent"]
            print_result(True, "General Purpose Agent application configured")
            
            # Check file types
            file_types = app_config.get("inputAttachmentTypes", [])
            required_types = ["application/pdf", "text/html", "text/plain", "text/csv", "image/png", "image/jpeg"]
            missing_types = [t for t in required_types if t not in file_types]
            
            if not missing_types:
                print_result(True, f"All required file types configured ({len(file_types)} types)")
            else:
                print_result(False, f"Missing file types: {missing_types}")
        else:
            print_result(False, "General Purpose Agent application not found")
            return False
        
        # Check models
        models = config.get("models", {})
        required_models = ["gpt-4o", "dall-e-3", "claude-sonnet-3-7"]
        missing_models = [m for m in required_models if m not in models]
        
        if not missing_models:
            print_result(True, f"All required models configured ({len(models)} models)")
        else:
            print_result(False, f"Missing models: {missing_models}")
            return False
        
        return True
    except Exception as e:
        print_result(False, f"Configuration test failed: {e}")
        return False

def main():
    print("\n" + "🎯"*40)
    print("GENERAL PURPOSE AGENT - INTEGRATION TESTS")
    print("Based on README.md test scenarios")
    print("🎯"*40)
    
    results = []
    
    # Configuration check
    results.append(("Configuration", test_configuration()))
    
    # Service health
    results.append(("Service Health", test_service_health()))
    
    # Step 1: Basic functionality
    results.append(("Step 1: Basic Functionality", test_step1_basic_functionality()))
    
    # Step 2: File extraction
    results.append(("Step 2: File Content Extraction", test_step2_file_extraction()))
    
    # Step 3: RAG search
    results.append(("Step 3: RAG Search", test_step3_rag_tool()))
    
    # Step 4: Image generation
    results.append(("Step 4: Image Generation", test_step4_image_generation()))
    
    # Step 5: Web search
    results.append(("Step 5: Web Search (MCP)", test_step5_web_search()))
    
    # Step 6: Python interpreter
    results.append(("Step 6: Python Code Interpreter", test_step6_python_interpreter()))
    
    # Step 7: Multi-model
    results.append(("Step 7: Multi-Model Support", test_step7_multi_model()))
    
    # Summary
    print("\n" + "="*80)
    print("INTEGRATION TEST SUMMARY")
    print("="*80)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:50s} {status}")
    
    all_passed = all(result for _, result in results)
    print("="*80)
    
    if all_passed:
        print("\n🎉 All integration tests PASSED!")
        print("\n📝 Next Steps:")
        print("   1. Start the agent: python task/app.py")
        print("   2. Open http://localhost:3000 in browser")
        print("   3. Test scenarios from README.md manually")
        return 0
    else:
        print("\n⚠️  Some integration tests FAILED.")
        print("   Review the output above and fix issues before manual testing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

