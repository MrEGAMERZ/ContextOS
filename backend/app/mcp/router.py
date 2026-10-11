from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.mcp.server import MCPServer

router = APIRouter(tags=["MCP"])

class ToolCallRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    method: str
    params: Optional[Dict[str, Any]] = None

@router.get("/api/mcp/tools")
async def get_mcp_tools(db: AsyncSession = Depends(get_db)):
    server = MCPServer(db)
    return {"tools": await server.list_tools()}

@router.post("/api/mcp/call")
async def call_mcp_tool(req: ToolCallRequest, db: AsyncSession = Depends(get_db)):
    server = MCPServer(db)
    return await server.execute_tool(req.tool, req.arguments)

@router.post("/mcp")
async def handle_mcp_jsonrpc(req: JSONRPCRequest, db: AsyncSession = Depends(get_db)):
    """Standard Model Context Protocol JSON-RPC 2.0 endpoint for Alexa+ integration"""
    server = MCPServer(db)

    if req.method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": False}
                },
                "serverInfo": {
                    "name": "ContextOS-MCP",
                    "version": "0.1.0"
                }
            }
        }
    elif req.method == "tools/list":
        tools = await server.list_tools()
        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "result": {"tools": tools}
        }
    elif req.method == "tools/call":
        params = req.params or {}
        tool_name = params.get("name") or params.get("tool")
        args = params.get("arguments") or {}
        if not tool_name:
            raise HTTPException(status_code=400, detail="Missing tool name in tools/call")
        res = await server.execute_tool(tool_name, args)
        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": str(res.get("data", res))
                    }
                ],
                "meta": {
                    "execution_ms": res.get("execution_ms"),
                    "sla_pass": res.get("sla_pass")
                }
            }
        }
    elif req.method == "ping":
        return {"jsonrpc": "2.0", "id": req.id, "result": {}}
    else:
        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "error": {"code": -32601, "message": f"Method '{req.method}' not found"}
        }
