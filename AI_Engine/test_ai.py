import ollama

response = ollama.chat(
    model='gemma3',
    messages=[
        {
            'role': 'user',
            'content': 'Explain CAT VARC in simple words'
        }
    ]
)

print(response['message']['content'])