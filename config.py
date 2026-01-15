DEEPWIKI_URL = "https://mcp.deepwiki.com/sse"

REPOSITORIES = {
    "wso2/financial-services-accelerator": "Financial Services Accelerator",
    "wso2/product-is": "Identity Server",
    "wso2/product-apim": "API Manager",
    "wso2/docs-is": "Identity Server Docs",
    "wso2/docs-apim": "API Manager Docs",
    "wso2/docs-mi": "Micro Integrator Docs",
    "wso2/docs-open-banking": "Open Banking Docs",
}

MODEL = "google-gla:gemini-2.5-flash"

SYSTEM_PROMPT = """You are a WSO2 Solutions Architect with knowledge of all WSO2 products.

Use the query_repo tool to search WSO2 GitHub repositories for accurate information.
Use explore_repo to understand repository structure.
Always cite sources with repository name and file paths.
Provide production-ready code examples when applicable."""
