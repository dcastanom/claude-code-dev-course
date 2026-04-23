# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@AGENTS.md

## IMPORTANT: Always consult /docs first

**Before writing any code**, you MUST check the `/docs` directory for a relevant documentation file and follow it. The `/docs` directory contains authoritative guides for the libraries and tools used in this project. Do not rely on training data when a doc file exists — read it first.

Key docs to consult:
- `docs/data-fetching.md` — **mandatory reading before any data fetching or database work**. Covers the Server Components-only rule, the `src/data/` helper pattern, and the per-user data scoping requirement.

## Commands

```bash
npm run dev        # Start dev server (Turbopack, default bundler)
npm run build      # Production build
npm run start      # Start production server
npm run lint       # Run ESLint
```

> Starting with Next.js 16, `next build` no longer runs the linter automatically.

To use Webpack instead of Turbopack: `next dev --webpack` or `next build --webpack`.

## Architecture

This is a **Next.js 16** App Router project using **React 19**, **TypeScript**, and **Tailwind CSS v4**.

- `src/app/` — App Router root. File-system routing: folders map to URL segments; a `page.tsx` makes a route public.
- `src/app/layout.tsx` — Root layout (required; wraps all routes with `<html>` and `<body>`).
- `src/app/page.tsx` — Home page (`/`).
- `src/app/globals.css` — Global styles (Tailwind entry point).
- `public/` — Static assets served from `/`.
- Path alias `@/*` maps to `src/*` (configured in `tsconfig.json`).

### App Router file conventions

| File | Purpose |
|---|---|
| `layout.tsx` | Shared UI wrapping child segments |
| `page.tsx` | Makes a route publicly accessible |
| `loading.tsx` | Suspense boundary / skeleton |
| `error.tsx` | Error boundary |
| `not-found.tsx` | 404 UI |
| `route.ts` | API endpoint |

Route groups `(group)` organize routes without affecting the URL. Private folders `_folder` are excluded from routing.

### Key version notes

- **Next.js 16** has breaking changes from prior versions — read `node_modules/next/dist/docs/` before writing any Next.js-specific code.
- **Tailwind CSS v4** — uses `@tailwindcss/postcss` plugin; config is in `postcss.config.mjs`, not `tailwind.config.js`.
- **ESLint 9** — flat config format (`eslint.config.mjs`), not `.eslintrc`.
