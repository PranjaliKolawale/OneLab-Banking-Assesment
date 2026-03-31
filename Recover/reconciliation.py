import pandas as pd

def reconcile_data(txn, settle):   # ✅ accept DataFrames

    # Clean column names
    txn.columns = txn.columns.str.strip().str.lower()
    settle.columns = settle.columns.str.strip().str.lower()

    issues = []

    # Merge
    merged = txn.merge(
        settle,
        on="transaction_id",
        how="outer",
        suffixes=("_txn", "_settle"),
        indicator=True
    )

    # 🔍 1. Missing / Unexpected
    for _, row in merged.iterrows():
        if row["_merge"] == "left_only":
            issues.append({
                "transaction_id": row["transaction_id"],
                "issue": "Missing Settlement"
            })

        elif row["_merge"] == "right_only":
            issues.append({
                "transaction_id": row["transaction_id"],
                "issue": "Unexpected Settlement"
            })

        else:
            # 🔍 2. Amount mismatch
            if round(row["amount_txn"], 2) != round(row["amount_settle"], 2):
                issues.append({
                    "transaction_id": row["transaction_id"],
                    "issue": "Amount Mismatch"
                })

    # 🔍 3. Duplicate settlements
    dup = settle[settle.duplicated("transaction_id", keep=False)]
    for txn_id in dup["transaction_id"].unique():
        issues.append({
            "transaction_id": txn_id,
            "issue": "Duplicate Settlement"
        })

    # 🔍 4. Refund without original (safe)
    if "type" in txn.columns:
        txn["type"] = txn["type"].astype(str)

        refunds = txn[txn["type"].str.lower() == "refund"]

        for _, row in refunds.iterrows():
            original_id = row.get("original_transaction_id", None)

            if pd.isna(original_id) or original_id not in txn["transaction_id"].values:
                issues.append({
                    "transaction_id": row["transaction_id"],
                    "issue": "Refund Without Original"
                })

    # 🔍 5. Net difference (not just rounding)
    txn_total = txn["amount"].sum()
    settle_total = settle["amount"].sum()
    net_diff = round(txn_total - settle_total, 2)

    issues_df = pd.DataFrame(issues)

    summary = {
        "Total Transactions": len(txn),
        "Total Settlements": len(settle),
        "Total Issues": len(issues_df),
        "Rounding Difference": net_diff   # keep name if needed
    }

    return issues_df, summary
