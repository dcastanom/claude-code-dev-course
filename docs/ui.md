# UI Coding Standards

## Component Library

**Only shadcn/ui components are permitted in this project.**

- Do NOT create custom UI components.
- Do NOT use raw HTML elements for UI (buttons, inputs, dialogs, etc.) when a shadcn/ui component exists.
- Do NOT install or use any other component library (e.g. MUI, Chakra, Radix directly, Headless UI).
- All shadcn/ui components live in `src/components/ui/` and are added via the shadcn CLI:

```bash
npx shadcn@latest add <component-name>
```

If a shadcn/ui component does not cover a need, raise it for discussion before building anything custom.

## Date Formatting

All date formatting must use **date-fns**.

Dates are displayed using ordinal day, abbreviated month, and 4-digit year:

| Date | Formatted output |
|------|-----------------|
| 2025-09-01 | 1st Sep 2025 |
| 2025-08-02 | 2nd Aug 2025 |
| 2026-01-03 | 3rd Jan 2026 |
| 2024-06-04 | 4th Jun 2024 |

Use the `format` function from `date-fns` with the token string `"do MMM yyyy"`:

```ts
import { format } from "date-fns";

format(new Date("2025-09-01"), "do MMM yyyy"); // "1st Sep 2025"
```

Do not use `toLocaleDateString`, `Intl.DateTimeFormat`, or any other date formatting approach.
