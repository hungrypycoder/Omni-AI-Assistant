# WSO2 Documentation Agent

Query any WSO2 GitHub repositories.

## Setup

```bash
pip install pydantic-ai mcp streamlit python-dotenv
```

Set your API key in `.env`:
```
GOOGLE_API_KEY=your_key_here
```

## Run

```bash
streamlit run app.py
```

## Docker

Build and run:
```bash
docker build -t wso2-agent .
docker run -p 8501:8501 -e GOOGLE_API_KEY=your_key_here wso2-agent
```

Open http://localhost:8501

## Configure Repositories

Edit `config.py` to add or remove repositories:

```python
REPOSITORIES = {
    "wso2/product-is": "Identity Server",
    "your-org/your-repo": "Your Description",
}
```
