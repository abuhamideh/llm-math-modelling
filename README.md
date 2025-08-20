# my_genai_project

This project uses Google's Gemini (via `google.generativeai`) to convert optimisation problem descriptions into structured JSON.

---

## 🚀 How to run

1. **Activate your virtual environment**  
   This virtual environment contains all your Python packages and your `GOOGLE_API_KEY`.

   ```bash
   source ~/genai-env/bin/activate
   ```

2. **Navigate to your project directory**

   ```bash
   cd ~/my_genai_project
   ```

3. **Run your script**

   ```bash
   python3 desc.py
   ```

---

## ⚙️ Requirements

- Python 3.11+ (or whatever your local version is)
- Virtual environment created using:

  ```bash
  python3 -m venv ~/genai-env
  ```

- Install your required packages inside the venv:

  ```bash
  source ~/genai-env/bin/activate
  pip install google-generativeai
  ```

---

## 🔑 Environment Variables

Make sure your virtual environment has your Google API key set:

```bash
export GOOGLE_API_KEY="your_api_key_here"
```

If you’ve already set it in your terminal session or `.bash_profile` / `.zshrc`, you’re good.

---

## 📝 Notes

- The virtual environment lives outside this folder (`~/genai-env`), which is perfectly fine and keeps this project clean.
- If you ever switch machines or share this project, recreate the virtual environment and reinstall packages using a `requirements.txt`.

---

✅ That’s all. Happy coding!
