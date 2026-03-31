import pandas as pd
from reconciliation import reconcile_data

# Helper function
def create_test_files(txn_data, settle_data):
    txn_file = "temp_txn.csv"
    settle_file = "temp_settle.csv"

    pd.DataFrame(txn_data).to_csv(txn_file, index=False)
    pd.DataFrame(settle_data).to_csv(settle_file, index=False)

    return txn_file, settle_file


# ✅ Test 1: Missing Settlement
def test_missing_settlement():
    txn_data = [
        {"transaction_id": "T1", "amount": 100},
        {"transaction_id": "T2", "amount": 200}
    ]

    settle_data = [
        {"transaction_id": "T1", "amount": 100}
    ]

    txn_file, settle_file = create_test_files(txn_data, settle_data)

    issues_df, _ = reconcile_data(txn_file, settle_file)

    assert "T2" in issues_df["transaction_id"].values


# ✅ Test 2: Unexpected Settlement
def test_unexpected_settlement():
    txn_data = [
        {"transaction_id": "T1", "amount": 100}
    ]

    settle_data = [
        {"transaction_id": "T1", "amount": 100},
        {"transaction_id": "T999", "amount": 50}
    ]

    txn_file, settle_file = create_test_files(txn_data, settle_data)

    issues_df, _ = reconcile_data(txn_file, settle_file)

    assert "T999" in issues_df["transaction_id"].values


# ✅ Test 3: Duplicate
def test_duplicate():
    txn_data = [
        {"transaction_id": "T1", "amount": 100}
    ]

    settle_data = [
        {"transaction_id": "T1", "amount": 100},
        {"transaction_id": "T1", "amount": 100}
    ]

    txn_file, settle_file = create_test_files(txn_data, settle_data)

    issues_df, _ = reconcile_data(txn_file, settle_file)

    assert "Duplicate Settlement" in issues_df["issue"].values


# ✅ Test 4: Amount Mismatch
def test_amount_mismatch():
    txn_data = [
        {"transaction_id": "T1", "amount": 100}
    ]

    settle_data = [
        {"transaction_id": "T1", "amount": 150}
    ]

    txn_file, settle_file = create_test_files(txn_data, settle_data)

    issues_df, _ = reconcile_data(txn_file, settle_file)

    assert "Amount Mismatch" in issues_df["issue"].values


# ✅ Test 5: Refund Without Original
def test_refund_without_original():
    txn_data = [
        {"transaction_id": "T1", "amount": 100, "type": "payment"},
        {"transaction_id": "T2", "amount": -50, "type": "refund", "original_transaction_id": "T999"}
    ]

    settle_data = [
        {"transaction_id": "T1", "amount": 100}
    ]

    txn_file, settle_file = create_test_files(txn_data, settle_data)

    issues_df, _ = reconcile_data(txn_file, settle_file)

    assert "Refund Without Original" in issues_df["issue"].values


# ✅ Test 6: Perfect Match
def test_perfect_match():
    txn_data = [
        {"transaction_id": "T1", "amount": 100}
    ]

    settle_data = [
        {"transaction_id": "T1", "amount": 100}
    ]

    txn_file, settle_file = create_test_files(txn_data, settle_data)

    issues_df, _ = reconcile_data(txn_file, settle_file)

    assert issues_df.empty