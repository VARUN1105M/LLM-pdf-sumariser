# Design Document (design.md)
## The Lenny Growth Assistant

**Design Philosophy:** World-Class Developer & Operator UX  
**Aesthetic:** Modern Dark Glassmorphism with Warm Amber Accent (`#F59E0B`)  
**Typography:** Plus Jakarta Sans (UI) & JetBrains Mono (Code/Metadata)  

---

## 1. UI/UX Principles

1. **Information Density without Clutter:** Growth operators demand deep tactical information. The interface balances compact, clean layouts with high typography contrast.
2. **Side-by-Side Co-Presence (Claude Artifacts Model):** Generating artifacts (playbooks, dashboards, essays) must never obscure the ongoing dialogue. The viewport splits fluidly into conversation on the left and active artifact on the right.
3. **Transparent Grounding:** Citations are not hidden behind footnotes. Grounded transcript references are displayed in structured citation cards featuring the guest's name, timestamp, and quotation excerpt.
4. **Instant Actionability:** One-click prompt chips allow an evaluator to experience key capabilities (Ship 30 for 30 essay, Shreyas Doshi L/G/P, Brian Chesky Founder Mode) in under 2 seconds.

---

## 2. Information Architecture

```
+---------------------------------------------------------------------------------------+
|  TOP BAR: Active Session Title | Model Status Indicator | Toggle Artifact Viewer     |
+---------------------+-----------------------------------+-----------------------------+
|  SIDEBAR (310px)    |  CHAT FEED (Flex-1)               |  ARTIFACT VIEWER (50% Split)|
|                     |                                   |                             |
|  [+ New Chat]       |  - Welcome Hero Card              |  [Preview] [Source] [📋] [✕]|
|                     |  - User Bubbles (Right-aligned)   |                             |
|  [Model Switcher]   |  - Assistant Bubbles (Left)       |  +-----------------------+  |
|   Ollama / Claude   |    - Markdown Formatted Text      |  | Sandboxed HTML /      |  |
|                     |    - Interactive Artifact Cards   |  | Formatted Markdown    |  |
|  [Curated Chips]    |    - Structured Citation Drawer   |  | Live Render           |  |
|  - Shreyas L/G/P    |                                   |  +-----------------------+  |
|  - Elena PLG        |  +-----------------------------+  |  Security Banner:           |
|  - Ship 30 Essay    |  | [ Chat Input Box         ]  |  | Sandboxed execution         |
|                     |  +-----------------------------+  |                             |
|  [Session History]  |                                   |                             |
+---------------------+-----------------------------------+-----------------------------+
```

---

## 3. Key Interaction States

### 3.1 Initial Empty State
- Displays the branded welcome hero card with key feature pills (*Grounded Citations*, *Ship 30 Skill*, *Artifact Viewer*, *Model Switcher*).
- Sidebar highlights prompt chips for immediate 1-click exploration.

### 3.2 Reasoning & Retrieval Loading State
- Input button locks with smooth transition.
- Assistant bubble displays an amber pulsating spinner with real-time text feedback: `Searching Lenny's Podcast transcripts & reasoning...`.

### 3.3 Artifact Generation State
- When an assistant generates an `<artifact>` XML block or HTML widget:
  - A prominent gradient callout card is rendered directly in the chat stream: `📑 [Title] - Click to view in side panel`.
  - The right-hand Artifact Viewer opens automatically with smooth cubic-bezier transitions.
  - The user can toggle between **Preview** (live rendering) and **Source** (raw code with 1-click copy).

### 3.4 Responsive Mobile/Tablet Breakpoints
- **Desktop ($\ge 1200\text{px}$):** 3-column view (Sidebar, Chat, Artifact Viewer).
- **Laptop / Tablet ($992\text{px} - 1199\text{px}$):** Sidebar collapses into an off-canvas drawer with hamburger trigger; Chat and Artifact pane share 50/50 split.
- **Mobile ($< 992\text{px}$):** Full-width stacked view; Artifact Viewer overlays full-screen with clear dismiss handle.

---

## 4. Accessibility & Inclusive Design (a11y)

1. **Color Contrast:** Foreground text (`#F3F4F6` and `#F59E0B`) on dark backgrounds (`#0A0E17`, `#111827`) satisfies WCAG AA contrast ratio of $> 7:1$.
2. **Keyboard Navigation:** Full tab order supported across sidebar buttons, model select dropdown, prompt chips, and message textarea.
3. **Form Semantics:** `aria-label` tags and semantic HTML form elements enable assistive screen reader parsing.
4. **Untrusted HTML Protection:** Sandboxed `iframe` uses `sandbox="allow-scripts"` without `allow-same-origin`, preventing untrusted injected styles or scripts from reading main-page DOM or cookies.
