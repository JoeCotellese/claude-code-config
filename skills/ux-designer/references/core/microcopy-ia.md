# ABOUTME: Micro-copy best practices and information architecture principles.
# ABOUTME: Covers button labels, error messages, content hierarchy, empty states, and onboarding copy.

# Micro-copy & Information Architecture

This reference covers the words and structure that make interfaces understandable: micro-copy (small pieces of UI text) and information architecture (how content is organized).

---

## Micro-copy Principles

### What is Micro-copy?
The small bits of text that guide users through an interface:
- Button labels
- Form labels and placeholders
- Error messages
- Success messages
- Tooltips and hints
- Empty states
- Confirmation dialogs
- Navigation labels

### Core Principles

**1. Be Clear, Not Clever**
- Clarity beats creativity
- Use familiar words
- Avoid jargon unless audience expects it
- Test with real users

**2. Be Concise**
- Every word should earn its place
- Front-load important information
- Cut filler words (just, simply, please)
- Short sentences, short paragraphs

**3. Be Helpful**
- Guide users toward success
- Anticipate questions
- Provide next steps
- Reduce cognitive load

**4. Be Human**
- Use natural language
- Match brand voice consistently
- Avoid robotic phrasing
- Show empathy in error states

---

## Button Labels

### Best Practices

| Pattern | Bad | Good |
|---------|-----|------|
| Use verbs | "Submit" | "Create account" |
| Be specific | "OK" | "Save changes" |
| Describe outcome | "Yes" | "Delete project" |
| Match the action | "Send" | "Send message" |

### Common Button Patterns

| Action | Recommended Label |
|--------|-------------------|
| Save data | "Save" or "Save changes" |
| Create item | "Create [item]" |
| Delete | "Delete [item]" |
| Cancel process | "Cancel" |
| Dismiss modal | "Done" or "Close" |
| Navigate forward | "Continue" or "Next" |
| Submit form | "[Verb] [noun]" e.g., "Create account" |
| Confirm destructive | Name the action: "Delete project" |

### Button Pairs

| Context | Primary | Secondary |
|---------|---------|-----------|
| Save dialog | "Save changes" | "Discard" |
| Delete confirmation | "Cancel" | "Delete" (destructive) |
| Form submission | "Create account" | "Cancel" |
| Upsell modal | "Upgrade now" | "Maybe later" |

**Note:** For destructive actions, make the safe option (Cancel) the primary/default button.

---

## Form Labels & Placeholders

### Labels

**Guidelines:**
- Always use visible labels (not just placeholders)
- Be concise but descriptive
- Use sentence case
- Indicate required vs optional clearly

| Bad | Good |
|-----|------|
| "Enter your email address here" | "Email" |
| "NAME" | "Full name" |
| "DOB" | "Date of birth" |

### Placeholders

**Purpose:** Show format or example, not the label

| Field | Placeholder |
|-------|-------------|
| Email | "name@example.com" |
| Phone | "(555) 555-5555" |
| Date | "MM/DD/YYYY" |
| Search | "Search products..." |

**Caution:** Placeholders disappear when typing. Never use as the only label.

### Help Text

**When to use:**
- Format requirements not obvious
- Security/privacy explanation needed
- Additional context helps completion

**Examples:**
- "Password must be at least 8 characters"
- "We'll never share your email"
- "Enter the name as it appears on your card"

---

## Error Messages

### Anatomy of a Good Error Message

1. **What happened** - State the problem clearly
2. **Why it happened** - Explain the cause (if helpful)
3. **How to fix it** - Provide actionable guidance

### Error Message Patterns

| Bad | Good |
|-----|------|
| "Invalid input" | "Please enter a valid email address" |
| "Error" | "That password is too short. Use at least 8 characters." |
| "Failed" | "We couldn't save your changes. Check your connection and try again." |
| "404" | "Page not found. It may have been moved or deleted." |

### Tone in Error Messages

**Don't blame the user:**
- Bad: "You entered an invalid email"
- Good: "That doesn't look like an email address"

**Be helpful, not technical:**
- Bad: "Error 500: Internal server error"
- Good: "Something went wrong on our end. Please try again."

**Show empathy:**
- Bad: "Transaction failed"
- Good: "We couldn't process your payment. Your card wasn't charged."

### Error Message Placement

- Inline: Below the field with the problem
- Summary: Top of form for multiple errors
- Toast/Banner: System-level errors
- Page: Unrecoverable errors (404, 500)

---

## Success Messages & Confirmation

### Success Message Guidelines

- Confirm what happened
- Indicate what's next (if applicable)
- Be brief

**Examples:**
- "Changes saved"
- "Message sent"
- "Account created. Check your email to verify."
- "Payment successful. You'll receive a receipt shortly."

### Confirmation Dialogs

**When to use:**
- Destructive actions
- Irreversible changes
- High-stakes decisions

