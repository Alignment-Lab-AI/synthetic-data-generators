import streamlit as st
import pandas as pd
import openai
import base64
import os

def generate_response(system_prompt, user_prompt, model="gpt-3.5-turbo", *args):
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]
    role = "assistant"
    for value in args:
        messages.append({"role": role, "content": value})
        role = "user" if role == "assistant" else "assistant"

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=2500,
        temperature=0,
    )
    return response.choices[0]["message"]["content"]

def generate_responses(df, selected_column, user_prompt, model):
    responses = []
    filename = 'output.csv'
    batch_size = 5

    for i in range(0, len(df), batch_size):
        batch_prompts = df.loc[i:i+batch_size-1, selected_column]
        batch_responses = [generate_response(prompt, user_prompt, model) for prompt in batch_prompts]

        df.loc[i:i+batch_size-1, "response"] = batch_responses
        df.loc[i:i+batch_size-1].to_csv(filename, mode='a', header=not os.path.exists(filename), index=False)

    return df

    if responses:
        start = len(df) - len(responses)
        df.loc[start:, "response"] = responses
        df.loc[start:].to_csv(filename, mode='a', header=not os.path.exists(filename), index=False)

    return df
def generate_csv_link(df):
    filename = 'output.csv'
    df.to_csv(filename, mode='a', header=not os.path.exists(filename), index=False)
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  
    href = f'<a href="data:file/csv;base64,{b64}" download="output.csv">Processed CSV File</a>'
    return href

def main():
    st.title('Generating Precise Tables')
    openai.api_key = st.text_input('API key', 'PUT KEY HERE')
    model = st.text_input('First Model', 'gpt-3.5-turbo')
    user_prompt = st.text_area("Put your first prompt here!")
    system_prompt = st.text_area("Paste your system prompt here")
    model_2 = st.text_input('Second Model', 'gpt-3.5-turbo')  # Second model input field
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    df = pd.read_csv(uploaded_file) if uploaded_file is not None else None
    selected_column = st.selectbox('Select the column to create instruct data from', df.columns) if df is not None else None
    num_loops = st.number_input('Number of times to loop the script', min_value=1, max_value=100, value=1, step=1)

    if st.button('Generate Responses'):
        for _ in range(num_loops):
            if df is not None and selected_column:
                df = generate_responses(df, selected_column, user_prompt, model)
                st.dataframe(df)
                st.markdown(generate_csv_link(df), unsafe_allow_html=True)
            else:
                first_res = generate_response(system_prompt, user_prompt, model)
                second_res = generate_response(system_prompt, first_res, model_2)  # Use the second model here
                data = {"question": [first_res], "context": [system_prompt], "answer": [second_res]}
                df = pd.DataFrame(data)
                st.dataframe(df)
                st.markdown(generate_csv_link(df), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
    
    #gpt will see the given cell in a csv or the given chunk of data at the same time as the first prompt, the data and the prompt are given to the second model, the two responses will be output to a line on a csv. for example {code snippet}'Generate a question based on the unique form function or shape of this code snippet and respond with ONLY the question" which goes to the second model which responds with {answer to question}, which writes a row as {question} {code} {answer}, can be easily tooled to generate instruction, qa, and various other forms of training data from sparse or unformatted data.

