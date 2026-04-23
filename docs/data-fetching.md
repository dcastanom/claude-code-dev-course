# Data Fetching

## Rule: Server Components Only

**ALL data fetching in this app MUST be done exclusively via React Server Components.**

Do NOT fetch data via:
- Route handlers (`src/app/api/*/route.ts`)
- Client components (`"use client"`)
- `useEffect` / `fetch` on the client
- Any other mechanism

If a component needs data, it must be a Server Component (no `"use client"` directive) that awaits a helper function from the `/data` directory.

## Rule: All Database Queries Go Through `/data` Helper Functions

Every database query must live in a helper function under `src/data/`. No component, route, or other file may import from `src/db/` or call Drizzle directly — that is the exclusive responsibility of `src/data/`.

Helper functions must use **Drizzle ORM** for all queries. **Raw SQL is forbidden.**

```
src/
  data/
    workouts.ts      ← helper functions for workout data
    exercises.ts     ← helper functions for exercise data
  db/
    schema.ts        ← Drizzle schema definitions only
```

## Rule: Users May Only Access Their Own Data

Every helper function in `src/data/` **must** scope queries to the currently authenticated user. This is non-negotiable.

1. Obtain the current user's ID from the auth session at the top of the helper function.
2. Add a `.where(eq(table.userId, userId))` clause (or equivalent) to every query.
3. Never accept a `userId` parameter from the caller — always resolve it from the session inside the helper so a caller cannot impersonate another user.
4. If no authenticated session exists, throw or return early — never fall through to an unscoped query.

### Example pattern

```ts
// src/data/workouts.ts
import { auth } from "@/lib/auth";
import { db } from "@/db";
import { workouts } from "@/db/schema";
import { eq } from "drizzle-orm";

export async function getWorkouts() {
  const session = await auth();
  if (!session?.user?.id) throw new Error("Unauthenticated");

  return db
    .select()
    .from(workouts)
    .where(eq(workouts.userId, session.user.id));
}
```

### Example Server Component consuming a helper

```tsx
// src/app/dashboard/page.tsx  — Server Component (no "use client")
import { getWorkouts } from "@/data/workouts";

export default async function DashboardPage() {
  const workouts = await getWorkouts();
  return <WorkoutList workouts={workouts} />;
}
```

## Summary

| Concern | Where it lives | Rule |
|---|---|---|
| Data fetching | Server Components only | No client-side fetching |
| Database queries | `src/data/*.ts` helpers | Drizzle ORM only, no raw SQL |
| Auth scoping | Inside every helper | Always filter by session user ID |
