import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
INPUT_PRICE_PER_M = 0.25
OUTPUT_PRICE_PER_M = 1.25
def run_chat():
    print('You: (type exit to quit)')
    system_message = "Your name is Alex. You are a helpful and friendly assistant who helps students learn about technology and computer science. You explain things clearly and always encourage curiosity."
    history = []
    total_input_tokens = 0
    total_output_tokens = 0
    while True:
        user_input = input('>> ')

        if user_input.lower() == 'exit':
            break

        history.append({'role': 'user', 'content': user_input})

        # Step 3: see full history sent to API
        print('History so far:', history)

        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=300,   # change to 50 for Step 2
            temperature=0.7,  # change to 0, then 1 for Step 2
            system=system_message,
            messages=history
        )

        # Step 1: inspect full response object
        print(response)
        print(f'Claude: {reply}')
        history.append({'role': 'assistant', 'content': reply})
        reply = response.content[0].text
        print(f'Claude: {reply}')
        history.append({'role': 'assistant', 'content': reply})
 
        # --- Token usage for this turn ---
        in_tokens = response.usage.input_tokens
        out_tokens = response.usage.output_tokens
        turn_total = in_tokens + out_tokens
 
        print(f'[Tokens used — In: {in_tokens} | Out: {out_tokens} | Total: {turn_total}]')
 
        # --- Bonus 2: running conversation totals ---
        total_input_tokens += in_tokens
        total_output_tokens += out_tokens
        running_total = total_input_tokens + total_output_tokens
 
        print(f'[Running total — In: {total_input_tokens} | Out: {total_output_tokens} | Total: {running_total}]')
 
        # --- Bonus 3: cost estimation (in cents) ---
        turn_cost_cents = (in_tokens * INPUT_PRICE_PER_M + out_tokens * OUTPUT_PRICE_PER_M) / 1_000_000 * 100
        running_cost_cents = (total_input_tokens * INPUT_PRICE_PER_M + total_output_tokens * OUTPUT_PRICE_PER_M) / 1_000_000 * 100
 
        print(f'[Estimated cost — This turn: {turn_cost_cents:.4f}¢ | Conversation total: {running_cost_cents:.4f}¢]')
 
run_chat()

#REFLECTION 1:
#When my ballet friends and I recommend dance moves when building the choreography, 
#the dance only makes sense if everyone remembers what we've already practiced and agreed on . If we started over every time someone adds a move, we'd keep repeating ourselves.
#The history list works the same way by giving the AI the whole conversation every time it responds.

#history.append({'role': 'assistant', 'content': reply})
#i thought that the chatbot would forget its previous answers.
#but what happened is The program still worked but the AI couldn't refer back to things it had already explained because only my messages were being saved 
#It sometimes repeated information or answered as if it hadn't spoken before.
#If i delete the break inside:if user_input.lower() == 'exit':break
# thought typing exit would still close the program but When I typed exit, the program didn't quit. Instead, it treated exit like a normal message

#I wasn't sure why the program wasn't connecting. I figured out it was because my API key wasn't working and was wrong, so the AI couldn't authenticate.

#lab2 
#Input tokens are the text, system prompts, and files you send into the AI, while output tokens are the text the model generates in response 
#They don't save your chat history on their end to keep things fast and secure. So, if you don't send the whole chat history every time, the API completely forgets what you were talking about two seconds ago
