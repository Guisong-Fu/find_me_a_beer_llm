import os
import time
import openai
from dotenv import load_dotenv, find_dotenv
import requests
import json

_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')

PUNK_API_BASE_URL = 'https://api.punkapi.com/v2/beers'


def get_completion(prompt, model="gpt-4", temperature=0.0, max_retries=5):
    base_delay = 5
    messages = [{"role": "system", "content": "You are an assistant that only speaks JSON. Do not write normal text"},
                {"role": "user", "content": prompt}]

    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message["content"]
        except openai.error.ServiceUnavailableError:
            delay = base_delay * (2 ** attempt)
            print(f"The server is overloaded or not ready yet. Retrying in {delay} seconds...")
            time.sleep(delay)

    raise Exception("All retries failed. The server is not responding.")


def infer_beer_request(beer_request_text):
    beer_request_prompt = f"""
    You are tasked with interpreting the following user request, infer the preferences where possible, and then structuring the information into JSON format:
    
    Here is the request text is delimited by triple backticks.
    
    ```{beer_request_text}```
    
    If you think there is any spelling or typo error, correct those errors first and proceed with the next steps.
    For example, the original request text is `Find me a strogn beer with AVB great than 10.0`, then it's very likely that the correct request should be `Find me a strong beer with ABV great than 10.0`.
    So in this case, correct the error and go with `Find me a strong beer with ABV great than 10.0` in the following steps.
        
    The user request may contain preferences regarding the following beer attributes:
    1. ABV (Alcohol by Volume): Ranges from 0.5 to 55. The user could specify 'ABV less than X' or 'ABV greater than X', parse to "abv_lt": X or "abv_gt": X.
    2. IBU (International Bitterness Units): Ranges from 8 to 1157. The user could specify a preferred range, parse to "ibu_lt": X or "ibu_gt": X.
    3. EBC (European Brewery Convention): Ranges from 8 to 600. The user could specify a preferred range, parse to "ebc_lt": X or "ebc_gt": X. For general terms, if the user says 'dark beer', interpret it as "ebc_gt": 40.
    4. Yeast: The user could specify a preferred yeast type, parse to "yeast": "yeast type".
    5. Brewed Year: The user could specify a 'brewed before' or 'brewed after' date in the format mm-yyyy, parse to "brewed_before": "mm-yyyy" or "brewed_after": "mm-yyyy".
    6. Hops: The user could specify a preferred hop, parse to "hops": "hop type".
    7. Malt: The user could specify a preferred malt, parse to "malt": "malt type".
    8. Food: The user could specify a preferred food pairing, try to infer the most relevant food type with only one or two words, parse to "food": "food type", if it is two words, use understore `_` to chain it up, for example, `fried chicken` should `fried_chicken`. You can exclude `food` word, for example, if the request is `find a beer to pair with spicy food`, you can simply return `spicy`, no need to return `spicy_food`.    

    If the request is vague, meaning the request does not include a specific requirement on the above attributes, for example, "Find a light beer". Then, firstly you will infer what the request could potentially mean, seconly, use the above attributes and its values ranges to represent the request. 
    For example, the request may say "Find me a dark strong beer", here the request does not specify any requirements on ABV/IBU/EBV, but if you think of it, you can easily find out, "dark" is revelant to EBC and "strong" is revelant to ABV. 
    Given the EBC range is from 8 to 600 and ABV range is 0.5 to 55, the request can be then converted to something like `ABV greater than 10 and EBC greater than 200`.
    
    Please process the request and provide the extracted attributes in JSON with the attributes only in this list of attributes `['food', 'hops', 'malt', 'yeast', 'brewed_after', 'brewed_before', 'ebc_gt', 'ebc_lt', 'ibu_gt', 'ibu_lt', 'abv_gt', 'abv_lt']`.
    If none of the above attributes can be extracted from the user's request, your output should be an empty JSON object: {{}}. Do NOT make up or include any attributes or keys that are not listed above. For example, creating an output like `{{"test": "test"}}` is strictly not allowed as `test` is not one of the listed attributes. Remember, if you can't extract the data based on the list above, return an empty JSON object: {{}}.
    
    No additional text or explanation is required in the output no matter if the result is empty or not.
    
    For example, if a user says 'Find me a strong beer that was brewed before May 2020 with an ABV above 5', you should return:
    
    {{"abv_gt":5, "brewed_before": "05-2020"}}
    
    A note: '*_lt' and '*_gt' in ABV/IBU/EBC refers to strictly less than or greater than. If you want to include 'alcohol-free' beer (which has an ABV less than 0.5), you should specify "abv_lt": 0.6 to include all beers with an ABV of 0.5.
    
    """

    return get_completion(beer_request_prompt)


