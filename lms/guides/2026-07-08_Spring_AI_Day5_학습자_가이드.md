# Spring AI Day5 학습자 가이드

> 2026-07-08 · Spring AI를 적용한 협약기업 서비스 구현
> 원본: learner-guide.html · ES LMS

---

Spring AI Day5 학습자 가이드

# 학습자 가이드 - Spring AI Day5

주제: Tool Calling / MCP

## 오늘 만드는 것

오늘도 처음부터 만들지 않습니다. day05-tool-calling-mcp-starter 프로젝트를 받으면, 그 안에 Day1~4에서 만든 기능이 이미 전부 들어있습니다. 그 위에 도구를 하나씩 늘리는 사다리로 Tool Calling과 MCP를 얹습니다.

오늘의 한 문장: 모델은 실행하지 않는다. 실행을 요청할 뿐이고, 실제 실행은 애플리케이션이 한다. 그리고 로컬 @Tool이든 외부 MCP 서버의 도구든, 결국 같은 ToolCallback으로 ChatClient에 붙는다.

|

| API
| 하는 일

| /api/ask
| 도구 없는 기본 챗 — 이전에 만든 것 (starter에 이미 있음)

| /api/tool/datetime
| 무인자 도구 하나 — 왕복 루프 증명 (오늘 1단계)

| /api/tool/customer
| 인자(@ToolParam) + record 반환 (2단계)

| /api/tool/rule
| 도메인 도구 하나 더 (3단계)

| /api/tool-chat
| 세 도구 전부, 모델이 선택 (4단계)

| /api/assistant
| 도구 + Chat Memory (5단계)

| /api/mcp/filesystem · /api/mcp/fetch
| 외부 MCP 서버 하나씩 (6·7단계)

| /api/mcp-chat · /api/mixed-chat
| 여러 서버 / 로컬+MCP 결합 (8·9단계)

## 0. 보일러플레이트 확인

day05-tool-calling-mcp-starter를 받으면 Day1~4 파일이 그대로 들어있습니다. GOOGLE_API_KEY를 설정하고 실행해서 /api/ask?question=지금 몇 시야?를 호출해보세요 — 모델은 실제 시각을 모르니 얼버무리거나 지어냅니다. 여기서 오늘의 질문이 나옵니다: 모델이 우리 앱의 함수를 부를 수 있다면?

## 1. Tool Calling — 모델은 요청만, 실행은 앱이

Tool Calling의 흐름은 왕복입니다.

- 앱이 모델에게 질문 + 도구 목록(이름·설명·입력 스키마)을 보냅니다.

- 모델이 "이 도구를 이 인자로 불러줘"라고 요청합니다(직접 실행 아님).

- 애플리케이션이 그 함수를 실행하고 결과를 모델에게 돌려줍니다.

- 모델이 그 결과로 최종 답을 만듭니다.

모델은 우리 함수·DB에 직접 접근하지 못합니다. 요청만 하고, 실행 권한은 애플리케이션이 쥡니다(보안). 이 왕복 루프는 Spring AI가 자동으로 돌려주므로, 우리가 쓰는 건 도구 하나와 .tools(...) 한 줄뿐입니다.

## 2. [1단계] 무인자 도구 — 왕복 루프 증명

tool/DateTimeTools.java (새 파일)

@Component
public class DateTimeTools {

@Tool(description = "현재 날짜와 시간을 사용자의 시간대 기준으로 반환한다")
String getCurrentDateTime() {
return LocalDateTime.now().atZone(LocaleContextHolder.getTimeZone().toZoneId()).toString();
}
}

description이 중요합니다 — 모델은 이 설명만 보고 "언제 이 도구를 부를지" 판단합니다.

ToolChatService.java (새 파일) — 로그를 눈으로 보려고 SimpleLoggerAdvisor를 붙입니다.

@Service
public class ToolChatService {

private final ChatClient chatClient;
private final DateTimeTools dateTimeTools;

public ToolChatService(ChatClient.Builder chatClientBuilder, DateTimeTools dateTimeTools) {
this.chatClient = chatClientBuilder.defaultAdvisors(new SimpleLoggerAdvisor()).build();
this.dateTimeTools = dateTimeTools;
}

public String chatDateTime(String question) {
return chatClient.prompt().user(question)
.tools(dateTimeTools) // ← 이 한 줄로 도구 전달
.call().content();
}
}

