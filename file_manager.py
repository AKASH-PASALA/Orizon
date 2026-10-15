import os
import subprocess
from pathlib import Path


# Orizon's permitted file-management location
BASE_DIR = Path.home() / "OrizonFiles"
BASE_DIR.mkdir(parents=True, exist_ok=True)


def create_folder(folder_name):
    folder_name = folder_name.strip()

    if not folder_name:
        return "Boss, please tell me the folder name."

    # Prevent paths outside OrizonFiles
    if Path(folder_name).name != folder_name or folder_name in {".", ".."}:
        return "Boss, I can only create folders inside OrizonFiles."

    folder = BASE_DIR / folder_name

    if folder.exists():
        return f"Boss, the folder {folder_name} already exists."

    folder.mkdir()
    return f"Boss, I created the folder {folder_name}."


def create_file(file_name):
    file_name = file_name.strip()

    if not file_name:
        return "Boss, please tell me the file name."

    # Allow simple filenames only
    if Path(file_name).name != file_name or file_name in {".", ".."}:
        return "Boss, I can only create files inside OrizonFiles."

    if not file_name.lower().endswith(".txt"):
        file_name += ".txt"

    file_path = BASE_DIR / file_name

    if file_path.exists():
        return f"Boss, {file_name} already exists. I didn't overwrite it."

    file_path.write_text("", encoding="utf-8")
    return f"Boss, I created {file_name}."


def open_folder(folder_name=None):
    if not folder_name:
        folder = BASE_DIR
    else:
        folder_name = folder_name.strip()

        if Path(folder_name).name != folder_name:
            return "Boss, I can only open folders inside OrizonFiles."

        folder = BASE_DIR / folder_name

    if not folder.exists() or not folder.is_dir():
        return "Boss, that folder doesn't exist."

    os.startfile(str(folder))
    return f"Boss, opening {folder.name}."


def search_file(file_name):
    file_name = file_name.strip().lower()

    if not file_name:
        return "Boss, please tell me which file to search for."

    matches = []

    for path in BASE_DIR.rglob("*"):
        if path.is_file() and file_name in path.name.lower():
            matches.append(path)

            if len(matches) >= 10:
                break

    if not matches:
        return f"Boss, I couldn't find a file matching {file_name}."

    results = "\n".join(str(path) for path in matches)
    print("Matching files:\n" + results)

    return f"Boss, I found {len(matches)} matching file(s). Their paths are printed in the terminal."


def read_text_file(file_name):
    file_name = file_name.strip()

    if Path(file_name).name != file_name or file_name in {".", ".."}:
        return "Boss, I can only read files inside OrizonFiles."

    file_path = BASE_DIR / file_name

    if not file_path.exists() or not file_path.is_file():
        return "Boss, I couldn't find that file."

    if file_path.suffix.lower() != ".txt":
        return "Boss, I can only read text files for now."

    if file_path.stat().st_size > 100_000:
        return "Boss, that file is too large for this basic reader."

    content = file_path.read_text(encoding="utf-8")

    if not content.strip():
        return f"Boss, {file_name} is empty."

    print(f"\nContents of {file_name}:\n{content}\n")

    # Keep spoken responses reasonably short.
    preview = content[:500]

    return f"Boss, here's the content of {file_name}: {preview}"


def list_files():
    items = list(BASE_DIR.iterdir())

    if not items:
        return "Boss, your OrizonFiles folder is empty."

    print("\nOrizonFiles contents:")
    for item in items:
        print(f"{'[Folder]' if item.is_dir() else '[File]'} {item.name}")

    return f"Boss, I found {len(items)} item(s). Their names are printed in the terminal."


if __name__ == "__main__":
    print(f"Orizon file workspace: {BASE_DIR}")
    print("File manager loaded successfully.")