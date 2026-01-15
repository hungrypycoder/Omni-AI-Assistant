import streamlit as st
import asyncio
import nest_asyncio
from config import REPOSITORIES
from agent import agent, create_deps

nest_asyncio.apply()

st.set_page_config(page_title="WSO2 AI Assistant", page_icon="W", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "repos" not in st.session_state:
    st.session_state.repos = list(REPOSITORIES.keys())
if "loop" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()


with st.sidebar:
    st.header("Repositories")
    
    if st.button("Select All"):
        st.session_state.repos = list(REPOSITORIES.keys())
        st.rerun()
    if st.button("Clear All"):
        st.session_state.repos = []
        st.rerun()
    
    st.divider()
    
    for repo, desc in REPOSITORIES.items():
        checked = repo in st.session_state.repos
        if st.checkbox(repo.split("/")[-1], value=checked, key=f"r_{repo}", help=desc):
            if repo not in st.session_state.repos:
                st.session_state.repos.append(repo)
        else:
            if repo in st.session_state.repos:
                st.session_state.repos.remove(repo)
    
    st.divider()
    st.caption(f"{len(st.session_state.repos)} repos selected")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()


st.title("WSO2 Documentation Assistant")
st.caption("Ask questions about WSO2 products")

if not st.session_state.repos:
    st.warning("Select at least one repository")
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Ask about WSO2 products..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Searching..."):
                try:
                    deps = create_deps(st.session_state.repos)
                    loop = st.session_state.loop
                    result = loop.run_until_complete(agent.run(prompt, deps=deps))
                    response = str(result.output) if hasattr(result, 'output') else str(result)
                except Exception as e:
                    response = f"Error: {e}"
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
