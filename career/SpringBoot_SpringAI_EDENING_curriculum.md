# Spring Boot · Spring AI — EDENING 코드 기반 커리큘럼

**Chris** · EDENING 백엔드(`C:\Users\user\EDENING`) · Dream 병행  
**갱신:** 2026-08-16

---

## 전제 (한 줄)

EDENING 백엔드는 **Spring Boot 4.1 + Java 21**이지만 **`spring-ai` 의존성은 없다.**  
LLM은 `HttpClient` + **Port/Adapter**로 직접 붙인다.

| 단계 | 목표 |
|------|------|
| **A. Spring Boot** | EDENING에서 Controller → Service → JPA → Security → Test 흐름을 **읽고·고치고·테스트** |
| **B. LLM 통합 (EDENING 방식)** | `AiFeedbackGateway`·조건부 설정·캐시·쿼터·서킷브레이커 이해 |
| **C. Spring AI** | EDENING Port를 **`ChatClient` / structured output**으로 **옆에서 비교** (본선 코드는 스펙·측정 경계 유지) |

**주당 8~10h** · **약 16주** (Dream ML · 에덴케어 ship과 병행)

**제품 헌법:** `docs/EDENING_정본.md` §6 — **LLM은 채점·숙련도·복습일정 계산 금지.** AI는 **formative feedback**만.

---

## Phase 0 — 환경 (1일)

```powershell
cd C:\Users\user\EDENING\backend
.\mvnw spring-boot:run          # :8080, dev + H2
cd C:\Users\user\EDENING
python scripts\check.py --fast
```

**읽을 것:** `backend/pom.xml`, `EnglishApplication.java`, `application.yml`의 `app.*` 접두사

**체크:** 스타터 목록(webmvc, data-jpa, security, redis, flyway)을 한 줄씩 설명할 수 있는가?

---

## Phase A — Spring Boot with EDENING (Week 1~8)

### Week 1 — HTTP + 레이어드 CRUD

**앵커:** `skill/SkillController` → `SkillService` → `SkillRepository`

| 학습 | EDENING에서 |
|------|-------------|
| `@RestController`, DI | 생성자 주입만 (필드 `@Autowired` 없음) |
| Validation | `@Valid` + DTO record |
| 페이징 | `PageResponse`, `Pageable` |

**실습**

1. `GET /api/v1/skills` — Postman/curl로 호출
2. `SkillController` 관련 `*ApiTest` / `*Test` 1개 읽기
3. **미니 과제:** `domain` 필터가 Repository까지 내려가는 **호출 그래프** 그리기

**파일**

- `backend/src/main/java/com/seedning/english/skill/SkillController.java`
- `backend/src/main/java/com/seedning/english/skill/SkillService.java`
- `backend/src/main/java/com/seedning/english/skill/SkillRepository.java`

---

### Week 2 — 설정 & 프로파일

**앵커:** `application.yml`, `AiProperties.java` (record + `@ConfigurationProperties`)

| 학습 | EDENING 패턴 |
|------|--------------|
| 외부 설정 | `app.ai.feedback.*`, env placeholder |
| 타입 안전 설정 | nested record, `@DefaultValue` |
| fail-closed | AI 기능 **기본 OFF** |

**실습:** `app.ai.feedback.enabled=false`일 때 어떤 `@Configuration`이 **아예 안 뜨는지** — `AiFeedbackDisabledWiringTest` 실행·읽기

**파일**

- `backend/src/main/resources/application.yml`
- `backend/src/main/java/com/seedning/english/ai/AiProperties.java`
- `backend/src/test/java/com/seedning/english/ai/AiFeedbackDisabledWiringTest.java`

---

### Week 3 — JPA & 트랜잭션

**앵커:** `word/`, `item/`, `catalog/` 중 택1

| 학습 | 확인 |
|------|------|
| Entity, Repository | `JpaRepository` |
| `@Transactional` | Service read-only vs write |
| Flyway | `backend/src/main/resources/db/migration/` |

**실습:** Flyway 마이그레이션 1개 열어 **테이블 ↔ Entity** 대응 적기

---

### Week 4 — 예외 & API 계약

**앵커:** `common/GlobalExceptionHandler`, `openapi/schema.json`

| 학습 | EDENING 규율 |
|------|--------------|
| `@RestControllerAdvice` | HTTP 상태 ↔ 도메인 예외 |
| OpenAPI | 프론트 타입의 정본 |

**실습:** 에러 응답 JSON 형태 1개 캡처 → 스펙과 대조

**파일**

- `backend/src/main/java/com/seedning/english/common/GlobalExceptionHandler.java`
- `openapi/schema.json`

---

### Week 5 — Security 기초

**앵커:** `platform/security/SecurityConfig.java` (앞 ~120줄)

