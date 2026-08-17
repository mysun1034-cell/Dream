# Spring AI Day4 학습자 가이드

> 2026-07-08 · Spring AI를 적용한 협약기업 서비스 구현
> 원본: learner-guide.html · ES LMS

---

Spring AI Day4 학습자 가이드

# 학습자 가이드 - Spring AI
Day4

주제: Multimodal — 이미지·PDF·오디오 입력

## 오늘 만드는 것

오늘도 처음부터 만들지 않습니다.
day04-multimodal-starter 프로젝트를
받으면, 그 안에 Day3에서 만든 기능이 이미 전부 들어있습니다. 그
위에 이미지·PDF·오디오 분석 엔드포인트를 얹습니다.

|

| API
| 하는 일

| /api/ask, /api/call-count,
/api/chat-memory
| Day3에서 만든 것 (starter에 이미 있음)

| /api/image-analysis
| 이미지(영수증 등)에서 정보를 구조화해서 추출 (오늘 추가)

| /api/pdf-analysis
| PDF 문서를 요약하고 핵심 항목을 추출 (오늘 추가)

| /api/audio-analysis
| 오디오 공지에서 일정·준비물을 구조화해서 추출 (오늘 추가)

오늘의 한 문장: UserMessage에 text
말고 media 필드 하나를 더 채우면, 어제 만든
ChatClient·Advisor·Chat Memory 구조를 그대로 재사용하면서 파일도 보낼 수
있다. 그리고 그 파일이 이미지든 PDF든 오디오든, 패턴은
똑같다.

## 0. 보일러플레이트 확인

day04-multimodal-starter를 받으면 Day3에서 만든 파일이
그대로 들어있습니다.

src/main/java/com/example/day04multimodal/
├── Day04MultimodalApplication.java
├── AssistantService.java (Day3에서 만든 것 — Advisor 4개 이미 적용됨)
├── ChatMemoryConfig.java (Day3에서 만든 것)
├── MemoryChatService.java (Day3에서 만든 것)
├── PersistentChatService.java (Day3에서 만든 것)
├── ApiController.java (Day3의 5개 엔드포인트 매핑됨)
└── advisor/
├── CallCounterAdvisor.java
└── MaxCharLengthAdvisor.java

GOOGLE_API_KEY 환경변수를 설정하고 실행해서,
/api/ask?question=안녕이 어제처럼 동작하는지 먼저
확인하세요. samples/ 폴더에 오늘 쓸 샘플
파일(sample-receipt.png,
sample-study-notice.pdf)이 이미 들어있습니다.

## 1. Bruno로 멀티파트 요청
구조 확인하기

파일 업로드는 지금까지 쓰던 쿼리 파라미터·JSON과 다르게
Content-Type: multipart/form-data; boundary=... 형식으로
인코딩됩니다. Bruno에서 파일 업로드 요청을 만들고 raw view(또는
curl -v)를 보면, 텍스트 필드와 파일 바이너리가 boundary로
구분되어 나란히 담긴 것을 확인할 수 있습니다.

------abc123
Content-Disposition: form-data; name="conversationId"

test-1
------abc123
Content-Disposition: form-data; name="file"; filename="receipt.png"
Content-Type: image/png

(PNG 바이너리 데이터...)
------abc123--

Spring MVC는 이 요청을 파싱해서 파일 부분을
MultipartFile로 넘겨줍니다.

## 2.
Media/MimeType/Resource
이해하기

- MimeType: 데이터 형식
(image/png, application/pdf 등)

- Resource: 실제 데이터를 담는 스프링
표준 추상화 (ByteArrayResource,
ClassPathResource 등)

- Media: 위 둘을 묶은 것 —
new Media(mimeType, resource)

ChatClient 플루언트 API에서는 .user() 람다
안에서 이렇게 씁니다.

chatClient.prompt()
.user(u -> u.text("이 사진을 설명해주세요")
.media(mimeType, resource))
.call()
.content();

업로드된 MultipartFile은 바이트를 그대로
ByteArrayResource에 담아 변환합니다.

