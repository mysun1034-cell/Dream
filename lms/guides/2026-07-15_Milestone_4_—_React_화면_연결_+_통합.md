# Milestone 4 — React 화면 연결 + 통합

> 2026-07-15 · 미니 프로젝트 2 -Spring AI를 활용한 기업서비스 구축 프로젝트
> 원본: milestone-checklist.html · ES LMS

---

Milestone 4 — React 화면 연결 + 통합

-

미니 프로젝트 2 · Day 4 / 5

# 마일스톤 4 — React 화면 연결 + 통합

마감18:00
계산 중…

Day3가 구현한 동작하는 API 위에서 React가 그대로 fetch → MVP 한 흐름이 화면에서 처음 동작.
React는 지난 학습에서 짜봤다 — 오늘 새로 하는 건 fetch POST + 단건 결과 렌더링뿐.

오늘의 핵심 — 보이는 데모0 / 2

보이는 데모 완성 — 이게 발표에서 보여줄 흐름

오늘의 핵심 — 보이는 데모 (반드시)

01
CORS 열고 React가 계약 그대로 fetch 호출 (URL·Method·필드명·타입 100% 일치)

02
버튼 클릭 → AI 결과가 화면에 뜬다 + 구조화 나눠 렌더링(category·answer) + 로딩/에러 상태
승부처

데모가 뜨면 — 오후 리프트

3번은 화면만 붙이는 게 아니라 어제 한 백엔드 작업을 한 번 더 하는 것 — 무겁다.
오늘 다 못 끝내도 정상, 커밋해두면 내일(Day5) 오전에 이어 마무리. README는 오늘 착수만.

03
2번째 기능을 풀스택으로 — 엔드포인트·서비스·저장(Day3 방식)부터, 그 다음 화면 → Spring AI 기능 최소 2개 매핑
오후

04
README 초안(백·프론트 실행 방법) 착수 + 동결할 데모 경로 1개 지정
오후

부수 운영 체크

a
키는 백엔드 전용(프론트에 키 없음) · 프론트·백 동시 기동
위생

b
PR·리뷰·보드 갱신 · 데모 화면 캡처 1장
부수

표준 예시 — CORS · fetch(계약대로) · 렌더링 (팀 주제로 대체)
▼

01CORS — 백엔드에 추가 (com.study)

@Configuration
public class CorsConfig implements WebMvcConfigurer {
@Override
public void addCorsMappings(CorsRegistry registry) {
registry.addMapping("/api/**")
.allowedOrigins("http://localhost:5173")
.allowedMethods("GET", "POST");
}
}

02React fetch — 계약 그대로 (GET을 POST로)

// 지난 학습: 목록 로드는 fetch GET, 보내기(send)만 EventSource였다.
// 오늘은 단건 → 보내기도 fetch POST. 그 GET에 method/body만 붙이면 됨.
const res = await fetch("http://localhost:8080/api/inquiries", {
method: "POST", // ← GET 아님 (오늘의 새 부분)
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ content }), // ← 반드시 stringify. 계약: { content }
});
if (!res.ok) throw new Error("요청 실패"); // 400/500 처리
const data = await res.json(); // { id, category, answer, createdAt }

03구조화 렌더링 — 단건 객체, 나눠서

// 지난엔 배열을 .map 했지만 오늘 data는 단건 객체 → .map 아님, 직접 접근
<span className="badge">{data.category}</span>
<p>{data.answer}</p>

▸ 막힐 때 빠른 점검

- 콘솔에 CORS 에러 → 백엔드 CorsConfig(/api/** · 5173 · GET·POST)

- 400인데 프론트는 멀쩡 → POST 3종 세트 빠짐(method·headers·body) 또는 JSON.stringify 안 함

- .map 하다 에러 → data는 배열 아니라 단건 객체. data.category로 직접 접근

- 200인데 화면 빔 → 계약 필드 불일치(answer vs reply). Network 탭에서 실제 응답 JSON 확인, 필드명 통일

- 응답이 아예 없음 → fetch URL 오타 / 백엔드 미기동 / 5173·8080 둘 다 떠야

- 키를 프론트에? → ❌ 키는 백엔드 전용, 프론트는 API만 호출

오늘 화면에 뜬 그 한 흐름이 내일부터 "절대 안 깨지는 데모 경로"가 된다.