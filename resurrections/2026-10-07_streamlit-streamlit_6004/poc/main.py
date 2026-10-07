import streamlit as st
import traceback

# ---------------------------------------------------------------------------
# Helper: safe execution wrapper to display errors without breaking the app
# ---------------------------------------------------------------------------
def safe_execute(func, *args, **kwargs):
    """Execute *func* catching any exception and showing it in the UI.

    Streamlit reruns the script on every interaction, so we want errors to be
    visible but not to stop the rest of the page from rendering.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error(f"Error: {e}")
        st.text(traceback.format_exc())
        return None

# ---------------------------------------------------------------------------
# Core concept: a tabs component that stores its selected index in session state
# ---------------------------------------------------------------------------
def tabs_with_state(tab_labels, key="_tabs_state", default_selected=0, on_change=None):
    """Render a simple tabs UI whose active tab is persisted in ``st.session_state``.

    Parameters
    ----------
    tab_labels: list[str]
        The names of the tabs.
    key: str
        Session‑state key used to store the selected index.
    default_selected: int
        Index of the tab that should be active on first render.
    on_change: callable | None
        Optional callback invoked when the user selects a different tab.
    """
    # Initialise the state if it does not exist yet
    if key not in st.session_state:
        st.session_state[key] = int(default_selected)

    # Render tab buttons horizontally
    cols = st.columns(len(tab_labels))
    for idx, (col, label) in enumerate(zip(cols, tab_labels)):
        # Highlight the active tab
        is_active = st.session_state[key] == idx
        style = "font-weight: bold;" if is_active else ""
        # Use a button; when clicked we update the session state
        if col.button(label, key=f"{key}_btn_{idx}", help=label, disabled=False):
            if st.session_state[key] != idx:
                st.session_state[key] = idx
                if callable(on_change):
                    on_change(idx)
        # Apply simple CSS to indicate the active tab (Streamlit 1.30+ supports markdown with HTML)
        col.markdown(f"<div style='{style}'>{label}</div>", unsafe_allow_html=True)

    # Return the index of the currently selected tab so callers can branch logic
    return st.session_state[key]

# ---------------------------------------------------------------------------
# Example usage of the tabs_with_state component
# ---------------------------------------------------------------------------
def main():
    st.title("Demo: Stateful Tabs with Streamlit")

    # Define tab labels
    tabs = ["Home", "Data", "Settings", "About"]

    # Optional callback to illustrate side‑effects when tab changes
    def tab_changed(new_index):
        st.info(f"Tab changed to: {tabs[new_index]}")

    # Render the tabs component; default is the second tab (index 1)
    selected = safe_execute(tabs_with_state, tabs, key="demo_tabs", default_selected=1, on_change=tab_changed)

    # Show content based on the selected tab
    if selected == 0:
        st.subheader("Home")
        st.write("Welcome to the home page!")
    elif selected == 1:
        st.subheader("Data")
        st.write("Here you could load and display data.")
        # Example of programmatically changing the tab after an action
        if st.button("Go to Settings programmatically"):
            st.session_state["demo_tabs"] = 2
            st.experimental_rerun()
    elif selected == 2:
        st.subheader("Settings")
        st.write("Adjust your preferences here.")
    elif selected == 3:
        st.subheader("About")
        st.write("Information about this demo.")
    else:
        st.write("Unknown tab index.")

# ---------------------------------------------------------------------------
# Run the app
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    safe_execute(main)