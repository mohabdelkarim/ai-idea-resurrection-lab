"""
PoC: Delete rows and columns from Gradio Dataframe (gradio-app/gradio#631)

Shows the correct implementation using Gradio's event system:
- A gr.Dataframe component holds the state
- Delete Row / Delete Column buttons trigger Python callbacks
- State is managed via gr.State (not by subclassing Dataframe)

Requirements: gradio>=4.0  (pip install gradio)
To run:  python poc/main.py  then open http://127.0.0.1:7860
"""

import gradio as gr
import pandas as pd


# ---------------------------------------------------------------------------
# Core logic (pure functions — easy to test without Gradio)
# ---------------------------------------------------------------------------

def delete_row(df: pd.DataFrame, row_index: int) -> pd.DataFrame:
    """Drop a row by integer index. Returns the updated DataFrame."""
    if df is None or df.empty:
        raise gr.Error("No data to delete from.")
    if row_index < 0 or row_index >= len(df):
        raise gr.Error(f"Row index {row_index} is out of range (0–{len(df)-1}).")
    return df.drop(index=df.index[row_index]).reset_index(drop=True)


def delete_column(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """Drop a column by name. Returns the updated DataFrame."""
    if df is None or df.empty:
        raise gr.Error("No data to delete from.")
    if col_name not in df.columns:
        raise gr.Error(f"Column '{col_name}' not found. Available: {list(df.columns)}")
    return df.drop(columns=[col_name])


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

def build_ui():
    initial_df = pd.DataFrame({
        "Name":  ["Alice", "Bob", "Carol"],
        "Score": [95, 82, 78],
        "Grade": ["A", "B", "C"],
    })

    with gr.Blocks(title="Dataframe Row/Column Delete") as demo:
        gr.Markdown("## Dataframe with Row and Column Delete")

        table = gr.Dataframe(value=initial_df, interactive=True)

        with gr.Row():
            row_input = gr.Number(label="Row index to delete", value=0, precision=0, minimum=0)
            del_row_btn = gr.Button("Delete Row", variant="secondary")

        with gr.Row():
            col_input = gr.Textbox(label="Column name to delete", placeholder="e.g. Score")
            del_col_btn = gr.Button("Delete Column", variant="secondary")

        del_row_btn.click(
            fn=lambda df, idx: delete_row(df, int(idx)),
            inputs=[table, row_input],
            outputs=table,
        )

        del_col_btn.click(
            fn=delete_column,
            inputs=[table, col_input],
            outputs=table,
        )

    return demo


# ---------------------------------------------------------------------------
# Tests (run without Gradio)
# ---------------------------------------------------------------------------

def _run_tests():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]})

    result = delete_row(df.copy(), 1)
    assert list(result["A"]) == [1, 3], "delete_row failed"
    print("  delete_row: PASS")

    result = delete_column(df.copy(), "B")
    assert "B" not in result.columns, "delete_column failed"
    print("  delete_column: PASS")

    print("All tests passed.")


if __name__ == "__main__":
    print("=== Running unit tests ===")
    _run_tests()
    print()
    print("=== Launching Gradio demo ===")
    print("Open http://127.0.0.1:7860")
    build_ui().launch()
