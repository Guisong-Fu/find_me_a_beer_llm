# Find a Beer Using GPT-4 Language Model

## Introduction
This project can interpret a user's request for a beer. For example, a request can be explicit, such as `Find me a beer with an ABV greater than 6.0, brewed after June 2020, and suitable for pairing with spicy food`. Alternatively, it can be vague, such as `Find me a strong, dark beer to pair with a steak`.

The processing of the user request involves 3 steps:
1. Use GPT-4 to infer the user's request. In this step, the model can handle explicit requests, vague requests, and spelling errors. The output is a JSON-formatted list of parameters to be used in the next step.
2. Use the parameters from the first step to make API calls to Punk API. This retrieves a list of beer options that meet the user's requirements.
3. Make another call to the GPT-4 API, allowing the model to select the beer that best suits the user's request.

## How to Run the Program:
1. Ensure you have the `openai` library installed.
2. Rename `.env_example` to `.env`, and replace the placeholder with your own OpenAI API key.
3. Open `pure_openai_api.py` and locate the `main` function at the bottom. Enter your beer request, then run :)
4. A webpage has also been built using Flask to visualize the results:
	- Ensure you have the `flask` library installed.
	- Run `web.py` and navigate to `http://127.0.0.1:5000` in your browser.
	- Enter your request in the provided field.
	- Click the `Find me the perfect beer` button.
	- Wait for the result to be displayed. Please be patient as it might take several seconds for all API calls to complete.

## Implementation Explanation:
1. How does the model handle ambiguous user inputs or spelling mistakes?
- Instructions are included in the prompt using the few-shot learning technique. For example, it provides explicit examples of how vague requests should be handled, and how spelling errors should be fixed.

2. What happens if the Punk API does not return any results for a given input?
- There are several reasons why the Punk API might not return any results for a given input:
	1. The parameters used in Punk API might be incorrect. Thus, we need to ensure that the input contains acceptable attributes for the Punk API, meaning we need to make the output from the first GPT4 is always in the format we want. 
	2. The user request might not be sufficiently clear. For example, `Find me a nice beer`, which no attributes can be used to represent such request.  
	3. The request might be too specific. For example, a request like `Find me a light beer to pair with a steak`. After the first inference, the parameters should be something like, `{"abv_lt": 4, "food":"steak"}`. But it may be that no light beer pairs well with steak in the Punk API or database, hence the result would be empty. To address this, a priority order is set up, and if the result is empty, parameters are excluded one by one, triggering new API calls. In this case, the second API call will be only looking for `{"abv_lt": 4}`.
	4. If no results are found after all these steps, the model will randomly pick 5 beers and let the language model choose the best in the next step, which ensures we will return something at least.

## Areas for Further Improvement:
1. Even though Punk API offers fuzzy search, but it seems to only carry out regex search. For instance, if you search for `food: meat` in the Punk API, it will only return `meatball` instead of other types of meat dishes. This could result in imperfect recommendations for food pairing. Various options can be explored to address this. For example, we can completely ignore food pairing in the first step, and let LLM read all beers and then further choose the beer that matches food pairing requirement.
2. It seems the Punk API uses a different measuring system. For instance, the EBC range provided by Punk API is from 8 to 600, while the actual EBC range found online is from 2 to 79. This discrepancy makes it difficult for the language model to determine what EBC value represents "dark".
3. More examples can be provided to the language model regarding vague requests. For instance, what is considered a "light beer", or a "strong beer".
4. In this project, I only use the pure OpenAI API. However, I believe that better results and cleaner code could be achieved with certain frameworks, such as Langchain. For instance, an agent could be used to gather more information from the internet about what is considered a light or strong beer, which could help make the parameters more precise.
5. OpenAI has recently released their function calling capabilities, which seem useful, but I haven't tried it myself yet.
6. Prompt can be further improved to reduce cost. 