ApiController.java에 추가

@GetMapping("/api/tool/datetime")
public String toolDatetime(@RequestParam String question) {
return toolChatService.chatDateTime(question);
}

/api/tool/datetime?question=지금 날짜와 시간 알려줘를 호출하면 실제 시각이 나옵니다. 응답에 실제 시각이 있다는 것 자체가 도구가 실행됐다는 증거입니다. 로그를 보면 toolCalls: getCurrentDateTime → ToolResponseMessage(앱이 실행한 결과) → 최종 답변의 왕복이 찍힙니다.

## 3. [2단계] 인자 + record 반환

tool/CustomerTools.java (새 파일)

@Component
public class CustomerTools {

public record CustomerGrade(String customerId, String name, String grade, String responseSla) {
}

private static final Map<String, CustomerGrade> CUSTOMERS = Map.of(
"C001", new CustomerGrade("C001", "김에이스", "VIP", "1시간 이내"),
"C002", new CustomerGrade("C002", "이보람", "일반", "1영업일 이내"),
"C003", new CustomerGrade("C003", "박신입", "신규", "1영업일 이내"));

@Tool(description = "고객 ID로 고객의 등급(VIP/일반/신규)과 최초 응답 목표 시간(SLA)을 조회한다")
CustomerGrade getCustomerGrade(
@ToolParam(description = "고객 ID (예: C001)") String customerId) {
CustomerGrade grade = CUSTOMERS.get(customerId);
if (grade == null) {
return new CustomerGrade(customerId, "(등록되지 않음)", "미확인", "확인 불가");
}
return grade;
}
}

- @ToolParam: 인자에 설명을 붙여 모델이 무엇을 넣을지 알게 합니다.

- record 반환: 문자열보다 필드가 명확해 모델이 결과를 정확히 씁니다(재호출 오류 감소).

- 없는 고객도 예외 대신 값으로: 도구가 예외를 던지면 루프가 깨집니다.

ToolChatService에 customerTools 필드와 chatCustomer()를 추가하고, /api/tool/customer를 매핑합니다. ?question=C002 고객 등급 알려줘 → "C002 고객(이보람 님)의 등급은 일반입니다. SLA는 1영업일 이내입니다."

## 4. [3단계] 도메인 도구 하나 더 — 같은 패턴

tool/CompanyRuleTools.java (새 파일) — RULES Map(배포·코드리뷰·근무·보안)에서 조회하는 @Tool. 만드는 모양은 2단계와 똑같습니다.

@Tool(description = "주제 키워드로 사내 개발팀 규칙을 조회한다. 사용 가능한 주제: 배포, 코드리뷰, 근무, 보안")
String getCompanyRule(@ToolParam(description = "규칙 주제 (예: 배포, 코드리뷰, 근무, 보안)") String topic) {
return RULES.getOrDefault(topic, "'" + topic + "' 주제의 규칙은 등록되어 있지 않습니다. ...");
}

복선: 같은 "사내 규칙"을 뒤에서는 mcp-sandbox/사내-규칙.md 파일로 두고 filesystem MCP 서버가 읽어 오게 합니다. 출처만 다를 뿐(코드 Map vs 파일) 둘 다 같은 ToolCallback으로 붙습니다.

/api/tool/rule?question=코드리뷰 규칙이 뭐야? → "모든 변경은 Pull Request로 올리고 최소 1인의 리뷰 승인 후 병합합니다."

## 5. [4단계] 세 도구 전부 — 모델이 선택

ToolChatService.chat()에서 셋을 한 번에 줍니다.

public String chat(String question) {
return chatClient.prompt().user(question)
.tools(dateTimeTools, customerTools, companyRuleTools)
.call().content();
}

/api/tool-chat?question=C003 고객 등급과 근무 규칙 알려줘 → 모델이 getCustomerGrade와 getCompanyRule 두 도구만 부릅니다(현재 시각은 안 부름). 어떤 도구를 언제 부를지는 모델이 각 도구의 description을 보고 판단합니다.