private ByteArrayResource toResource(MultipartFile file) {
try {
return new ByteArrayResource(file.getBytes());
}
catch (IOException e) {
throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "파일을 읽는 중 오류가 발생했습니다.", e);
}
}

이 변환 코드는 이미지든 PDF든 완전히 동일합니다.

## 3. 이미지 분석 엔드포인트
만들기

오늘은 JPEG/PNG만 허용합니다(HEIC 등은 거부). 그리고 Day2에서 배운
.entity()로 자유 텍스트가 아니라 구조화된 record로 결과를
받습니다.

ReceiptInfo.java (새 파일)

public record ReceiptInfo(String vendor, String totalAmount, String date, List<String> items) {
}

DocumentAnalysisService.java (새
파일)

@Service
public class DocumentAnalysisService {

private static final Set<String> ALLOWED_IMAGE_TYPES = Set.of(
MimeTypeUtils.IMAGE_JPEG_VALUE, MimeTypeUtils.IMAGE_PNG_VALUE);

private static final String PDF_CONTENT_TYPE = "application/pdf";

private final ChatClient chatClient;

public DocumentAnalysisService(@Qualifier("inMemoryChatMemory") ChatMemory chatMemory,
ChatClient.Builder chatClientBuilder,
CallCounterAdvisor callCounterAdvisor) {
this.chatClient = chatClientBuilder
.defaultAdvisors(
callCounterAdvisor,
MessageChatMemoryAdvisor.builder(chatMemory).build(),
new SimpleLoggerAdvisor(Ordered.LOWEST_PRECEDENCE))
.build();
}

public ReceiptInfo analyzeImage(MultipartFile file, String conversationId) {
validateImage(file);
ByteArrayResource resource = toResource(file);
MimeType mimeType = MimeType.valueOf(file.getContentType());

return chatClient.prompt()
.user(u -> u.text("이 영수증 이미지에서 상호명(vendor), 총 금액(totalAmount), 날짜(date), 구매 항목 목록(items)을 추출해 주세요.")
.media(mimeType, resource))
.advisors(spec -> spec.param(ChatMemory.CONVERSATION_ID, conversationId))
.call()
.entity(ReceiptInfo.class);
}

private void validateImage(MultipartFile file) {
if (file == null || file.isEmpty()) {
throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "이미지 파일이 필요합니다.");
}
String contentType = file.getContentType();
if (contentType == null || !ALLOWED_IMAGE_TYPES.contains(contentType)) {
throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
"JPEG 또는 PNG 이미지만 지원합니다. (받은 타입: " + contentType + ")");
}
}

// toResource(), analyzePdf(), validatePdf()는 아래에서 이어서 작성합니다.
}

ApiController.java에 추가

@PostMapping("/api/image-analysis")
public ReceiptInfo imageAnalysis(@RequestParam("file") MultipartFile file,
@RequestParam String conversationId) {
return documentAnalysisService.analyzeImage(file, conversationId);
}

samples/sample-receipt.png를 Bruno로 업로드해서
확인해보세요. 이렇게 나오면 성공입니다.

{
"vendor": "스프링 카페",
"totalAmount": "19,000원",
"date": "2026-07-06",
"items": ["아메리카노 x2", "카페라떼 x1", "치즈케이크 x1"]
}

## 4. PDF 분석
엔드포인트 만들기 — 이미지 코드 재사용

Google GenAI는 application/pdf 미디어 타입을 공식
지원합니다. 이미지와 완전히 같은 Media 패턴이고,
MimeType만 다릅니다.

PdfSummary.java (새 파일)

public record PdfSummary(String summary, List<String> keyPoints) {
}

DocumentAnalysisService.java에 이어서
작성

public PdfSummary analyzePdf(MultipartFile file, String conversationId) {
validatePdf(file);
ByteArrayResource resource = toResource(file);
MimeType mimeType = new MimeType("application", "pdf");

return chatClient.prompt()
.user(u -> u.text("이 PDF 문서를 한 문단으로 요약(summary)하고, 핵심 항목을 목록(keyPoints)으로 정리해 주세요.")
.media(mimeType, resource))
.advisors(spec -> spec.param(ChatMemory.CONVERSATION_ID, conversationId))
.call()
.entity(PdfSummary.class);
}

