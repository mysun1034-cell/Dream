import Link from "next/link";

export default function Home() {
  return (
    <main className="home">
      <header>
        <p className="eyebrow">Han Jungwook · Busan · Seoul</p>
        <h1>한정욱</h1>
        <p className="role">제품 오너 · 백엔드 엔지니어</p>
      </header>

      <p className="lede">
        해외 소싱·수입 물류 실무에서 출발해 프로덕션 소프트웨어를 만드는 데까지 온 스타트업 창업멤버입니다.
        장기요양보험 ERP와 아동 AI 영어학습 플랫폼의 백엔드를 설계·구축하면서, 각 제품이 지켜야 할 법규를 설계에
        반영해 왔습니다.
      </p>

      <nav className="link-cards" aria-label="이력서">
        <a className="link-card" href="/resume/ko">
          <span className="lc-k">이력서</span>
          <span className="lc-t">한국어</span>
          <span className="lc-d">경력 · 프로젝트 · 교육</span>
        </a>
        <a className="link-card" href="/resume/en" lang="en">
          <span className="lc-k">Resume</span>
          <span className="lc-t">English</span>
          <span className="lc-d">Experience · Projects · Education</span>
        </a>
      </nav>

      <footer>
        <a href="mailto:mysun1034@gmail.com">mysun1034@gmail.com</a>
        <a href="https://github.com/mysun1034-cell" target="_blank" rel="noopener noreferrer">
          github.com/mysun1034-cell
        </a>
        <Link className="board-link" href="/board">
          학습 보드
        </Link>
      </footer>
    </main>
  );
}
