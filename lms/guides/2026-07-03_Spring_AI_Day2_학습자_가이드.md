# Spring AI Day2 학습자 가이드

> 2026-07-03 · Spring AI를 적용한 협약기업 서비스 구현
> 원본: learner-guide.html · ES LMS

---

Spring AI Day2 학습자 가이드

# 학습자 가이드 — Spring AI Day2

주제: PromptTemplate과 Structured Output — AI 응답을 코드가 다루는 형식으로

오늘의 한 문장: 어제는 문자열을 주고 문자열을 받았다. 오늘부터는 템플릿에 값을 바인딩해서 주고, 타입으로 받는다.

## 오늘 만드는 것

| API | 하는 일

| /api/summary | 문의 요약 (PromptTemplate, 파라미터 2개)

| /api/classify/raw | 문의 분류 — 문자열로 받기 (비교용)

| /api/classify | 문의 분류 — record로 받기 (오늘의 핵심)

| 응용 1개 | List 매핑 (추천기, 목록 생성기 등 소재 자유)

## 0. 프로젝트 준비 (어제 복습)

- start.spring.io — Gradle-Groovy, Java 21, Spring Boot 4.1.x

- 의존성: Spring Web + Google GenAI

- 프로젝트명: day02-prompt-output

spring:
application:
name: day02-prompt-output
ai:
google:
genai:
api-key: ${GOOGLE_API_KEY}
chat:
model: gemini-3.1-flash-lite
temperature: 0.7

실행 구성에 GOOGLE_API_KEY 환경변수를 설정하세요. 키를 코드에 쓰지 않습니다!

## 1. PromptTemplate — 요약 API

문자열 연결(+) 대신 템플릿의 {변수}에 값을 바인딩합니다.

@Service
public class PromptService {

private final ChatClient chatClient;

public PromptService(ChatClient.Builder chatClientBuilder) {
this.chatClient = chatClientBuilder
.defaultSystem("""
당신은 온라인 쇼핑몰 고객센터의 AI 어시스턴트입니다.
항상 정중한 한국어로 답변하고, 확실하지 않은 내용은 추측하지 않습니다.
""")
.build();
}

public String summarize(String text, String audience) {
return chatClient.prompt()
.user(u -> u.text("""
다음 고객 문의를 {audience}가 읽기 좋게 3줄 이내로 요약하세요.
핵심 요구사항이 무엇인지 첫 줄에 쓰세요.

문의 내용: {text}
""")
.param("audience", audience)
.param("text", text))
.call()
.content();
}
}

- .user()에 문자열 대신 람다: .text()가 템플릿, .param("이름", 값)이 바인딩

- .defaultSystem(): 이 ChatClient의 모든 호출에 적용되는 기본 system 메시지

- 체인의 나머지(.call().content())는 어제와 동일

audience를 "신입 상담원" → "임원"으로 바꿔 재호출해 보세요. 같은 템플릿, 다른 결과가 나옵니다.

{audience}가 응답에 그대로 나오면, 템플릿의 {이름}과 .param("이름", ...) 일치부터 확인하세요.

## 2. 실험 — "JSON으로만 답하세요"는 왜 부족한가

private static final String CLASSIFY_TEMPLATE = """
다음 고객 문의를 분류하세요.

- category: 배송, 환불, 상품, 계정, 기타 중 하나
- priority: HIGH, MEDIUM, LOW 중 하나
- reason: 그렇게 분류한 이유 한 문장

문의 내용: {text}
""";

public String classifyRaw(String text) {
return chatClient.prompt()
.user(u -> u.text(CLASSIFY_TEMPLATE).param("text", text))
.call()
.content();
}

/api/classify/raw를 호출하고 응답의 모양을 관찰하세요. 마크다운 불릿? 표? 문장? 호출마다 다를 수 있습니다. "JSON으로만"을 붙여도 코드 펜스가 붙거나, 지시한 값(HIGH) 대신 다른 값(높음)이 오기도 합니다.

