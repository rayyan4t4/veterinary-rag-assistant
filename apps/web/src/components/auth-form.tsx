"use client";

import { useActionState } from "react";
import Link from "next/link";
import type { AuthState } from "@/app/(auth)/actions";

type Action = (state: AuthState, data: FormData) => Promise<AuthState>;
export function AuthForm({ action, mode }: { action: Action; mode: "login" | "signup" | "forgot" }) {
  const [state, formAction, pending] = useActionState(action, {});
  return <form action={formAction}>
    {mode === "signup" && <div className="field"><label htmlFor="display_name">Full name</label><input id="display_name" name="display_name" autoComplete="name" required /></div>}
    <div className="field"><label htmlFor="email">Email</label><input id="email" name="email" type="email" autoComplete="email" required /></div>
    {mode !== "forgot" && <div className="field"><label htmlFor="password">Password</label><input id="password" name="password" type="password" minLength={8} autoComplete={mode === "login" ? "current-password" : "new-password"} required /></div>}
    {state.error && <p className="form-error" role="alert">{state.error}</p>}
    {state.success && <p className="form-success" role="status">{state.success}</p>}
    <button className="btn" disabled={pending}>{pending ? "Please wait…" : mode === "login" ? "Sign in" : mode === "signup" ? "Create account" : "Send reset link"}</button>
    {mode === "login" && <Link href="/forgot-password">Forgot password?</Link>}
  </form>;
}
