export type Category = {
  slug: string;
  name: string;
  blurb: string;
};

// Dream 저장소 README의 표를 그대로 옮긴 분류다. 순서는 지금 학습 순서(SQL 먼저)를 따른다.
export const CATEGORIES: Category[] = [
  {
    slug: "palantir",
    name: "Palantir SQL·Python 통합교재",
    blurb: "DS·FDSE 지원자를 위한 40주 커리큘럼 — 기본·중급·심화, 연습문제 120개, 프로젝트 6종, 모의 면접",
  },
  { slug: "sql", name: "SQL · 데이터 모델링", blurb: "EdenCare 실제 모델을 ERD·정규화·SQL로 설명하는 트랙" },
  { slug: "python", name: "Python", blurb: "기초 · OOP · 실습" },
  { slug: "cs", name: "CS", blurb: "자료구조·알고리즘 · 시스템 설계 · OS·네트워크" },
  { slug: "english", name: "영어", blurb: "기술·면접 영어" },
  { slug: "ml", name: "ML · DL", blurb: "머신러닝·딥러닝 노트북과 개념 지도" },
  { slug: "genai", name: "생성형 AI 과정", blurb: "42수업 · 9교과목 커리큘럼 지도" },
  { slug: "llm", name: "LLM 실습", blurb: "API·RAG·로컬 sLM 실습 기록" },
  { slug: "career", name: "커리어", blurb: "프로필 · Spring Boot/AI 커리큘럼" },
  { slug: "qa", name: "질문·답변 일지", blurb: "그날그날 막힌 것과 답" },
];

export function categoryOf(slug: string): Category | undefined {
  return CATEGORIES.find((c) => c.slug === slug);
}

export type StudyDoc = {
  id: string;
  category: string;
  sort: number;
  title: string;
  source_path: string | null;
  body: string;
};
