---
name: receipt-filing
description: Process scanned business and personal documents by reading PDF content, analyzing to determine date and description, then renaming and organizing files into appropriate folders. Use this skill when the user asks to organize, file, or process scanned receipts, documents, or business/personal expense documents.
---

# Document Filing

## Overview

Automate the filing of scanned business and personal documents. Read PDF content directly to extract text and visual information, analyze the content to determine the document date and a brief description, then rename files appropriately and move them to the correct destination folder in OneDrive.

## When to Use This Skill

Use this skill when:
- User asks to organize or file scanned receipts or documents
- User wants to process PDFs in a receipts, scans, or documents folder
- User requests help with tax document organization
- User mentions receipt filing, document filing, or expense document management

## Workflow

### Step 0: MANDATORY - Determine Filing Type

**CRITICAL: Before any other processing, ALWAYS ask the user:**

"Is this business filing or personal filing?"

Use the AskUserQuestion tool with options:
- Business filing
- Personal filing

This determines:
- Target directory structure
- Filename format
- Filing conventions

### Step 1: Identify PDF Files

Identify all PDF files in the current directory (or user-specified directory). Confirm with the user how many files were found and that processing should proceed.

### Step 2: Read and Analyze Each Document

For each PDF file:

1. **Read the PDF** using the Read tool to extract text and visual content

2. **Analyze the content** to determine:
   - **Date**: Extract the document date in `YYYYMMDD` format (or `YYYYMM` if day is not available)
   - **Description**:
     - **Business**: Brief 2-5 word description suitable for tax filing (e.g., "parking in philadelphia", "office supplies", "client lunch")
     - **Personal**: Rich structured description following format: `Type_Subtype_Description[_Person]`
       - Read `references/personal-filing-taxonomy.md` for detailed guidance on Types, Subtypes, and formatting conventions
       - Common Types: Medical, Insurance, Home, Legal, Financial, Vehicle, Utilities, Tax
       - Include Person suffix only when document relates to specific family member: Joe, Trish, Benjamin, Megan
   - **Confidence**: Assess confidence level (high/medium/low) based on clarity of extracted information

3. **Flag for manual review** if:
   - PDF content is unclear or unreadable
   - Date cannot be determined (especially if year is unclear)
   - Confidence is low due to unclear or ambiguous content
   - Still process the file with best guess if possible, but note it needs review

### Step 3: Rename Files (In Current Directory)

For each successfully analyzed document:

1. **Generate new filename** based on filing type:

   **Business filing (Simple format for tax purposes):**
   - Format: `YYYYMMDD - receipt - description.pdf`
   - Example: `20251001 - receipt - parking in philadelphia.pdf`
   - Description: lowercase, brief (2-5 words), suitable for tax filing

   **Personal filing (Rich format for searchability):**
   - Format: `YYYY-MM-DD_Type_Subtype_Description[_Person].pdf`
   - Example: `2025-01-03_Medical_EOB_Dermatology_Joe.pdf`
   - See `references/personal-filing-taxonomy.md` for complete details on Types, Subtypes, Description formatting, and Person usage
   - Quick reference:
     - **Type**: Medical, Insurance, Home, Legal, Financial, Vehicle, Utilities, Tax
     - **Subtype**: EOB, Policy, Invoice, Bill, Statement, Contract, Receipt, etc.
     - **Description**: Brief, hyphenated text (e.g., `Roof-Repair`, `Adobe-CC`)
     - **Person**: Optional - Joe, Trish, Benjamin, Megan (when document is person-specific)
   - Use underscores between components, hyphens within descriptions
   - Capitalize first letter of each component

2. **Handle filename conflicts in current directory**: If renamed file already exists, append numeric suffix:
   - Business: `20251001 - receipt - parking in philadelphia (1).pdf`
   - Personal: `2025-01-03_Medical_EOB_Dermatology_Joe (1).pdf`

3. **Rename the file in place** (stays in current directory):
   ```bash
   # Business example:
   mv "original-filename.pdf" "20251001 - receipt - parking in philadelphia.pdf"

   # Personal example:
   mv "scan1.pdf" "2025-01-03_Medical_EOB_Dermatology_Joe.pdf"
   ```

4. **Provide rename summary**: Show user what files were renamed and their new names

### Step 4: User Verification

**STOP and ask user to verify**: "I've renamed all files. Please review the new filenames. Should I proceed with moving them to their final locations?"

Wait for user confirmation before proceeding to Step 5.

### Step 5: Move Files to Final Destinations

After user confirms the renamed files look correct:

1. **Determine target directory** based on filing type:

   **Business filing:**
   - Directory: `~/OneDrive/Family Room/Taxes/{YYYY} - Taxes/`
   - Example: `~/OneDrive/Family Room/Taxes/2025 - Taxes/`
   - Simple year-based folders for tax organization

   **Personal filing (Hybrid approach):**
   - Recent documents (last 2-3 years):
     - Directory: `~/OneDrive/Family Room/Active/`
     - Example: `~/OneDrive/Family Room/Active/2025-01-03_Medical_EOB_Dermatology_Joe.pdf`
   - Older documents:
     - Directory: `~/OneDrive/Family Room/Archive/{YYYY}/`
     - Example: `~/OneDrive/Family Room/Archive/2020/2020-05-15_Home_Invoice_Roof-Repair.pdf`
   - Extract year from date field to determine Active vs Archive
   - Use current year minus 2 as the cutoff (documents from 2023+ go to Active, older go to Archive/YYYY)

   For both types:
   - Create directories if they don't exist

