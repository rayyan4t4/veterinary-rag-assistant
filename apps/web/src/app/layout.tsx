import type { Metadata } from "next";
import "./globals.css";
export const metadata:Metadata={title:{default:"VetEvidence",template:"%s · VetEvidence"},description:"Evidence-grounded veterinary decision support"};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
