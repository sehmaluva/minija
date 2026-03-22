import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Providers } from "@/components/providers";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Minija",
  description: "Poultry Management System",
  generator: "sehmaluva",
  applicationName: "Minija",
  keywords: ["poultry", "management", "system"],
  authors: [{ name: "sehmaluva" }],
  creator: "sehmaluva",
  publisher: "sehmaluva",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head />
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
