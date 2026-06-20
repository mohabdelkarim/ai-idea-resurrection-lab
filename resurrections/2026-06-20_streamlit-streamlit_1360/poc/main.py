import streamlit as st
import json

def modal_popup(message):
    st.write("""
    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center;">
        <div style="background-color: white; padding: 20px; border-radius: 10px;">
            <p>"" + message + ""</p>
            <button onclick="window.location.href='/'">Close</button>
        </div>
    </div>
    """)

def main():
    st.title("Modal Popup Example")
    message = "This is a modal popup message"
    if st.button("Show Modal"):
        modal_popup(message)

if __name__ == '__main__':
    main()