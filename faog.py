import argparse, json
import sys
import os
import google.generativeai as genai 

# 1. Function to get structured user input
def get_user_modeling_request():
    """
    Prompts the user for structured details about their optimisation problem.
    """
    print("\nPlease provide details for your mathematical optimisation problem:")
    
    data_json = input("input json: ")
        
    return data_json

# 2. Function to call the LLM and get the raw response
# This function encapsulates all the Gemini API setup and interaction.
def call_llm_for_modeling(user_json):
    """
    Constructs a detailed prompt from user inputs and calls the Gemini API
    to generate a mathematical formulation and Python code.

    Args:
        objective: The user's description of the objective function.
        data: The user's description of relevant data.
        constraints: The user's description of constraints.

    Returns:
        The raw text response from the Gemini model, or an error message.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set. "
                         "Please ensure you've set it up permanently in your .bashrc (or similar) "
                         "and restarted your terminal as instructed previously.")
    
    # Configure the Google GenAI library with your API key
    genai.configure(api_key=api_key)

    model_name = "gemini-2.5-flash" 
    # --- End of API Setup ---

    # Construct the comprehensive prompt for the LLM.
    full_prompt_for_llm = (
        "You are an expert in mathematical optimisation and a highly skilled Python programmer "
        "specializing in operations research problems. Your task is to: \n"
        "1. Based on the provided details, formulate the corresponding mathematical optimisation problem. "
        "   This should include clear definitions of decision variables (with units/types/domains), "
        "   the objective function (clearly stating minimisation or maximisation), and all constraints.\n"
        "2. Generate complete, runnable Python code to solve this mathematical problem. "
        "   The code should use a suitable open-source optimization library like PuLP, Pyomo, or SciPy.optimize. "
        "   It must be well-commented, include all necessary imports, and provide clear output of the optimal solution "
        "   (objective value and variable values).\n\n"
        "Here are the specific details of the problem:\n"
        f"The JSON data can be found in {user_json}"
        "Present your response in two distinct sections to facilitate parsing:\n"
        "First, use the heading '### Mathematical Formulation' for the problem setup.\n"
        "Second, use the heading '### Python Code' followed by a Python code block enclosed in triple backticks (```python ... ```).\n"
        "Ensure variable names in the Python code directly reflect the mathematical formulation."
    )

    try:
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content(full_prompt_for_llm)
        
        # The .text attribute typically holds the main text content of the response
        return response.text
    except Exception as e:
        return f"An error occurred during the LLM call: {e}"

# 3. Main execution block (Orchestrates the functions)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Automated Mathematical Modeler"
    )
    parser.add_argument(
        "-i",
        "--input",
        help=(
            "Path to a JSON file containing the optimisation problem. "
            "If omitted, the program will read from STDIN (when data is "
            "piped in) or fall back to an interactive prompt."
        ),
    )
    args = parser.parse_args()

    print("🚀 Welcome to the Automated Mathematical Modeler!")
    print("Let's define your optimization problem step by step.\n")

    # Step 1: Obtain JSON that describes the optimisation problem
    if args.input:
        with open(args.input, "r", encoding="utf-8") as infile:
            probjson = infile.read()
    elif not sys.stdin.isatty():
        # Data has been piped in via STDIN
        probjson = sys.stdin.read()
    else:
        # Interactive fallback
        probjson = get_user_modeling_request()

    # Step 2: Pass the combined input to the LLM function
    print("\nProcessing your request and generating the model... Please wait, this might take a moment.")
    raw_llm_output = call_llm_for_modeling(probjson)

    # Step 3: Display the raw output from the LLM
    # In later phases, we'll parse and act on this. For now, we just print it.
    print("\n--- RAW LLM RESPONSE ---\n")
    print(raw_llm_output)
    print("\n------------------------\n")

    print("Generation complete. Review the output above.")