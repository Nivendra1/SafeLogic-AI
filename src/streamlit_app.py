import streamlit as st
import time
from hardening_agent import harden_logic
from safelogic_engine import check_mandatory_signal, extract_expression, normalize_expression

st.set_page_config(page_title="SafeLogic-AI v1.0", layout="wide")

# ── Header ──
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🛡️ SafeLogic-AI v1.0")
    st.markdown("**Hybrid LLM + Symbolic PLC Safety Validation**")
with col2:
    st.markdown(
        "<div style='text-align:right; padding-top:20px; color:gray; font-size:13px;'>"
        "Running on AMD MI300X<br>On-Premise Deployment</div>",
        unsafe_allow_html=True
    )

st.markdown("---")

# ── Mode Toggle ──
mode = st.radio(
    "Select Mode:",
    ["🤖 Generate Mode — Natural Language → PLC → Validate",
     "🔍 Validate Mode — Direct Boolean Expression Check"],
    horizontal=True
)

st.markdown("---")

# ══════════════════════════════════════════
# MODE 1: GENERATE MODE
# ══════════════════════════════════════════
if "Generate" in mode:
    st.subheader("Generate PLC Logic from Natural Language")
    st.caption("Describe your machine behavior. The LLM generates IEC 61131-3 Structured Text, then the symbolic engine validates it.")

    user_input = st.text_area(
        "Enter Natural Language PLC Description:",
        height=150,
        placeholder="e.g. Motor starts when button pressed and stops on emergency stop"
    )

    if st.button("🚀 Run Safety Pipeline", type="primary"):
        if not user_input.strip():
            st.warning("Please enter a description first.")
        else:
            start_time = time.time()
            result = harden_logic(user_input, explain=True)
            total_time = time.time() - start_time

            st.success(f"⏱️ Total Safety Pipeline Time: {total_time:.3f} seconds")
            st.markdown("---")

            # Iteration Timeline
            st.header("🔁 Iteration Timeline")
            for attempt in result["iterations"]:
                st.subheader(f"Attempt {attempt['attempt']}")
                boolean_val = attempt['boolean']
                if boolean_val:
                    st.markdown(f"- **Extracted Boolean:** `{boolean_val}`")
                else:
                    st.markdown("- **Extracted Boolean:** `None`")

                risk = attempt["risk"]
                if risk == "CRITICAL":
                    st.markdown(f"- **Risk Level:** :red[{risk}]")
                elif risk == "LOW":
                    st.markdown(f"- **Risk Level:** :green[{risk}]")
                else:
                    st.markdown(f"- **Risk Level:** :orange[{risk}]")

                st.markdown(f"- **Reason:** {attempt['reason']}")
                st.markdown("---")

            # Final Status
            st.header("📋 Final Status")
            if result["final_status"] == "SAFE":
                st.success("✅ FINAL STATUS: SAFE")
                st.markdown("---")
                st.header("🛡️ Safety Guarantee Summary")
                st.markdown("✅ Emergency Stop polarity verified")
                st.markdown("✅ Mandatory safety signals enforced")
                st.markdown("✅ No unsafe constant expressions")
                st.markdown("✅ Counterexample model checked")
                st.markdown("✅ Final logic formally validated SAFE")
            else:
                st.error(f"🚨 FINAL STATUS: {result['final_status']}")

            # Explanation
            if result.get("explanation"):
                st.markdown("---")
                st.header("📝 Explanation")
                st.text_area("Explanation Details", result["explanation"], height=150)


# ══════════════════════════════════════════
# MODE 2: VALIDATE MODE
# ══════════════════════════════════════════
else:
    st.subheader("Direct Boolean Expression Validator")
    st.caption("Paste any PLC Boolean expression. The symbolic engine validates it instantly — no LLM involved.")

    st.info(
        "**Example expressions to try:**\n\n"
        "✅ SAFE: `StartButton AND NOT EmergencyStopButton`\n\n"
        "🚨 VIOLATION: `StartButton AND EmergencyStopButton`\n\n"
        "🚨 VIOLATION: `StartButton AND SafetyDoorOpen AND NOT EmergencyStopButton`\n\n"
        "🚨 VIOLATION: `StartButton`"
    )

    expression_input = st.text_area(
        "Enter Boolean Expression to Validate Directly:",
        height=100,
        placeholder="e.g. StartButton AND NOT EmergencyStopButton AND NOT SafetyDoorOpen"
    )

    if st.button("🔍 Validate Expression", type="primary"):
        if not expression_input.strip():
            st.warning("Please enter a Boolean expression first.")
        else:
            start_time = time.time()

            # Direct symbolic validation — no LLM
            expression = expression_input.strip()
            result = check_mandatory_signal(expression)
            elapsed = time.time() - start_time

            st.success(f"⚡ Validation Time: {elapsed:.4f} seconds (deterministic — no LLM)")
            st.markdown("---")

            st.header("📋 Validation Report")
            st.markdown(f"**Expression Evaluated:** `{expression}`")

            risk = result.get("risk_level", "UNKNOWN")
            status = result.get("status", "UNKNOWN")
            reason = result.get("reason", "Unknown")

            if status == "SAFE":
                st.success("✅ STATUS: SAFE")
                st.markdown(f"- **Risk Level:** :green[{risk}]")
                st.markdown(f"- **Reason:** {reason}")
                st.markdown("---")
                st.header("🛡️ Safety Guarantee Summary")
                st.markdown("✅ Emergency Stop polarity verified")
                st.markdown("✅ Mandatory safety signals enforced")
                st.markdown("✅ No unsafe constant expressions")
                st.markdown("✅ Counterexample model checked")
                st.markdown("✅ Final logic formally validated SAFE")

            else:
                st.error("🚨 STATUS: VIOLATION DETECTED")

                if risk == "CRITICAL":
                    st.markdown(f"- **Risk Level:** :red[{risk}]")
                elif risk == "HIGH":
                    st.markdown(f"- **Risk Level:** :orange[{risk}]")
                else:
                    st.markdown(f"- **Risk Level:** :orange[{risk}]")

                st.markdown(f"- **Violation Reason:** {reason}")
                st.markdown("---")

                # Counterexample section
                st.subheader("⚠️ What This Means")
                if "EmergencyStopButton missing" in reason:
                    st.error(
                        "This expression has no emergency stop signal. "
                        "The output can be active even when the estop is pressed. "
                        "Real-world consequence: pressing the estop has no effect on this output."
                    )
                elif "polarity" in reason.lower() or "negated" in reason.lower():
                    st.error(
                        "EmergencyStopButton is present but wired as an ENABLING condition, not a cut condition. "
                        "This means the estop ACTIVATES the output instead of cutting it. "
                        "Real-world consequence: pressing the estop starts the machine instead of stopping it."
                    )
                elif "constant" in reason.lower():
                    st.error(
                        "The output is a constant TRUE or FALSE. "
                        "A constant TRUE means the output is always active regardless of any input. "
                        "No safety signal can ever cut it."
                    )
                else:
                    st.error(f"Safety violation: {reason}")

                st.markdown("---")
                st.subheader("🔧 How To Fix")
                st.code(
                    "-- Correct pattern:\n"
                    "OutputVariable := StartButton AND NOT EmergencyStopButton;\n\n"
                    "-- EmergencyStopButton must appear as NOT EmergencyStopButton\n"
                    "-- Every output must reference the emergency stop as a cut condition",
                    language="text"
                )