## 6. [5단계] 도구 + Chat Memory 결합

실제 어시스턴트는 대화 맥락도 기억해야 합니다. Day3의 MessageChatMemoryAdvisor와 오늘의 도구를 한 ChatClient에 함께 붙입니다.

HelpdeskAssistantService.java (새 파일)

@Service
public class HelpdeskAssistantService {

private final ChatClient chatClient;
private final DateTimeTools dateTimeTools;
private final CustomerTools customerTools;
private final CompanyRuleTools companyRuleTools;

public HelpdeskAssistantService(ChatClient.Builder chatClientBuilder,
@Qualifier("inMemoryChatMemory") ChatMemory chatMemory,
DateTimeTools dateTimeTools, CustomerTools customerTools, CompanyRuleTools companyRuleTools) {
this.chatClient = chatClientBuilder
.defaultSystem("""
당신은 사내 헬프데스크 AI 어시스턴트입니다.
고객 문의에 답할 때는 필요하면 도구로 고객 등급·사내 규칙·현재 시각을 확인하세요.
고객 등급(VIP/일반/신규)에 따라 응대 우선순위와 톤을 맞추세요.
정중하고 간결한 한국어로 답변하세요.
""")
.defaultAdvisors(
MessageChatMemoryAdvisor.builder(chatMemory).build(),
new SimpleLoggerAdvisor())
.build();
this.dateTimeTools = dateTimeTools;
this.customerTools = customerTools;
this.companyRuleTools = companyRuleTools;
}

public String chat(String question, String conversationId) {
return chatClient.prompt().user(question)
.tools(dateTimeTools, customerTools, companyRuleTools)
.advisors(spec -> spec.param(ChatMemory.CONVERSATION_ID, conversationId))
.call().content();
}
}

@Qualifier("inMemoryChatMemory")는 Day3에서 만든 빈을 그대로 재사용합니다. /api/assistant(질문 + conversationId)를 매핑하고, 같은 conversationId로 두 번 물어보세요.

[턴1] /api/assistant?question=C001 고객 등급 확인해줘&conversationId=hd-1
→ C001 고객님(김에이스 님)은 VIP 등급이시며, SLA는 1시간 이내입니다.
[턴2] /api/assistant?question=그 고객 SLA는?&conversationId=hd-1
→ C001 고객님의 최초 응답 목표 시간(SLA)은 1시간 이내입니다.

턴2는 "C001"도 "등급"도 말하지 않았는데 정확히 답합니다 — 턴1의 도구 호출 결과가 Chat Memory에 남아 재사용된 것입니다. (도구만 격리한 /api/tool-chat을 먼저 본 뒤 여기로 오면, "달라진 게 memory 때문"임이 분명해집니다.)

## 7. MCP — 도구를 표준 프로토콜로

getCompanyRule 같은 도구는 우리 앱에만 있습니다. "파일 읽기", "웹 가져오기" 같은 도구를 앱마다 새로 구현하는 대신, MCP(Model Context Protocol) 로 표준화된 서버에 붙어 그대로 가져다 씁니다. 핵심은 MCP 서버의 도구도 결국 ToolCallback으로 변환된다는 것 — 로컬 @Tool과 완전히 같은 방식으로 붙습니다.

의존성 (build.gradle)

implementation 'org.springframework.ai:spring-ai-starter-mcp-client'

샌드박스 — filesystem 서버가 읽어 올 폴더. 프로젝트 루트 아래 mcp-sandbox/에 사내-규칙.md·고객-등급-정책.md·자주묻는질문.md를 둡니다(헬프데스크 테마의 실제 내용).

application.yml

spring:
ai:
mcp:
client:
request-timeout: 60s # fetch는 웹을 가져오니 기본 20초로는 빠듯 → 60초
stdio:
connections:
filesystem:
command: npx
args: ["-y", "@modelcontextprotocol/server-filesystem", "${user.dir}/mcp-sandbox"]
fetch: # 같은 구조, command/args만 다름. fetch는 Python이라 uvx
command: uvx
args: ["mcp-server-fetch"]

