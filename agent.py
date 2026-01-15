import os
import sys
from typing import Optional, List
from dataclasses import dataclass
import dotenv

from pydantic_ai import RunContext
from pydantic_ai.agent import Agent

from config import REPOSITORIES, MODEL, SYSTEM_PROMPT, DEEPWIKI_URL
from deepwiki_client import get_client, DeepWikiClient

dotenv.load_dotenv()

if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
    print("Error: Set GOOGLE_API_KEY or OPENAI_API_KEY in .env")
    sys.exit(1)


@dataclass
class Deps:
    client: DeepWikiClient
    repos: List[str]


agent = Agent(MODEL, deps_type=Deps, system_prompt=SYSTEM_PROMPT)


@agent.tool
async def query_repo(ctx: RunContext[Deps], question: str, repo: Optional[str] = None) -> str:
    client = ctx.deps.client
    repos = ctx.deps.repos
    
    if repo:
        if repo not in repos and repo not in REPOSITORIES:
            return f"Repository '{repo}' not configured."
        result = await client.ask(repo, question)
        if result.success:
            return f"Source: {repo}\n\n{result.content}"
        return f"Could not query {repo}: {result.error}"
    
    relevant = select_repos(question, repos)
    for r in relevant[:2]:
        result = await client.ask(r, question)
        if result.success:
            return f"Source: {r}\n\n{result.content}"
    
    return "No results found in configured repositories."


@agent.tool
async def explore_repo(ctx: RunContext[Deps], repo: str) -> str:
    client = ctx.deps.client
    repos = ctx.deps.repos
    
    if repo not in repos and repo not in REPOSITORIES:
        available = "\n".join([f"- {r}" for r in repos[:10]])
        return f"Repository '{repo}' not configured. Available:\n{available}"
    
    result = await client.structure(repo)
    if result.success:
        return f"Repository: {repo}\n\n{result.content}"
    return f"Could not read {repo}: {result.error}"


@agent.tool
async def list_repos(ctx: RunContext[Deps]) -> str:
    repos = ctx.deps.repos
    lines = ["Available repositories:"]
    for r in repos:
        desc = REPOSITORIES.get(r, "")
        lines.append(f"- {r}: {desc}")
    return "\n".join(lines)


def select_repos(question: str, repos: List[str]) -> List[str]:
    q = question.lower()
    mapping = {
        "identity": ["wso2/product-is", "wso2/identity-apps", "wso2/docs-is"],
        "oauth": ["wso2/product-is", "wso2/identity-api-server"],
        "api": ["wso2/product-apim", "wso2/apim-apps", "wso2/docs-apim"],
        "open banking": ["wso2/financial-services-accelerator", "wso2/financial-open-banking"],
        "fapi": ["wso2/financial-services-accelerator", "wso2/financial-open-banking"],
        "integration": ["wso2/product-mi", "wso2/micro-integrator", "wso2/docs-mi"],
        "ballerina": ["ballerina-platform/ballerina-lang"],
        "asgardeo": ["asgardeo/asgardeo-auth-react-sdk", "asgardeo/asgardeo-auth-js-sdk"],
    }
    
    result = set()
    for key, values in mapping.items():
        if key in q:
            result.update(values)
    
    result = [r for r in result if r in repos]
    if not result:
        result = ["wso2/financial-services-accelerator", "wso2/product-is", "wso2/product-apim"]
        result = [r for r in result if r in repos]
    
    return result[:3]


def create_deps(repos: Optional[List[str]] = None) -> Deps:
    if repos is None:
        repos = list(REPOSITORIES.keys())
    return Deps(client=get_client(DEEPWIKI_URL), repos=repos)


async def ask(question: str, repos: Optional[List[str]] = None) -> str:
    deps = create_deps(repos)
    result = await agent.run(question, deps=deps)
    return str(result.output) if hasattr(result, 'output') else str(result)
