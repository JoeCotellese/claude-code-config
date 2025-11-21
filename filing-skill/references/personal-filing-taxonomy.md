# Personal Filing Taxonomy

This reference provides detailed guidance for categorizing personal documents using the rich filename format: `YYYY-MM-DD_Type_Subtype_Description[_Person].pdf`

## Document Types

### Medical
Medical care, insurance claims, bills, and health records.

**Common Subtypes:**
- `EOB` - Explanation of Benefits (insurance claim summaries)
- `Bill` - Medical bills and invoices
- `Statement` - Account statements from providers
- `Receipt` - Payment receipts
- `Records` - Medical records, test results, imaging
- `Insurance` - Health insurance cards, policy documents

**Example Descriptions:**
- `Cardiology-Visit`
- `Dermatology-Checkup`
- `Emergency-Room`
- `Lab-Work`
- `Prescription-Refill`
- `Annual-Physical`

**Examples:**
- `2025-03-20_Medical_EOB_Cardiology-Visit_Joe.pdf`
- `2024-11-15_Medical_Bill_Dermatology_Trish.pdf`
- `2024-09-10_Medical_Records_Annual-Physical_Benjamin.pdf`

### Insurance
Insurance policies, declarations, riders, and related documents (excluding medical EOBs).

**Common Subtypes:**
- `Policy` - Full policy documents
- `Declaration` - Policy declaration pages
- `Rider` - Policy riders and amendments
- `Quote` - Insurance quotes
- `Claim` - Insurance claims (non-medical)
- `Renewal` - Renewal notices
- `Card` - Insurance cards

**Example Descriptions:**
- `Home-Policy`
- `Auto-Policy`
- `Flood-Rider`
- `Umbrella-Policy`
- `Life-Insurance`
- `Homeowners-Renewal`

**Examples:**
- `2024-01-30_Insurance_Policy_Home-Flood.pdf`
- `2024-06-15_Insurance_Declaration_Auto-Honda.pdf`
- `2023-12-01_Insurance_Renewal_Homeowners.pdf`

### Home
Home-related documents including maintenance, repairs, improvements, utilities, and property records.

**Common Subtypes:**
- `Invoice` - Service invoices
- `Receipt` - Payment receipts
- `Estimate` - Service estimates
- `Warranty` - Appliance/system warranties
- `Inspection` - Home inspections
- `Deed` - Property deeds
- `Mortgage` - Mortgage documents
- `Tax` - Property tax bills

**Example Descriptions:**
- `Roof-Repair`
- `HVAC-Maintenance`
- `Plumbing-Fix`
- `Appliance-Warranty`
- `Purchase-288-Green` (for purchase-related docs, include address)
- `Property-Tax`
- `HOA-Fee`

**Examples:**
- `2024-11-03_Home_Invoice_Roof-Repair.pdf`
- `2019-11-15_Home_Inspection_Purchase-288-Green.pdf`
- `2024-03-20_Home_Warranty_Dishwasher.pdf`
- `2024-07-01_Home_Tax_Property-2024.pdf`

### Legal
Legal documents, contracts, and agreements.

**Common Subtypes:**
- `Contract` - Contracts and agreements
- `Deed` - Property deeds
- `Will` - Wills and estate documents
- `POA` - Power of attorney
- `Inspection` - Legal inspections
- `Certificate` - Certificates (birth, marriage, etc.)
- `License` - Licenses and permits

**Example Descriptions:**
- `Home-Purchase-288-Green`
- `Construction-Permit`
- `Marriage-Certificate`
- `Birth-Certificate-Benjamin`
- `Estate-Planning`

**Examples:**
- `2019-11-15_Legal_Inspection_Home-Purchase-288-Green.pdf`
- `2024-02-14_Legal_Contract_Solar-Installation.pdf`
- `2010-06-20_Legal_Certificate_Marriage.pdf`

### Financial
Bank statements, investment documents, loan documents, and financial records.

**Common Subtypes:**
- `Statement` - Bank/investment statements
- `Tax` - Tax documents (1099s, W2s, etc.)
- `Loan` - Loan documents
- `Receipt` - Financial receipts
- `Agreement` - Financial agreements
- `Report` - Financial reports

**Example Descriptions:**
- `Vanguard-Q4`
- `Bank-Statement-Chase`
- `1099-Vanguard`
- `W2-Employer`
- `Mortgage-Refinance`

**Examples:**
- `2023-12-31_Financial_Statement_Vanguard-Q4.pdf`
- `2024-01-31_Financial_Tax_1099-Vanguard.pdf`
- `2024-10-30_Financial_Statement_Chase-Checking.pdf`

### Vehicle
Vehicle-related documents including registration, insurance, maintenance, and repairs.

**Common Subtypes:**
- `Registration` - Vehicle registration
- `Title` - Vehicle title
- `Insurance` - Auto insurance (can also use Insurance type)
- `Maintenance` - Service records
- `Repair` - Repair invoices
- `Receipt` - Purchase receipts

**Example Descriptions:**
- `Hyundai-Registration`
- `Honda-Oil-Change`
- `Tesla-Repair`
- `Brake-Service`

