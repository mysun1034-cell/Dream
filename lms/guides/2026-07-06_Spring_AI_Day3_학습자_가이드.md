# Spring AI Day3 학습자 가이드

> 2026-07-06 · Spring AI를 적용한 협약기업 서비스 구현
> 원본: learner-guide.html · ES LMS

---

Spring AI Day3 학습자 가이드

# 학습자 가이드 — Spring AI Day3

주제: Advisor와 Chat Memory — 반복되는 LLM 호출 공통 처리와 대화 맥락

오늘의 한 문장: 어제는 응답을 타입으로 받았다. 오늘부터는 호출 자체에 공통 규칙이 자동으로 걸리고, 대화가 기억된다.

## 오늘 만드는 것

오늘은 처음부터 만들지 않습니다. day03-advisor-memory-starter 프로젝트를 받아서, 그 위에 아래 기능을 얹습니다.

| API | 하는 일

| /api/ask | 기본 질의응답 (starter에 이미 있음)

| /api/ask-limited | 응답 길이 제한값을 호출별로 지정 (오늘 추가)

| /api/call-count | 이번 서버 실행 동안 LLM 호출 횟수 조회 (오늘 추가)

| /api/chat-memory | In-Memory Chat Memory 적용 대화형 API (오늘 추가)

| /api/chat-persistent | H2(JDBC) 기반 영구 Chat Memory 적용 대화형 API (오늘 추가)

## 0. 보일러플레이트 확인

day03-advisor-memory-starter를 받으면 AssistantService.ask()와 /api/ask 하나만 있습니다. GOOGLE_API_KEY 환경변수를 설정하고 먼저 실행해서 정상 동작하는지 확인하세요.

## 1. 커스텀 Advisor 만들기

Advisor는 LLM 요청/응답을 가로채는 인터셉터입니다.

### 1.1 응답 길이 제한 Advisor

advisor/MaxCharLengthAdvisor.java (새로 만듦)

public class MaxCharLengthAdvisor implements CallAdvisor {

public static final String MAX_CHAR_LENGTH = "maxCharLength";
private final int defaultMaxCharLength;
private final int order;

public MaxCharLengthAdvisor(int defaultMaxCharLength, int order) {
this.defaultMaxCharLength = defaultMaxCharLength;
this.order = order;
}

@Override
public int getOrder() { return this.order; }

@Override
public ChatClientResponse adviseCall(ChatClientRequest request, CallAdvisorChain chain) {
ChatClientRequest mutatedRequest = augmentPrompt(request);
ChatClientResponse response = chain.nextCall(mutatedRequest);
return response;
}

private ChatClientRequest augmentPrompt(ChatClientRequest request) {
Integer maxCharLength = (Integer) request.context().get(MAX_CHAR_LENGTH);
int limit = maxCharLength != null ? maxCharLength : this.defaultMaxCharLength;
String instruction = limit + "자 이내로 답변해 주세요.";

Prompt augmentedPrompt = request.prompt().augmentUserMessage(
userMessage -> UserMessage.builder()
.text(userMessage.getText() + " " + instruction)
.build());

return request.mutate().prompt(augmentedPrompt).build();
}
}

포인트: augmentUserMessage()는 기존 메시지를 덮어쓰지 않고 뒤에 덧붙입니다.

### 1.2 LLM 호출 횟수 카운터 Advisor

advisor/CallCounterAdvisor.java (새로 만듦)

@Component
public class CallCounterAdvisor implements CallAdvisor {

private final AtomicInteger callCount = new AtomicInteger(0);

@Override
public int getOrder() { return Ordered.LOWEST_PRECEDENCE - 1; }

@Override
public ChatClientResponse adviseCall(ChatClientRequest request, CallAdvisorChain chain) {
ChatClientResponse response = chain.nextCall(request);
this.callCount.incrementAndGet();
return response;
}

public int getCallCount() { return this.callCount.get(); }
}

@Component로 등록해야 여러 서비스에서 같은 인스턴스를 공유해 카운트가 제대로 누적됩니다.

## 2. AssistantService에 Advisor 얹기

AssistantService.java (수정 — 생성자만 바뀝니다)

public AssistantService(ChatClient.Builder chatClientBuilder, CallCounterAdvisor callCounterAdvisor) {
this.chatClient = chatClientBuilder
.defaultSystem("...")
.defaultAdvisors(
new MaxCharLengthAdvisor(300, Ordered.HIGHEST_PRECEDENCE),
new SafeGuardAdvisor(
List.of("욕설", "계좌번호", "폭력", "폭탄"),
"해당 질문은 민감한 콘텐츠 요청이므로 응답할 수 없습니다.",
Ordered.HIGHEST_PRECEDENCE + 1),
callCounterAdvisor,
new SimpleLoggerAdvisor(Ordered.LOWEST_PRECEDENCE))
.build();
}

ask() 메서드는 한 글자도 바뀌지 않습니다 — 이게 오늘의 핵심입니다.

application.yml에 로그 설정을 추가하면 SimpleLoggerAdvisor의 요청/응답 로그를 볼 수 있습니다.

logging:
level:
org.springframework.ai.chat.client.advisor: DEBUG

/api/ask 호출 시 순서: MaxCharLengthAdvisor(전처리) → SimpleLoggerAdvisor(request) → LLM 호출 → SimpleLoggerAdvisor(response) → CallCounterAdvisor → MaxCharLengthAdvisor(후처리). 먼저 전처리한 게 나중에 후처리하는 양파 구조를 로그로 확인하세요.

