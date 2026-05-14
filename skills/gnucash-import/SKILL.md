---
name: gnucash-import
effort: low
description: Process WSFS bank statement PDFs into QIF files for GnuCash import
user_invocable: true
trigger: /gnucash-import
arguments: "<pdf_path> [pdf_path...]"
---

# GnuCash Import Skill

Process WSFS Bank statement PDFs into QIF files importable by GnuCash.

## Setup

Copy `config.example.json` to `config.json` and fill in your paths:

```bash
cp config.example.json ~/.claude/skills/gnucash-import/config.json
```

## Config

Load settings from `~/.claude/skills/gnucash-import/config.json`:

- **gnucash_file** — path to your `.gnucash` file
- **bank_account** — GnuCash account path for the bank (e.g., `Assets:Current Assets:Checking Account`)
- **output_directory** — where to write QIF files and statement metadata
- **payee_mappings** — path to `payee_mappings.json` for raw description → clean payee name mapping

Additional derived settings:
- **QIF Type:** `!Type:Bank`
- **Output filename:** `YYYYMM.qif`
- **Statement metadata:** `<output_directory>/statement_metadata.json`

## Steps

### 1. Extract payee→account mappings from GnuCash

Run this to get existing mappings:

```bash
gunzip -c "<gnucash_file>" | python3 -c "
import sys, xml.etree.ElementTree as ET
tree = ET.parse(sys.stdin)
root = tree.getroot()
accounts = {}
for acct in root.iter('{http://www.gnucash.org/XML/gnc}account'):
    name = acct.find('{http://www.gnucash.org/XML/act}name').text
    acct_id = acct.find('{http://www.gnucash.org/XML/act}id').text
    parent_el = acct.find('{http://www.gnucash.org/XML/act}parent')
    accounts[acct_id] = {'name': name, 'parent': parent_el.text if parent_el is not None else None}
def get_path(aid):
    parts = []
    while aid and aid in accounts:
        parts.append(accounts[aid]['name'])
        aid = accounts[aid]['parent']
    parts.reverse()
    return ':'.join(parts[1:])
ns_trn = '{http://www.gnucash.org/XML/trn}'
ns_split = '{http://www.gnucash.org/XML/split}'
pm = {}
for txn in root.iter('{http://www.gnucash.org/XML/gnc}transaction'):
    d = txn.find(f'{ns_trn}description')
    if d is None or not d.text: continue
    for s in txn.findall(f'.//{ns_split}account'):
        if s.text in accounts:
            p = get_path(s.text)
            if p and not p.startswith('Assets:Current Assets:Checking'):
                pm[d.text.strip()] = p
for k in sorted(pm): print(f'{k} -> {pm[k]}')
"
```

Also load `payee_mappings.json` from the skill directory for raw description → clean payee name mapping.

Also extract the full chart of accounts for categorizing unknown payees.

### 2. Read each PDF

Use the Read tool to read the PDF. The WSFS statement format:

- **Header:** Statement Date on page 1 gives the year/month
- **Transaction Detail** section contains the transactions
- Each transaction starts with a date line (`Mon DD`) followed by type (ACH DEPOSIT, DEBIT CARD, POS PURCHASE, CHECK)
- Subsequent lines contain merchant details (terminal numbers, addresses, transaction dates)
- **Deposits** column = money in (positive), **Withdrawals** column = money out (shown as negative like `-$9.18`)

### 3. Parse and clean transactions

For each transaction extract:
- **Date:** `Mon DD` + year from statement header
- **Payee:** Clean using `payee_mappings.json`. Match raw description substrings (case-insensitive) to clean payee names. Strip terminal numbers, addresses, masked account numbers (`XXXX`), `TRAN DATE` lines.
- **Amount:** Deposits are positive, withdrawals are negative (strip the `-$` prefix, keep sign)
- **Memo:** Transaction type (ACH DEPOSIT, DEBIT CARD, POS PURCHASE, CHECK)

### 4. Categorize transactions

Match cleaned payee names against the payee→account map from step 1 (fuzzy match is fine). For unknown payees, suggest a category from the chart of accounts based on the description. Mark uncertain matches with `[?]`.

### 5. Check for duplicates

Before generating, check if the output QIF file already exists in the output directory. If it does, **warn the user** and ask before overwriting.

### 6. Present for confirmation

**Compact format for known payees:**
```
Jan 2026: 7 transactions, 7 known payees. Net: +$141.72 ✓
```

**Only show detail table for unknown/uncertain payees:**
```
Unknown/uncertain transactions requiring review:
| # | Date       | Payee                | Amount   | Suggested Account              |
|---|------------|----------------------|----------|--------------------------------|
| 3 | 01/15/2026 | Some New Vendor      |  -$50.00 | Expenses:Miscellaneous    [?]  |
```

Ask user to confirm or provide corrections (e.g., "3 -> Expenses:Office Supplies").

When user corrects an unknown payee, offer to add the mapping to `payee_mappings.json` for future use.

### 7. Generate QIF

Write the QIF file to the output directory, named `YYYYMM.qif`.

**QIF format:**
```
!Account
NAssets:Current Assets:Checking Account
TBank
^
!Type:Bank
DMM/DD/YYYY
PPayee Name
T-amount
LAccount:Path
MTransaction Type
^
```

- `D` = date in MM/DD/YYYY
- `P` = cleaned payee name
- `T` = amount (negative for withdrawals, positive for deposits)
- `L` = GnuCash account path
- `M` = memo (transaction type: DEBIT CARD, ACH DEPOSIT, POS PURCHASE, CHECK)
- `^` = end of transaction record

### 8. Write statement metadata

After generating QIF, update `statement_metadata.json` in the output directory. This is a running JSON file keyed by `YYYYMM` with balance and transaction data extracted from the statement's Balance Summary section.

Read the existing file first, add/update the entry for this month, and write it back:

```json
{
  "YYYYMM": {
    "statement_date": "MM/DD/YYYY",
    "beginning_balance": 1234.56,
    "ending_balance": 1345.67,
    "deposits": 200.00,
    "withdrawals": 88.89,
    "transaction_count": 7
  }
}
```

Verify continuity: the previous month's `ending_balance` should equal this month's `beginning_balance`. Warn if it doesn't.

### 9. Validate and report

Verify:
- Sum of all transactions matches the statement's net change (ending balance - beginning balance)
- Number of transactions matches the statement summary counts

Report the QIF file path, then output reconciliation info:

```
Import in GnuCash: File → Import → Import QIF...

Reconciliation (Actions → Reconcile):
  Statement Date: MM/DD/YYYY
  Ending Balance: $X,XXX.XX
```