${user.dir}는 앱 실행 위치(프로젝트 루트)로 해석되어 PC마다 자동으로 맞습니다.

## 8. 서버별로 도구를 골라 주는 카탈로그

connection마다 McpSyncClient 빈이 하나씩 생깁니다. 이들을 List로 받아 서버 이름으로 filesystem/fetch를 가려냅니다. 그리고 시작 시 한 번만 도구를 해석해 캐시합니다.

McpToolCatalog.java (새 파일)

@Component
public class McpToolCatalog {

private final ToolCallback[] filesystemTools;
private final ToolCallback[] fetchTools;
private final ToolCallback[] allTools;

public McpToolCatalog(List<McpSyncClient> mcpClients) {
this.allTools = toolsFrom(mcpClients);
this.filesystemTools = toolsFrom(clientsNamed(mcpClients, "filesystem"));
this.fetchTools = toolsFrom(clientsNamed(mcpClients, "fetch"));
}

public ToolCallback[] filesystemTools() { return filesystemTools; }
public ToolCallback[] fetchTools() { return fetchTools; }
public ToolCallback[] allTools() { return allTools; }

private static List<McpSyncClient> clientsNamed(List<McpSyncClient> clients, String nameFragment) {
return clients.stream()
.filter(c -> c.getServerInfo().name().toLowerCase().contains(nameFragment))
.toList();
}

private static ToolCallback[] toolsFrom(List<McpSyncClient> clients) {
return SyncMcpToolCallbackProvider.builder().mcpClients(clients).build().getToolCallbacks();
}
}

왜 시작 시 한 번만? getToolCallbacks()는 서버에 tools/list를 보내는 작업입니다. 요청마다 새로 만들면 매 호출이 서버 응답성에 묶여, fetch가 느릴 때 filesystem 질문까지 타임아웃납니다. 한 번 해석해 캐시하는 게 정석입니다.

## 9. [6·7·8단계] MCP 서버 하나씩 → 여러 서버

McpChatService.java (새 파일) — 도구는 호출마다 .tools(...)로 넘겨 엔드포인트별로 다른 서버를 붙입니다.

@Service
public class McpChatService {

private final ChatClient chatClient;
private final McpToolCatalog catalog;

public McpChatService(ChatClient.Builder chatClientBuilder, McpToolCatalog catalog) {
this.chatClient = chatClientBuilder.defaultAdvisors(new SimpleLoggerAdvisor()).build();
this.catalog = catalog;
}

public String chatFilesystem(String q) {
return chatClient.prompt().user(q).tools((Object[]) catalog.filesystemTools()).call().content();
}
public String chatFetch(String q) {
return chatClient.prompt().user(q).tools((Object[]) catalog.fetchTools()).call().content();
}
public String chat(String q) {
return chatClient.prompt().user(q).tools((Object[]) catalog.allTools()).call().content();
}
}

.tools(...)는 @Tool 객체와 ToolCallback 배열을 모두 받는 이종 메서드입니다(deprecated된 .toolCallbacks(...) 대신 사용).

- /api/mcp/filesystem?question=접근 가능한 파일을 확인하고 사내 규칙 문서에서 배포 규칙만 한 줄로 알려줘. → "배포는 화·목 오후에만 …" (모델이 list_allowed_directories → list_directory → read_text_file을 연쇄 호출)

- /api/mcp/fetch?question=https://example.com 을 가져와 제목만 → "Example Domain"

- fetch 전용 엔드포인트에 "파일 읽어줘"를 하면 못 읽습니다 — filesystem 도구가 없으니까요. 이게 서버별 분리가 실제로 된다는 증거입니다.

경로 주의: 질문에 "mcp-sandbox 폴더의…"라고 하면 모델이 경로를 이중으로 붙여 오류가 납니다. 경로는 서버 허용 루트 기준 상대입니다. "접근 가능한 파일을 먼저 확인하고"처럼 목록부터 유도하세요.

## 10. [9단계] 로컬 @Tool + MCP 도구를 한 ChatClient에 — 캡스톤

