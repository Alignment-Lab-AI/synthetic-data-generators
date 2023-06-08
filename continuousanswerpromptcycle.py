import openai
import pandas as pd
import streamlit as st
import time

            
def call_openai(api_key, model, prompt, temperature):
    openai.api_key = api_key
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(model=model, messages=messages, max_tokens=250, temperature=temperature)
    return response['choices'][0]['message']['content'].strip()
    
def update_csv(res1, res2, res3, temperature):
    data = {"Response 1": [res1], "Response 2": [res2], "Response 3": [res3], "Temperature": [temperature]}
    df = pd.DataFrame(data)

    try:
        df_existing = pd.read_csv('synthetiqat.csv')
        df_updated = pd.concat([df_existing, df], ignore_index=True)
    except FileNotFoundError:
        df_updated = df

    df_updated.to_csv('synthetiqat.csv', index=False)

def main():
    st.set_page_config(page_title='OpenAI Interaction', layout='wide')

    st.title("Streamlit OpenAI Interface")
    api_key = st.text_input("Enter your OpenAI API Key here:", type='password')
    models = ['gpt-4', 'gpt-4-0314', 'gpt-4-32k', 'gpt-4-32k-0314', 'gpt-3.5-turbo', 'gpt-3.5-turbo-0301']
    model_selected = st.selectbox("Select the Model", model)
    
    
    user_prompt_1 = st.text_input('Prompt 1', '')
    response_1 = st.empty()
    user_prompt_2 = st.text_input('Prompt 2', '')
    response_2 = st.empty()
    user_prompt_3 = st.text_input('Prompt 3', '')
    response_3 = st.empty()

    run_continuous = st.checkbox("Run Continuously?")
    
    temperature = 0.1
    
    if st.button('Create interaction') or run_continuous:
        while True:
            res1 = call_openai(api_key, model_selected, user_prompt_1, temperature)
            res2 = call_openai(api_key, model_selected, res1 + user_prompt_2, temperature)
            res3 = call_openai(api_key, model_selected, res1 + user_prompt_3, temperature)

            response_1.text(res1)
            response_2.text(res2)
            response_3.text(res3)

            update_csv(res1, res2, res3, temperature)
            
            time.sleep(1)
            temperature += 0.1
            if temperature > 0.9:
                temperature = 0.1

            if not run_continuous:
                break
                
if __name__ == "__main__":
    main()
    
    #gpt will respond to a given prompt such as 'give me a single random small reasoning task that can be returned as text" this will pass the resopnse to a second prompt such as 'respond with step by step instructions to complete this task', the second response is passed to a third instance which can be given a prompr such as 'return the outcome of the following chain of reasoning'  all three responses are then recorded as a row on a csv.   alternate uses can be "ask a question a user who has mistaken an ai for a human might ask", "respond to the following question in the manner an ai should properly respond when mistaken for a human","rephrase the following response to provide an example of the way a real human would have responded instead"      script can be run continuously, and will cycle through temeprature settings to provide variations in the event that the prompts dont generate a diverse set of responses.

