import gradio as gr
import pandas as pd
from gradio.components import Dataframe

class CustomDataframe(Dataframe):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delete_row_button = gr.Button("Delete Row")
        self.delete_col_button = gr.Button("Delete Column")
        self.delete_row_input = gr.Number(label="Row Index", value=0)
        self.delete_col_input = gr.Textbox(label="Column Name")

    def delete_row(self, row_index):
        try:
            self.value.drop(index=row_index, inplace=True)
            return self.value
        except Exception as e:
            print(f"Error deleting row: {e}")

    def delete_col(self, col_name):
        try:
            self.value.drop(columns=[col_name], inplace=True)
            return self.value
        except Exception as e:
            print(f"Error deleting column: {e}")

def main():
    # Create a sample dataframe
    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": [4, 5, 6],
        "C": [7, 8, 9]
    })

    # Create a custom dataframe component
    custom_df = CustomDataframe(df)

    # Define event listeners for delete buttons
    custom_df.delete_row_button.click(
        custom_df.delete_row,
        custom_df.delete_row_input,
        custom_df
    )

    custom_df.delete_col_button.click(
        custom_df.delete_col,
        custom_df.delete_col_input,
        custom_df
    )

    # Launch the Gradio app
    gr.Interface(
        lambda: custom_df,
        inputs=None,
        outputs=custom_df,
        title="Custom Dataframe"
    ).launch()

if __name__ == "__main__":
    main()