"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import AuthGate from "../../AuthGate";

type PyodideInterface = {
  runPythonAsync: (code: string) => Promise<unknown>;
  setStdout: (opts: { batched: (s: string) => void }) => void;
  setStderr: (opts: { batched: (s: string) => void }) => void;
};

declare global {
  interface Window {
    loadPyodide?: (opts?: { indexURL?: string }) => Promise<PyodideInterface>;
  }
}

const PYODIDE_VERSION = "0.26.4";
const CDN = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

// 개발 모드의 React Strict Mode는 effect를 두 번 실행한다. 두 번째 실행이 "이미 <script> 태그가
// 있으니 됐다"고 즉시 resolve해버리면, 첫 번째 실행이 붙인 스크립트가 아직 로드 중일 때 loadPyodide가
// undefined인 채로 넘어가 버린다. 실제로 전역에 함수가 잡혔는지까지 확인해서 이 경합을 막는다.
function loadPyodideScript(src: string): Promise<void> {
  if (typeof window.loadPyodide === "function") return Promise.resolve();
  return new Promise((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(`script[src="${src}"]`);
    if (existing) {
      existing.addEventListener("load", () => resolve());
      existing.addEventListener("error", () => reject(new Error("Pyodide 스크립트를 불러오지 못했습니다.")));
      return;
    }
    const el = document.createElement("script");
    el.src = src;
    el.onload = () => resolve();
    el.onerror = () => reject(new Error("Pyodide 스크립트를 불러오지 못했습니다."));
    document.head.appendChild(el);
  });
}

function PythonPractice() {
  const pyRef = useRef<PyodideInterface | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [code, setCode] = useState('print("hello")\n');
  const [output, setOutput] = useState("");
  const [running, setRunning] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function boot() {
      try {
        await loadPyodideScript(CDN + "pyodide.js");
        if (!window.loadPyodide) throw new Error("Pyodide를 찾지 못했습니다.");
        const py = await window.loadPyodide({ indexURL: CDN });
        if (cancelled) return;
        pyRef.current = py;
        setStatus("ready");
      } catch (e) {
        if (!cancelled) setStatus("error");
        console.error("Pyodide 로딩 실패:", e);
      }
    }
    void boot();
    return () => {
      cancelled = true;
    };
  }, []);

  async function run() {
    const py = pyRef.current;
    if (!py) return;
    setRunning(true);
    setOutput("");
    let captured = "";
    py.setStdout({ batched: (s) => (captured += s + "\n") });
    py.setStderr({ batched: (s) => (captured += s + "\n") });
    try {
      const result = await py.runPythonAsync(code);
      if (result !== undefined && result !== null) captured += String(result);
      setOutput(captured || "(출력 없음)");
    } catch (e) {
      setOutput(captured + (e instanceof Error ? e.message : String(e)));
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="wrap narrow">
      <header className="top">
        <div>
          <p className="eyebrow">
            <Link href="/study">공부방</Link>
          </p>
          <h1>Python 연습장</h1>
          <p className="goal">브라우저 안에서 바로 Python을 실행합니다. 처음 열 때는 내려받는 데 시간이 좀 걸립니다.</p>
        </div>
      </header>

      <section className="card practice">
        <div className="card-head">
          <h2>코드 실행</h2>
          <span className="practice-status">
            {status === "loading" ? "Python 준비 중…" : status === "error" ? "준비하지 못했습니다" : "준비됨"}
          </span>
        </div>
        <textarea className="practice-editor" spellCheck={false} value={code} onChange={(e) => setCode(e.target.value)} />
        <div className="practice-bar">
          <button type="button" onClick={run} disabled={status !== "ready" || running}>
            {running ? "실행 중…" : "실행"}
          </button>
        </div>
        {output && <p className="practice-output">{output}</p>}
        {status === "error" && (
          <p className="banner" role="alert">
            Python 실행 환경을 불러오지 못했습니다. 잠시 뒤 새로고침해 주세요.
          </p>
        )}
      </section>
    </div>
  );
}

export default function PythonPracticePage() {
  return <AuthGate>{() => <PythonPractice />}</AuthGate>;
}
