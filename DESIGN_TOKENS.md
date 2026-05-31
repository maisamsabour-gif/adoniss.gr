# ADONIS Design Token System — v1.0

Single source of truth for all brand colors, interactions, and component styles.  
**File:** `adonis/static/css/tokens.css`

---

## Brand Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--adonis-navy-900` | `#0B1B33` | Darkest bg — hero, footer, header |
| `--adonis-navy-700` | `#1A2B4A` | Medium navy — cards, hover states |
| `--adonis-navy-500` | `#2C4570` | Lighter navy — borders, dividers |
| `--adonis-blue-600` | `#1E5AA8` | Royal blue — links, CTAs, active |
| `--adonis-blue-300` | `#5B9BD5` | Hover tint on dark surfaces |
| `--adonis-blue-100` | `#EAF2FF` | Soft tint backgrounds |
| `--adonis-white`    | `#FFFFFF` | White |
| `--adonis-gray-50`  | `#F5F7FA` | Alternating section bg |
| `--adonis-gray-200` | `#E2E6ED` | Borders, form inputs |
| `--adonis-gray-500` | `#8A93A6` | Secondary text, placeholder |
| `--adonis-gray-800` | `#2D3340` | Primary text on white |
| `--adonis-gold`     | `#C9A961` | Premium accent — ≤ 5% of any page |

---

## Semantic Mappings (use these in component CSS)

### Backgrounds
| Token | Maps to |
|-------|---------|
| `--color-bg` | `--adonis-white` |
| `--color-bg-alt` | `--adonis-gray-50` |
| `--color-bg-dark` | `--adonis-navy-900` |
| `--color-bg-card` | `--adonis-white` |
| `--color-bg-card-hover` | `--adonis-blue-100` |

### Text
| Token | Maps to |
|-------|---------|
| `--color-text` | `--adonis-gray-800` — body text on white |
| `--color-text-muted` | `--adonis-gray-500` — secondary / meta |
| `--color-text-invert` | `--adonis-white` — text on dark bg |
| `--color-text-heading` | `--adonis-navy-900` — headings on white |

### Borders
| Token | Maps to |
|-------|---------|
| `--color-border` | `--adonis-gray-200` |
| `--color-border-dark` | `rgba(255, 255, 255, 0.10)` |

### Primary (navy)
| Token | Maps to |
|-------|---------|
| `--color-primary` | `--adonis-navy-900` |
| `--color-primary-hover` | `--adonis-navy-700` |
| `--color-primary-active` | `--adonis-navy-500` |

### Interactive (royal blue)
| Token | Maps to |
|-------|---------|
| `--color-interactive` | `--adonis-blue-600` |
| `--color-interactive-hover` | `--adonis-blue-300` |
| `--color-interactive-soft` | `--adonis-blue-100` |

---

## Component Recipes

### Navbar / Header
```css
background: var(--nav-bg);                  /* rgba(11, 27, 51, 0.65) — transparent */
background: var(--nav-bg-scrolled);         /* rgba(11, 27, 51, 0.96) — on scroll */
border-bottom: 1px solid var(--nav-border);
```
**Nav link:** `color: var(--nav-link-color)` | hover: `background: var(--nav-link-hover-bg)`  
**Active:** `border-bottom: 2px solid var(--nav-link-active-border)`

### Dropdown / Submenu
```css
background: var(--dropdown-bg);        /* white */
color:       var(--dropdown-text);     /* charcoal */
border:      1px solid var(--dropdown-border);
box-shadow:  var(--dropdown-shadow);
```
Hover row: `background: var(--dropdown-hover-bg)` + `color: var(--dropdown-hover-text)`

### Buttons
```css
/* Primary */
background: var(--btn-primary-bg);    /* navy */
color:      var(--btn-primary-text);  /* white */

/* Outline */
border: 1px solid var(--btn-outline-border);
color:  var(--btn-outline-text);

/* Ghost (on dark surfaces) */
background: var(--btn-ghost-bg);
border: 1px solid var(--btn-ghost-border);
```

### Forms
```css
border:       1px solid var(--input-border);
border-focus: 1px solid var(--input-border-focus);
color:        var(--input-text);
placeholder:  var(--input-placeholder);
box-shadow:   var(--input-shadow-focus); /* on :focus */
```

---

## Gold Usage Rule — **≤ 5% surface per page**

Gold (`--adonis-gold: #C9A961`) is allowed ONLY for:
- Logo mark / wordmark
- Price / investment amount highlights
- A single primary CTA button per page (hero or consult section)

**Never use gold for:**  navigation, section backgrounds, body text, card borders, hover states, secondary buttons.

---

## How to Add a New Color

1. Add the primitive to `tokens.css` under `/* 1. Primitive color ramp */`
2. Add a semantic mapping under `/* 2. Semantic mappings */`
3. Use only `var(--color-*)` in component CSS

```css
/* tokens.css */
:root {
  --adonis-teal-600: #0D9488;  /* NEW primitive */
  --color-confirmation: var(--adonis-teal-600); /* semantic alias */
}
```

---

## File Load Order (every page)

```html
<link rel="stylesheet" href="{% static 'css/tokens.css' %}">      <!-- 1st -->
<link rel="stylesheet" href="{% static 'css/style.min.css' %}">   <!-- 2nd (main site) -->
<!-- or -->
<link rel="stylesheet" href="{% static 'css/fa-new/home.css' %}"> <!-- 2nd (fa-new) -->
```

---

## Files Using This Token System

| File | Status |
|------|--------|
| `css/tokens.css` | Master token file |
| `css/style.css` | Updated — `:root` maps to tokens |
| `css/golden_visa_landing.css` | Updated — `--gv-*` maps to tokens |
| `css/fa-new/home.css` | Updated — `--adonis-fa-new-*` maps to tokens |
| `css/fa-new/hero-scroll.css` | Uses navy/blue brand colors |

---

## Legacy Variable Names (style.css only)

These confusingly-named variables exist in `style.css` for backwards compatibility.  
**Do NOT use them in new CSS.** They map to the correct brand colors:

| Legacy name | Actual meaning | Maps to |
|-------------|---------------|---------|
| `--color-gold` | Primary blue | `--adonis-blue-600` |
| `--color-white` | Dark navy bg | `--adonis-navy-900` |
| `--color-black` | White text | `--adonis-white` |
