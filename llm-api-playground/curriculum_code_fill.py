"""얇은 print-only 칸을 실제 예제로 덮어쓴다."""


def register(put):
    put(
        "core05",
        "hallu",
        """
from openai import OpenAI             # API 창구
client = OpenAI()                     # 키는 환경변수
r = client.chat.completions.create(
    model="gpt-5.4-nano",
    messages=[{"role": "user", "content": "오늘 서울 아침 기온을 숫자로만."}],
)
print(r.choices[0].message.content)   # 문장은 나와도 창밖을 본 값이 아니다
print("환각: 그럴듯함 ≠ 사실")        # 사실이 필요하면 도구/검색을 붙인다
""",
    )
    put(
        "core05",
        "limit",
        """
docs = [                              # 찾아 둔 조각들
    "개장 시간 09:00",
    "주차는 지하 2층",
    "오늘 날씨 맑음",                 # 질문과 무관한 조각
]
q = "몇 시에 열어요?"
picked = [d for d in docs if "시간" in d or "열" in q]  # 관련만 고른다
prompt = "참고:\\n" + "\\n".join(picked) + "\\n질문: " + q
print(prompt)                         # 윈도우에 관련만 넣는 게 RAG 의 시작
print("한도", 1024, "토큰 — 전체를 안 넣는다")
""",
    )
    put(
        "api01",
        "finish",
        """
from openai import OpenAI
client = OpenAI()
r = client.chat.completions.create(
    model="gpt-5.4-nano",
    messages=[{"role": "user", "content": "1부터 200까지 한 줄로."}],
    max_completion_tokens=16,         # 일부러 예산을 작게
)
msg = r.choices[0].message
print("content =", msg.content)       # 짧으면 빈 문자열일 수도
print("finish_reason =", r.choices[0].finish_reason)  # stop 또는 length
print("usage =", r.usage)             # 생각 토큰에 예산을 다 쓰면 length
""",
    )
    put(
        "st02",
        "deploy",
        """
from pathlib import Path
root = Path(".")                      # 프로젝트 폴더
need = ["app.py", "requirements.txt"]
for name in need:
    print(name, "있음" if (root / name).exists() else "없음")
print("1) git add · commit · push")
print("2) share.streamlit.io 에서 Main file: app.py")
print("3) data/ 폴더도 저장소에 같이 올린다")
""",
    )
    put(
        "ml03",
        "ce",
        """
import numpy as np
def ce(p_true, p_pred):
    p_pred = np.clip(p_pred, 1e-9, 1) # 로그 0 방지
    return -np.sum(p_true * np.log(p_pred))
y = np.array([0, 0, 1, 0])            # 정답은 세 번째 클래스
print("자신 있게 맞힘", ce(y, np.array([0.05, 0.05, 0.85, 0.05])))
print("자신 있게 틀림", ce(y, np.array([0.85, 0.05, 0.05, 0.05])))
# MSE 를 시그모이드에 얹으면 언덕이 울퉁불퉁해질 수 있다
""",
    )
    put(
        "ml03",
        "bv",
        """
train = {"simple": 0.62, "memorize": 0.99, "ok": 0.88}
test = {"simple": 0.60, "memorize": 0.71, "ok": 0.86}
for name in train:
    gap = train[name] - test[name]
    if train[name] < 0.7 and test[name] < 0.7:
        tag = "High Bias — 모델이 너무 단순"
    elif gap > 0.15:
        tag = "High Variance — 훈련만 외움"
    else:
        tag = "Good Fit"
    print(name, "train", train[name], "test", test[name], tag)
""",
    )
    put(
        "ml04",
        "gini",
        """
def gini(counts):
    n = sum(counts)                   # 방 안의 개수
    if n == 0:
        return 0.0
    return 1 - sum((c / n) ** 2 for c in counts)  # 1 - Σ p²
print("한 색만", gini([6, 0]))        # 0 — 완전 정돈
print("반반", gini([3, 3]))           # 0.5 — 제일 어지러움
print("5:1", gini([5, 1]))            # 질문이 갈랐는지 이 숫자로 본다
""",
    )
    put(
        "ml05",
        "unsup",
        """
import numpy as np
from sklearn.cluster import KMeans
X = np.array([[0, 0], [0.2, 0.1], [5, 5], [5.1, 4.8]])  # 정답 y 없음
km = KMeans(n_clusters=2, n_init=10, random_state=0).fit(X)
print(km.labels_)                     # 가까운 것끼리 번호만 붙는다
print("지도는 (x,y) / 비지도는 x 만")
""",
    )
    put(
        "dl01",
        "xor",
        """
import numpy as np
pts = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
xor = np.array([0, 1, 1, 0])          # 엇갈린 정답
w, b = np.array([1.0, 1.0]), -0.5     # 어떤 직선을 잡아도
pred = ((pts @ w + b) > 0).astype(int)
print("직선 예측", pred, "정답", xor)
print("맞은 개수", (pred == xor).sum(), "/ 4 — 직선 하나로는 불가")
""",
    )
    put(
        "dl01",
        "act",
        """
import numpy as np
W1 = np.array([[1.0, 2.0], [0.0, 1.0]])
W2 = np.array([[1.0, 0.0], [0.0, 1.0]])
x = np.array([1.0, 1.0])
linear = (x @ W1) @ W2                # 활성 없이 두 층
one = x @ (W1 @ W2)                   # 한 층과 같다
print(linear, one, np.allclose(linear, one))
print("그래서 층 사이에 ReLU 가 있어야 쌓은 이유가 생긴다")
""",
    )
    put(
        "dl02",
        "bp",
        """
# 순전파: x → h → yhat → Loss
# 역전파: dL/dyhat → dL/dW2 → dL/dW1
x, w1, w2, y = 2.0, 0.5, -1.0, 1.0
h = w1 * x
yhat = w2 * h
loss = 0.5 * (yhat - y) ** 2
dL_dyhat = yhat - y
dL_dw2 = dL_dyhat * h                 # 출력층 몫
dL_dw1 = dL_dyhat * w2 * x            # 은닉층 몫 — 연쇄
print("loss", loss, "dW2", dL_dw2, "dW1", dL_dw1)
""",
    )
    put(
        "dl02",
        "vg",
        """
import numpy as np
def sigmoid_grad(z):
    s = 1 / (1 + np.exp(-z))
    return s * (1 - s)                # 최댓값 0.25
g = 1.0
for layer in range(6):
    g *= sigmoid_grad(0.0)            # 제일 큰 기울기만 곱해도
    print(layer + 1, "층 뒤", g)
print("은닉에 시그모이드를 쌓으면 앞층이 안 배운다")
""",
    )
    put(
        "dl02",
        "opt",
        """
w, g = 2.0, 0.8                       # 지금 가중치와 기울기
print("SGD ", w - 0.1 * g)            # 모든 칸에 같은 보폭
m, v = 0.0, 0.0                       # Adam 의 모멘텀·제곱평균
m = 0.9 * m + 0.1 * g
v = 0.999 * v + 0.001 * (g ** 2)
print("Adam", w - 0.1 * m / ((v ** 0.5) + 1e-8))
# model.compile(optimizer="adam", ...)
""",
    )
    put(
        "dl03",
        "curve",
        """
history = {
    "loss":     [0.90, 0.60, 0.40, 0.25, 0.15],
    "val_loss": [0.88, 0.58, 0.42, 0.45, 0.55],
}
for ep, (tr, va) in enumerate(zip(history["loss"], history["val_loss"]), 1):
    mark = " ← val 반전, 여기부터 외움" if ep > 1 and va > history["val_loss"][ep - 2] else ""
    print(f"epoch {ep} train {tr:.2f} val {va:.2f}{mark}")
""",
    )
    put(
        "dl03",
        "inv",
        """
import numpy as np
keep = 0.7                            # Dropout(0.3) → 70% 만 켠다
a = np.array([1.0, 1.0, 1.0, 1.0])
mask = np.array([1, 1, 1, 0])         # 마지막 뉴런을 끔
raw = a * mask                        # 합이 3 으로 줄어든다
inv = raw / keep                      # 학습 때 미리 1/0.7 보정
print("보정 전 평균", raw.mean(), "보정 후", inv.mean())
print("테스트는 마스크 없이 그대로 — inverted")
""",
    )
    put(
        "dl04",
        "flatbad",
        """
import numpy as np
img = np.arange(28 * 28).reshape(28, 28)
print("이웃 픽셀 (0,0)(0,1) 값", img[0, 0], img[0, 1])
flat = img.reshape(-1)
print("펼친 뒤 인덱스", 0, 1, "값은 이웃으로 남음")
print("(0,27)과 (1,0)은 그림에선 이웃, 벡터에선", 27, "과", 28)
print("자리 정보가 사라지니 Conv 가 필요하다")
""",
    )
    put(
        "dl04",
        "share",
        """
dense = 784 * 32 + 32                 # 위치마다 다른 가중치
conv = (3 * 3 * 1 + 1) * 32           # 같은 3x3 을 전 칸에
print("Dense 파라미터", dense)
print("Conv2D 파라미터", conv)
print("비율", round(dense / conv, 1), "배 — 가중치 공유")
""",
    )
    put(
        "dl04",
        "pad",
        """
def out_size(n, k, pad, stride):
    return (n - k + 2 * pad) // stride + 1
print("valid 3x3 stride1", out_size(28, 3, 0, 1))  # 26
print("same  3x3 stride1", out_size(28, 3, 1, 1))  # 28 — 크기 유지
print("same  3x3 stride2", out_size(28, 3, 1, 2))  # 14 — 해상도 절반
""",
    )
    put(
        "dl05",
        "vis",
        """
import numpy as np
# conv.weights[0].numpy() 의 모양은 (3, 3, 1, 32)
w = np.random.randn(3, 3, 1, 32) * 0.1
print("필터 개수", w.shape[-1], "커널", w.shape[:2])
print("한 장 꺼내기", w[:, :, 0, 0].round(2))
print("학습 전후를 imshow 로 나란히 그리는 게 Day 5 시각화")
""",
    )
    put(
        "dl05",
        "tl",
        """
import keras
base = keras.applications.MobileNetV2(
    include_top=False,                # 남이 붙인 1000클래스 머리를 뗀다
    weights="imagenet",
    input_shape=(224, 224, 3),
)
base.trainable = False                # 눈(몸통)은 얼린다
model = keras.Sequential([
    base,
    keras.layers.GlobalAveragePooling2D(),
    keras.layers.Dense(10, activation="softmax"),  # 내 10클래스만 학습
])
print(model.count_params(), "trainable", sum(w.shape.num_elements() for w in model.trainable_weights))
""",
    )
    put(
        "dl05",
        "det",
        """
# from ultralytics import YOLO
# res = YOLO("yolov8n.pt")("photo.jpg")
# for b in res[0].boxes:
#     print(b.xyxy, b.cls, b.conf)
boxes = [                             # 한 장에 상자 개수가 가변
    {"cls": "cat", "xyxy": [10, 20, 80, 90]},
    {"cls": "cup", "xyxy": [100, 40, 140, 88]},
]
print("분류는 라벨 1개, 탐지는", len(boxes), "개")
for b in boxes:
    print(b)
""",
    )
    put(
        "mini1",
        "cover",
        """
main = ["소개 첫 줄"]                # GitHub 의 main
a = main + ["A가 소개를 고침"]
b = main + ["B가 소개를 고침"]        # 같은 줄을 각자 고침
print("A push 후 main =", a)
print("B가 main에 직접 push 하면", b, "← A 작업이 사라진다")
print("그래서 feat 가지 + PR")
""",
    )
    put(
        "mini1",
        "br",
        """
cmds = [
    "git pull origin main",           # 최신 발표본을 받는다
    "git switch -c feat/yh-readme",   # 내 책상을 만든다
    "git add README.md",
    "git commit -m 'docs: 소개 추가'",
]
for c in cmds:
    print(c)
print("main 은 만지지 않는다")
""",
    )
    put(
        "mini1",
        "pr",
        """
flow = [
    "git push origin feat/yh-readme",
    "GitHub → Compare & pull request",
    "리뷰어가 읽고 Approve",
    "Merge → main 에 합쳐짐",
    "git switch main && git pull",    # 내 PC 도 최신으로
]
for i, step in enumerate(flow, 1):
    print(i, step)
""",
    )
    put(
        "mini1",
        "flow",
        """
day = ["pull", "switch -c feat/이름-작업", "add", "commit", "push", "PR", "merge", "pull"]
for i, step in enumerate(day, 1):
    print(f"{i}. git {step}" if step != "PR" else f"{i}. GitHub 에서 PR")
print("팀원 merge 후 마지막 pull 을 빼먹으면 내 컴퓨터가 옛것이다")
""",
    )
    put(
        "mini1",
        "rule",
        """
rules = {
    "main 직접 push": "금지",
    "작업 전": "git pull origin main",
    "가지 이름": "feat/이름-작업 (영문)",
    "같은 줄": "동시에 안 고친다",
}
for k, v in rules.items():
    print(f"{k}: {v}")
""",
    )
    put(
        "sai01",
        "arch",
        """
// 사용자 → Controller → Service → ChatClient → Gemini
@RestController
class ChatController {
    private final ChatClient chat;
    ChatController(ChatClient.Builder b) { this.chat = b.build(); }
    @GetMapping("/api/chat")
    String chat(String message) {
        return chat.prompt().user(message).call().content();
    }
}
""",
    )
    put(
        "sai01",
        "why",
        """
// 프로바이더 JSON 을 직접 안 짠다. yml 만 바꾼다.
// spring.ai.openai.api-key  또는  spring.ai.google.genai.api-key
public String ask(ChatClient chat, String q) {
    return chat.prompt().user(q).call().content(); // 코드는 동일
}
""",
    )
    put(
        "sai01",
        "chat",
        """
String answer = chatClient.prompt()
    .system("초등 선생님처럼 짧게")   // 역할
    .user(message)                   // 질문
    .call()
    .content();                      // 문자열
""",
    )
    put(
        "sai01",
        "tok",
        """
// 토큰 = 과금·한도 단위. 입력 + 출력 둘 다.
// 한글은 자주 여러 조각. RPM/RPD 를 넘기면 거절.
int inputTokens = 37;
int outputTokens = 80;
System.out.println("이번 호출 ≈ " + (inputTokens + outputTokens));
""",
    )
    put(
        "sai01",
        "temp",
        """
String a = chatClient.prompt()
    .user("자기소개 한 줄")
    .options(ChatOptions.builder().temperature(0.1).build()) // 뻔하고 안전
    .call().content();
String b = chatClient.prompt()
    .user("자기소개 한 줄")
    .options(ChatOptions.builder().temperature(1.2).build()) // 다양
    .call().content();
""",
    )
    put(
        "sai02",
        "tpl",
        """
return chatClient.prompt()
    .user(u -> u.text("다음 문의를 {audience}가 읽게 3줄 요약: {text}")
        .param("audience", audience)
        .param("text", text))
    .call()
    .content();
""",
    )
    put(
        "sai02",
        "ask",
        """
String raw = chatClient.prompt()
    .user("JSON으로만 답하세요. 카테고리와 우선순위. 문의: " + text)
    .call()
    .content();
// raw 에 마크다운 ``` 이나 다른 키가 섞일 수 있다
System.out.println(raw);              // 부탁이지 계약이 아니다
""",
    )
    put(
        "sai02",
        "ent",
        """
public record InquiryResult(String category, String priority, String reason) {}
public InquiryResult classify(String text) {
    return chatClient.prompt()
        .user("다음 문의를 분류: " + text)
        .call()
        .entity(InquiryResult.class);  // 코드가 result.priority() 를 읽는다
}
""",
    )
    put(
        "sai02",
        "list",
        """
public record Movie(String title, int year, String reason) {}
public List<Movie> recommend(String mood) {
    return chatClient.prompt()
        .user(mood + "에 어울리는 영화 3편")
        .call()
        .entity(new ParameterizedTypeReference<List<Movie>>() {});
}
""",
    )
    put(
        "sai02",
        "nat",
        """
return chatClient.prompt()
    .user(text)
    .call()
    .entity(InquiryResult.class,
        spec -> spec.useProviderStructuredOutput());
// 생성 단계부터 스키마를 강제. 오늘은 눈으로만.
""",
    )
    put(
        "sai03",
        "adv",
        """
public class MaxCharLengthAdvisor implements CallAdvisor {
    private final int max;
    public ChatClientResponse adviseCall(ChatClientRequest req, CallAdvisorChain chain) {
        ChatClientResponse res = chain.nextCall(req); // 모델 호출
        // 후처리: 너무 긴 답을 자른다
        return res;
    }
    public String getName() { return "max-len"; }
    public int getOrder() { return 10; }
}
""",
    )
    put(
        "sai03",
        "order",
        """
// getOrder() 가 작을수록 전처리는 먼저, 후처리는 나중 (양파)
// 0: Logger  10: MaxLen  20: Memory
this.chatClient = builder
    .defaultAdvisors(logger, maxLen, memoryAdvisor)
    .build();
""",
    )
    put(
        "sai03",
        "mem",
        """
ChatMemory memory = MessageWindowChatMemory.builder()
    .maxMessages(20)
    .build();
ChatClient chat = builder
    .defaultAdvisors(MessageChatMemoryAdvisor.builder(memory).build())
    .build();
// 모델이 기억하는 게 아니다. 앱이 이전 말을 다시 넣는다.
""",
    )
    put(
        "sai03",
        "cid",
        """
return chatClient.prompt()
    .user(question)
    .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, conversationId))
    .call()
    .content();
// conversationId 가 없으면 메모리 Advisor 가 예외를 던진다
""",
    )
    put(
        "sai03",
        "jdbc",
        """
// InMemory: 프로세스 종료면 리셋
// spring.ai.chat.memory.repository.jdbc + H2/Postgres
@Bean
ChatMemory persistent(ChatMemoryRepository repo) {
    return MessageWindowChatMemory.builder()
        .chatMemoryRepository(repo)
        .maxMessages(20)
        .build();
}
""",
    )
    put(
        "sai04",
        "mp",
        """
@PostMapping(value = "/api/image-analysis", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
public ReceiptInfo analyze(@RequestPart("file") MultipartFile file) {
    // JSON 이 아니라 boundary 로 나뉜 파일 + 필드
    return service.analyze(file);
}
""",
    )
    put(
        "sai04",
        "media",
        """
Media media = new Media(MimeTypeUtils.IMAGE_PNG, toResource(file));
return chatClient.prompt()
    .user(u -> u.text("이 사진에 뭐가 보이나요?").media(media))
    .call()
    .content();
""",
    )
    put(
        "sai04",
        "three",
        """
Media img = new Media(MimeTypeUtils.IMAGE_PNG, imgRes);
Media pdf = new Media(MediaType.APPLICATION_PDF, pdfRes);
Media wav = new Media(MimeType.valueOf("audio/wav"), wavRes);
// toResource → media → entity(record). MIME 만 다르다
""",
    )
    put(
        "sai04",
        "ec",
        """
ReceiptInfo boxed = chatClient.prompt()
    .user(u -> u.text("영수증을 읽어").media(media))
    .call()
    .entity(ReceiptInfo.class);       // DB/분기용 칸
String free = chatClient.prompt()
    .user(u -> u.text("영수증을 읽어").media(media))
    .call()
    .content();                       // 사람이 읽는 글
""",
    )
    put(
        "sai04",
        "replay",
        """
// 같은 conversationId 로 다음 질문을 하면
// 이전 이미지·PDF 바이트가 다시 실릴 수 있다
String follow = chatClient.prompt()
    .user("방금 그 사업자번호가 뭐야?")
    .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, id))
    .call()
    .content();
""",
    )
    put(
        "sai05",
        "req",
        """
@Component
public class DateTimeTools {
    @Tool(description = "현재 날짜와 시간을 사용자의 시간대 기준으로 반환한다")
    public String now() {
        return LocalDateTime.now().toString(); // 실행은 이 메서드
    }
}
// chatClient.prompt().user(q).tools(dateTimeTools).call().content();
""",
    )
    put(
        "sai05",
        "desc",
        """
@Tool(description = "고객 등급을 조회한다. 고객 아이디가 있을 때만 쓴다")
public CustomerGrade grade(@ToolParam(description = "고객 아이디") String id) {
    return repo.find(id);             // 모델은 이 자바를 안 본다
}
// 고르는 기준은 description 뿐이다
""",
    )
    put(
        "sai05",
        "mcp",
        """
chatClient.prompt()
    .user("README 를 읽어서 요약해")
    .tools((Object[]) catalog.filesystemTools()) // 남이 띄운 파일 도구
    .call()
    .content();
""",
    )
    put(
        "sai05",
        "boot",
        """
// MCP Client 는 부팅 때 서버에 연결한다
// npx/uvx 가 없으면 컨텍스트 로딩 실패 → /api/chat 까지 같이 죽음
// 대응: 서버를 선택 의존으로, 실패해도 앱은 뜨게
""",
    )
    put(
        "sai05",
        "exp",
        """
@Component
public class HelpdeskMcp {
    @McpTool(description = "사내 FAQ 한 줄을 반환한다")
    public String faq(String topic) { // @Tool 과 별개 — 노출용
        return rules.getOrDefault(topic, "없음");
    }
}
""",
    )
    put(
        "sai06",
        "flux",
        """
String boxed = chatClient.prompt().user(q).call().content();
Flux<String> stream = chatClient.prompt().user(q).stream().content();
stream.subscribe(token -> System.out.print(token)); // 생기는 대로
""",
    )
    put(
        "sai06",
        "sse",
        """
@GetMapping(value = "/api/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<ServerSentEvent<String>> stream(String q, String id) {
    return helpdesk.chatStream(q, id)
        .map(t -> ServerSentEvent.builder(t).build())
        .doOnComplete(() -> {});      // 완료 후 EventSource 재연결을 끈다
}
""",
    )
    put(
        "sai06",
        "two",
        """
// SPRING_AI_CHAT_MEMORY : LLM 최근 20개 (윈도우)
// chat_history          : 화면 복원용 전체 (JPA)
@GetMapping("/api/history")
List<HistoryMessage> history(String conversationId) {
    return repo.findByConversationIdOrderByCreatedAt(conversationId);
}
""",
    )
    put(
        "sai06",
        "cors",
        """
@Configuration
class CorsConfig implements WebMvcConfigurer {
    public void addCorsMappings(CorsRegistry r) {
        r.addMapping("/api/**")
            .allowedOrigins("http://localhost:5173"); // React
    }
}
// 5173 화면 / 8080 API / 5432 DB
""",
    )
    put(
        "sai06",
        "dock",
        """
# compose.yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: helpdesk
    ports:
      - "5432:5432"
""",
    )
    put(
        "mini2",
        "strat",
        """
layers = {
    "main": "발표본 — 마일스톤 때만",
    "dev": "통합. PR 의 base",
    "feat/이니셜-작업": "할 일 하나",
}
for name, why in layers.items():
    print(f"{name:20} {why}")
print("작업은 dev 에서 따서 dev 로 PR")
""",
    )
    put(
        "mini2",
        "sync",
        """
cmds = [
    "git fetch origin",
    "git merge origin/dev",           # PR 전에 충돌을 내 자리에서
]
for c in cmds:
    print(c)
print("오래 안 당기면 충돌이 커진다")
""",
    )
    put(
        "mini2",
        "conf",
        """
marker = '''
<<<<<<< HEAD
@GetMapping("/api/products")   # 내 것
=======
@GetMapping("/api/items")      # 팀원 것
>>>>>>> feat/other
'''
print(marker)
print("둘을 살릴지 한쪽만 살릴지 사람이 정한다")
print("git merge --abort 면 시작 전으로")
""",
    )
    put(
        "mini2",
        "rev",
        """
steps = [
    "PR → Files changed",
    "줄 번호 옆 + 에 댓글",
    "Approve 또는 Request changes",
    "고치면 다시 push — 같은 PR 에 쌓인다",
]
for i, s in enumerate(steps, 1):
    print(i, s)
""",
    )
    put(
        "mini2",
        "issue",
        """
print("Issue #12 로그인 API")
print("브랜치 12-login-api")
print("PR 본문: Fixes #12  → merge 되면 이슈가 닫힌다")
print("보드: Todo / In Progress / Done")
ignore = [".env", "*.pem", "node_modules/", "build/"]
print("커밋 금지", ignore)
""",
    )
    put(
        "ptn01",
        "loop",
        """
import torch
import torch.nn as nn
model = nn.Linear(4, 3)
opt = torch.optim.Adam(model.parameters(), lr=0.01)
xb, yb = torch.randn(8, 4), torch.randint(0, 3, (8,))
crit = nn.CrossEntropyLoss()
opt.zero_grad()                       # 1 이전 기울기 삭제
pred = model(xb)                      # 2 순전파
loss = crit(pred, yb)                 # 3 손실
loss.backward()                       # 4 기울기
opt.step()                            # 5 한 걸음
print(float(loss))
""",
    )
    put(
        "ptn02",
        "tok",
        """
en = "I don't like cats."
print("split ", en.split())           # don't 가 한 덩어리
ko = "학교에서는 파이썬을 배웁니다"
print("ko split", ko.split())         # '학교에서는' 이 안 갈라진다
print("형태소 예", ["학교", "에서", "는", "파이썬", "을", "배우", "ㅂ니다"])
""",
    )
    put(
        "ptn02",
        "sub",
        """
vocab = {"텐서": 10, "플로우": 11}
word = "텐서플로우"
if word in vocab:
    ids = [vocab[word]]
else:
    ids = [vocab.get("텐서", 1), vocab.get("플로우", 1)]  # 있는 조각
print(word, "→", ids)
print("없는 단어를 통째 <unk> 로 안 버린다. 토큰 수 = 돈")
""",
    )
    put(
        "ptn03",
        "order",
        """
import torch
emb = {
    "개가": torch.tensor([1.0, 0.0]),
    "사람을": torch.tensor([0.0, 1.0]),
    "물었다": torch.tensor([1.0, 1.0]),
}
bag = lambda ws: sum((emb[w] for w in ws), torch.zeros(2))
a = bag(["개가", "사람을", "물었다"])
b = bag(["사람을", "개가", "물었다"])
print(a, b, torch.allclose(a, b))     # True — 순서가 사라짐
print("그래서 은닉 상태가 있는 RNN 이 필요하다")
""",
    )
    put(
        "ptn03",
        "lpad",
        """
import torch
from torch.nn.utils.rnn import pad_sequence
s = torch.tensor([11, 22, 33])        # 실제 내용
right = torch.nn.functional.pad(s, (0, 2))   # [11,22,33,0,0] 뒤쪽 패딩
left = torch.nn.functional.pad(s, (2, 0))    # [0,0,11,22,33] 앞쪽 패딩
print("뒤쪽", right, "← 마지막이 0 이면 RNN 이 빈칸을 읽고 끝")
print("앞쪽", left, "← 마지막이 내용. 분류는 이 쪽")
""",
    )
    put(
        "ptn03",
        "van",
        """
beta = 0.9                            # W_h 한 번 곱할 때 남는 비율
for t in (1, 5, 10, 30, 100):
    print(f"거리 {t:3d} → 신호 {beta ** t:.6f}")
print("앞 단어 기울기가 0 으로 간다. 내일은 더하는 길 + 게이트")
""",
    )
    put(
        "ptn04",
        "mul",
        """
print("0.9 ** 30 =", 0.9 ** 30)       # 사라진다
print("0.99 ** 30 =", 0.99 ** 30)
c, f, i, g = 2.0, 0.95, 0.3, 1.0      # 셀, forget, input, 후보
c = f * c + i * g                     # 더해서 흐른다
print("한 스텝 뒤 셀", c)
""",
    )
    put(
        "ptn04",
        "cell",
        """
def lstm_step(c_prev, x_t, f, i, g):
    c_t = f * c_prev + i * g          # 덧셈 고속도로
    return c_t
c = 1.0
for t in range(5):
    c = lstm_step(c, x_t=1, f=0.95, i=0.1, g=0.5)
    print("t", t + 1, "c", round(c, 4))
print("곱만 하던 RNN 과 달리 앞 기억이 남는다")
""",
    )
    put(
        "ptn04",
        "seed",
        """
acc = {
    "RNN":  [0.669, 0.633, 0.633],
    "LSTM": [0.753, 0.753, 0.735],
}
for name, xs in acc.items():
    mean = sum(xs) / len(xs)
    noise = max(xs) - min(xs)
    print(name, "평균", round(mean, 3), "흔들림", round(noise, 3))
gap = abs(sum(acc["LSTM"]) - sum(acc["RNN"])) / 3
print("차이", round(gap, 3), ">", "흔들림*2 여야 '낫다'고 말한다")
""",
    )