private void validatePdf(MultipartFile file) {
if (file == null || file.isEmpty()) {
throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "PDF 파일이 필요합니다.");
}
String contentType = file.getContentType();
if (!PDF_CONTENT_TYPE.equals(contentType)) {
throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
"PDF 파일(application/pdf)만 지원합니다. (받은 타입: " + contentType + ")");
}
}

ApiController.java에 추가

@PostMapping("/api/pdf-analysis")
public PdfSummary pdfAnalysis(@RequestParam("file") MultipartFile file,
@RequestParam String conversationId) {
return documentAnalysisService.analyzePdf(file, conversationId);
}

samples/sample-study-notice.pdf로 확인해보세요.

## 5.
오디오 분석 엔드포인트 만들기 — 같은 패턴, 세 번째 모달리티

오디오도 이미지·PDF와 완전히 같은 Media 패턴입니다.
MimeType만 audio/wav(또는
audio/mpeg)로 다릅니다.

AudioSummary.java (새 파일)

public record AudioSummary(String schedule, List<String> preparations) {
}

이 record에는 장소(위치) 필드가 일부러 없습니다 —
이유는 §9에서 확인합니다.

DocumentAnalysisService.java에 이어서
작성

public AudioSummary analyzeAudio(MultipartFile file, String conversationId) {
validateAudio(file);
ByteArrayResource resource = toResource(file);
MimeType mimeType = MimeType.valueOf(file.getContentType());

return chatClient.prompt()
.user(u -> u.text("""
이 오디오 공지에서 모임 요일과 시간(schedule)과 준비물 목록(preparations)만 정리해 주세요.
장소(카페 이름 등 위치 정보)는 절대 포함하지 마세요.
""")
.media(mimeType, resource))
.advisors(spec -> spec.param(ChatMemory.CONVERSATION_ID, conversationId))
.call()
.entity(AudioSummary.class);
}

private void validateAudio(MultipartFile file) {
if (file == null || file.isEmpty()) {
throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "오디오 파일이 필요합니다.");
}
String contentType = file.getContentType();
if (contentType == null || !ALLOWED_AUDIO_TYPES.contains(contentType)) {
throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
"WAV 또는 MP3 오디오만 지원합니다. (받은 타입: " + contentType + ")");
}
}

ApiController.java에 추가

@PostMapping("/api/audio-analysis")
public AudioSummary audioAnalysis(@RequestParam("file") MultipartFile file,
@RequestParam String conversationId) {
return documentAnalysisService.analyzeAudio(file, conversationId);
}

samples/sample-study-notice-audio.wav로 확인해보세요.
실제 응답:

{"schedule":"목요일 저녁 7시","preparations":["노트북"]}

원본 오디오에는 “카페 소나무에서 진행됩니다”라는 장소가 분명히
나오는데, 응답에는 장소가 없습니다. 프롬프트에서 “장소는 절대 포함하지
마세요”라고 명시했기 때문입니다 — 이 “의도된 누락”이 §9의 실험에서
쓰입니다.

## 6. 세 코드를 나란히 비교하기

toResource()는 이미지·PDF·오디오 세 곳 모두에서
완전히 동일하게 재사용됩니다. 다른 건
MimeType 생성 방식과 .entity()로 받는
타입뿐입니다.

|

| 구분
| 이미지
| PDF
| 오디오

| toResource(file)
| 동일
| 동일
| 동일

| MimeType
| MimeType.valueOf(file.getContentType())
| new MimeType("application", "pdf")
| MimeType.valueOf(file.getContentType())

| .entity() 타입
| ReceiptInfo
| PdfSummary
| AudioSummary

## 7. 방어 코드 확인

파일 크기 제한을 미리 설정합니다
(application.yml, starter에 이미 반영되어
있음)

spring:
servlet:
multipart:
max-file-size: 10MB
max-request-size: 10MB
web:
error:
include-message: always

- 파일 없이 호출 → 400

