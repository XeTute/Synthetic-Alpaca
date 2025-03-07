# Synthetic-Data-Generation
A stubborn & lightweight (for Python at least) one-file pipeline for synthetic data generation. Currently only supports the Alpaca format, but there are plans to roll out versions for other (often-used) JSON formats.  

---
![image](https://github.com/user-attachments/assets/9f42b1ed-9000-4538-aba0-7d89645d5050)
---

Example datasets generated using this repo:

- [XeTute/Eastern-Alpaca-14k](https://huggingface.co/datasets/XeTute/Eastern-Alpaca-14k): 14 * 1024 instruction, input & output rows

If you also published one generated with this script and want it to appear here, just open a pull request ;)

## ⏩ Quickstart
First, download the `main.py` file from this repo. If you don't trust it, please just read the code, it's nothing too complex.  
To quickly get up and running execute one of following command depending on your OS:  
Microsoft Windows:
```cmd
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/XeTute/Synthetic-Data-Generation/refs/heads/main/main.py" -OutFile "./main.py"
pip install requests
python main.py
```
or, on Linux:
```cmd
wget "https://raw.githubusercontent.com/XeTute/Synthetic-Data-Generation/refs/heads/main/main.py"
pip install requests
python main.py
```

And that's it! Here's an example usage:
```cmd
Enter the OpenAI-Compatible completions endpoint link (or /v1/chat/completions/-compatible): https://ai.xetute.com/v1/chat/completions
Enter your API key: 0
Only one model available. Auto-selected: koboldcpp/EN_ZH-7B-iQ4
How many samples do you need? 1024
Enter topics (example: "Versatile questions about Pakistan", etc.): Questions about the Islamic Republic of Pakistan, STEM and Islam
Enter system prompt (leave empty for none): You are a helpful AI assistant.
How many k context length does your endpoint support? 7
```
And that should do the work. If one request fails, the script will automatically retry till it gets a valid response from the server.  

---

<footer style="margin-top: 3rem; text-align: center; color: #ff5500; max-height: fit-content;">
  <em style="font-size: 1.2rem; text-shadow: 0 0 8px #ff5500;">
    Long live the Islamic Republic of Pakistan; Glory to the Islamic Republic of Pakistan 🇵🇰
  </em>
  <img src="https://upload.wikimedia.org/wikipedia/commons/3/32/Flag_of_Pakistan.svg" alt="Pakistan Flag" style="margin-top: 1rem; border: 2px solid #00ffff; padding: 3px;">
</footer>
