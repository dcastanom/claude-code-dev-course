import { format, parseISO } from "date-fns";
import { Dumbbell } from "lucide-react";
import { getWorkoutsByDate } from "@/data/workouts";
import { DatePicker } from "./_components/DatePicker";

type Props = {
  searchParams: Promise<{ date?: string }>;
};

export default async function DashboardPage({ searchParams }: Props) {
  const { date: dateParam } = await searchParams;
  const date = dateParam ? parseISO(dateParam) : new Date();

  const workouts = await getWorkoutsByDate(date);

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      <div className="mx-auto max-w-2xl px-4 py-10">
        <h1 className="mb-6 text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          Workout Dashboard
        </h1>

        <DatePicker initialDate={date} />

        <div className="mt-8">
          <h2 className="mb-4 text-sm font-medium uppercase tracking-widest text-zinc-500 dark:text-zinc-400">
            Workouts — {format(date, "do MMM yyyy")}
          </h2>

          {workouts.length === 0 ? (
            <p className="rounded-lg border border-dashed border-zinc-200 px-6 py-12 text-center text-sm text-zinc-400 dark:border-zinc-800">
              No workouts logged for this day.
            </p>
          ) : (
            <ul className="space-y-3">
              {workouts.map((workout) => (
                <li
                  key={workout.id}
                  className="flex items-center gap-4 rounded-lg border border-zinc-200 bg-white px-5 py-4 dark:border-zinc-800 dark:bg-zinc-900"
                >
                  <span className="flex h-9 w-9 items-center justify-center rounded-full bg-zinc-100 dark:bg-zinc-800">
                    <Dumbbell className="h-4 w-4 text-zinc-600 dark:text-zinc-400" />
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="truncate font-medium text-zinc-900 dark:text-zinc-50">
                      {workout.name}
                    </p>
                    <p className="text-sm text-zinc-500 dark:text-zinc-400">
                      {format(workout.startedAt, "h:mm a")}
                      {workout.completedAt
                        ? ` – ${format(workout.completedAt, "h:mm a")}`
                        : " · In progress"}
                    </p>
                  </div>
                  {!workout.completedAt && (
                    <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-medium text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                      Active
                    </span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