| 학습 | EDENING |
|------|---------|
| `SecurityFilterChain` | deny-by-default |
| 세션 + CSRF | SPA 패턴 |
| Role | STUDENT vs ADMIN |

**실습:** `spring-boot-starter-security-test` 예제 grep → `@WithMockUser` 패턴 이해

**파일**

- `backend/src/main/java/com/seedning/english/platform/security/SecurityConfig.java`

---

### Week 6 — Redis & 캐시

**앵커:** `ai/cache/CaffeineFeedbackCacheStore`, `RedisFeedbackCacheStore`

| 학습 | |
|------|--|
| `@ConditionalOnProperty` | 로컬 Caffeine vs Redis |
| StringRedisTemplate | 피드백 캐시 키 |

**실습:** 캐시 ON/OFF 설정 diff만 읽고 **어떤 빈이 바뀌는지** 목록화

---

### Week 7 — 비동기 & 게이트웨이

**앵커:** `AiFeedbackGateway.java` (cache → quota → breaker → LLM → fallback)

| 학습 | |
|------|--|
| `AsyncTaskExecutor` | `AiFeedbackConfig`의 executor bean |
| afterCommit | DB 커밋 뒤 LLM 호출 |

**실습:** Gateway 흐름을 **5단계 다이어그램**으로 그리기 (코드 수정 X)

**파일**

- `backend/src/main/java/com/seedning/english/ai/gateway/AiFeedbackGateway.java`
- `backend/src/main/java/com/seedning/english/ai/AiFeedbackConfig.java`

---

### Week 8 — 통합 테스트

**앵커:** `AiFeedbackGatewayTest`, `*IT.java`, `@Tag("integration")`

| 학습 | |
|------|--|
| `@SpringBootTest` | 컨텍스트 전체 |
| MockMvc / RestTestClient | HTTP 슬라이스 |
| Testcontainers | PG/Redis (`-Pintegration`) |

**Phase A 산출물:** “Skill CRUD + AI wiring OFF/ON” **아키텍처 노트 2페이지**

---

## Phase B — LLM 통합, EDENING 방식 (Week 9~12)

### Week 9 — Port / Adapter

| EDENING | 역할 |
|---------|------|
| `LlmFeedbackClient` | Port (인터페이스) |
| `OpenAiResponsesFeedbackAdapter` | Adapter (HTTP + JSON) |
| `FormativeFeedbackService` | 도메인 계약 |

**Spring AI 대응:** Port ≈ `ChatClient`를 감싼 **자체 인터페이스**

**실습:** Adapter에서 **request JSON 조립 → POST → response parse** 3함수 이름만 추적

**파일**

- `backend/src/main/java/com/seedning/english/ai/provider/LlmFeedbackClient.java`
- `backend/src/main/java/com/seedning/english/ai/provider/OpenAiResponsesFeedbackAdapter.java`

---

### Week 10 — 조건부 설정 & fail-loud

**앵커:** `AiFeedbackConfig.java`, `ImageGenConfiguration.java` (더 작은 예)

```java
@ConditionalOnProperty(prefix = "app.ai.feedback", name = "enabled", havingValue = "true")
```

**실습:** enabled=true인데 API key 없으면 **기동 실패** — 왜 “조용히 degraded”가 아닌지 한 paragraph

**파일**

- `backend/src/main/java/com/seedning/english/image/ImageGenConfiguration.java`

---

### Week 11 — 회복력 (Resilience)

**앵커:** `CircuitBreaker`, `RequestCoalescer`, `LedgerQuotaGuard`, `TemplateFallbackProvider`

| 패턴 | 목적 |
|------|------|
| Circuit breaker | LLM 장애 시 차단 |
| Coalescing | 동일 요청 중복 호출 방지 |
| Quota + ledger | 비용·일일 한도 |
| Template fallback | LLM 실패 시 **결정론적** 대체 |

**실습:** `CircuitBreakerTest` 읽고 — 어떤 입력이 OPEN 만드는지

**파일**

- `backend/src/test/java/com/seedning/english/ai/gateway/CircuitBreakerTest.java`

---

### Week 12 — 두 번째 LLM 유스케이스

**앵커:** `activity/speaking/conversation/HttpSpeakingProviders.java`  
**스펙:** `docs/specs/SpeakingConversation.md` (LLM이 completion/score 결정 **금지**)

**실습:** Speaking vs Formative feedback — **공통 패턴 3개 / 다른 점 3개** 표

**Phase B 산출물:** “EDENING LLM 경계” 1pager (면접용 EN bullet 가능)

---

## Phase C — Spring AI 브릿지 (Week 13~16)

EDENING **본선을 spring-ai로 갈아엎지 않고**, **별도 학습 모듈**에서 대응 관계를 체득한다.

### Week 13 — Spring AI Hello World (sandbox)

