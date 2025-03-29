import requests
import time
import json
import re
import ast

chunksize = 2
alpaca = False
convlength = 16

def extract_list(response_text):
    cleaned_text = re.sub(r'```(?:python|json)?', '', response_text).strip()
    start = cleaned_text.find('[')
    end = cleaned_text.rfind(']')
    if start == -1 or end == -1 or end < start:
        raise ValueError("No valid list found in the response.")

    list_str = cleaned_text[start:end+1]
    try:
        inputs = ast.literal_eval(list_str)
    except Exception as e:
        raise ValueError("Error parsing list from response.") from e

    if not isinstance(inputs, list):
        raise ValueError("Parsed object is not a list.")

    if len(inputs) == 1 and isinstance(inputs[0], str) and "\n" in inputs[0]:
        inputs = [inp.strip() for inp in inputs[0].split('\n') if inp.strip()]

    inputs = [item for item in inputs if isinstance(item, str)]

    seen = set()
    deduped = []
    for item in inputs:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    inputs = deduped

    return inputs

pollseed = 0
def generate(endpoint, model, key, msg, temperature, maxlength, recursion=True):
    global pollseed
    payload = { "temperature": temperature, "max_completion_tokens": maxlength, "messages": msg, "model": model }
    headers = { "Content-Type": "application/json", "Authorization": f"Bearer {key}" }
    
    try:
        if endpoint == "https://text.pollinations.ai/openai":
            response = requests.post(endpoint + f"?seed={pollseed}", json=payload, headers=headers)
            response.raise_for_status()
            pollseed += 1
        else:
            response = requests.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    except Exception as e:
        print(f"\r>> Error: {e}")
        if not recursion:
            return None
        
        print("\r>> Failed getting any response from endpoint; re-trying...", end="")
        while True:  # Fix recursion crashes
            time.sleep(2)
            response = generate(endpoint, model, key, msg, temperature, maxlength, False)
            if response is not None:
                print("\r")
                return response

def lineinput(prompt):
    val = ""
    buffer = ""

    print(prompt)
    while True:
        buffer = str(input(">_ "))
        if (buffer == "-END-"):
            break
        else:
            val = val + buffer + '\n'
    return val

def getinputs(chunksize, topics, systemprompt, endpoint, model, apikey, maxinput):
    try:
        msg = []
        prompt = f"Generate {chunksize} highly diverse/versatile text-inputs and wrap them strictly in a Python list ([\"input\", ...]), each relevant to:\n{topics}"
        if (len(systemprompt) > 0):
            msg.append({ "role": "system", "content": systemprompt } )
        msg.append({ "role": "user", "content": prompt })

        inputs = extract_list(generate(endpoint, model, apikey, msg, 1.3, maxinput, True))
        return inputs
    except:
        print("\r>> Failed to get inputs, re-trying...", end="")
        return getinputs(chunksize, topics, systemprompt, endpoint, model, apikey, maxinput)

def inline(string):
    return string.replace('\n', "\\n")

def maxlength(string, max):
    if (len(string) > max):
        string = string[:max - 3] + "..."
    return string

def inverseroles(conversation):
    for msg in conversation:
        if msg["role"] == "user":
            msg["role"] = "assistant"
        elif msg["role"] == "assistant":
            msg["role"] = "user"
    return conversation

def main():

    endpoint = str(input(">_ Enter chat/completions URL: "))
    apikey = str(input(">_ Enter API-key for endpoint: "))
    model = str(input(">_ Enter model to use: "))
    samples = int(input(">_ Enter n samples: "))
    maxoutput = int(input(">_ Enter max tokens per response: "))
    topics = lineinput(">_ Enter topics (-END- if done; include examples if possible):")
    systemprompt = lineinput(">_ Enter system prompt (-END- if none):")
    saveat = str(input(">_ Filename (will append .json): "))

    data = []
    inputs = []

    print(">> Collecting inputs...", end="")
    while len(inputs) < samples:
        needed = samples - len(inputs)
        new_batch = getinputs(
            min(chunksize, needed),
            topics,
            "You generate a Python list for message inputs.\nPython lists are structured like [string, ...].",
            endpoint, model, apikey, maxoutput
        )

        unique_new = [item for item in new_batch if item not in inputs]
        unique_new = unique_new[:needed]
        inputs.extend(unique_new)
        print(f"\r>> Collected {len(inputs)}/{samples} inputs.", end="")

    if (len(inputs) > samples):
        inputs = inputs[:samples]
        print(f"\n>> Note: Got {len(inputs)} samples, removed {len(inputs) - samples} samples.", end="")

    print("\n>> Collected inputs.")

    if alpaca:
        outputs = []

        print(">> Starting generation for Alpaca-format")
        print(">> Collecting \"output\" column...")
        for x in range(samples):
            print(f">> Input: {inline(maxlength(inputs[x], 80))}")

            msg = []
            if (len(systemprompt) > 0):
                msg.append({ "role": "system", "content": systemprompt })
            msg.append({ "role": "user", "content": inputs[x] })

            outputs.append(generate(endpoint, model, apikey, msg, 0.7, maxoutput, True))
            data.append({ "instruction": systemprompt, "input": inputs[x], "output": outputs[x] })
            print(f">> Output: {inline(maxlength(outputs[x], 80))}")
            print(f">> Added sample {x} / {samples} to list.")
        print(">> Collected outputs.")

    else:   

        print(f">> Starting generation for ShareGPT-format")
        for x in range(samples):
            conversation = [ { "role": "system", "content": systemprompt }, { "role": "user", "content": inputs[x] } ]

            while len(conversation) < convlength:
                conversation.append({ "role": "assistant" if (conversation[-1]["role"] == "user") else "user", "content": generate(endpoint, model, apikey, conversation, 1, maxoutput, True) })
                conversation = inverseroles(conversation)

            print(f"\r>> Generated {x + 1}/{samples} conversations.", end="")
            data.append(conversation)

    saveat = saveat + ".json"
    with open(saveat, 'w') as f:
        json.dump(data, f, indent=2)
    print(f">> Done; saved through {saveat}")

if __name__ == '__main__':
    main()
