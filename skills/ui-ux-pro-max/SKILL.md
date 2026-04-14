# UI UX Pro Max

An AI skill that provides design intelligence for building professional UI/UX across multiple platforms and frameworks.

## Overview

UI UX Pro Max is a comprehensive design system generator that analyzes your project requirements and generates complete, tailored design systems. It includes:

- **67 UI Styles** - Glassmorphism, Claymorphism, Minimalism, Brutalism, Neumorphism, Bento Grid, Dark Mode, AI-Native UI, and more
- **161 Color Palettes** - Industry-specific palettes aligned 1:1 with the 161 product types
- **57 Font Pairings** - Curated typography combinations with Google Fonts imports
- **25 Chart Types** - Recommendations for dashboards and analytics
- **13 Tech Stacks** - React, Next.js, Astro, Vue, Nuxt.js, Nuxt UI, Svelte, SwiftUI, React Native, Flutter, HTML+Tailwind, shadcn/ui, Jetpack Compose
- **99 UX Guidelines** - Best practices, anti-patterns, and accessibility rules
- **161 Reasoning Rules** - Industry-specific design system generation

## Directory Structure

```
src/ui-ux-pro-max/
├── data/          # CSV databases (styles, colors, typography, etc.)
├── scripts/       # Python search engine & design system generator
└── templates/     # Platform-specific templates
```

## Usage

### Design System Generation

```bash
# Generate design system with ASCII output
python3 skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness" --design-system -p "Serenity Spa"

# Generate with Markdown output
python3 skills/ui-ux-pro-max/scripts/search.py "fintech banking" --design-system -f markdown

# Domain-specific search
python3 skills/ui-ux-pro-max/scripts/search.py "glassmorphism" --domain style
python3 skills/ui-ux-pro-max/scripts/search.py "elegant serif" --domain typography
python3 skills/ui-ux-pro-max/scripts/search.py "dashboard" --domain chart

# Stack-specific guidelines
python3 skills/ui-ux-pro-max/scripts/search.py "form validation" --stack react
python3 skills/ui-ux-pro-max/scripts/search.py "responsive layout" --stack html-tailwind
```

### Persist Design System

```bash
# Generate and persist to design-system/MASTER.md
python3 skills/ui-ux-pro-max/scripts/search.py "SaaS dashboard" --design-system --persist -p "MyApp"

# Also create a page-specific override file
python3 skills/ui-ux-pro-max/scripts/search.py "SaaS dashboard" --design-system --persist -p "MyApp" --page "dashboard"
```

## Example Output

The design system generator produces a comprehensive output including:

- **Pattern** - Landing page structure recommendations
- **Style** - UI style with keywords and best use cases
- **Colors** - Primary, secondary, CTA, background, and text colors
- **Typography** - Font pairings with Google Fonts links
- **Key Effects** - Recommended animations and interactions
- **Anti-patterns** - What NOT to do for your industry
- **Pre-delivery Checklist** - Accessibility and UX validation

## Supported Industries

The reasoning engine includes specialized rules for:

| Category | Examples |
|----------|----------|
| **Tech & SaaS** | SaaS, Micro SaaS, B2B Service, Developer Tool / IDE, AI/Chatbot Platform, Cybersecurity Platform |
| **Finance** | Fintech/Crypto, Banking, Insurance, Personal Finance Tracker, Invoice & Billing Tool |
| **Healthcare** | Medical Clinic, Pharmacy, Dental, Veterinary, Mental Health, Medication Reminder |
| **E-commerce** | General, Luxury, Marketplace (P2P), Subscription Box, Food Delivery |
| **Services** | Beauty/Spa, Restaurant, Hotel, Legal, Home Services, Booking & Appointment |
| **Creative** | Portfolio, Agency, Photography, Gaming, Music Streaming, Photo/Video Editor |
| **Lifestyle** | Habit Tracker, Recipe & Cooking, Meditation, Weather, Diary, Mood Tracker |
| **Emerging Tech** | Web3/NFT, Spatial Computing, Quantum Computing, Autonomous Drone Fleet |

## Prerequisites

Python 3.x is required for the search script.

## License

MIT License - see LICENSE file for details.

## Source

https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
