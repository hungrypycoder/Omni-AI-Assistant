import logging
import asyncio
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from mcp import ClientSession
    from mcp.client.sse import sse_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


@dataclass
class QueryResult:
    repo: str
    content: str
    success: bool
    error: Optional[str] = None


class DeepWikiClient:
    def __init__(self, server_url: str, timeout: int = 60, retries: int = 2):
        self.server_url = server_url
        self.timeout = timeout
        self.retries = retries
    
    async def _call_tool(self, tool: str, args: dict) -> str:
        async with sse_client(self.server_url) as streams:
            read, write = streams
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool, args)
                if result.content:
                    return result.content[0].text
                return ""
    
    async def ask(self, repo: str, question: str) -> QueryResult:
        if not MCP_AVAILABLE:
            return QueryResult(repo=repo, content="", success=False, error="MCP not installed")
        
        for attempt in range(self.retries):
            try:
                content = await asyncio.wait_for(
                    self._call_tool("ask_question", {"repoName": repo, "question": question}),
                    timeout=self.timeout
                )
                if content:
                    return QueryResult(repo=repo, content=content, success=True)
                return QueryResult(repo=repo, content="", success=False, error="No content")
            except asyncio.TimeoutError:
                if attempt < self.retries - 1:
                    await asyncio.sleep(1)
                    continue
                return QueryResult(repo=repo, content="", success=False, error="Request timed out")
            except Exception as e:
                if attempt < self.retries - 1:
                    await asyncio.sleep(1)
                    continue
                return QueryResult(repo=repo, content="", success=False, error=str(e))
        return QueryResult(repo=repo, content="", success=False, error="Max retries exceeded")
    
    async def structure(self, repo: str) -> QueryResult:
        if not MCP_AVAILABLE:
            return QueryResult(repo=repo, content="", success=False, error="MCP not installed")
        
        for attempt in range(self.retries):
            try:
                content = await asyncio.wait_for(
                    self._call_tool("read_wiki_structure", {"repoName": repo}),
                    timeout=self.timeout
                )
                if content:
                    return QueryResult(repo=repo, content=content, success=True)
                return QueryResult(repo=repo, content="", success=False, error="No content")
            except asyncio.TimeoutError:
                if attempt < self.retries - 1:
                    await asyncio.sleep(1)
                    continue
                return QueryResult(repo=repo, content="", success=False, error="Request timed out")
            except Exception as e:
                if attempt < self.retries - 1:
                    await asyncio.sleep(1)
                    continue
                return QueryResult(repo=repo, content="", success=False, error=str(e))
        return QueryResult(repo=repo, content="", success=False, error="Max retries exceeded")


_client = None

def get_client(url: str) -> DeepWikiClient:
    global _client
    if _client is None:
        _client = DeepWikiClient(url)
    return _client
