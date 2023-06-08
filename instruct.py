import streamlit as st
import pandas as pd
import openai
from io import StringIO
import base64
import os


# Function to generate responses
def generate_response(system_prompt, user_prompt, model="gpt-3.5-turbo", *args):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    for value in args:
        messages.append({"role": "assistant" if messages[-1]["role"] == "user" else "user", "content": value})

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=2500,
        temperature=0.7,
    )

    return response.choices[0]["message"]["content"]


def main():
    st.title('Generating Precise Tables')
    openai.api_key = st.text_input('API key', 'PUT KEY HERE')
    model = st.text_input('Model', 'gpt-3.5-turbo')
    user_prompt = st.text_area("Put your first prompt here!")
    enable_second_prompt = st.checkbox('Enable second prompt')
    num_iterations = st.number_input('Number of iterations', min_value=1, value=1, step=1)

    uploaded_file = st.file_uploader("Or upload a CSV file")

    if uploaded_file is not None:
        df_file = pd.read_csv(uploaded_file)
        column_choice = st.selectbox('Select a column to create instructions for, df_file.columns)

        if st.button('Start Script'):
            data = {"context": [], "first_prompt": [], "first_response": [], "second_response": []}

            for _ in range(num_iterations):
                for index, row in df_file.iterrows():
                    system_prompt = row[column_choice]
                    data["context"].append(system_prompt)
                    data["first_prompt"].append(user_prompt)

                    first_res = generate_response(system_prompt, user_prompt, model)
                    data["first_response"].append(first_res)

                    if enable_second_prompt:
                        second_res = generate_response(system_prompt, first_res, model)
                        data["second_response"].append(second_res)

            output_df = pd.DataFrame(data)
            st.dataframe(output_df)
            output_df.to_csv('output.csv', mode='a', header=not os.path.exists('output.csv'), index=False)
            st.write('CSV has been written to a local file named "output.csv".')


if __name__ == "__main__":
    main()
    
    #gpt will see the given cell in a csv or the given chunk of data at the same time as the first prompt, the data and the prompt are given to the second model, the two responses will be output to a line on a csv. for example {code snippet}'Generate a question based on the unique form function or shape of this code snippet and respond with ONLY the question" which goes to the second model which responds with {answer to question}, which writes a row as {question} {code} {answer}, can be easily tooled to generate instruction, qa, and various other forms of training data from sparse or unformatted data.

