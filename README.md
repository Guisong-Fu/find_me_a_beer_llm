# Find a beer using GPT-4 LLM

## Introduction
This project can infer user request on beer. For example, a request can be explict `Find me a beer with ABV greater than 6.0 and brewed year after 2020 June to pair with spicy food`; or it can also be vague, for example `Find me a strong dark beer to pair with steak`.

It basically comes with 4 steps:
1. Infer user request using GPT4. In the prompt for this step, it can handle explicit request, vague request and spelling errors. The output from this step is a list of parameters in JSOn format which will be used in the next step.
2. Make Punk API calls using the parameters generated from the first step, fetch a list of beer options that meet the requirements.
3. Make another GPT4 API call, and let GPT4 choose one beer that caters to the request most.


## How to run:
1. Make sure you have `openai` library installed.
2. Rename `.env_example` to `.env` , and replace with your own openai API key.
3. Open `pure_openai_api.py` and locate `main` function in the bottom, enter your own beer request.
4. (WIP): I also built a webpage using Flask to visualize it.
	a. make sure you have `flask`  installed.
	b. run `web.py` and open `http://127.0.0.1:5000` from your browser.
	c. Enter your request
	d. click `Find me the perfect beer` button
	e. Wait for result to be displayed. Please be patient in this step, it might take several second before all API calls finsish.

## Implementation Explaination:
1. What if the user input is ambiguous or contains spelling mistakes?
- I included instructions in the prompt using `few-shot` techniques, meaning I explictly provided some examples how vague request should be handled, and how typo erros should be fixed.
2. What if the Punk API does not return any results for the given input?
There can be many reasons why Punk API does not return any result for the given input.
	a. It can be the given input is incorrect. Thus we need to enhance and make sure the the input is indeed having the attributes that are accpetable by Punk API.
	B. The user request cannot be inferred well. For example, `Find me a nice beer`. 
	c. It can be the request is too narrow. For example, a request can be "Find a light beer to pair with steak". After the first inference, the parameters should be something like, `{"abv_lt": 4, "food":"steak"}`. But in Punk API or database, it may happen that no light beer is a good pair with steak, so the result will be empty. To address this, I set up a priority order(which is my preference when selecting beers), if the result is empty, then start exclude parameters one by one, and make new Punk API calls. In this case, the second API will be only looking for `{"abv_lt": 4}`.
	d. If in the end, the result is still empty, then randomly pick 5 beers and let LLM to choose the best in the next step.


## What can be further improved?
1. Punk API offers `fuzzy search`, but I guess what it really does is just by doing some `regex search`. For example, in Punk API, if you look for `food: meat`, it will only return `meatball` instead of other meat food. This will result in inperfect recommendation for food pairing. I was thinking about a few options, for example, maybe we can ignore `food` in the first step, and let LLM get all beers and let LLM decide the best food pairing. But I guess that will add more cost, so I didn't do it.
2. Punk API is using different measure system I guess? For example, the EBC range from Punk is from 8 to 600, but the actual EBC range I found on line is something from 2 to 27. This makes LLM cannot decide what EBC value can represent "dark".
3. In terms of vague request, we can provide more examples to LLM. For example, what is considered as "light beer", what is considered as "strong beer".
4. In this example, I'm only using pure openai api. I think, if I use some frameworks, for example `langchain`. I may achive better result and cleaner code. For example, I may use agent to look for more information from the internet about "what is considerred as light or strong beer" and then future make the parametermore precise.
5. OpenAI just released their function calling, it seems useful, but I haven't tried it myself.

