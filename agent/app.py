import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv() #set up earthing the program needs bfr it can begin 

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# pricing per million tokens (haiku)
#storing variables that can be used through the thingy
INPUT_PRICE_PER_M = 0.25
OUTPUT_PRICE_PER_M = 1.25


def run_chat():
    print('You: (type exit to quit, or /summary to get a recap)')

    
    # this is basically the "personality + rules" i give the agent before it talks to anyone
    #without this , claude has no rules no name no personality and no context to follow 
    system_message = """
    You are Tala, an Interview Coach.

    Your job is to help the user practice and prepare for job interviews.
    When the user shares something (like a worry, a question, or a practice answer),
    you respond like a supportive but honest coach.

    Rules:
    - Always stay focused on interview prep (technical, behavioral, or system design).
    - Always give specific, useful feedback — not just "good job!"
    - Never make up facts about the user's background only use what they tell you


    Scoring rubric (use this when the user gives a practice answer to score): 
    - 5 = Clear, structured, confident, specific examples
    - 4 = Good answer, missing a little detail or structure
    - 3 = Okay, but vague or unfocused
    - 2 = Weak structure, hard to follow
    - 1 = Doesn't answer the question asked 

    Response format:
    - Start with a one-sentence summary of what the user said.
    - Then give your response (feedback, advice, or a question).
    - If the user gave a practice answer, score it 1-5 with a short reason.
    - End with one follow-up question.
    """

    history = [] 
    total_input_tokens = 0
    total_output_tokens = 0
    scores = []  #  keep track of every score 

    # ask the user what they're working on today, store it,
    # and stick it into every message so the agent doesn't forget
    goal = input('Before we start — what is your goal for this session? >> ')
    #repeatdly perform main task until the stopping condition is met 
    while True:
        user_input = input('>> ')
        if user_input.strip() == '': #stops an empty enter press from crashing the API call
            print("(type something, or 'exit' to quit)")
            continue
        if user_input.lower() == 'exit':
            break
        if user_input.strip().lower() == '/summary': #lets the user get a recap without restarting the whole program 
            # we ask Claude itself to summarize the convo so far
            summary_prompt = "Please give a structured summary of everything we've discussed in this session so far, organized by topic."
            history.append({'role': 'user', 'content': summary_prompt})
            #send data to an external service model and recieve a respone 
            response = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=300,
                temperature=0.7,
                system=system_message,
                messages=history
            )

            reply = response.content[0].text
            print(f'\n--- SUMMARY ---\n{reply}\n---------------\n')
            history.append({'role': 'assistant', 'content': reply})
            continue  # skip the rest of the loop
        #we need to keep on reminding the claude of our goal so that it doesnt lose focus after a long cha
        message_with_goal = f"(session goal: {goal}) {user_input}"
        history.append({'role': 'user', 'content': message_with_goal})

        print('History so far:', history)

        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=300,
            temperature=0.7,
            system=system_message,
            messages=history
        )

        print(response)

        # get the actual text reply out of the response BEFORE using it
        reply = response.content[0].text
        print(f'Claude: {reply}')
        history.append({'role': 'assistant', 'content': reply})

        
        import re #regex = a tool for finding patterns in text, not just exact words
        score_match = re.search(r'\b([1-5])\s*/\s*5\b|\bScore:\s*([1-5])\b', reply)
        if score_match:
            found_score = int(score_match.group(1) or score_match.group(2))
            scores.append(found_score)

        #token usage per turn 
        in_tokens = response.usage.input_tokens
        out_tokens = response.usage.output_tokens
        turn_total = in_tokens + out_tokens
        print(f'[Tokens used — In: {in_tokens} | Out: {out_tokens} | Total: {turn_total}]')

        # running totals across the whole chat 
        total_input_tokens += in_tokens
        total_output_tokens += out_tokens
        running_total = total_input_tokens + total_output_tokens
        print(f'[Running total — In: {total_input_tokens} | Out: {total_output_tokens} | Total: {running_total}]')

        # cost estimate 
        turn_cost_cents = (in_tokens * INPUT_PRICE_PER_M + out_tokens * OUTPUT_PRICE_PER_M) / 1_000_000 * 100
        running_cost_cents = (total_input_tokens * INPUT_PRICE_PER_M + total_output_tokens * OUTPUT_PRICE_PER_M) / 1_000_000 * 100
        print(f'[Estimated cost — This turn: {turn_cost_cents:.4f}¢ | Conversation total: {running_cost_cents:.4f}¢]')

    # when the user types "exit" show the average score if we tracked any
    if scores:
        average_score = sum(scores) / len(scores)
        print(f'\nYour average interview answer score this session: {average_score:.1f}/5 (based on {len(scores)} scored answers)')
    else:
        print('\nNo scored answers this session.')


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

#lab2 + reflections 
#Input tokens are the text, system prompts, and files you send into the AI, while output tokens are the text the model generates in response 
#They don't save your chat history on their end to keep things fast and secure. So, if you don't send the whole chat history every time, the API completely forgets what you were talking about two seconds ago
#It’s like ordering extra toppings on a burgrt a build-your-own joint, but they charge you for every single topping on the touchpad every time you take another bite
#You start with just cheese (cheap), but then you add sauces (+ $0.50), then mushrooms (+ $0.50), then jalapenos (+ $0.50). By your fourth bite, you aren't just paying for the new jalapeno; you are being re-charged for the cheese, pepperoni, and mushrooms all over again
#You have to watch that total cost closely because every bite you take of that same burger gets  more expensive.
#i thought that the AI will "forget" everything it just said to me (history.append({'role': 'assistant', 'content': reply}))
#The next time i type a message, the API only receives my  prompts without its own prior responses.
#but turns out Because i amn't saving Claude's responses to history
#  the conversation history becomes a one-sided monologue of just my inputs.
# my input_tokens count will go much slower because iamnot paying to re-send Claude's long paragraphs back to the server
# but Claude will act incredibly confused because it has no memory of its own previous replies
#thought the code would run fine and print Claude's response, maybe just duplicating it since there are two print statements back-to-back
#The code crashes with a NameError: name 'reply' is not defined
#reliazed that python reads code line-by-line from top to bottom

#lab3 : 
#i got the rubic scoring from google (to help scoring well)
# A compass never argues with the traveler
# It quietly points north.
# Every step is still their own.
# The direction was always there
#Removing system=system_message :
# the code is still going to work but it  wont know that u are a student and it will have a dead vibe 
# if i deleted one of the rules for example :"always give specific feedback" 
# the student that inputs wont always get it and if i didnt say "end with a question each time"
#then the ai will just give u the answer and not speak anything else 
#for the respone thing, if i change of them to "always answer with essays"
# it resulted in a massive wall of text that crashed my termial 
#bug diary: for me its the issue of the API key, at first i thought that its wrong because i copied it wrong 
#but turned out th API key itself was wrong and resulted in an authentication error
#i was very confused on how i had to add this two times in my code but turns out its like having two different buttons that both send a message to claude but each button sends a different kind of message 
#so basically i am choosing which one to call based on what the user typed 
#the system prompet is  like WAZE ,  it doesnt drive the car but it makes the AI navigiate it to places