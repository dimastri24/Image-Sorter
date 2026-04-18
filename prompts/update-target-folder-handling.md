# Refactor Target Folder Handling

## Objective
Improve how target folders are stored, managed, and displayed in the application.

---

## Step 1 — Migrate Config Format (TXT → JSON)

### Goal
Replace the existing `config-target.txt` with a JSON-based configuration.

### Requirements
- Change storage format from:

meme
trash
hololive

````
to:
```json
[
  "D:\\images\\fgo",
  "D:\\images\\meme"
]
````

* Store **absolute paths only**
* Ensure compatibility with Windows path format

### Validation Rule (IMPORTANT)

* If **source image folder is not selected**:

  * Conversion from `.txt` → `.json` MUST NOT proceed
  * Show error message:

    > "Please select a source folder before converting target folders."
  * Keep `.txt` file unchanged
  * Still create `config-target.json` as an **empty array**

### Tasks

* Create a new config file (e.g., `config-target.json`)
* Implement:

  * Load JSON config
  * Save JSON config
* Add fallback:

  * If old `.txt` exists:

    * Attempt conversion
    * Apply validation rule above

---

## Step 2 — Update "Select Folder" Behavior

### Goal

Ensure selected folders are stored as absolute paths

### Tasks

* Modify "Select Folder" feature:

  * Use full/absolute path instead of folder name
* Update any logic that depends on folder name:

  * Must now extract folder name using:

    * `os.path.basename(path)`

---

## Step 3 — Update "Add Folder" Logic

### Goal

Align folder creation behavior with new config format

### Validation Rule (IMPORTANT)

* If **source image folder is not selected**:

  * Block folder creation
  * Show error message:

    > "Please select a source folder first."

### Current Behavior

* Folder is created inside currently opened directory

### Required Changes

* Keep folder creation behavior **unchanged**
* But:

  * Store the **absolute path** of the created folder in JSON config

### Tasks

* After creating folder:

  * Resolve full path
  * Append to JSON config

---

## Step 4 — Enhance Input Field (Search + Add)

### Goal

Make input field multifunctional:

* Search existing folders
* Add new folder if not found

### Behavior

* When user types:

  * Filter Listbox items in real-time
* If match found:

  * Show filtered results
* If no match:

  * Show "Add Folder" button with hint text

### UX Notes

* The "Add" button should clearly indicate:

  * It performs the same action as manual add
* Keep interaction simple and intuitive

### Tasks

* Implement:

  * Case-insensitive search
  * Dynamic List filtering
* Add conditional UI:

  * Show/hide "Add" button based on search result

---

## Step 5 — Redesign Folder List UI

### Goal

Improve Listbox into a visual grid (Explorer-like)

### Requirements

* Replace simple vertical list with:

  * Grid / card layout
* Each item should contain:

  * Folder name (label)
  * Preview image (if available)

### Preview Image Rules

* Load first image found inside folder
* Supported formats:

  * `.jpg`, `.png`, `.jpeg`, etc.
* If no image:

  * Show placeholder

### Tasks

* Replace Listbox with custom UI container:

  * e.g., Frame + Grid system
* Implement:

  * Thumbnail generation
  * Image caching (optional but recommended)

---