**Examples:**
- `2024-06-01_Vehicle_Registration_Hyundai.pdf`
- `2024-08-15_Vehicle_Maintenance_Honda-Oil-Change.pdf`
- `2024-09-20_Vehicle_Repair_Brake-Service.pdf`

### Utilities
Utility bills and statements.

**Common Subtypes:**
- `Bill` - Utility bills
- `Statement` - Account statements
- `Agreement` - Service agreements

**Example Descriptions:**
- `Electric-PECO`
- `Gas-PGW`
- `Water-PWD`
- `Internet-Comcast`
- `Phone-Verizon`

**Examples:**
- `2024-10-15_Utilities_Bill_Electric-PECO.pdf`
- `2024-10-20_Utilities_Bill_Internet-Comcast.pdf`
- `2024-10-25_Utilities_Bill_Water-PWD.pdf`

### Tax
Personal tax documents (not business). Use this for personal tax returns and related documents that don't fit other categories.

**Common Subtypes:**
- `Return` - Tax returns
- `Payment` - Tax payments
- `Notice` - IRS/state notices
- `Extension` - Extension requests

**Example Descriptions:**
- `Federal-Return`
- `PA-State-Return`
- `Property-Tax`
- `Estimated-Payment`

**Examples:**
- `2024-04-15_Tax_Return_Federal-2023.pdf`
- `2024-04-15_Tax_Return_PA-State-2023.pdf`
- `2024-01-15_Tax_Payment_Q4-Estimated.pdf`

## Person Names

When a document relates to a specific family member, append the person's name. Only include when the person is the primary subject or recipient of the document.

**Valid Person Names:**
- `Joe` - Joseph Cotellese
- `Trish` - Trish Cotellese
- `Benjamin` - Son
- `Megan` - Daughter

**When to Include Person:**
- Medical documents (EOBs, bills, records)
- Personal legal documents (birth certificates, licenses)
- Individual financial documents (W2s, 1099s for specific person)
- Vehicle documents if ownership is individual

**When to Omit Person:**
- Joint documents (home insurance, mortgage, etc.)
- Family/household documents (utility bills, property tax)
- Documents that apply to the entire household

**Examples with Person:**
- `2025-03-20_Medical_EOB_Cardiology-Visit_Joe.pdf`
- `2024-11-15_Medical_Bill_Dermatology_Trish.pdf`
- `2010-08-15_Legal_Certificate_Birth-Benjamin.pdf`

**Examples without Person:**
- `2024-11-03_Home_Invoice_Roof-Repair.pdf` (applies to household)
- `2024-01-30_Insurance_Policy_Home-Flood.pdf` (joint policy)
- `2024-10-15_Utilities_Bill_Electric-PECO.pdf` (household bill)

## Description Formatting

### Use Hyphens Within Descriptions
- Use hyphens to separate words within the description component
- Do NOT use spaces or underscores within descriptions
- Capitalize each word (Title Case)

**Good Examples:**
- `Roof-Repair`
- `Adobe-Creative-Cloud`
- `Purchase-288-Green`
- `Q4-Statement`

**Bad Examples:**
- `Roof Repair` (spaces not allowed)
- `roof-repair` (not capitalized)
- `Roof_Repair` (underscores within descriptions)

### Keep Descriptions Concise
- Aim for 2-4 words
- Be specific enough to identify the document
- Include key identifiers (addresses, company names, specific services)

### Address References
When documents relate to a specific property, include the street address:
- Format: `123-Green` or `288-Green-St` (use hyphens)
- Include in description: `Purchase-288-Green`, `Inspection-288-Green`

### Company/Provider Names
Include specific company or provider names when relevant:
- `Adobe-CC` (use common abbreviations)
- `Vanguard-401k`
- `Chase-Checking`
- `PECO-Electric`

## Edge Cases and Disambiguation

### Documents with Multiple Categories
Some documents could fit multiple categories. Use this priority:
1. **Primary purpose** - What is the document's main function?
2. **Most searchable** - Which category would you most likely search for?

**Examples:**
- Home insurance claim → `Insurance_Claim_Roof-Damage` (primary purpose is insurance)
- Medical bill payment receipt → `Medical_Receipt_Payment-Dermatology` (medical context more important)
- Vehicle insurance → `Insurance_Policy_Auto-Honda` or `Vehicle_Insurance_Honda` (either works, be consistent)

### Tax-Related Documents
- Business receipts → Use business filing system (separate)
- Personal tax returns → `Tax_Return_Federal-2023`
- Documents that support personal taxes but fit another category → Use that category (e.g., medical bills stay `Medical_Bill_...`)

### Ambiguous Dates
- Use document date (when it was issued/created), not when received or filed
- If unclear, use the most prominent date on the document
- If no date visible, use scan/download date and flag for review

### File Extensions
- Always preserve original extension: `.pdf`, `.jpg`, `.png`, etc.
- Format applies to all file types, not just PDFs

## Consistency Tips

1. **Create a conventions log** - As you file documents, note any new patterns or edge cases
2. **Abbreviate consistently** - If you use "CC" for Creative Cloud, always use it
3. **Address format** - Pick one format for addresses and stick to it (e.g., always `288-Green`)
4. **Date precision** - Always use `YYYY-MM-DD` format, never vary
5. **Review periodically** - Every few months, search for inconsistencies and batch-rename if needed
