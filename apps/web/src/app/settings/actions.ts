"use server";
import {revalidatePath} from "next/cache";import {z} from "zod";import {createClient} from "@/lib/supabase/server";
export type SettingsState={error?:string;success?:string};
export async function saveSettings(_:SettingsState,data:FormData):Promise<SettingsState>{const parsed=z.object({display_name:z.string().trim().max(120),locale:z.enum(["en","ur"])}).safeParse(Object.fromEntries(data));if(!parsed.success)return{error:"Check the profile fields."};const supabase=await createClient();const {data:auth}=await supabase.auth.getClaims();const id=auth?.claims?.sub;if(!id)return{error:"Your session expired."};const {error}=await supabase.from("profiles").upsert({id,...parsed.data});if(error)return{error:error.message};revalidatePath("/settings");return{success:"Settings saved."}}
