# UI/UX Refactor — Tkinter Application

## Objective
Modernize the UI design, improve layout consistency, and enhance user experience without breaking existing functionality.

---

## Execution Strategy

- Execute **one step at a time**
- Do **not combine steps**
- After each step:
  - Ensure UI still renders correctly
  - Do not break existing logic

---

## Step 1 — Window Initialization & Positioning

### Goal
Improve initial app appearance

### Requirements
- Open the application window at the **center of the screen**
- Ensure consistent initial window size

### Tasks
- Calculate screen width & height
- Set window position dynamically
- Avoid hardcoded offsets

---

## Step 2 — Global Styling System

### Goal
Replace default Tkinter styling with a more modern look

### Style Guidelines
- Base colors:
  - Primary: Blue
  - Neutral: Light/Dark Gray
- Use:
  - Softer rounded corners (simulate if needed)
  - Flat design (no harsh borders)
- Improve:
  - Buttons
  - Input fields
  - Containers (frames)

### Tasks
- Create centralized styling config (colors, fonts, spacing)
- Apply consistent styles across all widgets

---

## Step 3 — Layout Spacing & Alignment Fixes

### Goal
Fix spacing inconsistencies

### Tasks
- Add top margin to:
  - "Select Image Folder" button
- Ensure consistent padding across:
  - Left and right frames
- Align components visually into clear sections

---

## Step 4 — Source Preview Stability

### Goal
Prevent UI resizing caused by image preview

### Requirements
- Source preview box must have **fixed width**
- Image should:
  - Fit inside container
  - Maintain aspect ratio

### Tasks
- Wrap preview in fixed-size container
- Resize image before rendering

---

## Step 5 — Scroll Behavior Improvement

### Goal
Improve usability of folder list

### Requirements
- Enable **mouse wheel scrolling**
- Keep scrollbar functional

### Tasks
- Bind mouse scroll event to list container
- Ensure smooth scrolling behavior

---

## Step 6 — Target Folder Card Redesign

### Goal
Modernize folder list UI

### Requirements
- Remove:
  - Ugly borders
  - Excess padding
- Card design:
  - Image preview → full width
  - Folder name:
    - Overlay on image (bottom)
    - With background for contrast

### Tasks
- Redesign each folder item as a "card"
- Use layered layout:
  - Image (background)
  - Label (overlay)

---

## Step 7 — Responsive Grid Layout

### Goal
Make folder grid adaptive

### Requirements
- Responsive columns:
  - Minimum: 2 columns
  - Maximum: 5 columns
- Adjust based on window width

### Tasks
- Calculate number of columns dynamically
- Re-render layout on window resize

---

## Step 8 — Navigation Controls Update

### Goal
Improve navigation flow

### Requirements
- Move "Skip" button:
  - To left frame
  - Below source preview
- Add:
  - "Back" / "Previous" button
  - Position: left side of "Skip"

### Tasks
- Reorganize button layout
- Ensure logical tab order

---

## Step 9 — Remove Unused Controls

### Goal
Simplify UI

### Tasks
- Remove:
  - "Quit" button

---

## Step 10 — Search Input Enhancement

### Goal
Improve usability and visual consistency

### Requirements
- Full width within right frame
- Modern styling:
  - Padding
  - Clean border
  - Consistent font

### Tasks
- Replace default Entry styling
- Align with global design system

---

## Step 11 — Button Color Semantics

### Goal
Improve clarity through color usage

### Guidelines
- Use color based on action:
  - Primary (blue): main actions
  - Neutral (gray): secondary actions
  - Warning (optional): destructive actions

### Tasks
- Assign consistent color roles to:
  - Select Folder
  - Add
  - Skip
  - Back

---

## Final Notes

- Do not introduce new dependencies unless necessary
- Keep Tkinter compatibility
- Maintain performance (especially image rendering)
- Avoid breaking existing features

---

## Deliverables

- Fully modernized UI
- Responsive layout
- Improved usability and navigation
- Consistent styling system