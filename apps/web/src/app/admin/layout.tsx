import { forbidden } from "next/navigation";
import { createClient } from "@/lib/supabase/server";

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createClient();
  const { data } = await supabase.auth.getClaims();
  const metadata = data?.claims?.app_metadata;
  const isAdmin = metadata && typeof metadata === "object" && "role" in metadata && metadata.role === "admin";
  if (!isAdmin) forbidden();
  return children;
}