**Structure:**
1. **Title**: State the action (e.g., "Delete project?")
2. **Body**: Explain consequences
3. **Actions**: Clear, specific button labels

**Example:**
```
Delete "My Project"?

This will permanently delete the project and all its files.
This action cannot be undone.

[Cancel]  [Delete project]
```

---

## Empty States

### Purpose
Turn "nothing here" into "here's what you can do."

### Components

1. **Illustration** (optional): Visual context
2. **Headline**: What this space is for
3. **Description**: Why it's empty, what goes here
4. **Action**: How to add content

### Examples by Context

**First-time use:**
```
Welcome to Projects

This is where your projects will appear.
Create your first project to get started.

[Create project]
```

**No search results:**
```
No results for "xyz"

Try different keywords or check your spelling.
You can also browse all products.

[Browse all]
```

**Completed tasks:**
```
All done!

You've completed all your tasks for today.
Enjoy your free time, or add something new.

[Add task]
```

**Error state:**
```
Couldn't load your data

Check your internet connection and try again.

[Try again]
```

---

## Onboarding Copy

### Principles

- **Progress, not perfection**: Get users to value quickly
- **Just-in-time**: Teach when relevant, not all at once
- **Skippable**: Don't trap users in tutorials
- **Benefit-focused**: "You can..." not "This feature..."

### Onboarding Patterns

**Welcome screen:**
```
Welcome to [App]

[One sentence value proposition]

[Get started]
```

**Feature introduction:**
```
New: Dark Mode

Switch to dark mode to reduce eye strain
and save battery.

[Try it]  [Not now]
```

**Tooltip/Coach mark:**
```
Tap here to add your first item
```

**Progressive disclosure:**
- Show basics first
- Reveal advanced features as user progresses
- "Did you know..." for power features

---

## Information Architecture

### What is IA?
How content is organized, labeled, and connected. Good IA means users can find what they need.

### IA Principles

**1. Organize for users, not org charts**
- Group by user tasks, not internal structure
- Use language users understand
- Test with card sorting

**2. Create clear hierarchy**
- Broad and shallow beats deep and narrow
- Aim for 7±2 items per level
- Most important items first

**3. Use meaningful labels**
- Descriptive, not clever
- Consistent terminology
- Avoid jargon

**4. Provide multiple paths**
- Search + browse + shortcuts
- Cross-links between related items
- Recent/favorites for frequent access

### Navigation Labels

**Best Practices:**
- Use nouns for destinations ("Settings" not "Set up")
- Be specific ("Order history" not "History")
- Be consistent (don't mix "Preferences" and "Settings")
- Front-load distinctive words

| Bad | Good |
|-----|------|
| "Stuff" | "Files" |
| "More" | "Settings" |
| "Manage" | "Account" |
| "Go to dashboard" | "Dashboard" |

### Content Hierarchy

**Visual signals:**
- Size: Larger = more important
- Position: Top/left = higher priority
- Space: More space = more importance
- Depth: Primary → Secondary → Tertiary

**Structural signals:**
- Headings create outline
- Groups show relationships
- Sequence implies process

---

## Writing for Scanning

### How Users Read

**They don't read, they scan:**
- F-pattern on text-heavy pages
- Headlines and first sentences
- Links and buttons
- Bulleted lists

### Writing for Scanners

**Headlines:**
- Front-load keywords
- Be specific and descriptive
- Use parallel structure in lists

**Body text:**
- One idea per paragraph
- Lead with the conclusion
- Use bullets for lists
- Bold key terms (sparingly)

**Links:**
- Descriptive text ("View pricing" not "Click here")
- Indicate destination
- Don't use "click here" or "learn more" alone

---

## Content Strategy Checklist

### Before Writing

- [ ] Who is the audience?
- [ ] What do they need to accomplish?
- [ ] What do they already know?
- [ ] What's the emotional context?
- [ ] What voice/tone is appropriate?

### While Writing

- [ ] Is it clear?
- [ ] Is it concise?
- [ ] Is it helpful?
- [ ] Is it human?
- [ ] Does it guide to action?

### After Writing

- [ ] Read it aloud
- [ ] Cut unnecessary words
- [ ] Check for jargon
- [ ] Verify consistency
- [ ] Test with users

---

## Quick Reference

### Words to Avoid

| Instead of | Use |
|------------|-----|
| Please | (just say the thing) |
| Simply/Just | (implies it's easy when it might not be) |
| Invalid | "doesn't match" or be specific |
| Abort | Cancel |
| Execute | Run |
| Terminate | End or Stop |
| Click here | [Descriptive link text] |

### Voice & Tone

**Voice** = Personality (consistent)
**Tone** = Emotional inflection (varies by context)

| Context | Tone |
|---------|------|
| Success | Celebratory, brief |
| Error | Empathetic, helpful |
| Onboarding | Welcoming, encouraging |
| Settings | Neutral, clear |
| Destructive action | Serious, clear |
