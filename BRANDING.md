# GFT Branding & Visual Identity — Web Application Specification

> **Source**: GFT Beyond Brand Book series and internal brand guidelines
> All branding details below come from the GFT Beyond Brand Book series and related internal documentation.

**References:**
- [GFT Beyond Brand Book EN 2025](https://gft365.sharepoint.com/sites/Our_Brand/Shared%20Documents/03_GFT_Beyond_Brand_Book_EN_2025.pdf?web=1)
- [GFT Let's Go Beyond Brand Book (Internal Only)](https://gft365.sharepoint.com/sites/Our_Brand/SiteAssets/SitePages/TopicHome(1)/GFT_Let-s_Go_Beyond_Brand_Book_Internal_Only.pdf?web=1)

---

# GFT Branding & Visual Identity — Web Application Specification

## 1. Brand Principles & Intent

The GFT brand identity is built on clarity, trust, and consistency across all digital and physical touchpoints. The brand book emphasizes that every application must reflect a **cohesive, modern, and next‑gen technology identity**, ensuring visual harmony and intuitive user experience.

For web applications, this means:

- Clean, minimalistic layouts
- Strong hierarchy and high accessibility
- Consistent use of colors, typography, spacing, and iconography
- Seamless integration of semantic (UI state) colors with the GFT core palette

---

## 2. Color System

### 2.1 Core Color World (GFT Primary Identity)

The GFT color world represents the brand visually and is the foundation for all digital design. While the Brand Book spans multiple palettes, the **semantic colors are most critical** for web applications, as they ensure clarity, accessibility, and UX consistency.

### 2.2 Semantic Colors (for UI States & System Feedback)

These are mandatory for all interactive interfaces:

| Purpose              | HEX         | RGB           | CMYK             |
|----------------------|-------------|---------------|------------------|
| **Error Red**        | `#D20000`   | 210 / 0 / 0   | 0 / 90 / 100 / 0 |
| **Warning Yellow**   | `#FFBB00`   | 255 / 187 / 0 | 0 / 30 / 95 / 0  |
| **Success Green**    | `#00B427`   | 0 / 180 / 39  | 66 / 0 / 100 / 0 |
| **Information Blue** | `#006BD6`   | 0 / 107 / 214 | 85 / 45 / 0 / 0  |

**Usage rules:**

- Must be used consistently across all components (forms, alerts, buttons, validation messages, badges)
- Must remain visually harmonious with GFT’s primary color world
- Should meet WCAG AA contrast minimums in all combinations

---

## 3. Logo Usage

- GFT logo must appear **unmodified** and with adequate clear space
- For co‑branding scenarios:
  - Logos must appear **horizontally aligned**
  - Same visual size for both logos
  - Separated by a **vertical divider line** equal to *1 logo square height / 20* (example: 5 mm → 0.25 mm line)
  - GFT logo is always placed **last**

This applies to login screens, splash pages, dashboards, customer portals, or any shared‑brand application surface.

---

## 4. Typography

From the GFT Brand Book (section “Brand Identity / Visual Identity”):

- Typography must remain **clean, modern, and consistent** with the brand tone
- Web applications should adhere to the type hierarchy defined in the Brand Book to ensure clarity and scalability

Use cases:

- Clear headline hierarchy (H1→H6)
- Larger spacing and comfortable line-height
- Uniform type weights to maintain a professional tone

If your system uses design tokens, define:

```css
font-primary: <brand-approved font>;
font-size-base: 16px;
font-line-height-base: 1.5;
```

> **Note**: The Brand Book specifies typography but does not provide specific font names — use official brand fonts from Papirfly or the global MarCom team.

---

## 5. Imagery & Visual Language

Guidelines from SharePoint Theme & Brand Book:

- Use updated **Beyond 2025** visuals (headers, images, icons) available in SharePoint when editing
- Imagery style must follow the GFT visual language: modern, clean, technology‑forward, human‑centric

Use cases:

- Consistent header visuals
- Icons from the official set only
- Avoid decorative, off‑brand, or mixed‑style imagery

---

## 6. Components & Interaction Design

### General Rules

- All UI components must adhere to the brand’s **semantic color rules** for states
- Spacing, padding, and grid layout should reflect GFT’s clean, minimalistic style
- Interactions must be intuitive and aligned with digital accessibility principles

### Examples:

- **Buttons**:
  - Primary = brand core color
  - Success/Warning/Error states = semantic colors above
- **Forms**:
  - Validation → error red, info blue
- **Alerts**:
  - Success / Info / Warning / Error aligned exactly to semantic palette

---

## 7. Accessibility Guidelines

Based on the Brand Book’s emphasis on intuitive, understandable visual cues:

- All color use must support **clear meaning at a glance**
- Pair color with secondary cues (icons, text) for accessibility
- Maintain minimum 4.5:1 contrast

---

## 8. Governance & Resources

### For branding compliance:

- **Email**: <brandmanagement@gft.com>

### For imagery & assets:

- GFT Papirfly Brand Hub (official asset library)
- [SharePoint Theme Guideline](https://gft365.sharepoint.com/_layouts/15/Doc.aspx?sourcedoc=%7B51A0DCB4-20C1-49FD-B40A-C03E385D146C%7D&file=1225_GFT_Beyond_Sharepoint_Theme_Guideline.pptx)

### For SharePoint or internal platform updates:

- **Email**: <EmployeeCommunications@gft.com>

---

## 9. Deliverable‑Ready Summary for Web App Specs

Include these in your final specification:

### Branding Requirements

- Follow GFT Brand Book (Beyond 2025) for visual identity
- Use semantic colors exactly as defined
- Use approved fonts from brand hub
- Use GFT imagery, quick link visuals, and icons

### UI Requirements

- Ensure state consistency using semantic colors
- Ensure accessibility (WCAG AA)
- Keep layout minimalistic, modern, and clean

### Logo Requirements

- GFT logo unmodified, with proper spacing
- Use co‑branding rules where applicable

### Source of Truth

- GFT Beyond Brand Books (02, 03, 07 editions)
- SharePoint Theme Guideline
- Papirfly brand hub
