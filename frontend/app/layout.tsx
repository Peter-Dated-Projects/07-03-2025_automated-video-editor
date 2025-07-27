import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "Brainrotter",
  description: "Automated Video Editor for Instagram Brainrot Reels",
  generator: "Brainrotter",
  applicationName: "Brainrotter",
  keywords: [
    "brainrotter",
    "automated video editor",
    "instagram reels",
    "video editing",
    "AI video editor",
    "reels editor",
    "social media video editor",
    "video automation",
  ],
  authors: [
    {
      name: "petthepotat",
      url: "https://peterzhang.dev",
    },
  ],
  icons: {
    icon: "/logo-512x.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
