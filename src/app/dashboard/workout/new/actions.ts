"use server";

import { z } from "zod";
import { createWorkout } from "@/data/workouts";

const CreateWorkoutSchema = z.object({
  name: z.string().min(1).max(100),
  startedAt: z.coerce.date(),
});

export async function createWorkoutAction(name: string, startedAt: Date) {
  const parsed = CreateWorkoutSchema.parse({ name, startedAt });
  return createWorkout(parsed.name, parsed.startedAt);
}