2. **Handle filename conflicts at destination**: If file already exists at destination, append numeric suffix:
   - Business: `20251001 - receipt - parking in philadelphia (1).pdf`
   - Personal: `2025-01-03_Medical_EOB_Dermatology_Joe (1).pdf`

3. **Move the files**:
   ```bash
   # Business example:
   mv "20251001 - receipt - parking in philadelphia.pdf" "~/OneDrive/Family Room/Taxes/2025 - Taxes/"

   # Personal example (recent):
   mv "2025-01-03_Medical_EOB_Dermatology_Joe.pdf" "~/OneDrive/Family Room/Active/"

   # Personal example (older):
   mv "2020-05-15_Home_Invoice_Roof-Repair.pdf" "~/OneDrive/Family Room/Archive/2020/"
   ```

### Step 6: Final Summary Report

After processing all files, provide a summary:
- Total files processed
- Successfully filed count
- Files flagged for manual review (with reasons)
- Any errors encountered

For flagged items, include:
- Original filename
- Reason for flagging
- Best guess analysis (if available)

## Example Usage

### Example 1: Business Filing

**User request:**
> "Process the receipts in this folder"

**Workflow:**
1. **Ask filing type:** "Is this business filing or personal filing?" → User selects "Business filing"
2. List PDF files: `receipt1.pdf`, `receipt2.pdf`, `receipt3.pdf`
3. **Step 3 - Rename files in current directory:**
   - Read each PDF with Read tool
   - Analyze content: date=20251015, description="office depot supplies"
   - Rename in place: `receipt1.pdf` → `20251015 - receipt - office depot supplies.pdf`
   - Show rename summary
4. **Step 4 - User verification:** Ask user to confirm renamed files look correct
5. **Step 5 - Move files:** After confirmation, move files to `~/OneDrive/Family Room/Taxes/2025 - Taxes/`
6. Report final summary with any flagged items

### Example 2: Personal Filing

**User request:**
> "File these documents"

**Workflow:**
1. **Ask filing type:** "Is this business filing or personal filing?" → User selects "Personal filing"
2. List PDF files: `scan1.pdf`, `scan2.pdf`, `scan3.pdf`
3. **Step 3 - Rename files in current directory:**
   - Read each PDF with Read tool
   - Analyze content and apply rich filename format:
     - `scan1.pdf`: date=2025-03-20, type=Medical, subtype=EOB, description=Cardiology-Visit, person=Joe
     - `scan2.pdf`: date=2024-11-03, type=Home, subtype=Invoice, description=Roof-Repair
     - `scan3.pdf`: date=2019-11-15, type=Legal, subtype=Inspection, description=Home-Purchase-288-Green
   - Rename in place:
     - `scan1.pdf` → `2025-03-20_Medical_EOB_Cardiology-Visit_Joe.pdf`
     - `scan2.pdf` → `2024-11-03_Home_Invoice_Roof-Repair.pdf`
     - `scan3.pdf` → `2019-11-15_Legal_Inspection_Home-Purchase-288-Green.pdf`
   - Show rename summary
4. **Step 4 - User verification:** Ask user to confirm renamed files look correct
5. **Step 5 - Move files:** After confirmation, move to appropriate directories:
   - First two → `~/OneDrive/Family Room/Active/` (recent, 2023+)
   - Third one → `~/OneDrive/Family Room/Archive/2019/` (older)
6. Report final summary with any flagged items

## Important Notes

### Filing Type Selection
- **ALWAYS ask if this is business or personal filing before processing**
- This determines filename format, directory structure, and filing conventions

### Business Filing (Simple for Tax Purposes)
- Format: `YYYYMMDD - receipt - description.pdf`
- Target: `~/OneDrive/Family Room/Taxes/{YYYY} - Taxes/`
- Description: lowercase, brief (2-5 words), suitable for tax filing
- Philosophy: Keep it simple for tax organization

### Personal Filing (Rich for Searchability)
- Format: `YYYY-MM-DD_Type_Subtype_Description[_Person].pdf`
- Targets:
  - Recent (2023+): `~/OneDrive/Family Room/Active/`
  - Older: `~/OneDrive/Family Room/Archive/{YYYY}/`
- **See `references/personal-filing-taxonomy.md`** for complete taxonomy with examples
- Quick summary:
  - **Types**: Medical, Insurance, Home, Legal, Financial, Vehicle, Utilities, Tax
  - **Subtypes**: EOB, Policy, Invoice, Bill, Statement, Contract, Receipt, etc.
  - **Description**: Hyphenated (e.g., `Roof-Repair`, `Adobe-CC`, `Purchase-288-Green`)
  - **Person**: Joe, Trish, Benjamin, Megan (only when document is person-specific)
- Philosophy: Flat structure with rich filenames enables powerful search using `fd` and `rg`

### Search Examples for Personal Files
```bash
# Find all medical docs for Joe
fd "_Medical_.*_Joe" ~/OneDrive/Family\ Room/

# Find anything about 288 Green St
fd "288-Green" ~/OneDrive/Family\ Room/

# Find all insurance policies
fd "_Insurance_Policy" ~/OneDrive/Family\ Room/

# Full-text search
rg "roof replacement" ~/OneDrive/Family\ Room/
```

### General Guidelines
- **Two-step process**: Always rename files first (in current directory), wait for user verification, then move to final destinations
- This allows user to review and catch any issues before files are moved away
- Prefer full date over month-only when available
- Always flag uncertain items but still process with best guess when possible
- Create target folders as needed
- The Read tool handles PDFs natively (both text-based and image-based)
- PDFs are processed page-by-page, extracting both text and visual content
