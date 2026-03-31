import streamlit as st
import pandas as pd
from reconciliation import reconcile_data

st.set_page_config(page_title="Reconciliation System", layout="wide")

st.title("💳 Transaction Reconciliation System")

st.markdown("Upload **Platform Transactions** and **Bank Settlements** files")

# File upload
txn_file = st.file_uploader("Upload Transactions CSV", type=["csv"])
settle_file = st.file_uploader("Upload Settlements CSV", type=["csv"])

if txn_file and settle_file:

    # ✅ Read files once (for checking only)
    txn_df = pd.read_csv(txn_file)
    settle_df = pd.read_csv(settle_file)

    # Normalize column names
    txn_cols = txn_df.columns.str.lower().str.strip()
    settle_cols = settle_df.columns.str.lower().str.strip()

    # ✅ Swap detection logic
    if "settlement_id" in txn_cols:
        st.error("❌ You uploaded a Settlements file in the Transactions section")
        st.stop()

    if "settlement_id" not in settle_cols:
        st.error("❌ You uploaded a Transactions file in the Settlements section")
        st.stop()

    # ✅ Run original logic (no change)
    issues_df, summary = reconcile_data(txn_df, settle_df)

    st.subheader("📊 Summary")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Transactions", summary["Total Transactions"])
    col2.metric("Settlements", summary["Total Settlements"])
    col3.metric("Issues Found", summary["Total Issues"])
    col4.metric("Rounding Diff", summary["Rounding Difference"])

    st.subheader("⚠️ Issues Detected")

    if not issues_df.empty:
        issue_filter = st.selectbox(
            "Filter by Issue Type",
            ["All"] + list(issues_df["issue"].unique())
        )

        if issue_filter != "All":
            issues_df = issues_df[issues_df["issue"] == issue_filter]

        st.dataframe(issues_df, use_container_width=True)
    else:
        st.success("✅ No issues found!")

    # Download report
    csv = issues_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Report",
        data=csv,
        file_name="reconciliation_report.csv",
        mime="text/csv"
    )

else:
    st.info("Please upload both files to proceed.")
