import { NewWorkoutForm } from "./_components/NewWorkoutForm";

export default function NewWorkoutPage() {
  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      <div className="mx-auto max-w-lg px-4 py-10">
        <h1 className="mb-8 text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          New Workout
        </h1>
        <NewWorkoutForm />
      </div>
    </div>
  );
}