자연어 형식 지시는 부탁입니다. 코드가 소비할 결과라면 부탁으로는 부족합니다.

## 3. Structured Output — record로 받기

public record InquiryResult(String category, String priority, String reason) {
}

이 record의 필드 구성이 곧 모델에게 보낼 형식 명세(JSON 스키마)가 됩니다.

public InquiryResult classify(String text) {
return chatClient.prompt()
.user(u -> u.text(CLASSIFY_TEMPLATE).param("text", text))
.call()
.entity(InquiryResult.class);
}

raw 버전과의 차이는 반환 타입과 마지막 한 줄뿐입니다. .entity()가 내부에서 ① 스키마 기반 형식 지시를 프롬프트에 자동 삽입 ② 모델 호출 ③ 응답을 파싱해 record로 변환합니다.

같은 문의를 두 API에 보내 나란히 비교하세요. typed 버전은 항상 이 구조입니다.

{"category":"배송","priority":"HIGH","reason":"특정 기한 내에 상품 수령이 필요한 긴급한 배송 문의이기 때문입니다."}

이 비교 캡처가 오늘 제출물의 핵심입니다.

## 4. List 매핑 — 여러 건 받기

### record 여러 건 — ParameterizedTypeReference

public record MovieRecommendation(String title, int year, String reason) {
}

public List<MovieRecommendation> recommendMovies(String mood) {
return chatClient.prompt()
.user(u -> u.text("{mood} 기분일 때 볼 만한 영화 3편을 추천하세요.")
.param("mood", mood))
.call()
.entity(new ParameterizedTypeReference<List<MovieRecommendation>>() {});
}

.entity(List.class)는 안 됩니다. 제네릭 타입 정보는 컴파일 후 지워지므로(타입 소거) ParameterizedTypeReference로 전달합니다.

### 문자열 목록 — ListOutputConverter

public List<String> packingList(String destination, int days) {
return chatClient.prompt()
.user(u -> u.text("{destination}(으)로 {days}일 여행을 갈 때 챙길 준비물 목록을 만드세요.")
.param("destination", destination)
.param("days", days))
.call()
.entity(new ListOutputConverter(new DefaultConversionService()));
}

| 받고 싶은 것 | 쓰는 것

| 객체 한 건 | .entity(MyRecord.class)

| 객체 여러 건 | .entity(new ParameterizedTypeReference<List<MyRecord>>() {})

| 문자열 목록 | .entity(new ListOutputConverter(new DefaultConversionService()))

## 5. 응용 과제 (하나 이상)

- 영화/음악/책 추천기 (record List)

- 여행 준비물 목록 (ListOutputConverter)

- 회의록 액션아이템 추출기 — ActionItem(assignee, task, due) 리스트

- 이력서 키워드 추출기 — SkillProfile(strengths, keywords, jobFit)

- few-shot 실험 — 분류 템플릿에 예시 2개를 넣고 애매한 문의에서 zero-shot과 비교

무료 한도를 아끼려면 같은 입력을 재사용하세요. 429 RESOURCE_EXHAUSTED가 나오면 잠시 기다립니다.

## 6. README와 제출

README에 실행 방법, API 목록 표, 사용 모델, 배운 것(raw vs typed 소감 한 줄)을 정리하고 GitHub에 push합니다.

push 전 최종 확인: API Key가 코드·yml·커밋 어디에도 없는가?

제출물: GitHub URL / /api/summary 캡처 / /api/classify vs /api/classify/raw 비교 캡처 / 응용 API 캡처

## 자주 만나는 오류

| 증상 | 확인할 것

| {text}가 응답에 그대로 | .param() 이름과 템플릿 변수 이름

| .entity() 변환 예외 | 서버 로그에서 모델 응답 원문 확인 후 재호출

| record 필드가 null | 필드명과 프롬프트 항목명 일치 여부

| List<Object>가 옴 | List.class 대신 ParameterizedTypeReference

| 429 | 같은 입력 재사용, 잠시 대기

| 호출 시 500 | GOOGLE_API_KEY 환경변수