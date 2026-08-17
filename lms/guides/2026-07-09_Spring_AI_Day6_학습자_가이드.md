# Spring AI Day6 학습자 가이드

> 2026-07-09 · Spring AI를 적용한 협약기업 서비스 구현
> 원본: learner-guide.html · ES LMS

---

Spring AI Day6 학습자 가이드

# 학습자 가이드 - Spring AI Day6

주제: Streaming/Flux + Front → Back → AI → DB 통합

## 오늘 만드는 것

오늘은 Spring AI 6일 과정의 마지막 날이자 첫 프론트엔드 day입니다. 처음부터 만들지 않습니다. day06-streaming-react-starter 프로젝트를 받으면, Day5까지 만든 헬프데스크 코어(ChatClient · 로컬 도구 3종 · Chat Memory)가 이미 들어 있습니다. 그 위에 스트리밍 · DB 영속 · React 화면만 얹습니다.

오늘의 목표는 완벽한 숙달이 아니라 하나의 흐름을 끝까지 경험하는 것입니다: 브라우저에 문의를 넣으면 답이 토큰별로 흘러나오고, 창을 닫았다 열어도 대화가 DB에서 복원됩니다.

최종 결과물: AI 사내 헬프데스크 채팅 화면 하나. 전체 그림은 이렇습니다.

[프론트 · React 5173] 채팅 UI · EventSource(브라우저 내장)
[백엔드 · Spring AI 8080] ApiController · HelpdeskService(ChatClient + tools + memory)

EventSource ──① 문의(SSE 스트림)───────▶ ApiController
채팅 UI ──② history(새로고침 복원)──▶ ApiController
ApiController ──▶ HelpdeskService
HelpdeskService ──stream() + tools + memory──▶ Gemini(gemini-3.1-flash-lite)
HelpdeskService ──JDBC ChatMemory────────────▶ PostgreSQL(Docker · 5432)

1막에서 ①번 화살표(스트리밍)를, 2막에서 DB·②·CORS·React를 붙입니다. 이 앱은 그대로 미니 프로젝트 2의 출발 템플릿이 됩니다.

2막 구성

|
| 막 | 내용

| 1막 (개념) | 스트리밍 — call() vs stream(), Flux<String>, SSE, EventSource

| 2막 (통합) | Docker로 PostgreSQL 기동 → JDBC ChatMemory로 영속 → history 조회 → CORS → React로 연결

## [1막] 스트리밍 개념

### 1. call() vs stream() — 왜 스트리밍인가

지금까지 Day1~5는 응답을 항상 call().content() 로 받았습니다 — 다 만들어진 뒤 한 번에. 답변이 길어지면(수백 자) 사용자는 완성될 때까지 빈 화면을 봅니다. 반면 ChatGPT·Gemini 화면은 글자가 흘러나옵니다. 그 차이의 핵심이 첫 글자까지의 시간(TTFT, time-to-first-token) 입니다.

- call() 은 전체 답이 만들어질 때까지 서버가 붙잡고 있다가 통째로 반환합니다. 긴 답일수록 첫 화면까지 오래 걸립니다.

- stream() 은 첫 토큰이 나오자마자 사용자에게 보냅니다. 총 시간이 같아도 체감 지연이 크게 줄어듭니다.

- 비유: call() 은 음식을 다 만들어 한 접시에 내오는 것, stream() 은 만들어지는 대로 조금씩 내오는 오마카세.

핵심은 "총 생성 시간"이 아니라 "첫 글자가 언제 보이나"입니다. 같은 답(총 3.0초)을 두 방식으로 받을 때:

call() │████████████ 생성 중 (화면은 빈 채) ████████████│▓ 통째로 등장
0s 3.0s ← 첫 글자 = 3.0s

stream() │▓흐르는 텍스트… … … … … … … … … … … … … … …│ 완료
0s └ 첫 글자 = 0.4s (TTFT) 3.0s

같은 3.0초여도 stream()은 0.4초에 이미 "반응"합니다 → 훨씬 빠르게 느껴집니다.

Spring AI에서는 호출 체인의 마지막만 바뀝니다.

// 완성 후 한 번에
String answer = chatClient.prompt().user(q).call().content(); // String

// 토큰이 오는 대로
Flux<String> tokens = chatClient.prompt().user(q).stream().content(); // Flux<String>

- Flux<String> 은 Reactor의 리액티브 스트림입니다. "0개 이상의 String이 시간에 걸쳐 흘러오는 통로" 정도로 이해하면 충분합니다(오늘은 리액티브 이론에 깊이 들어가지 않습니다).

- WebFlux 스타터 없이도 됩니다. spring-ai 가 Reactor Core를 끌어오므로, 우리 프로젝트는 spring-boot-starter-webmvc(WebFlux 아님) 그대로 Flux 를 씁니다.