**새 경로 제안:** `backend/src/test/java/.../learning/springai/` 또는 로컬 `~/spring-ai-lab` (EDENING 트리 오염 방지)

```xml
<!-- lab pom only -->
<dependency>
  <groupId>org.springframework.ai</groupId>
  <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
</dependency>
```

| EDENING | Spring AI |
|---------|-----------|
| `OpenAiResponsesFeedbackAdapter` | `ChatClient.prompt().call()` |
| `AiProperties.models.base.id` | `spring.ai.openai.chat.options.model` |
| `FeedbackSchemas` / JSON schema | `BeanOutputConverter` / structured output |

**실습:** 같은 프롬프트를 **Adapter 50줄** vs **ChatClient 10줄**로 각각 호출 → **차이 메모**

---

### Week 14 — Structured output & safety

| EDENING | Spring AI |
|---------|-----------|
| `FeedbackOutputSafetyValidator` | output parser + 자체 validator |
| `OpenAiSafetyIdentifier` | metadata / user id hashing |

**실습:** JSON schema로 “피드백 3필드” 고정 출력

---

### Week 15 — RAG / Embedding (개념)

EDENING 본선에 VectorStore **없음** → **개념 + lab**

| Spring AI | EDENING 연결 |
|-----------|--------------|
| `EmbeddingModel` | catalog 검색 **미래** |
| `VectorStore` | “콘텐츠 검색” — **채점 아님** |

**실습:** `catalog/` 도메인 가정 → “강의 설명 embedding 검색” **설계만**

---

### Week 16 — 통합 비교 & 포지셔닝

**면접/자소 30초 (EN):**

> I shipped a regulated product backend on Spring Boot. LLM integration uses Port/Adapter + gateway so formative feedback stays outside measurement boundaries. Spring AI maps to the same boundary with ChatClient and structured output for faster experiments.

**Phase C 산출물:** `OpenAiResponsesFeedbackAdapter` ↔ `ChatClient` **대응표 1장**

---

## 주간 리듬 (추천)

| 요일 | 1.5h | 내용 |
|------|------|------|
| 월 | 읽기 | 앵커 파일 1개 + 호출 그래프 |
| 화 | 테스트 | 관련 `*Test` 실행·assertion 이해 |
| 수 | 스펙 | `docs/specs/` 해당 절 30분 |
| 목 | 실습 | curl / 작은 수정 / 다이어그램 |
| 금 | 정리 | `qa/` 또는 노트 10줄 |

---

## EDENING 파일 북마크 12

| # | 경로 (EDENING repo) | 이유 |
|---|---------------------|------|
| 1 | `backend/pom.xml` | 스택 정본 |
| 2 | `skill/SkillController.java` | CRUD 교과서 |
| 3 | `application.yml` | `app.*` 플래그 |
| 4 | `ai/AiProperties.java` | ConfigurationProperties record |
| 5 | `image/ImageGenConfiguration.java` | 가장 작은 conditional bean |
| 6 | `ai/provider/LlmFeedbackClient.java` | Port |
| 7 | `ai/provider/OpenAiResponsesFeedbackAdapter.java` | HTTP LLM |
| 8 | `ai/AiFeedbackConfig.java` | 수동 bean 조립 |
| 9 | `ai/gateway/AiFeedbackGateway.java` | 운영급 orchestration |
| 10 | `activity/speaking/conversation/HttpSpeakingProviders.java` | 2nd LLM case |
| 11 | `platform/security/SecurityConfig.java` | Security |
| 12 | `test/.../AiFeedbackDisabledWiringTest.java` | feature flag 검증 |

**보너스:** `FormativeFeedbackService.java` + `ActivityFeedbackController.java` — AI OFF일 때 학습이 깨지지 않는 HTTP 표면

---

## Chris 맞춤 우선순위

- 에덴케어(FastAPI) 경험 → **Week 1~4는 2주 압축** 가능
- Palantir FDSE 전 **Week 5(Security)** + **Week 9~12(AI gateway)** 깊게
- Dream ML(Ch.2-2) 병행: **평일 EDENING 1h + 주말 3h**

---

## Spring AI ↔ EDENING 대응 (요약)

| Spring AI concept | EDENING equivalent |
|---|---|
| `ChatClient` | `LlmFeedbackClient` / `TutorConversationPort` + HTTP adapters |
| `@ConfigurationProperties` for models | `AiProperties`, `SpeakingProviderProperties`, `OpenAiImageProperties` |
| Conditional auto-config | `@ConditionalOnProperty` fail-closed (`app.ai.feedback.enabled`, etc.) |
| Observability/cost | `ai/ledger/*` usage ledger |

---

## 관련 Dream 문서

- [profile_chris.md](./profile_chris.md)
- [FDE_roadmap_2y.md](./FDE_roadmap_2y.md)
- [SQL_data_modeling_track.md](./SQL_data_modeling_track.md)
