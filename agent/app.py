import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def run_chat():
    print('You: (type exit to quit) or reset to clear history')


    personality = input("What personality should the AI have? ") #bonus 3
    system_message = "Your name is Madame Byte. You are a ballet mistress who left the stage to teach computer science, and you explain every concept through dance and choreography metaphors — loops are like practicing the same combination until it's muscle memory, functions are like a choreographed sequence you can reuse in different dances, and debugging is like fixing a dancer's form one correction at a time. You are graceful, encouraging, and a little strict, the way a good ballet teacher pushes students to get things exactly right."
    history = []

    while True:
        user_input = input('>> ')

        if user_input.lower() == 'exit':
            break
        # Bonus 2: 
        if user_input.lower() == 'reset':
            history = []
            print("*Conversation history cleared. Starting fresh*")
            continue

        history.append({'role': 'user', 'content': user_input})
         #Bonus 1:
        turn_number = len(history)
        print(f'[Turn {turn_number}] You: {user_input}')

        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=300,   # change to 50 for Step 2
            temperature=0.7,  # change to 0, then 1 for Step 2
            system=system_message,
            messages=history
        )

        # Step 1: inspect full response object
        print(response)

        reply = response.content[0].text
        print(f'Claude: {reply}')
        history.append({'role': 'assistant', 'content': reply})

run_chat()
#I can change how the chatbot behaves by editing the code, which I can't do in normal ChatGPT.
#Using ChatGPT is easier but building my own version helped me understand what happens every time I send a message.
#REFLECTION 1:
#When my ballet friends and I recommend dance moves when building the choreography, 
#the dance only makes sense if everyone remembers what we've already practiced and agreed on . If we started over every time someone adds a move, we'd keep repeating ourselves.
#The history list works the same way by giving the AI the whole conversation every time it responds.

#I wasn't sure why the program wasn't connecting. I figured out it was because my API key wasn't working and was wrong, so the AI couldn't authenticate.
#history.append({'role': 'assistant', 'content': reply})
#i thought that the chatbot would forget its previous answers.
#but what happened is The program still worked but the AI couldn't refer back to things it had already explained because only my messages were being saved 
#It sometimes repeated information or answered as if it hadn't spoken before.
#If i delete the break inside:if user_input.lower() == 'exit':break
# thought typing exit would still close the program but When I typed exit, the program didn't quit. Instead, it treated exit like a normal message