- JPEG/PNG(또는 PDF, WAV/MP3)가 아닌 파일로 호출 → 400 (친절한 메시지
포함)

- 10MB 넘는 파일로 호출 → 413 (이때는 본문이 비어있는 게 정상입니다 —
톰캣이 Spring 컨트롤러에 요청이 도달하기 전에 커넥션을 끊기 때문)

## 8. 누적 통합 —
Day3 Advisor·Chat Memory 재적용 확인

DocumentAnalysisService 생성자에 이미
CallCounterAdvisor와 MessageChatMemoryAdvisor,
SimpleLoggerAdvisor를 등록했습니다. /api/ask와
/api/image-analysis를 번갈아 호출한 뒤
/api/call-count를 조회해보세요 — 카운트가 하나로
이어집니다. 같은 @Component 빈을 여러 서비스가 공유하기
때문입니다.

## 9.
(CHALLENGE, 선택) Chat Memory가 실제로 기억하는 것 확인하기

같은 conversationId로 이미지 분석 → PDF 분석 → 오디오
분석을 각각 호출한 뒤, /api/chat-memory에 “방금 그 세 가지
내용을 종합해서 정리해줘”라고 물어보세요. 세 결과가 자연스럽게
종합됩니다.

이제 흥미로운 실험을 해봅니다 — 구조화 출력에 저장하지 않은 정보를
물어보세요.

질문: 방금 그 영수증에 적힌 사업자번호가 뭐야?
응답: 영수증에 적힌 사업자번호는 **123-45-67890**입니다.

질문: 방금 그 모임 장소가 어디야?
응답: 제공해주신 오디오 공지에 따르면 모임 장소는 '카페 소나무'입니다.

ReceiptInfo record에는
vendor·totalAmount·date·items만
있고 사업자번호는 없습니다. AudioSummary record에도
schedule·preparations만 있고 장소는 없습니다.
그런데도 둘 다 정확히 맞췄다는 건, Chat Memory가 분석 결과 텍스트만
저장한 게 아니라 원본 미디어(이미지·오디오) 자체를 그대로
저장하고, 후속 호출마다 다시 전송하고 있다는 뜻입니다 —
이미지뿐 아니라 오디오에서도 똑같이 재현됩니다. 대화가 길어질수록
멀티모달 호출 비용도 함께 커진다는 걸 기억하세요 — 모달리티가
이미지·PDF·오디오 세 가지로 늘어난 만큼 이 실험은 재시도를 2~3회 이내로
하는 게 좋습니다(샘플 파일도 작게 유지하세요).

## 10. README와 제출

- 실행 방법, API 목록(어제 3개 + 오늘 3개), 이미지·PDF·오디오 응답
캡처, 판별 실험 결과(선택)를 README에 정리

- API Key가 코드/저장소에 없는지, data/ 폴더가
.gitignore에 있는지 확인

- Git commit, GitHub push, LMS에 저장소 URL 제출

## 자주 만나는 오류

|

| 증상
| 원인
| 해결

| 파일을 올려도 텍스트만 응답
| .media()를 빼먹음
| .user(u -> u.text(...).media(mimeType, resource))
확인

| 400 (JPEG/PNG만 지원)
| HEIC 등 화이트리스트 밖 MIME
| JPEG/PNG로 변환해서 재업로드 (의도된 동작)

| 400 (WAV/MP3만 지원)
| 화이트리스트 밖 오디오 포맷
| WAV 또는 MP3로 변환해서 재업로드 (의도된 동작)

| 413, 응답 본문 비어있음
| 10MB 초과
| 정상 동작 — 상태 코드만 확인하면 됨

| 커스텀 메시지가 응답에 안 보임
| server.error.include-message(구버전 이름) 사용
| spring.web.error.include-message(Boot 4 이름)로
수정

| PDF 엔드포인트에서 이상한 응답
| 실제로 이미지 파일을 올림
| Content-Type이 application/pdf인지
확인

| AudioSummary에 요약문이 없어 이상함
| 장소를 구조화 출력에서 의도적으로 제외했기 때문
| 의도된 것 — §9의 판별 실험을 위한 설계