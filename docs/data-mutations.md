# Data Mutations

## Rule: All Database Mutations Go Through `/data` Helper Functions

Every database mutation (insert, update, delete) must live in a helper function under `src/data/`. No server action, component, or other file may import from `src/db/` or call Drizzle directly — that is the exclusive responsibility of `src/data/`.

Helper functions must use **Drizzle ORM** for all mutations. **Raw SQL is forbidden.**

```
src/
  data/
    workouts.ts      ← helper functions for workout queries AND mutations
    exercises.ts     ← helper functions for exercise queries AND mutations
  db/
    schema.ts        ← Drizzle schema definitions only
```

### Example mutation helper

```ts
// src/data/workouts.ts
import { auth } from "@clerk/nextjs/server";
import { db } from "@/db";
import { workouts } from "@/db/schema";
import { eq, and } from "drizzle-orm";

export async function createWorkout(name: string, startedAt: Date) {
  const { userId } = await auth();
  if (!userId) throw new Error("Unauthenticated");

  const [workout] = await db
    .insert(workouts)
    .values({ userId, name, startedAt })
    .returning();

  return workout;
}

export async function deleteWorkout(id: string) {
  const { userId } = await auth();
  if (!userId) throw new Error("Unauthenticated");

  await db
    .delete(workouts)
    .where(and(eq(workouts.id, id), eq(workouts.userId, userId)));
}
```

## Rule: Mutations Must Be Triggered via Server Actions

All data mutations must be initiated through **Next.js Server Actions**. Do NOT mutate data via:

- Route handlers (`src/app/api/*/route.ts`)
- Client-side `fetch` calls
- `useEffect` or event handlers that call an API directly

## Rule: Server Actions Live in Colocated `actions.ts` Files

Each server action must be defined in an `actions.ts` file colocated next to the route segment that uses it — not in a shared global file.

```
src/app/
  workouts/
    page.tsx         ← Server Component
    actions.ts       ← Server Actions for this route
  workouts/[id]/
    page.tsx
    actions.ts       ← Server Actions scoped to this segment
```

Every `actions.ts` file must begin with the `"use server"` directive.

```ts
// src/app/workouts/actions.ts
"use server";
```

## Rule: Server Action Parameters Must Be Typed — No `FormData`

All server action parameters must use explicit TypeScript types. `FormData` is forbidden as a parameter type.

**Wrong:**
```ts
export async function createWorkoutAction(data: FormData) { ... }
```

**Right:**
```ts
export async function createWorkoutAction(name: string, startedAt: Date) { ... }
```

## Rule: All Server Actions Must Validate Arguments with Zod

Every server action must validate its arguments using **Zod** before calling any helper function or touching any data. Never trust caller-supplied values without parsing them first.

### Full example

```ts
// src/app/workouts/actions.ts
"use server";

import { z } from "zod";
import { createWorkout } from "@/data/workouts";

const CreateWorkoutSchema = z.object({
  name: z.string().min(1).max(100),
  startedAt: z.coerce.date(),
});

export async function createWorkoutAction(
  name: string,
  startedAt: Date
) {
  const parsed = CreateWorkoutSchema.parse({ name, startedAt });
  return createWorkout(parsed.name, parsed.startedAt);
}
```

If validation fails, Zod will throw and the action will return an error to the caller — this is the intended behavior.

## Rule: Never Use `redirect()` Inside Server Actions

Server actions must **not** call `redirect()` from `next/navigation`. Redirecting from a server action is forbidden.

Instead, return the result from the server action and perform the navigation client-side using `router.push()` after the action resolves.

**Wrong:**
```ts
// actions.ts
import { redirect } from "next/navigation";

export async function createWorkoutAction(name: string, startedAt: Date) {
  const parsed = CreateWorkoutSchema.parse({ name, startedAt });
  await createWorkout(parsed.name, parsed.startedAt);
  redirect("/dashboard"); // ← forbidden
}
```

**Right:**
```ts
// actions.ts
export async function createWorkoutAction(name: string, startedAt: Date) {
  const parsed = CreateWorkoutSchema.parse({ name, startedAt });
  return createWorkout(parsed.name, parsed.startedAt);
}

// ClientComponent.tsx
startTransition(async () => {
  await createWorkoutAction(name, startedAt);
  router.push("/dashboard"); // ← navigate after action resolves
});
```

## Rule: Users May Only Mutate Their Own Data

The same auth-scoping requirement from data fetching applies to mutations. Every `src/data/` mutation helper must:

1. Resolve the current user's ID from the auth session internally.
2. Scope the mutation with a `.where(eq(table.userId, userId))` clause (or equivalent) so a user can never modify another user's records.
3. Never accept a `userId` parameter from the caller.

## Summary

| Concern | Where it lives | Rule |
|---|---|---|
| Database mutations | `src/data/*.ts` helpers | Drizzle ORM only, no raw SQL |
| Triggering mutations | Server Actions only | No route handlers, no client fetch |
| Server Action location | Colocated `actions.ts` | One file per route segment |
| Parameter types | Explicit TypeScript types | `FormData` is forbidden |
| Input validation | Zod inside every action | Parse before calling any helper |
| Auth scoping | Inside every `src/data/` helper | Always filter by session user ID |
| Post-action navigation | Client component via `router.push()` | Never call `redirect()` inside a server action |
