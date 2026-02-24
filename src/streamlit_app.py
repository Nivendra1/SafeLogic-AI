import streamlit as st
import time
from hardening_agent import harden_logic


st.set_page_config(page_title="SafeLogic-AI v1.0", layout="wide")

st.title("SafeLogic-AI v1.0")
st.markdown("Hybrid LLM + Symbolic PLC Safety Validation")

st.markdown(
    "<div style='text-align:right;'>Running on AMD MI300X — On-Premise Deployment</div>",
    unsafe_allow_html=True
)

st.markdown("---")

user_input = st.text_area(
    "Enter Natural Language PLC Description:",
    height=150
)

if st.button("Run Safety Pipeline"):

    start_time = time.time()

    # 🔥 EXPLAIN MODE ENABLED HERE
    result = harden_logic(user_input, explain=True)

    total_time = time.time() - start_time

    st.success(f"Total Safety Pipeline Time: {total_time:.3f} seconds")

    st.markdown("---")
    st.header("Iteration Timeline")

    for attempt in result["iterations"]:
        st.subheader(f"Attempt {attempt['attempt']}")

        st.markdown(f"- **Extracted Boolean:** `{attempt['boolean']}`")

        risk = attempt["risk"]
        if risk == "CRITICAL":
            st.markdown(f"- **Risk Level:** :red[{risk}]")
        elif risk == "LOW":
            st.markdown(f"- **Risk Level:** :green[{risk}]")
        else:
            st.markdown(f"- **Risk Level:** :orange[{risk}]")

        st.markdown(f"- **Reason:** {attempt['reason']}")
        st.markdown("---")

    st.header("Final Status")

    if result["final_status"] == "SAFE":
        st.success("FINAL STATUS: SAFE")

        st.header("Safety Guarantee Summary")
        st.markdown("✅ Emergency Stop polarity verified")
        st.markdown("✅ Mandatory safety signals enforced")
        st.markdown("✅ No unsafe constant expressions")
        st.markdown("✅ Counterexample model checked")
        st.markdown("✅ Final logic formally validated SAFE")

    else:
        st.error(f"FINAL STATUS: {result['final_status']}")

    # 🔥 EXPLANATION BLOCK
    if result.get("explanation"):
        st.markdown("---")
        st.header("Explanation")
        st.text_area("Explanation Details", result["explanation"], height=150)