def is_json(raw):
    try:
        _ = json.loads(raw)
    except ValueError as e:
        return False
    return True


def get_random_beers():
    result = []
    for _ in range(3):
        time.sleep(1)
        result = result + requests.get(PUNK_API_BASE_URL + "/random").json()

    return result


def calling_punk_api(beer_request_json):
    time.sleep(1)

    if not is_json(beer_request_json):
        print("Beer Request Prompt returns more wrong format, return random beers")
        return get_random_beers()

    if len(json.loads(beer_request_json)) == 0:
        print("The request cannot be inferred, return random beers")
        return get_random_beers()

    params = '&'.join(f'{key}={value}' for key, value in json.loads(beer_request_json).items())
    puk_api_url = PUNK_API_BASE_URL + "?per_page=5&" + params

    print("Generated API URL:", puk_api_url)  # Step 3: Print the generated API URL

    punk_api_response = requests.get(puk_api_url)

    if punk_api_response.status_code == 200:
        return punk_api_response.json()

    else:
        print("Punk API does not response correctly, return random beers")
        return get_random_beers()


def remove_keys_in_order(json_str):
    json_dict = json.loads(json_str)

    # This is the order of importance to me when I choose beers :)
    keys = ['food', 'hops', 'malt', 'yeast', 'brewed_after', 'brewed_before', 'ebc_gt', 'ebc_lt', 'ibu_gt', 'ibu_lt',
            'abv_gt', 'abv_lt']
    for key in keys:
        if key in json_dict:
            del json_dict[key]
            json_str = json.dumps(json_dict)
            return json_str


def extract_info(json_str):
    data = json.loads(json_str)

    keys = ['name', 'tagline', 'first_brewed', 'description', 'image_url', 'abv', 'ibu', 'target_fg', 'target_og',
            'ebc', 'ingredients', 'food_pairing']

    # Construct a new dictionary that only contains the keys in the provided list
    extracted_data = {k: data[k] for k in keys if k in data}

    # Convert the new dictionary back into a JSON string
    extracted_json_str = json.dumps(extracted_data)

    return extracted_json_str


def parse_punk_api(punk_response_json, beer_request_prompt_response):
    while len(punk_response_json) < 1:
        beer_request_prompt_response = remove_keys_in_order(beer_request_prompt_response)
        punk_response_json = calling_punk_api(beer_request_prompt_response)

    beer_options = []
    for beer_option in punk_response_json:
        extracted_json_str = extract_info(json.dumps(beer_option))
        beer_options.append(extracted_json_str)

    return beer_options


def recommend_beer_request(beer_request_text, beer_options):
    final_answer_prompt = f"""
    You are tasked with choosing the beer that caters to the request most from the list of beer options. 
    
    The beer request from the user is the following: 
    ```{beer_request_text}```
    
    The list of beer options is in format with a list of JSON records:
    ```{beer_options}``` 
    
    Perform the following actions, no need to include your reasoning in the output.
    1 - Interpret what user wants according to the request
    2 - Pick one beer that caters to the request most from the list of beer options. If no good match can be found, just randomly pick one from the beer options. You have to return one beer, you cannot leave it empty. 
    3 - Think of why you think this would be the best choice
    
    Output should be in this format:
    
    {{
        "name": Take name from the option that you think would be the best,
        "title": Take title from the option that you think would be the best,
        "first_brewed": Take first_brewed from the option that you think would be the best,
        "abv": Take abv from the option that you think would be the best,
        "ibu": Take ibu from the option that you think would be the best,,
        "ebc": Take ebc from the option that you think would be the best,,
        "food_pairing": Take food_pairing from the option that you think would be the best,,
        "image_url": Take image_url from the option that you think would be the best,
        "recommendation_text": Write down a short recommendation to the customer why you would recommend this beer. 
    }}
    
    """

    return final_answer_prompt


def find_beer(beer_request_text):
    beer_request_prompt_response = infer_beer_request(beer_request_text)
    print("Beer Request Inference:", beer_request_prompt_response)

    punk_response_json = calling_punk_api(beer_request_prompt_response)

    beer_options = parse_punk_api(punk_response_json, beer_request_prompt_response)
    print("Beer Options: ", beer_options)

    return get_completion(recommend_beer_request(beer_request_text, beer_options), temperature=0.5)


if __name__ == '__main__':

    beer_request_text = f"""
    ENTER YOUR OWN BEER REQUEST  
    """

    print(find_beer(beer_request_text))
