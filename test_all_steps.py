#!/usr/bin/env python3
"""
Comprehensive test script for General Purpose Agent implementation
Tests all steps according to README.md and Implementation.md
"""
import sys
import os
import asyncio
import requests
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_step_1_imports():
    """Test Step 1: Verify all imports work"""
    print("\n" + "="*80)
    print("STEP 1: Testing Core Agent Imports")
    print("="*80)
    
    try:
        from task.app import app, GeneralPurposeAgentApplication
        from task.agent import GeneralPurposeAgent
        from task.prompts import SYSTEM_PROMPT
        from task.tools.base import BaseTool
        print("✅ All imports successful")
        print(f"✅ SYSTEM_PROMPT length: {len(SYSTEM_PROMPT)} characters")
        print(f"✅ App object created: {type(app)}")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step_2_file_tools():
    """Test Step 2: File Content Extraction Tool"""
    print("\n" + "="*80)
    print("STEP 2: Testing File Content Extraction Tool")
    print("="*80)
    
    try:
        from task.tools.files.file_content_extraction_tool import FileContentExtractionTool
        tool = FileContentExtractionTool(endpoint="http://localhost:8080")
        print(f"✅ FileContentExtractionTool created: {tool.name}")
        print(f"✅ Tool schema available: {bool(tool.schema)}")
        return True
    except Exception as e:
        print(f"❌ File tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step_3_rag_tool():
    """Test Step 3: RAG Search Tool"""
    print("\n" + "="*80)
    print("STEP 3: Testing RAG Search Tool")
    print("="*80)
    
    try:
        from task.tools.rag.rag_tool import RagTool
        from task.tools.rag.document_cache import DocumentCache
        cache = DocumentCache.create()
        tool = RagTool(
            endpoint="http://localhost:8080",
            deployment_name="gpt-4o",
            document_cache=cache
        )
        print(f"✅ RagTool created: {tool.name}")
        print(f"✅ DocumentCache created")
        return True
    except Exception as e:
        print(f"❌ RAG tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step_4_image_generation():
    """Test Step 4: Image Generation Tool"""
    print("\n" + "="*80)
    print("STEP 4: Testing Image Generation Tool")
    print("="*80)
    
    try:
        from task.tools.deployment.image_generation_tool import ImageGenerationTool
        tool = ImageGenerationTool(endpoint="http://localhost:8080")
        print(f"✅ ImageGenerationTool created: {tool.name}")
        return True
    except Exception as e:
        print(f"❌ Image generation tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step_5_mcp_tools():
    """Test Step 5: MCP Tools (Web Search)"""
    print("\n" + "="*80)
    print("STEP 5: Testing MCP Tools")
    print("="*80)
    
    try:
        from task.tools.mcp.mcp_client import MCPClient
        from task.tools.mcp.mcp_tool import MCPTool
        print("✅ MCPClient and MCPTool imports successful")
        
        # Test MCP server connectivity (non-blocking)
        try:
            response = requests.get("http://localhost:8051/health", timeout=2)
            print(f"✅ DuckDuckGo MCP server is running")
        except:
            print("⚠️  DuckDuckGo MCP server not accessible (may need to start)")
        
        return True
    except Exception as e:
        print(f"❌ MCP tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step_6_python_interpreter():
    """Test Step 6: Python Code Interpreter"""
    print("\n" + "="*80)
    print("STEP 6: Testing Python Code Interpreter")
    print("="*80)
    
    try:
        from task.tools.py_interpreter.python_code_interpreter_tool import PythonCodeInterpreterTool
        print("✅ PythonCodeInterpreterTool import successful")
        
        # Test Python interpreter MCP server connectivity
        try:
            response = requests.get("http://localhost:8050/health", timeout=2)
            print(f"✅ Python Interpreter MCP server is running")
        except:
            print("⚠️  Python Interpreter MCP server not accessible (may need to start)")
        
        return True
    except Exception as e:
        print(f"❌ Python interpreter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_docker_services():
    """Test Docker services are running"""
    print("\n" + "="*80)
    print("Testing Docker Services")
    print("="*80)
    
    services = {
        "Core": "http://localhost:8080/health",
        "Chat": "http://localhost:3000",
        "Themes": "http://localhost:3001",
        "DuckDuckGo MCP": "http://localhost:8051",
        "Python Interpreter MCP": "http://localhost:8050",
    }
    
    results = {}
    for name, url in services.items():
        try:
            if "health" in url:
                response = requests.get(url, timeout=2)
                results[name] = response.status_code == 200
            else:
                response = requests.get(url, timeout=2)
                results[name] = response.status_code in [200, 302, 404]  # 404 is OK for root
        except:
            results[name] = False
    
    all_passed = True
    for name, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {name}: {'Running' if status else 'Not accessible'}")
        if not status:
            all_passed = False
    
    return all_passed

def test_config():
    """Test configuration files"""
    print("\n" + "="*80)
    print("Testing Configuration")
    print("="*80)
    
    try:
        import json
        config_path = project_root / "core" / "config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        # Check required keys
        checks = {
            "Application exists": "general-purpose-agent" in config.get("applications", {}),
            "GPT-4o model exists": "gpt-4o" in config.get("models", {}),
            "DALL-E-3 model exists": "dall-e-3" in config.get("models", {}),
            "Claude Sonnet exists": "claude-sonnet-3-7" in config.get("models", {}),
        }
        
        all_passed = True
        for check_name, result in checks.items():
            status_icon = "✅" if result else "❌"
            print(f"{status_icon} {check_name}")
            if not result:
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def main():
    print("\n" + "🎯"*40)
    print("GENERAL PURPOSE AGENT - COMPREHENSIVE TEST SUITE")
    print("🎯"*40)
    
    results = []
    
    # Test configuration
    results.append(("Configuration", test_config()))
    
    # Test Docker services
    results.append(("Docker Services", test_docker_services()))
    
    # Test Step 1: Core Agent
    results.append(("Step 1: Core Agent Imports", test_step_1_imports()))
    
    # Test Step 2: File Tools
    results.append(("Step 2: File Content Extraction", test_step_2_file_tools()))
    
    # Test Step 3: RAG Tool
    results.append(("Step 3: RAG Search", test_step_3_rag_tool()))
    
    # Test Step 4: Image Generation
    results.append(("Step 4: Image Generation", test_step_4_image_generation()))
    
    # Test Step 5: MCP Tools
    results.append(("Step 5: MCP Tools (Web Search)", test_step_5_mcp_tools()))
    
    # Test Step 6: Python Interpreter
    results.append(("Step 6: Python Code Interpreter", test_step_6_python_interpreter()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:50s} {status}")
    
    all_passed = all(result for _, result in results)
    print("="*80)
    if all_passed:
        print("\n🎉 All tests PASSED!")
        return 0
    else:
        print("\n⚠️  Some tests FAILED. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

