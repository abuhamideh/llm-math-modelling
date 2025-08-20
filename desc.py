import os
import sys
import csv
import json
from pathlib import Path
import argparse

# Optional dependencies for additional file types
try:
    import pandas as pd
except Exception:
    pd = None

try:
    from docx import Document
except Exception:
    Document = None

try:
    import PyPDF2
except Exception:
    PyPDF2 = None

import google.generativeai as genai


def summarise_instance_file(path: Path, max_preview_lines: int = 20) -> dict:
    """
    Return a dict with:
      type: 'csv' | 'tsv' | 'json' | 'txt' | 'unknown'
      details: human summary string
      preview: short textual preview for the prompt
    """
    info = {"type": "unknown", "details": "", "preview": ""}
    if not path or not path.exists():
        return info

    suffix = path.suffix.lower()
    try:
        if suffix in [".csv", ".tsv", ".txt"]:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                sample = f.read(4096)
                f.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    delimiter = dialect.delimiter
                except Exception:
                    delimiter = "," if suffix == ".csv" else ("\t" if suffix == ".tsv" else " ")
                lines = []
                for i, line in enumerate(f):
                    if i >= max_preview_lines:
                        break
                    lines.append(line.rstrip("\n"))
                has_header = False
                try:
                    has_header = csv.Sniffer().has_header(sample)
                except Exception:
                    pass
                info["type"] = "csv" if delimiter == "," else ("tsv" if delimiter == "\t" else "txt")
                info["details"] = (
                    f"text table with delimiter '{delimiter}', "
                    f"{'with' if has_header else 'without'} header row, "
                    f"{len(lines)}-line preview below"
                )
                info["preview"] = "\n".join(lines)
        elif suffix in [".xlsx", ".xls", ".xlsm", ".xlsb"]:
            if pd is None:
                info["type"] = "excel"
                info["details"] = (
                    "Excel file detected but pandas is not installed. Install 'pandas' and an Excel engine such as 'openpyxl' to enable preview."
                )
                info["preview"] = ""
            else:
                try:
                    # Open workbook and list sheets
                    xls = pd.ExcelFile(path)
                    sheet_names = list(xls.sheet_names)
                    max_sheets = 3  # cap number of sheets to preview to avoid huge output
                    shown_sheets = sheet_names[:max_sheets]

                    preview_chunks = []
                    for sn in shown_sheets:
                        try:
                            df = pd.read_excel(xls, sheet_name=sn, nrows=max_preview_lines)
                            cols = list(df.columns)
                            lines = []
                            # Header
                            lines.append(",".join(str(c) for c in cols))
                            # Rows
                            for _, row in df.iterrows():
                                lines.append(",".join(str(x) for x in row.tolist()))
                            chunk = f"[Sheet: {sn}]\n" + "\n".join(lines)
                            preview_chunks.append(chunk)
                        except Exception as sheet_err:
                            preview_chunks.append(f"[Sheet: {sn}] error reading sheet: {sheet_err}")

                    info["type"] = "excel"
                    info["details"] = (
                        f"Excel workbook with {len(sheet_names)} sheet(s); showing up to {len(shown_sheets)} sheet(s), "
                        f"{max_preview_lines} row preview per sheet"
                    )
                    info["preview"] = "\n\n".join(preview_chunks) if preview_chunks else "(no previewable data)"
                except Exception as e:
                    info["type"] = "excel"
                    info["details"] = f"error reading excel file: {e}"
                    info["preview"] = ""
        elif suffix == ".json":
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
            if isinstance(data, list):
                shape = f"list with {len(data)} elements"
                keys = []
                if data and isinstance(data[0], dict):
                    keys = sorted({k for row in data[:5] for k in row.keys()})
                info["type"] = "json"
                info["details"] = shape + (f", object keys include: {', '.join(keys)}" if keys else "")
                info["preview"] = json.dumps(data[:3], ensure_ascii=False, indent=2)
            elif isinstance(data, dict):
                info["type"] = "json"
                keys = list(data.keys())[:10]
                info["details"] = f"object with top-level keys: {', '.join(keys)}"
                info["preview"] = json.dumps({k: data[k] for k in keys}, ensure_ascii=False, indent=2)
            else:
                info["type"] = "json"
                info["details"] = "json value"
                info["preview"] = json.dumps(data, ensure_ascii=False, indent=2)
        elif suffix == ".docx":
            if Document is None:
                info["type"] = "docx"
                info["details"] = "Word document detected but python-docx is not installed. Install 'python-docx' to enable preview."
                info["preview"] = ""
            else:
                try:
                    doc = Document(str(path))
                    lines = []
                    for para in doc.paragraphs:
                        if para.text.strip():
                            lines.append(para.text.strip())
                        if len(lines) >= max_preview_lines:
                            break
                    info["type"] = "docx"
                    info["details"] = f"Word document; {len(lines)}-line text preview below"
                    info["preview"] = "\n".join(lines)
                except Exception as e:
                    info["type"] = "docx"
                    info["details"] = f"error reading docx file: {e}"
                    info["preview"] = ""
        elif suffix == ".pdf":
            if PyPDF2 is None:
                info["type"] = "pdf"
                info["details"] = "PDF detected but PyPDF2 is not installed. Install 'PyPDF2' to enable preview."
                info["preview"] = ""
            else:
                try:
                    with open(path, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        text_parts = []
                        # Extract text from up to the first 2 pages
                        for i, page in enumerate(reader.pages[:2]):
                            try:
                                text_parts.append(page.extract_text() or "")
                            except Exception:
                                pass
                        text = "\n".join(text_parts)
                        lines = text.splitlines()[:max_preview_lines]
                    info["type"] = "pdf"
                    info["details"] = f"PDF document; preview extracted from first {min(2, len(getattr(reader, 'pages', [])))} pages"
                    info["preview"] = "\n".join(lines)
                except Exception as e:
                    info["type"] = "pdf"
                    info["details"] = f"error reading pdf file: {e}"
                    info["preview"] = ""
        else:
            with path.open("rb") as f:
                blob = f.read(4096)
            try:
                text = blob.decode("utf-8", errors="ignore")
            except Exception:
                text = ""
            info["type"] = "unknown"
            info["details"] = "unknown format, showing first 4KB as text"
            info["preview"] = "\n".join(text.splitlines()[:max_preview_lines])
    except Exception as e:
        info["type"] = "unknown"
        info["details"] = f"error reading file: {e}"
        info["preview"] = ""
    return info


def call_gemini(full_description, history, instance_meta=None, allow_proposed=False):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Make sure GOOGLE_API_KEY is set in your environment.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    if instance_meta and instance_meta.get("preview"):
        instance_section = (
            "\n\nAn instance file is provided. Base the 'Instance file format' section "
            "strictly on this file's real layout. Do not invent fields or columns. "
            "Describe delimiter, header presence, ordering, and how fields map to symbols and indices.\n"
            f"- Detected type: {instance_meta.get('type')}\n"
            f"- Details: {instance_meta.get('details')}\n"
            "Preview of the instance file (truncated):\n"
            "```\n" + instance_meta.get("preview") + "\n```\n"
        )
    else:
        if allow_proposed:
            instance_section = (
                "\n\nNo instance file is provided. You may propose a concise, example-style instance file format "
                "consistent with your abstraction, as in the examples."
            )
        else:
            instance_section = (
                "\n\nNo instance file is provided. In the 'Instance file format' section, write exactly: "
                "'Not provided.' Do not propose or invent any file format."
            )
    
        # Detect when user asked for whole numbers
# Detect when user asked for whole numbers
    needs_integrality = any(s in (full_description or "").lower()
                            for s in ["integer", "integers", "whole number", "whole numbers"])

    style_rules = (
        "Write a clear, plain-English specification using EXACTLY these sections and headings:\n"
        "# Input data\n# Solution\n# Constraints\n# Objective function\n# Instance file format\n# Solution file format\n\n"
        "Style rules:\n"
        "- Prefer domain words from the user's text (e.g., eggs, bacon, sandwiches) instead of abstract symbols.\n"
        "- Avoid sets and indices unless strictly necessary. Use simple phrases like 'The number of X', 'For each X, ...'.\n"
        "- Keep bullets short and concrete. No parentheses glosses, no equations under constraints.\n"
        "- In '# Solution', write a single plain sentence like 'An assignment of exams to time slots' or 'Quantities of each item to produce'.\n"
        "- In '# Constraints', use short sentences. If none are required, write 'None.' and optionally one plain allowance sentence.\n"
        "- In '# Objective function', use a single clear sentence in plain English. If helpful, you may define one helper quantity with 'Let ...' and give a 1-line example.\n"
        "- In '# Instance file format', describe exactly how to read the provided file when one is given. If no instance file is provided and proposing is not allowed, write exactly 'Not provided.'\n"
        "- In '# Solution file format', end with 'Use 1-based indexing.'\n"
        f"- If the user's text clearly requires whole numbers, include the constraint 'Quantities are integers.' This applies here: {'yes' if needs_integrality else 'no'}.\n"
        "- Be concise. No extra sections, no symbols like P, I, a(i) unless necessary for clarity."
    )

    examples_plain = (
        "\n\nExample A (Assignment):\n"
        "# Input data\n"
        "- The number of people.\n"
        "- The number of jobs.\n"
        "- A cost for assigning each person to each job.\n\n"
        "# Solution\n"
        "An assignment of people to jobs.\n\n"
        "# Constraints\n"
        "- Each person is assigned to exactly one job.\n"
        "- Each job is assigned to exactly one person.\n\n"
        "# Objective function\n"
        "The sum of the costs of the chosen person–job pairs.\n\n"
        "# Instance file format\n"
        "Text file. The first line contains the number of people n. The next n lines contain n space-separated integers giving the cost matrix; row is the person, column is the job.\n\n"
        "# Solution file format\n"
        "Text file. One space-separated line with n numbers: for each person, the job assigned to them. Use 1-based indexing.\n\n"
        "Example B (Resource selection):\n"
        "# Input data\n"
        "- The number of tasks.\n"
        "- For each task, the resource it uses and the profit it yields.\n"
        "- The total available resource.\n\n"
        "# Solution\n"
        "A selection of tasks to perform.\n\n"
        "# Constraints\n"
        "- The total resource used by the selected tasks does not exceed the available resource.\n\n"
        "# Objective function\n"
        "The sum of profits of the selected tasks.\n\n"
        "# Instance file format\n"
        "Text file. The first line contains the number of tasks and the total resource. Each of the next lines contains the resource and profit for one task, space-separated.\n\n"
        "# Solution file format\n"
        "Text file. One space-separated line with one number per task: 1 if selected, 0 otherwise. Use 1-based indexing.\n\n"
        "Example C (Two-resource production):\n"
        "# Input data\n"
        "- The number of item types.\n"
        "- For each item type, how much of resource A and resource B it uses, and the profit per unit.\n"
        "- The total available amount of resource A.\n"
        "- The total available amount of resource B.\n\n"
        "# Solution\n"
        "Quantities of each item type to produce.\n\n"
        "# Constraints\n"
        "- The total use of resource A does not exceed its availability.\n"
        "- The total use of resource B does not exceed its availability.\n\n"
        "# Objective function\n"
        "The sum of profits from the produced quantities.\n\n"
        "# Instance file format\n"
        "CSV file. The first line contains the number of item types and the two resource totals. Each of the next lines contains the two resource usages and the profit for one item type, space-separated.\n\n"
        "# Solution file format\n"
        "Text file. One space-separated line with one number per item type: the quantity to produce. Use 1-based indexing.\n"
    )

    prompt = (
        "You are an expert in mathematical optimisation. "
        "Rewrite the user's problem description into a precise, human-readable specification with the six sections below.\n\n"
        + style_rules
        + examples_plain
        + instance_section
        + "\n\nHere is the problem description:\n\n"
        + str(full_description)
        + "\n\nConversation so far:\n\n"
        + str(history)
    )

    response = model.generate_content(prompt)
    return getattr(response, "text", "").strip() or "(no text returned)"


def main():
    parser = argparse.ArgumentParser(
        description="Generate LP or MILP spec from a description, optionally grounded on an instance file."
    )
    # Positional like your original: desc, optional out, optional instance
    parser.add_argument("description_file", help="Path to a text file containing the problem description")
    parser.add_argument("output_file", nargs="?", help="Optional output .txt path for the generated specification")
    parser.add_argument("instance_file", nargs="?", help="Optional instance data file to infer the Instance file format from")

    # Optional flags too, if you prefer
    parser.add_argument("--out", dest="out_flag", help="Alternate way to set output .txt path")
    parser.add_argument("--instance", dest="instance_flag", help="Alternate way to set instance data file")
    parser.add_argument("--allow-proposed-instance", action="store_true",
                        help="Allow proposing a generic instance format when no instance file is provided")

    args = parser.parse_args()
    if args.output_file and args.instance_file:
        def looks_like_instance(p):
            s = str(p).lower()
            return any(
                s.endswith(ext)
                for ext in (".csv", ".tsv", ".json", ".xlsx", ".xls", ".xlsm", ".xlsb", ".docx", ".pdf")
            ) or "instance" in s
        def looks_like_output(p):
            s = str(p).lower()
            return s.endswith(".txt") and "instance" not in s
        if looks_like_instance(args.output_file) and looks_like_output(args.instance_file):
            args.output_file, args.instance_file = args.instance_file, args.output_file
            print("\u001b[33m:| Note: detected swapped arguments; treating the 2nd arg as instance and 3rd as output.\u001b[0m")


    desc_path = Path(args.description_file)
    if not desc_path.exists():
        print(f"\u001b[31m:( Error: File '{desc_path}' not found. \u001b[0m")
        return

    output_path = args.out_flag or args.output_file
    if output_path and not output_path.endswith(".txt"):
        output_path += ".txt"

    # Resolve instance path from positional or flag
    instance_path_str = args.instance_flag or args.instance_file
    instance_meta = summarise_instance_file(Path(instance_path_str)) if instance_path_str else None

    try:
        with desc_path.open("r", encoding="utf-8", errors="ignore") as f:
            userinput = f.read()
    except FileNotFoundError:
        print(f"\u001b[31m:( Error: File '{desc_path}' not found. \u001b[0m")
        return

    conversation = ""
    while True:
        response = call_gemini(
            userinput,
            conversation,
            instance_meta=instance_meta,
            allow_proposed=args.allow_proposed_instance
        )

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f_spec:
                f_spec.write(response)
            print(f"\n\u001b[32m:) Specification output written to {output_path} \u001b[0m")
        else:
            print("\n--- GENERATED PROBLEM SPECIFICATION ---\n")
            print(response)
            print("\n---------------------------------------")

        addition = input("\u001b[32m:) If you want to add or clarify details, please enter them now (or type 'done' to finish): \u001b[0m")
        if addition.strip().lower() == "done":
            break

        userinput += "\n" + addition
        conversation += f"\nUser: {addition}\nAI: {response}\n"


if __name__ == "__main__":
    main()


#PLAN:
# ACCEPT EXCEL FILES + WORD + PDFS (basic preview added).
# BE MORE TALKATIVE & SAY 'THIS WASNT SPECIFIED SO I SUGGEST THIS SOLUTION' (EG SOUNDS LIKE YOU WANT TO MAXIMSIE REVENUE, AM I RIGHT?)
# TEST DATA: ADD MORE SYNTHETIC DATA TO TEST ON. 
# PERHAPS SOURCES OF REAL PROBLEMS OR TEXT BOOK EXAMPLES
# AI GEN'D DATA