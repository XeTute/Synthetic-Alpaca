#!/usr/bin/env python3
import requests
import json
import ast
import re
import sys
import logging
import time

# Set up fancy logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

def extract_list(response_text):
    """
    Extract a Python list from the response text.
    This function removes common code block markers and then
    attempts to locate the list by finding the first '[' and the last ']'.
    If the resulting list has one multi-line string element,
    it splits that string into individual inputs.
    """
    # Remove common code block markers if present
    cleaned_text = re.sub(r'```(?:python|json)?', '', response_text).strip()
    
    # Find the first '[' and the last ']' to extract the list portion
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
    
    # If the list contains a single multi-line string, split it into separate inputs.
    if len(inputs) == 1 and isinstance(inputs[0], str) and "\n" in inputs[0]:
        inputs = [inp.strip() for inp in inputs[0].split('\n') if inp.strip()]
    return inputs

def main():
    # Get and validate user input
    try:
        n = int(input("How many samples do you need? "))
        if n <= 0:
            logging.error("Number of samples must be positive.")
            sys.exit(1)
    except ValueError:
        logging.error("Invalid input for number of samples.")
        sys.exit(1)

    topics = input("Enter topics (examples: Questions about STEM, Greetings(\"Hi\", \"Sup\"), et cetera): ").strip()
    if not topics:
        logging.error("Topics cannot be empty.")
        sys.exit(1)

    try:
        context_length = int(input("How many k context length does your endpoint support? "))
        context_length *= 1024
    except ValueError:
        logging.error("Invalid input for context length.")
        sys.exit(1)

    # API configuration
    url = "https://ai.xetute.com/v1/chat/completions/"
    headers = {"Content-Type": "application/json"}

    all_inputs = []
    chunk_index = 0

    # Keep requesting chunks until we have at least n unique inputs.
    while True:
        unique_inputs = list(dict.fromkeys(all_inputs))
        if len(unique_inputs) >= n:
            break

        chunk_index += 1
        missing = n - len(unique_inputs)
        # Request either 8 inputs per chunk or only the number still needed.
        chunk_size = 8 if missing >= 8 else missing

        input_prompt = (
            f"Generate exactly {chunk_size} unique inputs about {topics}. \n"
            f"Return ONLY a list formatted like: [\"input1\", \"input2\", ...]"
        )

        # Retry indefinitely until we can successfully parse the returned list.
        while True:
            try:
                response = requests.post(url, json={
                    "max_completion_tokens": context_length,
                    "messages": [{"role": "user", "content": input_prompt}]
                }, headers=headers).json()
                if "error" in response:
                    logging.error(f"API Error: {response['error']['message']}")
                    time.sleep(1)
                    continue
                inputs_text = response['choices'][0]['message']['content']
                current_inputs = extract_list(inputs_text)
                break  # Successfully parsed the inputs; exit retry loop.
            except Exception as e:
                logging.error(f"Parsing failed: {e}")
                logging.info("Raw response content:")
                logging.info(inputs_text if 'inputs_text' in locals() else "No response received.")
                logging.info("Retrying this chunk...")
                time.sleep(1)

        all_inputs.extend(current_inputs)
        unique_inputs = list(dict.fromkeys(all_inputs))
        logging.info(
            f"Chunk {chunk_index} processed. Requested {chunk_size} inputs, "
            f"received {len(current_inputs)} inputs. Unique inputs so far: {len(unique_inputs)}."
        )

    # Ensure exactly n unique inputs
    unique_inputs = list(dict.fromkeys(all_inputs))
    if len(unique_inputs) > n:
        logging.info(f"Received more unique inputs than requested ({len(unique_inputs)} instead of {n}). Using first {n} inputs.")
        unique_inputs = unique_inputs[:n]

    # Generate Q&A pairs (input-output pairs) using each input, with progress logging
    dataset = []
    total = len(unique_inputs)
    logging.info("Starting generation of input-output pairs...")
    for i, inp in enumerate(unique_inputs, start=1):
        while True:
            try:
                q_response = requests.post(url, json={
                    "max_completion_tokens": context_length,
                    "messages": [
                        {"role": "system", "content": "You are a helpful AI Assistant."},
                        {"role": "user", "content": inp}
                    ]
                }, headers=headers).json()
                output = q_response['choices'][0]['message']['content']
                break
            except Exception as e:
                logging.error(f"Error processing input: {inp} - {e}. Retrying...")
                time.sleep(1)

        dataset.append({
            "instruction": "You are a helpful AI Assistant.",
            "input": inp,
            "output": output
        })
        progress = (i / total) * 100
        logging.info(f"Processed sample {i}/{total} ({progress:.2f}%)")

    # Save the resulting dataset to data.json
    if dataset:
        try:
            with open('data.json', 'w') as f:
                json.dump(dataset, f, indent=2)
            logging.info(f"Successfully generated {len(dataset)} samples in data.json")
        except Exception as e:
            logging.error(f"Error saving file: {e}")
    else:
        logging.error("No valid samples generated.")

if __name__ == '__main__':
    main()
