# SETUP AND REFACTOR CODE

## Context

* My environment workspace is Windows
* This is a simple Python application using Tkinter
* This app helps users categorize sets of images into different folders

---

## SETUP

1. Initialize a virtual environment for this project (venv)
2. Activate the virtual environment (Windows)
3. Install required dependencies:

   * tkinter (if needed / ensure available)
   * Pillow
4. Create a `requirements.txt` file
5. Create a `.gitignore` file and include:

   * venv/
   * **pycache**/
   * *.pyc
   * *.pyo
   * *.pyd
   * .Python
   * build/
   * dist/

---

## REFACTOR

Refactor the existing `main.py` (monolithic script) into a structured and modular Python codebase.

### Goals

* Improve readability and maintainability
* Apply separation of concerns
* Keep existing functionality unchanged
* Make the code scalable for future features

---

### Target Structure

Restructure the project into:

project_root/
│
├── app/
│   ├── **init**.py
│   ├── main.py              # entry point (UI bootstrap)
│   ├── ui/                  # Tkinter UI logic
│   │   └── main_window.py
│   ├── services/            # business logic
│   │   └── image_service.py
│   ├── utils/               # helper functions
│   │   └── file_utils.py
│   └── config/              # configuration
│       └── settings.py
│
├── assets/                  # optional (icons, etc.)
├── tests/                   # optional for future
├── requirements.txt
└── README.md

---

### Refactoring Instructions

1. Move UI-related code (Tkinter widgets, layout, event handling) into:

   * `app/ui/main_window.py`

2. Extract image processing and file handling logic into:

   * `app/services/image_service.py`

3. Move reusable helper functions (e.g. file operations, path handling) into:

   * `app/utils/file_utils.py`

4. Keep `main.py` minimal:

   * Only responsible for starting the application

5. Add clear function and class boundaries:

   * Avoid large functions
   * Use descriptive naming

6. Remove duplicated code if any

7. Ensure all imports are clean and relative within the package

---

### Constraints

* Do NOT change the core functionality
* Do NOT introduce unnecessary complexity
* Keep the code beginner-friendly
* Avoid over-engineering

---

### Output Format

Provide:

1. The new folder structure
2. Full code for each new file
3. Brief explanation of what each module does
4. Instructions to run the app

---

### Notes

* Prioritize clarity over cleverness
* Keep the UI logic separate from business logic
* Make sure the app still runs after refactor
