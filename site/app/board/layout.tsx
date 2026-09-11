import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "학습 보드 · 한정욱",
  robots: { index: false, follow: false },
};

export default function BoardLayout({ children }: { children: ReactNode }) {
  return children;
}
