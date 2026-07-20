"""Streamlit Web Interface for Epistemic Forge.

Provides a GUI alternative to the CLI, exposing Hermes routing options 
and rendering the Neuro-Symbolic Claim Lattice visually.
"""
import streamlit as st
from epistemic_forge.models import ProjectSpec
from epistemic_forge.pipeline.arsenal_run import run_pipeline

st.set_page_config(page_title="Epistemic Forge", page_icon="🧠", layout="wide")

st.title("🧠 Epistemic Forge")
st.markdown("### Neuro-Symbolic State Machine for LLMs")

with st.sidebar:
    st.header("🌐 Hermes Universal Routing")
    model_choice = st.text_input("Target Model", value="gpt-4o-mini", help="e.g., 'openai/gpt-4o', 'anthropic/claude-3-5-sonnet', 'ollama/llama3'")
    api_base = st.text_input("Custom API Base (Optional)", help="For local deployments via vLLM or Ollama.")
    
    st.header("Project Configuration")
    domain = st.selectbox("Reasoning Domain", ["hybrid", "research", "philosophy", "kaggle", "freelance"])

st.subheader("Define Your Inquiry")
title = st.text_input("Project Title", placeholder="e.g., Predictive Processing")
question = st.text_area("Core Premise / Question", placeholder="If the brain is a prediction machine, what happens to moral responsibility?")

if st.button("Ignite Synthesis Pipeline", type="primary"):
    if not title or not question:
        st.warning("Please provide both a title and a question.")
    else:
        with st.spinner(f"Dispatching experts via {model_choice}..."):
            try:
                # Execution
                result = run_pipeline(
                    title=title,
                    question=question,
                    domain=domain
                    # Further deep integration needed to pass model_choice strictly to the run.
                )
                
                st.success("Synthesis Complete.")
                
                # Render Claims as expandable cards
                if hasattr(result, "claims"):
                    st.markdown("### 🌳 Epistemic Claim Lattice")
                    for claim in result.claims:
                        c_dict = claim.model_dump() if hasattr(claim, "model_dump") else claim
                        with st.expander(f"Claim: {c_dict.get('text', '')}"):
                            st.write("**Supports:**")
                            for s in c_dict.get("support", []):
                                st.markdown(f"- ✅ {s}")
                            st.write("**Objections:**")
                            for o in c_dict.get("objections", []):
                                st.markdown(f"- ❌ {o}")
            except Exception as e:
                st.error(f"Critical Pipeline Error: {e}")
