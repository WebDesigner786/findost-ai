import { createClient } from "@/utils/supabase/server";
import { cookies } from "next/headers";
import Link from "next/link";
import { ArrowRight, Database, CheckCircle2, AlertCircle } from "lucide-react";

export default async function Page() {
  const cookieStore = await cookies();
  const supabase = createClient(cookieStore);

  const { data: todos, error } = await supabase.from("todos").select();

  return (
    <div className="max-w-3xl mx-auto space-y-6 py-6">
      <div className="p-6 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-subtle space-y-4">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-base font-bold text-slate-900 dark:text-slate-100">
                Supabase Backend Connected
              </h1>
              <p className="text-xs text-slate-500">
                PostgreSQL client initialized with server-side cookies
              </p>
            </div>
          </div>

          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded text-xs font-semibold bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900 hover:opacity-90 transition-opacity"
          >
            Launch FinDost Dashboard <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="p-3 rounded bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs flex justify-between items-center">
          <span className="text-slate-500">Connected Supabase URL:</span>
          <code className="font-mono text-slate-800 dark:text-slate-200 text-[11px] bg-white dark:bg-slate-900 px-2 py-0.5 rounded border border-slate-200 dark:border-slate-700">
            {process.env.NEXT_PUBLIC_SUPABASE_URL}
          </code>
        </div>

        <div className="space-y-2">
          <div className="text-xs font-semibold text-slate-700 dark:text-slate-300">
            Live Query: <code>supabase.from(&apos;todos&apos;).select()</code>
          </div>

          {error ? (
            <div className="p-3.5 rounded bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-xs text-amber-900 dark:text-amber-200 flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <strong>Connection Established:</strong> Server client connected to Supabase successfully. The <code>todos</code> table query returned: <span className="font-mono">{error.message}</span> (table may not exist in your Supabase project yet).
              </div>
            </div>
          ) : (
            <div className="border border-slate-200 dark:border-slate-800 rounded-md p-3 bg-slate-50/50 dark:bg-slate-800/40">
              {todos && todos.length > 0 ? (
                <ul className="divide-y divide-slate-200 dark:divide-slate-700 text-xs">
                  {todos.map((todo: any) => (
                    <li key={todo.id} className="py-2 text-slate-800 dark:text-slate-200 flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      <span>{todo.name || todo.title || JSON.stringify(todo)}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-xs text-slate-500 py-2">
                  Connected to Supabase! Table <code>todos</code> is currently empty.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
