# Spring AI Day1 학습자 가이드

> 2026-07-02 · Spring AI를 적용한 협약기업 서비스 구현
> 원본: learner-guide.html · ES LMS

---

Spring AI Day1 학습자 가이드

# Spring AI Day1 학습자 가이드

2026-07-02 · 생성형 AI 서비스 구조, 환경설정, ChatClient 첫 호출

## 오늘 만드는 것

day01-chat-client 프로젝트를 만들고 Gemini 응답을 반환하는 API를 구현합니다.

- /api/chat: 기본 Gemini 응답

- /api/teacher: 교사 역할을 부여한 응답

- 미니 도구 엔드포인트 2개 이상

- README 작성 후 GitHub push

## 핵심 구조

사용자 -> Controller -> Service -> AI 모델(Gemini) -> Service -> Controller -> 사용자

CRUD에서 DB에 물어봤다면, 오늘은 AI 모델에 물어봅니다. Controller와 Service 구조는 그대로 유지됩니다.

## 환경

| 항목 | 값

| Java | 21

| Spring Boot | 4.1.x

| Spring AI | 2.0.0 GA

| Provider | Google GenAI / Gemini

| Model | gemini-3.1-flash-lite

## API Key 원칙

실제 API Key는 코드나 GitHub에 올리지 않습니다. application.yml에서는 ${GOOGLE_API_KEY}로만 참조합니다.

spring:
ai:
google:
genai:
api-key: ${GOOGLE_API_KEY}

## 첫 호출 코드

@GetMapping("/api/chat")
public String chat(@RequestParam String message) {
return chatClient.prompt()
.user(message)
.call()
.content();
}

GOOGLE_API_KEY="발급받은_키" ./gradlew bootRun

curl -G "http://localhost:8080/api/chat" \
--data-urlencode "message=안녕, 너는 누구야? 한 문장으로 대답해줘."

## 미니 실습

| 과제 | API 예시

| 코드 설명 도우미 | /api/code-helper

| README 작성 도우미 | /api/readme-helper

| 면접 질문 생성기 | /api/interview-helper

| CS 개념 설명기 | /api/concept-helper

| FAQ 응답기 | /api/faq-helper

## 제출

- GitHub 저장소 URL

- /api/chat 응답 캡처

- /api/teacher 응답 캡처

- 미니 도구 2개 이상 응답 캡처

## 막혔을 때

| 증상 | 확인

| javac 없음 | JDK가 아니라 JRE만 설치됨

| 앱 시작 실패 | Gradle 오류, Java 버전, YAML 들여쓰기

| 호출 시 500 | API_KEY_INVALID, 환경변수

| 429 오류 | RPM/RPD 초과