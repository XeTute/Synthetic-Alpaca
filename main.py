import requests
import json
import re
import ast

chunksize = 8

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

    seen = set()
    deduped = []
    for item in inputs:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    inputs = deduped

    return inputs

def generate(endpoint, model, key, msg, temperature, maxlength):
    payload = { "temperature": temperature, "max_completion_tokens": maxlength, "messages": msg, "model": model }
    headers = { "Content-Type": "application/json", "Authorization": f"Bearer {key}" }
    try:
        response = requests.post(endpoint, json=payload, headers=headers).json()
        return response["choices"][0]["message"]["content"]
    except:
        print("\r>> Failed getting any response from endpoint; re-trying...", end="")
        return generate(endpoint, model, key, msg, temperature, maxlength)

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
        prompt = f"Generate {chunksize} highly diverse/versatile text-inputs and wrap them strictly into a Python list ([\"input\", ...]), each relevant to:\n{topics}"
        if (len(systemprompt) > 0):
            msg.append({ "role": "system", "content": systemprompt } )
        msg.append({ "role": "user", "content": prompt })

        inputs = extract_list(generate(endpoint, model, apikey, msg, 1, maxinput))
        return inputs
    except:
        print("\r>> Failed to get inputs, re-trying...")
        return getinputs(chunksize, topics, systemprompt, endpoint, model, apikey, maxinput)

def inline(string):
    return string.replace('\n', "\\n")

def maxlength(string, max):
    if (len(string) > max):
        string = string[:max - 3] + "..."
    return string

def main():
    endpoint = str(input(">_ Enter chat/completions URL: "))
    apikey = str(input(">_ Enter API-key for endpoint: "))
    model = str(input(">_ Enter model to use: "))
    samples = int(input(">_ Enter n samples: "))
    maxinput = int(input(f">_ Enter max tokens per {chunksize} question: "))
    maxoutput = int(input(">_ Enter max tokens per output: "))
    topics = lineinput(">_ Enter topics (-END- if done; include examples if possible):")
    systemprompt = lineinput(">_ Enter system prompt (-END- if none):")
    saveat = str(input(">_ Filename (will append .json): "))

    data = []
    inputs = []
    outputs = []
    print(">> Collecting \"input\" column...")
    while len(inputs) < samples:
        needed = samples - len(inputs)
        current_chunk = min(chunksize, needed)
        new_batch = getinputs(current_chunk, topics, "You generate a Python list for message inputs.", endpoint, model, apikey, maxinput)

        unique_new = [item for item in new_batch if item not in inputs]
        unique_new = unique_new[:needed]
        inputs.extend(unique_new)
        print(f"\r>> Collected {len(inputs)}/{samples} inputs.", end="")
    
    if (len(inputs) > samples):
        inputs = inputs[:samples]
        print(f"\n>> Note: Got {len(inputs)} samples, removed {len(inputs) - samples} samples.", end="")
    print("\n>> Collected inputs.")

    print(">> Collecting \"output\" column...")
    for x in range(samples):
        print(f">> Input: {inline(maxlength(inputs[x], 80))}")
        msg = []
        if (len(systemprompt) > 0):
            msg.append({ "role": "system", "content": systemprompt })
        msg.append({ "role": "user", "content": inputs[x] })

        outputs.append(generate(endpoint, model, apikey, msg, 0.7, maxoutput))
        data.append({ "instruction": systemprompt, "input": inputs[x], "output": outputs[x] })
        print(f">> Output: {inline(maxlength(outputs[x], 80))}\n--- Added sample {x} / {samples} to list.")
    print(">> Collected outputs.")

    saveat = saveat + ".json"
    with open(saveat, 'w') as f:
        json.dump(data, f, indent=1)
    print(f">> Done; saved through {saveat}")

if __name__ == '__main__':
    main()
