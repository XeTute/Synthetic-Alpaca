# Synthetic-Alpaca
A stubborn & lightweight (for Python at least) one-file pipeline for synthetic data generation. Currently only supports the Alpaca format, but there are plans to roll out versions for other (often-used) JSON formats.  

---
[![image](https://github.com/user-attachments/assets/b6560081-b334-4c73-ac35-ebe3db5bd2b4)](https://huggingface.co/Hamzah-Asadullah/)
---

Example datasets generated using this repo:

- [Hamzah-Asadullah/TA-4k](https://huggingface.co/datasets/Hamzah-Asadullah/TA-4k): TA (short for Tiny-Alpaca) 4k is a dataset with 4,096 rows, each with three columns, for instruction-tuning

If you also published one generated with this script and want it to appear here, just open a pull request ;)

## ⏩ Quickstart
First, download the `main.py` file from this repo. If you don't trust it, please just read the code, it's nothing too complex.  
To quickly get up and running execute one of following command depending on your OS:  
Microsoft Windows:
```cmd
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/XeTute/Synthetic-Alpaca/refs/heads/main/main.py" -OutFile "./main.py"
pip install requests
python main.py
```
or, on Linux:
```cmd
wget "https://raw.githubusercontent.com/XeTute/Synthetic-Alpaca/refs/heads/main/main.py"
pip install requests
python main.py
```

And that's it! Here's an example usage:
```cmd
Enter chat/completions URL: https://ai.xetute.com/v1/chat/completions
Enter API-key for endpoint: 0
Enter model to use: 0
Enter n samples: 1024
Enter max tokens per 8 question: 4096
Enter max tokens per output: 1024
Enter topics (-END- if done; include examples if possible):
Fun facts about Cats in Pakistan
-END-
Enter system prompt (-END- if none):
You are a helpful, accurate & playful assistant.    
-END-
Filename (will append .json): data
```
And that should do the work. If one request fails, the script will automatically retry till it gets a valid response from the server.  

## Star History

<a href="https://www.star-history.com/#XeTute/Synthetic-Data-Generation&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=XeTute/Synthetic-Alpaca&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=XeTute/Synthetic-Alpaca&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=XeTute/Synthetic-Alpaca&type=Date" />
 </picture>
</a>

---

<footer style="margin-top: 3rem; text-align: center; color: #ff5500; max-height: fit-content;">
  <em style="font-size: 1.2rem; text-shadow: 0 0 8px #ff5500;">
    Long live the Islamic Republic of Pakistan; Glory to the Islamic Republic of Pakistan 🇵🇰
  </em>
  <img src="https://upload.wikimedia.org/wikipedia/commons/3/32/Flag_of_Pakistan.svg" alt="Pakistan Flag" style="margin-top: 1rem; border: 2px solid #00ffff; padding: 3px;">
</footer>
