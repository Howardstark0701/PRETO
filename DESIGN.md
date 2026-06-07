---
name: Tactical Intelligence System
colors:
  surface: '#0d141d'
  surface-dim: '#0d141d'
  surface-bright: '#333a44'
  surface-container-lowest: '#080f17'
  surface-container-low: '#151c25'
  surface-container: '#192029'
  surface-container-high: '#232a34'
  surface-container-highest: '#2e353f'
  on-surface: '#dce3f0'
  on-surface-variant: '#bacac4'
  inverse-surface: '#dce3f0'
  inverse-on-surface: '#2a313b'
  outline: '#84948f'
  outline-variant: '#3b4a45'
  surface-tint: '#27dfbe'
  primary: '#46f1cf'
  on-primary: '#00382e'
  primary-container: '#00d4b4'
  on-primary-container: '#005648'
  inverse-primary: '#006b5a'
  secondary: '#c0c6db'
  on-secondary: '#293040'
  secondary-container: '#404758'
  on-secondary-container: '#aeb5c9'
  tertiary: '#cfd9ec'
  on-tertiary: '#27313f'
  tertiary-container: '#b3bdcf'
  on-tertiary-container: '#424c5c'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#55fcda'
  primary-fixed-dim: '#27dfbe'
  on-primary-fixed: '#00201a'
  on-primary-fixed-variant: '#005143'
  secondary-fixed: '#dce2f7'
  secondary-fixed-dim: '#c0c6db'
  on-secondary-fixed: '#141b2b'
  on-secondary-fixed-variant: '#404758'
  tertiary-fixed: '#d9e3f6'
  tertiary-fixed-dim: '#bdc7d9'
  on-tertiary-fixed: '#121c2a'
  on-tertiary-fixed-variant: '#3d4756'
  background: '#0d141d'
  on-background: '#dce3f0'
  surface-variant: '#2e353f'
typography:
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Karla
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Karla
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Karla
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  data-lg:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  data-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 12px
  margin: 16px
---

## Brand & Style

This design system is engineered for high-stakes intelligence analysis, open-source investigation, and complex data visualization. The aesthetic is rooted in technical minimalism and "Gothamic" brutalism, prioritizing information density and rapid cognitive processing over decorative elements.

The target audience consists of analysts and operators who require a "heads-up display" (HUD) experience. The emotional response is one of precision, authority, and cold efficiency. Every pixel must serve a functional purpose; there is no room for ornamentation. The visual language utilizes a dark-mode-first approach with sharp edges, technical monospaced accents, and a restricted palette to reduce eye strain during long-term monitoring sessions.

## Colors

The palette is anchored in deep, cold blacks and slate blues to create a high-contrast environment that makes data "pop."

- **Base Background:** Used for the lowest level of the application shell.
- **Panel Background:** Used for primary work areas, sidebars, and modular widgets.
- **Primary Accent:** A high-visibility cyan used sparingly for active states, primary actions, and critical data points.
- **Success/Warning/Danger:** Utilize the primary cyan for success, a muted amber for warnings, and a sharp crimson for alerts, all maintaining the same vibrance levels to ensure UI consistency.

## Typography

The typographic hierarchy is designed for maximum legibility in data-dense environments.

- **Space Grotesk** is used for headlines and navigation anchors, providing a geometric, technical feel.
- **Karla** serves as the primary workhorse for body text and UI labels, chosen for its excellent readability and space efficiency.
- **JetBrains Mono** is reserved for metadata, coordinates, timestamps, and code snippets. It signals to the user that the information is "raw" or "system-generated."

Line heights are kept tight to maximize the amount of information visible on screen without sacrificing the vertical rhythm.

## Layout & Spacing

This design system employs a **fluid grid** model with a hard 4px baseline. The layout is modular, resembling a command-center dashboard where panels can be resized or collapsed.

- **Density:** Information density is "High." Margins and gutters are minimized (12px-16px) to allow for multi-column data views and complex graph visualizations.
- **Breakpoints:**
  - **Desktop (1440px+):** 12-column grid, modular panels.
  - **Tablet (768px - 1439px):** 6-column grid, sidebars collapse into icons.
  - **Mobile (Under 768px):** Single-column stack, focus on critical alerts and search.
- **Alignment:** All elements must align to the 4px grid. Components should use `space-between` logic to push data to the edges of containers, emphasizing the "no wasted space" philosophy.

## Elevation & Depth

In this design system, depth is conveyed through **tonal layering** and **low-contrast outlines** rather than traditional shadows. Shadows are strictly prohibited to maintain the "flat HUD" aesthetic.

- **Level 0 (Base):** #0b0e14. Used for the global background.
- **Level 1 (Panels):** #111827. Used for the primary container surfaces.
- **Level 2 (Inlays/Modals):** #1f2937. Used for nested elements or floating menus.
- **Borders:** All panels and interactive elements are defined by a 1px solid border (#374151). When an element is focused or active, the border shifts to the primary accent color (#00d4b4).
- **Separators:** 1px lines are used to bisect data rows within panels, creating a clear, spreadsheet-like structure.

## Shapes

The shape language is **Sharp (0px)**. All containers, buttons, inputs, and cards must have square corners. This reinforces the technical, industrial nature of the system and ensures that elements can be packed tightly together without the visual "gaps" created by rounded corners.

The only exception to this rule is for iconography or specific circular status indicators (e.g., online/offline dots).

## Components

### Buttons
- **Primary:** Solid #00d4b4 background with #0b0e14 text. Sharp corners.
- **Secondary:** Transparent background, 1px #00d4b4 border, #00d4b4 text.
- **Ghost:** No border, muted gray text, turns primary cyan on hover.

### Inputs & Fields
- **Search/Text:** #111827 background with a bottom-only or subtle 1px border. Labels are always `label-caps` in JetBrains Mono, positioned above the field.
- **State:** Active inputs receive a full #00d4b4 border glow (0px spread).

### Data Tables
- The core of the system. High-density rows (32px height). Header cells use `label-caps`. Alternate row striping is not used; instead, 1px separators provide the grid.

### Chips & Tags
- Rectangular, 1px border, utilizing JetBrains Mono for the internal text. Used for "Attributes" or "Metadata."

### Cards/Panels
- Must include a "Header" area with a 1px bottom border and an "Action" area for panel-specific controls (e.g., Refresh, Expand, Filter).

### Graph Nodes
- Represented by sharp squares or diamonds. Connections between nodes are 1px solid lines, using primary cyan for "active" paths.
