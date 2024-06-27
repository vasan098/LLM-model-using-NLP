import streamlit as st
import requests
import json
import csv
import datetime

# Function to fetch available models
def list_ollama_models():
    """
    Lists locally available ollama models.
    """
    url = "http://localhost:11434/api/tags"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        models = data["models"]
        return [model["name"] for model in models]
    else:
        st.error("Error fetching models.")
        return []

# Function to save input-output data to CSV
def save_to_csv(input_output, model_name):
    """
    Saves the given input-output data as rows in a CSV file named 'output-{model_name}.csv'.

    Args:
    input_output (Iterable or Iterable of Iterables): The data to be saved in the CSV file.
    """
    with open(f'output-{model_name}.csv', mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        row_data = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), *input_output]
        writer.writerow(row_data)

# Function to generate response from API
def generate_response(input_text, model_name):
    """
    Generates a response from an API using the given input and saves the input and output to a CSV file.

    Args:
    input_text (str): The input prompt text.
    model_name (str): The selected model name.

    Returns:
    The generated response text from the API.
    """
    url = "http://localhost:11434/api/generate"
    headers = {'Content-Type': 'application/json'}
    data = {"model": model_name, "stream": False, "prompt": input_text, "context": []}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_text = json.loads(response.text)["response"]
        save_to_csv([input_text, response_text], model_name)
        return response_text
    else:
        st.error(f"Error: {response.status_code}, {response.text}")
        return None

# Function to clear conversation history
def clear_history(model_name):
    """
    Clears conversation history for a specific model.
    """
    with open(f'output-{model_name}.csv', mode='w', newline=''):
        pass

# App Title and Description
st.title("🤖 CODE BREAKERS 🚀")
st.markdown(
    """
    Welcome to CODE BREAKERS! This app uses the Ollama AI model to generate responses based on your input prompts.
    """
)

# Sidebar - Model Selection and History
st.sidebar.title("Model Selection")
available_models = list_ollama_models()
if not available_models:
    st.sidebar.warning("No models available.")
else:
    model_name = st.sidebar.selectbox("Select Model", available_models)

    if st.sidebar.button("Clear History", key="clear_history"):
        if st.sidebar.checkbox("Confirm Clear History"):
            clear_history(model_name)
            st.sidebar.success("Conversation history cleared.")

# Main Content - Input and Output
st.subheader("Enter your prompt below:")
input_text = st.text_area("Input Prompt", height=100)

if st.button("Generate Response"):
    if input_text.strip() == "":
        st.warning("Please enter a prompt before generating a response.")
    else:
        with st.spinner("Generating response..."):
            response = generate_response(input_text, model_name)
            if response:
                st.subheader("Generated Response:")
                st.info(response)