계좌번호처럼 민감한 질문을 넣으면 SafeGuardAdvisor가 LLM을 아예 호출하지 않고 차단 응답을 돌려줍니다.

## 3. Chat Memory (In-Memory)

LLM은 상태가 없습니다. /api/ask로 이름을 알려주고 다음 호출에 물어보면 기억하지 못합니다.

ChatMemoryConfig.java (새로 만듦)

@Configuration
public class ChatMemoryConfig {

@Bean("inMemoryChatMemory")
public ChatMemory inMemoryChatMemory() {
return MessageWindowChatMemory.builder()
.chatMemoryRepository(new InMemoryChatMemoryRepository())
.maxMessages(20)
.build();
}

@Bean("jdbcChatMemory")
public ChatMemory jdbcChatMemory(JdbcChatMemoryRepository jdbcChatMemoryRepository) {
return MessageWindowChatMemory.builder()
.chatMemoryRepository(jdbcChatMemoryRepository)
.maxMessages(20)
.build();
}
}

MemoryChatService.java (새로 만듦)

@Service
public class MemoryChatService {

private final ChatClient chatClient;

public MemoryChatService(@Qualifier("inMemoryChatMemory") ChatMemory chatMemory,
ChatClient.Builder chatClientBuilder) {
this.chatClient = chatClientBuilder
.defaultAdvisors(MessageChatMemoryAdvisor.builder(chatMemory).build())
.build();
}

public String chat(String question, String conversationId) {
return chatClient.prompt()
.user(question)
.advisors(spec -> spec.param(ChatMemory.CONVERSATION_ID, conversationId))
.call()
.content();
}
}

책을 보고 있다면 주의하세요 — 교재의 PromptChatMemoryAdvisor는 Spring AI 2.0.0에서 완전히 삭제되어 컴파일이 안 됩니다. MessageChatMemoryAdvisor만 사용하세요.

conversationId는 필수입니다 — 빠뜨리면 IllegalArgumentException이 납니다.

## 4. Controller에 매핑하고 비교하기

같은 conversationId로 두 번 호출해서 이름을 기억하는지 확인하세요.

GET /api/chat-memory?question=내 이름은 민준이야. 기억해줘.&conversationId=my-test-1
GET /api/chat-memory?question=내 이름이 뭐라고 했지?&conversationId=my-test-1

/api/ask(Memory 없음)로 같은 실험을 해보면 정반대 결과가 나옵니다 — 이 차이를 캡처하는 것이 오늘 제출물의 핵심입니다.

## 5. H2(JDBC)로 영구 저장하기

build.gradle에 의존성 3개 추가:

implementation 'org.springframework.boot:spring-boot-starter-jdbc'
implementation 'org.springframework.ai:spring-ai-starter-model-chat-memory-repository-jdbc'
runtimeOnly 'com.h2database:h2'

application.yml에 설정 추가:

spring:
ai:
chat:
memory:
repository:
jdbc:
initialize-schema: always
datasource:
url: jdbc:h2:file:./data/chatmemory
driver-class-name: org.h2.Driver
username: sa
password:

initialize-schema: embedded(공식 문서 기본값)로 두면 H2 파일 모드에서 스키마 테이블이 생성되지 않습니다. 반드시 always로 명시하세요.

PersistentChatService.java는 MemoryChatService와 구조가 완전히 같고, @Qualifier("jdbcChatMemory")만 다릅니다.

### 재시작 테스트 — 오늘의 핵심 체험

- /api/chat-persistent?question=내 이름은 OO야. 기억해줘.&conversationId=test1 호출

- 서버를 완전히 종료합니다 (Ctrl+C)

- 서버를 다시 실행합니다

- /api/chat-persistent?question=내 이름이 뭐라고 했지?&conversationId=test1로 다시 물어봅니다

같은 실험을 /api/chat-memory(In-Memory)로도 해보세요. 둘의 결과가 다릅니다 — 이 대조가 오늘 제출물의 하이라이트입니다.

## 6. README와 제출

실행 방법, API 목록 표, 사용한 Advisor 목록, In-Memory vs JDBC 재시작 테스트 결과, 배운 것 한 줄을 정리하고 GitHub에 push합니다.

push 전 최종 확인: API Key가 코드·yml·커밋 어디에도 없는가? data/ 폴더가 .gitignore에 들어있는가?

제출물: GitHub URL / Advisor 체이닝 순서 로그 캡처 / Memory 없음 vs 있음 비교 캡처 / 재시작 후 응답 캡처

## 자주 만나는 오류

| 증상 | 확인할 것

| Advisor를 만들었는데 동작이 안 바뀜 | defaultAdvisors()에 실제로 등록했는지

| Advisor 순서가 뒤죽박죽 | 서로 다른 getOrder() 값을 줬는지

| IllegalArgumentException | conversationId 파라미터를 빼먹지 않았는지

| H2 스키마 테이블 없음 오류 | initialize-schema: always인지

| 재시작해도 대화가 안 남음 | jdbc:h2:mem:이 아니라 jdbc:h2:file:인지

| SafeGuardAdvisor가 정상 질문도 차단 | sensitiveWords 목록이 너무 일반적이지 않은지