### 1-1. 먼저 콘솔로 — 스트리밍을 눈으로 확인

브라우저·SSE·JSON은 잠깐 미루고, stream().content() 가 주는 Flux<String> 이 정말 토큰을 나눠 흘리는지부터 백엔드 콘솔에서 봅니다. 스트리밍의 본질만 떼어낸, 함정 0개짜리 단계입니다.

// 확인용 엔드포인트 (진짜 SSE 엔드포인트는 §4에서 만듭니다)
@GetMapping(value = "/api/chat/stream-console", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> streamConsole(@RequestParam String question,
@RequestParam(defaultValue = "console") String conversationId) {
return helpdeskAssistantService.chatStream(question, conversationId)
.doOnNext(token -> System.out.print("[" + token + "]")) // 지나가는 청크를 엿보기(peek)
.doOnComplete(() -> System.out.println("\n[스트림 완료]"));
}

curl -N "http://localhost:8080/api/chat/stream-console?question=환불 규정을 한 문장으로 안내해줘&conversationId=demo"

백엔드 콘솔 출력(실측):

[저][희 회사의 환불 규정은 결제일로부터 7일 이내에 미][사용 상태인 경우에 한하여 전액 환불이 가능합니다.]
[스트림 완료]

- 대괄호 경계 = Flux 가 여러 번 나눠 방출했다는 증거. 이게 스트리밍입니다(청크 크기는 모델·응답마다 다릅니다).

- 공백이 그대로 살아 있습니다. 즉 서버가 내보내는 토큰은 멀쩡합니다 — 뒤에서 볼 "공백 뭉갬(함정 A)"은 서버가 아니라 브라우저가 SSE를 파싱하는 경계에서 생깁니다. (그래서 서버를 WebFlux로 바꿔도 함정은 사라지지 않습니다 — §3 참고.)

### 2. 왜 SSE인가 — text/event-stream 과 EventSource

- SSE(Server-Sent Events): 서버가 클라이언트로 한 방향으로 이벤트를 계속 흘려보내는 표준입니다. HTTP 응답의 Content-Type: text/event-stream 으로 열고, data: 라인 하나가 이벤트 하나가 됩니다.

- 왜 SSE인가: 스트리밍 채팅은 서버→클라이언트 단방향이면 충분합니다(양방향이 필요 없으니 WebSocket은 과합니다). 게다가 브라우저에 EventSource 가 내장돼 있어 별도 라이브러리가 필요 없습니다 — 첫 프론트 day에 딱 맞습니다.

- 트레이드오프: EventSource 는 GET만 되고 요청 본문·커스텀 헤더가 없습니다. 그래서 question · conversationId를 쿼리 파라미터로 넘깁니다. (큰 본문·헤더가 필요하면 fetch + ReadableStream 을 써야 하지만 오늘 범위 밖입니다.)

### 3. ⚠ 스트리밍의 두 함정 (1막의 핵심)

스트리밍은 빌드·테스트·lint가 다 통과해도 조용히 실패할 수 있습니다. 브라우저에서 눈으로 확인하지 않으면 놓치는 두 가지가 있고, 아래 코드는 둘 다 해결한 정답입니다.

함정 A — SSE가 공백을 뭉갠다. 토큰을 날문자열로 data: 에 실으면, SSE 규격상 data: 뒤 선행 공백 한 칸이 제거되고 값 안의 줄바꿈이 이벤트 경계로 해석됩니다. 그 결과 청크 경계에서 띄어쓰기가 사라집니다.

❌ 날문자열로 실으면
토큰 " 합니다"(앞 공백) ──▶ data: 합니다 ──▶ SSE가 선행 공백 1칸 제거 ──▶ 화면 "처리해야합니다"

✅ JSON으로 감싸면
토큰 " 합니다" ──▶ data:{"text":" 합니다"} ──▶ 따옴표 안 공백 보존 ──▶ JSON.parse(e.data).text → " 합니다" ✅

예: "처리해야 합니다" 가 화면엔 "처리해야합니다", "것에 그치지" 가 "것에그치지" 로 붙어 버립니다. 한국어라 티가 덜 나지만 분명히 깨집니다.

- 해결: 각 토큰을 JSON으로 감싸서 보냅니다({"text":"..."}). 따옴표 안에서는 공백·줄바꿈이 그대로 보존되고, 클라이언트는 JSON.parse(e.data).text 로 되꺼냅니다. record StreamChunk 하나면 Spring이 자동으로 JSON 직렬화합니다.

함정 B — EventSource 는 무한 재연결한다. Flux 가 완료돼 서버가 SSE를 닫으면, EventSource 는 그것을 연결 끊김으로 보고 자동으로 다시 연결합니다. 그러면 같은 질문이 도구 호출·메모리까지 통째로 재실행되며 응답이 반복됩니다(Gemini 호출도 매번 재과금).

Flux 완료 → 서버가 SSE 닫음
│
▼
클라가 완료 신호를 받았나?
│
├─ 아니오(신호 없음) ──▶ EventSource가 끊김으로 오해 → 자동 재연결
│ └─▶ 같은 질문 재실행(tool + memory + 과금 반복)
│ └─▶ 다시 "Flux 완료"로 ⟲ 무한 루프
│
└─ 예(done 이벤트 수신) ──▶ es.close() → 재연결 없음 ✅

완료 신호가 없으면 같은 답변이 몇 번이고 반복됩니다 — 명백한 무한 루프입니다.

주의: 완료 이벤트를 event:done 만 보내고 data를 비우면 여전히 재연결됩니다 — SSE는 data가 비면 이벤트를 전달하지 않기 때문입니다. 완료 이벤트도 반드시 data를 채워야 합니다({"text":""}).

- 해결: 스트림 끝에 done 이벤트(빈 내용이라도 data 포함) 를 덧붙이고, 클라이언트가 done 을 받으면 eventSource.close() 로 스스로 닫습니다.

Q. WebFlux를 넣으면 StreamChunk·done 코드 없이 더 단순해지나요?

아니요. ① 우리는 이미 WebFlux 없이(spring-boot-starter-webmvc만) 스트리밍이 됩니다 — Spring MVC가 Flux 반환 SSE를 지원합니다. ② 두 함정은 서버가 아니라 브라우저 경계 문제입니다: 함정 A는 EventSource 가 data: 를 파싱할 때 공백을 지우고(§1-1에서 봤듯 서버 토큰은 멀쩡), 함정 B는 브라우저의 자동 재연결입니다. 서버 프레임워크를 바꿔도 둘 다 그대로입니다. 튜토리얼이 Flux<String> 만으로 "잘 되는" 것처럼 보이는 건 영어 토큰이라 공백 소실이 눈에 안 띄고 재연결 처리를 생략했기 때문입니다 — 한국어에선 곧바로 깨집니다. StreamChunk+done 은 프레임워크와 무관한 견고한 정답입니다.

## 4. 백엔드 — 스트리밍 엔드포인트

작성 파일 3개. 서비스는 .call() 을 .stream() 으로만 바꾸고, 컨트롤러가 SSE로 감쌉니다.

src/main/java/com/study/day06streamingreact/HelpdeskAssistantService.java (스트리밍 메서드 추가)

/**
* 스트리밍판 — call() 대신 stream().content()로 Flux<String>를 반환한다.
* 토큰이 생성되는 대로 방출되며, tool·memory advisor는 그대로 함께 동작한다
* (tool 호출 라운드가 끝난 뒤 최종 답변이 토큰 단위로 스트리밍된다).
*/
public Flux<String> chatStream(String question, String conversationId) {
return chatClient.prompt()
.user(question)
.tools(dateTimeTools, customerTools, companyRuleTools)
.advisors(spec -> spec.param(ChatMemory.CONVERSATION_ID, conversationId))
.stream()
.content();
}

src/main/java/com/study/day06streamingreact/StreamChunk.java (공백 보존용 JSON 래퍼 — 함정 A 해결)

public record StreamChunk(String text) {
}

src/main/java/com/study/day06streamingreact/ApiController.java (스트리밍 엔드포인트)

@GetMapping(value = "/api/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<ServerSentEvent<StreamChunk>> chatStream(@RequestParam String question,
@RequestParam String conversationId) {
// 각 토큰을 StreamChunk(record)로 감싸면 Spring이 data:{"text":"..."} JSON으로 직렬화한다(공백 보존).
Flux<ServerSentEvent<StreamChunk>> tokens = helpdeskAssistantService
.chatStream(question, conversationId)
.map(chunk -> ServerSentEvent.builder(new StreamChunk(chunk)).build());
// 완료 신호. SSE는 data가 비면 이벤트를 전달하지 않으므로 반드시 data를 채운다(함정 B 해결).
Flux<ServerSentEvent<StreamChunk>> done = Mono
.just(ServerSentEvent.<StreamChunk>builder(new StreamChunk("")).event("done").build())
.flux();
return tokens.concatWith(done);
}

- produces = MediaType.TEXT_EVENT_STREAM_VALUE 가 이 엔드포인트를 SSE로 만듭니다. WebMVC에서도 Flux 반환을 SSE로 흘려보낼 수 있습니다(WebFlux 불필요).

- 도구를 쓰는 질문이면 먼저 tool 호출 라운드가 돌고(이 라운드는 스트리밍되지 않음), 그 뒤 최종 답변만 토큰 단위로 흐릅니다. 스트리밍 + tool + memory가 함께 동작합니다.

### 브라우저에서 확인

앱을 실행하고 주소창에 직접 열어 봅니다.

http://localhost:8080/api/chat/stream?question=환불 규정 알려줘&conversationId=test-1

data:{"text":"..."} 이벤트가 토큰별로 도착하고, 마지막에 event:done 이 오면 성공입니다. 공백·줄바꿈이 보존돼 있는지 확인하세요.

## [2막] 통합 — Docker · DB · React

## 5. Docker로 PostgreSQL 기동

### 5.1 왜 실제 DB 서버인가

지금까지 대화는 InMemoryChatMemoryRepository — 앱을 재시작하면 사라집니다. 진짜 서비스는 독립된 DB 서버(PostgreSQL 등)에 데이터를 둡니다. 미니 프로젝트 2도 DB가 필요합니다. 오늘 그 DB 서버를 세우는 경험을 합니다.

왜 Docker인가: PostgreSQL을 OS에 직접 설치하면 버전·경로·서비스 등록이 사람마다 다르고 되돌리기 어렵습니다. Docker는 docker compose up 한 줄로 정해진 버전의 DB를 띄우고, down 으로 깔끔히 지웁니다. 인프라를 코드(compose.yaml)로 고정하는 첫 경험입니다.

### 5.2 Windows 최초 설치 (Docker Desktop / WSL2)

Docker Desktop은 Windows에서 WSL2(경량 리눅스 커널) 위에서 컨테이너를 돌립니다. 구조는 이렇습니다.

Windows 11
└─▶ WSL2 (경량 리눅스 커널)
└─▶ Docker Desktop 엔진
└─▶ postgres:16 컨테이너 :5432
▲
│ JDBC
Spring Boot 8080 (jdbc:postgresql://localhost:5432) ──┘

처음 쓴다면 아래 순서대로 설치합니다. (설치 화면 스크린샷은 Docker 공식 문서 docs.docker.com/desktop/setup/install/windows-install 를 참고하세요.)

- 요구사항 확인: Windows 10/11 64-bit, 8GB RAM, BIOS/UEFI에서 하드웨어 가상화 활성화.

- WSL2 설치(1회, 관리자 PowerShell): wsl --install → wsl --update → 재부팅 → wsl --version 으로 확인.

- Docker Desktop 내려받기: 공식 사이트에서 Windows 설치 파일(또는 Microsoft Store).

- 설치: Docker Desktop Installer.exe 실행. 설정 화면에서 "Use WSL 2 instead of Hyper-V" 를 선택합니다. 완료 후 Docker Desktop을 실행합니다.

- 확인: docker --version / docker compose version / docker run hello-world 가 되면 성공입니다.

### 5.3 compose.yaml

프로젝트 루트에 compose.yaml 을 둡니다.

services:
postgres:
image: postgres:16
container_name: helpdesk-postgres
environment:
POSTGRES_DB: helpdesk
POSTGRES_USER: helpdesk
POSTGRES_PASSWORD: helpdesk
ports:
- "5432:5432"
volumes:
- helpdesk-pgdata:/var/lib/postgresql/data

volumes:
helpdesk-pgdata:

- 기동: docker compose up -d → 확인: docker ps → 종료: docker compose down(데이터까지 지우려면 docker compose down -v).

- volumes 로 named volume을 두면 컨테이너를 지웠다 다시 만들어도 데이터가 남습니다.

## 6. JDBC ChatMemory — LLM 컨텍스트를 DB에 영속(윈도우)

이번 단계는 LLM에게 줄 최근 맥락을 DB에 남깁니다. memory advisor가 대화마다 자동으로 SPRING_AI_CHAT_MEMORY에 씁니다. 단, 이건 최근 20개 윈도우라 오래된 건 지워집니다 — 사람이 볼 전체 이력은 §7에서 별도 테이블에 따로 쌓습니다.

문의 ──▶ MessageChatMemoryAdvisor ──▶ user·assistant 자동 기록(최근 20개 윈도우)
▼
[PostgreSQL · SPRING_AI_CHAT_MEMORY]

Day3에서 검증한 JDBC ChatMemory 패턴을 datasource · 드라이버만 바꿔 Postgres로 옮깁니다. 코드는 dialect를 URL로 자동 감지하므로 거의 그대로입니다.

build.gradle (의존성 3개 추가)

implementation 'org.springframework.boot:spring-boot-starter-jdbc'
implementation 'org.springframework.ai:spring-ai-starter-model-chat-memory-repository-jdbc'
implementation 'org.springframework.boot:spring-boot-starter-data-jpa' // §7 chat_history용
runtimeOnly 'org.postgresql:postgresql'

src/main/resources/application.yml (datasource + 스키마 자동 생성 + JPA)

spring:
ai:
chat:
memory:
repository:
jdbc:
initialize-schema: always # 기동 시 SPRING_AI_CHAT_MEMORY 테이블 자동 생성
datasource:
url: jdbc:postgresql://localhost:5432/helpdesk
username: helpdesk
password: helpdesk
jpa: # §7 chat_history(@Entity)를 Hibernate가 만든다. Postgres 기본은 none.
hibernate:
ddl-auto: update
open-in-view: false

⚠ 의존성과 datasource는 함께 추가하세요. jdbc 스타터만 넣고 datasource 없이 실행하면 DataSourceAutoConfiguration이 URL을 못 찾아 부팅이 실패합니다(Failed to configure a DataSource: 'url' attribute is not specified…). 그래서 앞의 Docker 단계(§5)에서 Postgres를 먼저 띄운 뒤, 의존성+datasource를 같은 단계에서 넣습니다.

### 📌 JPA를 쓰나요? 테이블(DDL)은 누가 만드나요?

- 테이블이 둘, 방식도 둘입니다. SPRING_AI_CHAT_MEMORY(윈도우 memory)는 Spring AI가 순수 JDBC로 쓰고 @Entity가 없습니다. 반면 §7의 chat_history(전체 이력)는 우리가 JPA(@Entity, Hibernate)로 관리합니다.

- DDL도 테이블마다 다릅니다. SPRING_AI_CHAT_MEMORY는 initialize-schema: always로 스타터가 방언별 스키마(schema-postgresql.sql)를 실행해 만들고, chat_history는 ddl-auto: update로 Hibernate가 @Entity에서 만듭니다. 스타터가 만드는 실제 DDL:

CREATE TABLE IF NOT EXISTS SPRING_AI_CHAT_MEMORY (
conversation_id VARCHAR(36) NOT NULL,
content TEXT NOT NULL,
type VARCHAR(10) NOT NULL CHECK (type IN ('USER', 'ASSISTANT', 'SYSTEM', 'TOOL')),
"timestamp" TIMESTAMP NOT NULL,
sequence_id BIGINT NOT NULL
);
-- + conversation_id 기준 인덱스 2개(timestamp, sequence_id)

- 재시작해도 안전한 이유: DDL이 전부 CREATE … IF NOT EXISTS라 멱등입니다. 이미 있으면 건너뛰므로 always여도 다시 만들거나 에러 나지 않습니다.

src/main/java/com/study/day06streamingreact/ChatMemoryConfig.java (jdbc 빈 추가)

// JdbcChatMemoryRepository는 스타터가 DataSource로부터 자동설정한다.
// 대화가 SPRING_AI_CHAT_MEMORY 테이블에 쌓여 앱·DB를 재시작해도 남는다.
@Bean("jdbcChatMemory")
public ChatMemory jdbcChatMemory(JdbcChatMemoryRepository jdbcChatMemoryRepository) {
return MessageWindowChatMemory.builder()
.chatMemoryRepository(jdbcChatMemoryRepository)
.maxMessages(20)
.build();
}

그리고 HelpdeskAssistantService 생성자의 한정자를 바꿉니다: @Qualifier("inMemoryChatMemory") → @Qualifier("jdbcChatMemory"). 이 한 줄이 "휘발" → "영속"의 스위치입니다.

주의 — 이 테이블은 "전체 이력"이 아니라 최근 20개 윈도우입니다. maxMessages(20) 이므로 대화가 20개를 넘으면 저장할 때 오래된 메시지가 DB에서 삭제됩니다(항상 최근 ~20개만 남음). 목적이 "LLM에게 줄 최근 맥락 관리"라서 그렇습니다. 그래서 사람이 볼 전체 이력은 지우지 않는 별도 테이블이 필요합니다 — 바로 다음 §7에서 chat_history(JPA)를 만들어 거기에 쌓고, /api/history는 그쪽을 읽습니다.

### 확인

- 앱 기동 시 spring_ai_chat_memory 테이블이 자동 생성됩니다(conversation_id · content · type · timestamp · sequence_id 컬럼).

- 같은 conversationId로 멀티턴을 이어 봅니다. 턴1 "제 이름은 홍길동입니다" → 턴2 "제 이름이 뭐라고 했죠?" → 답변 "홍길동 님이라고 말씀해 주셨습니다". 턴2가 DB의 턴1을 읽어 이어집니다.

- 앱·DB를 재시작한 뒤에도 같은 대화가 남아 있으면 영속 성공입니다.

교육 포인트 — tool 메시지는 저장되지 않는다: JdbcChatMemoryRepository 는 tool-call/tool-response 메시지를 저장 시 조용히 버립니다. 헬프데스크가 도구를 써도 history엔 사용자 질문과 최종 답변 텍스트만 남습니다. 버그가 아니라 설계입니다 — history 화면에 도구 내부 왕복이 안 보이는 이유입니다.

## 7. chat history — 전체 이력 테이블(JPA)에 쌓고 복원

윈도우 memory(§6)는 20개가 넘으면 오래된 걸 지웁니다. 그래서 전체 이력 전용 테이블 chat_history 를 JPA로 만들고, 스트리밍 엔드포인트가 질문 도착 시 user, 응답 완료 시 assistant 를 여기에 직접 저장합니다. /api/history 는 이 테이블을 읽어 20개를 넘어도 처음부터 전부 복원합니다.

ChatHistoryEntry.java (JPA @Entity — 이력 한 줄, 삭제 없이 쌓음)

@Entity
@Table(name = "chat_history")
public class ChatHistoryEntry {
@Id @GeneratedValue(strategy = GenerationType.IDENTITY)
private Long id;
@Column(nullable = false) private String conversationId;
@Column(nullable = false) private String role; // "user" / "assistant"
@Column(nullable = false, columnDefinition = "text") private String content;
@Column(nullable = false) private Instant createdAt;
// 기본 생성자 + 인자 생성자 + getter (전체 코드는 master-note 참고)
}

ChatHistoryRepository.java (JpaRepository — save()·CRUD는 공짜)

public interface ChatHistoryRepository extends JpaRepository<ChatHistoryEntry, Long> {
List<ChatHistoryEntry> findByConversationIdOrderByIdAsc(String conversationId);
}

ChatHistoryService.java (저장·조회를 chat_history로)

@Service
public class ChatHistoryService {
private final ChatHistoryRepository repository;
public ChatHistoryService(ChatHistoryRepository repository) { this.repository = repository; }

public List<HistoryMessage> history(String conversationId) {
return repository.findByConversationIdOrderByIdAsc(conversationId).stream()
.map(e -> new HistoryMessage(e.getRole(), e.getContent()))
.toList();
}

// 저장 실패는 로그만 남기고 삼킨다 → 이력 저장이 스트림 완료(done)를 깨지 않게(함정 B 재발 방지)
public void save(String conversationId, String role, String content) {
try { repository.save(new ChatHistoryEntry(conversationId, role, content, Instant.now())); }
catch (Exception ex) { /* log.warn(...) */ }
}
}

ApiController.java — 스트림 엔드포인트가 질문/답변을 저장, history는 조회

// /api/chat/stream 안에서:
chatHistoryService.save(conversationId, "user", question); // 질문 저장
StringBuilder answer = new StringBuilder();
Flux<ServerSentEvent<StreamChunk>> tokens = helpdeskAssistantService
.chatStream(question, conversationId)
.doOnNext(answer::append) // 토큰 모으기
.map(chunk -> ServerSentEvent.builder(new StreamChunk(chunk)).build())
.doOnComplete(() -> chatHistoryService.save(conversationId, "assistant", answer.toString()));

// 조회 엔드포인트:
@GetMapping("/api/history")
public List<HistoryMessage> history(@RequestParam String conversationId) {
return chatHistoryService.history(conversationId);
}

- 확인(실측): 한 대화에 12턴을 보내면 chat_history 엔 24행(user 12 + assistant 12) 전부, 그동안 SPRING_AI_CHAT_MEMORY 는 20행으로 유지됩니다. /api/history?conversationId=... → 24개 [{"role":"user",...},{"role":"assistant",...}](소문자, 줄바꿈 보존).

- tool 메시지는 여기에도 안 남습니다: 우리가 저장하는 건 사용자 질문과 최종 답변 텍스트뿐입니다.

## 8. CORS — 8080과 5173은 다른 출처

- 왜 막히나: 브라우저의 same-origin 정책상 React 개발 서버(localhost:5173)에서 백엔드(localhost:8080)로의 요청은 포트가 달라 다른 출처로 취급돼 기본 차단됩니다.

- 해결: 백엔드가 5173을 명시적으로 허용합니다.

React 5173 ──GET localhost:8080/api/...──▶ 같은 출처?(proto + host + port 일치?)
│
├─ 아니오(5173 ≠ 8080) ──▶ 브라우저 기본 차단(콘솔에 CORS 에러)
│ ┊
│ ┊ CorsConfig가 5173 허용
│ ▼
└──────────────────────────▶ 통과 ✅

src/main/java/com/study/day06streamingreact/CorsConfig.java

@Configuration
public class CorsConfig implements WebMvcConfigurer {
@Override
public void addCorsMappings(CorsRegistry registry) {
registry.addMapping("/api/**")
.allowedOrigins("http://localhost:5173")
.allowedMethods("GET", "POST");
}
}

- 개발용이라 5173만 엽니다. 배포 땐 실제 도메인으로 좁힙니다. CORS가 없으면 React 화면은 뜨지만 콘솔에 CORS 에러가 나고 응답이 비어 보입니다(흔한 함정).

## 9. React로 연결

방식: 셋업을 직접 경험하도록 npm create vite 부터 스캐폴드하고, 스트리밍·history 같은 핵심 로직 코드는 제공받아 붙입니다.

### 9.1 스캐폴드

npm create vite@latest frontend -- --template react # create-vite 9, React 19.2, Vite 8
cd frontend
npm install
npm run dev # http://localhost:5173

- 개발 서버(5173)와 백엔드(8080)는 역할이 다릅니다 — 5173은 React 화면을 서빙하고, 화면 JS가 8080의 API를 호출합니다. 둘 다 떠 있어야 합니다.

- 패키지 매니저는 npm 을 씁니다(취업 현장·미니2 표준).

- API key는 절대 프론트에 두지 않습니다 — 키는 백엔드(8080) 전용이고, 프론트는 백엔드 API만 부릅니다.

### 9.2 제공 핵심 코드 — frontend/src/App.jsx

핵심만 발췌합니다. 앞의 두 함정 해결이 그대로 클라이언트에 반영돼 있습니다.

const API = 'http://localhost:8080'
// conversationId를 localStorage에 고정 → 새로고침해도 같은 대화, history 복원됨
const [conversationId] = useState(() => {
let id = localStorage.getItem('conversationId')
if (!id) { id = 'web-' + Date.now(); localStorage.setItem('conversationId', id) }
return id
})

// 마운트 시: 이전 대화를 DB에서 불러와 화면 복원
useEffect(() => {
fetch(`${API}/api/history?conversationId=${conversationId}`)
.then((r) => r.json()).then(setMessages).catch(() => {})
}, [conversationId])

function send() {
// ... 사용자 메시지 추가, status 'loading'
const url = `${API}/api/chat/stream?question=${encodeURIComponent(q)}&conversationId=${conversationId}`
const es = new EventSource(url) // 브라우저 내장 — 별도 라이브러리 없음
let acc = ''
es.onmessage = (e) => { // 각 청크
setStatus('streaming')
acc += JSON.parse(e.data).text // {"text":"..."} → 공백·줄바꿈 보존 (함정 A)
setStreaming(acc)
}
es.addEventListener('done', () => { // 완료 신호 → 반드시 close (함정 B)
setMessages((m) => [...m, { role: 'assistant', text: acc }])
setStatus('idle'); es.close()
})
es.onerror = () => { es.close(); /* 백엔드 미기동/CORS 안내 */ }
}

- 3상태(idle / loading / streaming)로 사용자에게 진행을 보여줍니다(로딩 점 → 흐르는 텍스트 + 커서).

- conversationId 를 localStorage 에 고정하는 게 새로고침 복원의 핵심입니다 — 같은 id라야 마운트 시 /api/history 가 지난 대화를 돌려줍니다.

### 9.3 end-to-end 확인

- 화면에 문의를 입력 → 답이 토큰별로 흘러나옴(공백·줄바꿈 정상) → 완료. 답변은 C001=김에이스 VIP를 인식하고 환불 규정을 안내합니다(도구 동작).

- 새로고침 → /api/history 가 DB에서 이전 대화를 불러와 화면 복원.

front → back → ai → db → 복원까지 한 바퀴가 돌면 오늘의 목표 달성입니다.

React(5173) ──GET /api/history (마운트)──▶ Spring(8080) ──chat_history 전체 조회──▶ Postgres
React(5173) ◀──[{role,text}...] 화면 복원── Spring(8080) ◀──이전 메시지 전부──────── Postgres
React(5173) ──GET /api/chat/stream(EventSource)──▶ Spring(8080) ──stream()+tools+memory──▶ Gemini
React(5173) ◀──data:{"text":"..."} (토큰별 SSE)── Spring(8080) ◀──토큰...─────────────── Gemini
Spring(8080) ──user·assistant 저장(chat_history)──▶ Postgres
React(5173) ◀──event:done → close()───────── Spring(8080)

## 10. 마무리 — 완주 순서 · README · 미니 프로젝트 2 씨앗

### 완주 순서 (이 순서를 지키세요)

- [1막] 스트리밍 엔드포인트 → ./gradlew bootRun — 이때는 Postgres가 필요 없습니다(아직 DB를 안 붙였으니까) → 브라우저에서 토큰별 도착 확인.

- [2막] docker compose up -d(먼저) → 의존성 + datasource를 함께 추가 → 테이블 자동 생성 확인.

- @Qualifier를 jdbcChatMemory로 스위치 → 재시작 후에도 대화가 남는지 확인(영속).

- /api/history → CORS → React 스캐폴드 → 핵심 코드 붙이기 → end-to-end(새로고침 복원).

- 주의: 순서 역전 금지, 그리고 의존성만 추가하고 datasource 없이 실행하지 말 것(부팅 실패). 필수 완결(스트리밍 + 연동)을 먼저, 다듬기는 그다음.

### README 작성

- 실행 방법(docker compose up -d → 백엔드 → npm run dev), API 목록(/api/chat/stream · /api/history), 스트리밍 화면 캡처, 새로고침 복원 캡처를 정리합니다.

- API Key가 코드·저장소·프론트에 없는지 확인합니다.

### 미니 프로젝트 2로 잇기

오늘 만든 앱(React 채팅 UI + 스트리밍 백엔드 + DB 영속)은 미니2의 출발 템플릿입니다. 확장 방향(주제 후보):

- 협약기업 고객지원 봇: 기업별 FAQ·정책을 시스템 프롬프트/도구로 주입, 문의 유형 자동 분류(Day2 구조화 출력).

- 사내 지식 헬프데스크: 첨부 문서(이미지/PDF) 분석(Day4 멀티모달) + 대화 영속.

- 상담 이력 대시보드: 오늘 만든 chat_history(JPA)를 확장해(고객ID·카테고리 컬럼 추가) 과거 상담을 검색·요약·통계.

"이 예시에서 무엇을 바꾸면 내 주제가 되나"를 각자 한 문장으로 적어 옵니다.

## 자기 점검 체크리스트

- call().content() 와 stream().content() 의 반환 타입을 각각 말할 수 있다(String / Flux<String>), 사용자 체감 차이도 설명할 수 있다.

- 토큰을 날문자열이 아니라 JSON({"text":...})으로 SSE에 싣는 이유(공백·줄바꿈 보존, 함정 A)를 안다.

- EventSource 가 무한 재연결하는 상황과, 서버(done 이벤트에 data 채우기)·클라이언트(close()) 양쪽 해결법(함정 B)을 안다.

- InMemoryChatMemoryRepository → JdbcChatMemoryRepository 로 바꾸면 무엇이 달라지는지, 코드상 스위치(@Qualifier)가 어디인지 안다.

- 8080 백엔드와 5173 프론트 사이에 CORS가 필요한 이유를 안다.

- 새로고침해도 대화가 복원되려면 conversationId 가 고정돼야 함을 안다.

- SPRING_AI_CHAT_MEMORY(윈도우 20개)와 chat_history(전체·JPA)의 차이, /api/history가 후자를 읽는 이유를 안다.

- docker compose up -d → 앱 재시작 후에도 대화가 남는 것을 직접 확인했다.

- front → back → ai → db → 복원 한 바퀴를 브라우저에서 완주했다.

- 미니 프로젝트 2 주제 후보를 한 문장으로 적었다.

## 핵심 용어

|
| 용어 | 정의

| 스트리밍 | 응답을 완성 전에 토큰이 오는 대로 흘려보내는 방식

| Flux<String> | Reactor의 리액티브 스트림 — 여러 String이 시간에 걸쳐 흐름

| stream().content() | ChatClient의 스트리밍 호출 — Flux<String> 반환

| SSE | Server-Sent Events — 서버→클라이언트 단방향 스트림(text/event-stream)

| EventSource | 브라우저 내장 SSE 클라이언트(GET 전용)

| TTFT | time-to-first-token — 첫 글자까지의 시간(체감 지연)

| ServerSentEvent | Spring이 SSE 이벤트를 표현하는 타입(event/data)

| CORS | 다른 출처(포트) 간 요청 허용 정책

| JDBC ChatMemory | 대화를 관계형 DB에 저장하는 ChatMemory 구현

| SPRING_AI_CHAT_MEMORY | JDBC chat memory가 쓰는 테이블(최근 20개 윈도우, 초과분 삭제)

| chat_history | 전체 대화 이력 테이블(append-only). JPA로 관리, /api/history가 읽음

| JPA / @Entity | 자바 객체를 DB 테이블에 매핑(Hibernate). 여기선 chat_history 관리

| conversationId | 대화를 구분·이어가는 키(memory·history의 기준)

| Docker Compose | 컨테이너(여기선 Postgres)를 코드로 정의·기동하는 도구

| Vite | React 개발 서버·번들러(기본 5173)

| 복원 | 마운트 시 history를 불러와 이전 대화를 화면에 되살림