오늘의 결론을 코드로. 로컬 도구와 MCP 도구를 한 프롬프트에 함께 붙입니다.

MixedChatService.java (새 파일) — 핵심 한 줄:

return chatClient.prompt()
.user(question)
.tools(dateTimeTools, customerTools, companyRuleTools, // 로컬 @Tool
catalog.allTools()) // + 모든 MCP 서버 도구
.call().content();

/api/mixed-chat?question=C002 고객 등급을 확인하고, 비밀번호를 잊었을 때 어떻게 하는지 FAQ 문서에서 찾아서 둘 다 알려줘.

→ 로컬 getCustomerGrade(등급)와 MCP read_text_file(FAQ 파일)이 한 대화에서 함께 발화합니다. 출처가 다른 도구를 모델이 자연스럽게 골라 쓰는 건, 둘 다 같은 ToolCallback이기 때문입니다.

## 11. (CHALLENGE, 선택) 우리 앱을 MCP 서버로 노출

지금까지 남의 MCP 서버를 소비(Client) 했다면, 이번엔 우리 도구를 MCP 서버로 노출(Server) 합니다. 노출은 @Tool이 아니라 @McpTool(별개 애너테이션)로 합니다.

implementation 'org.springframework.ai:spring-ai-starter-mcp-server-webmvc'

server:
protocol: STREAMABLE # webmvc + STREAMABLE이라 기존 REST 웹앱과 한 프로세스에서 /mcp 제공
name: helpdesk-mcp-server
version: 1.0.0

tool/HelpdeskMcpServerTools.java (새 파일) — @McpTool로 두 도구 노출:

@Component
public class HelpdeskMcpServerTools {
// CustomerTools, CompanyRuleTools 주입 ...

@McpTool(name = "get_customer_grade", description = "고객 ID로 등급과 SLA를 조회한다")
public CustomerTools.CustomerGrade getCustomerGrade(
@McpToolParam(description = "고객 ID (예: C001)") String customerId) {
return customerTools.getCustomerGrade(customerId);
}

@McpTool(name = "get_company_rule", description = "주제로 사내 규칙을 조회한다")
public String getCompanyRule(@McpToolParam(description = "규칙 주제") String topic) {
return companyRuleTools.getCompanyRule(topic);
}
}

앱을 기동하면 로그에 Registered tools: 2가 찍힙니다. MCP Inspector로 외부에서 우리 도구를 호출해봅니다:

npx @modelcontextprotocol/inspector --cli http://localhost:8080/mcp --transport http --method tools/list
# → get_customer_grade, get_company_rule 두 도구 조회됨

이제 우리 앱은 MCP 클라이언트(filesystem·fetch 소비)이자 MCP 서버(도구 2개 노출) 를 겸합니다 — 같은 도구, 방향만 반대입니다.

## 12. README와 제출

- 실행 방법, API 목록(누적), Tool 사다리 각 단계 캡처, /api/assistant 2턴 캡처, MCP filesystem·fetch·mixed-chat 캡처를 README에 정리

- API Key가 코드/저장소에 없는지 확인

- Git commit, GitHub push, LMS에 저장소 URL 제출

## 자주 만나는 오류

|

| 증상
| 원인
| 해결

| tool이 안 불림
| @Tool(description=...) 없음/모호, .tools() 미등록
| 설명을 구체적으로, .tools(...)에 등록

| MCP 실습에서 앱이 아예 안 뜸
| MCP 서버 연결 실패(npx/uvx 부재 등) → 컨텍스트 전체 실패
| npx --version/uvx --version 확인, 서버 명령을 직접 실행해 보기

| filesystem이 ENOENT
| 경로를 이중으로 붙임
| 경로는 서버 허용 루트 기준 상대 — "접근 가능한 파일 먼저 확인" 유도

| filesystem 질문인데 타임아웃
| MCP 도구를 요청마다 재해석
| 카탈로그처럼 시작 시 한 번만 해석해 캐시

| fetch 타임아웃
| 웹 지연
| request-timeout: 60s, 그래도 느리면 재시도

| @McpTool인데 목록에 없음
| 클라이언트측 @Tool과 혼동
| 노출은 @McpTool/@McpToolParam