# Authentication

## Rule: Clerk Is the Only Auth Provider

**This app uses [Clerk](https://clerk.com) for all authentication.** Do NOT use NextAuth, Auth.js, custom sessions, JWTs, cookies, or any other auth mechanism.

- Package: `@clerk/nextjs`
- All Clerk components and helpers are imported from `@clerk/nextjs` (client-side) or `@clerk/nextjs/server` (server-side).

## Rule: Wrap the App in `<ClerkProvider>`

`<ClerkProvider>` must wrap the entire application. It lives in `src/app/layout.tsx` and must not be moved or removed.

```tsx
// src/app/layout.tsx
import { ClerkProvider } from "@clerk/nextjs";

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <ClerkProvider>
          {children}
        </ClerkProvider>
      </body>
    </html>
  );
}
```

## Rule: Get the Current User in Server Code

In Server Components, `src/data/` helpers, and `route.ts` files, always use `auth()` from `@clerk/nextjs/server`:

```ts
import { auth } from "@clerk/nextjs/server";

const { userId } = await auth();
if (!userId) throw new Error("Unauthenticated");
```

Never import `auth` from the client-side `@clerk/nextjs` package in server code.

## Rule: Protect Routes with Clerk Middleware

Route protection is handled by Clerk middleware in `src/middleware.ts`. Do not implement manual redirect logic inside pages or layouts to gate access — configure it in the middleware instead.

## Rule: Use Clerk UI Components for Sign-In / Sign-Up

Use Clerk's built-in components for all auth UI. Do not build custom sign-in or sign-up forms.

| Need | Component |
|---|---|
| Sign-in button | `<SignInButton mode="modal" />` |
| Sign-up button | `<SignUpButton mode="modal" />` |
| User avatar / account menu | `<UserButton />` |
| Conditional rendering by auth state | `<Show when="signed-in">` / `<Show when="signed-out">` |

All of these are imported from `@clerk/nextjs`.

## Summary

| Concern | Approach |
|---|---|
| Auth provider | Clerk (`@clerk/nextjs`) only |
| App wrapper | `<ClerkProvider>` in root layout |
| User ID (server) | `auth()` from `@clerk/nextjs/server` |
| Route protection | Clerk middleware (`src/middleware.ts`) |
| Auth UI | Clerk components — no custom forms |
