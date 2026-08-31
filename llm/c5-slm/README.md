# c5-slm

Transformer의 기본 계산부터 LLM 추론, vLLM 서빙, OpenAI 호환 API, GPU 운영, EDENING 적용까지 연결해서 실습하는 저장소입니다.

## 학습 문서

첨부된 학습 대화는 내용을 줄이거나 요약하지 않고, 이해 순서에 맞춰 하나의 흐름으로 재구성했습니다.

- [LLM · Transformer · vLLM · EDENING 연결 학습 노트](docs/vllm-study.md)
- [첨부 원문 보존본](docs/vllm-study-source.txt)

문서의 연결 순서는 다음과 같습니다.

```text
Attention
  → Self-Attention
    → Transformer
      → GPT/LLM의 다음 토큰 생성
        → Prefill·Decode와 KV Cache
          → PagedAttention·Continuous Batching·Prefix Caching
            → vLLM 추론·서빙 엔진
              → OpenAI 호환 API
                → GPU 구매·임대와 EDENING 운영
                  → Stripe 사례와 실무 판단
```

## 노트북

- `day1/local.ipynb`: 로컬 Transformer 모델 추론
- `day1/precision_and_config.ipynb`: 정밀도와 모델 설정
- `day2/`: 모델 실행 및 추론 관련 실습
- `day3/request.ipynb`: Ollama OpenAI 호환 API 요청과 동시 요청
- `day3/vllm.ipynb`: vLLM OpenAI 호환 API 연결 및 동시 요청

## Ubuntu·WSL2 실행

Ubuntu 터미널에서 저장소로 이동합니다.

```bash
cd "/mnt/c/Users/금정산2-PC02/Desktop/Dream/llm/c5-slm"
source .venv/bin/activate
code .
```

VS Code에서는 커널을 `c5-slm (3.12.x)` 또는 `Python (c5-slm Ubuntu)`로 선택하고, 노트북 셀을 위에서부터 순서대로 실행합니다.

## vLLM 서버 실행

vLLM 설치는 서버 실행과 별개의 단계입니다. 설치 명령 뒤에 채팅 앱의 시간표시가 붙지 않도록 하고, `--torch-backend auto`의 `auto` 뒤에는 다른 문자가 없어야 합니다.

```bash
source /mnt/c/Users/금정산2-PC02/Desktop/Dream/llm/c5-slm/.venv/bin/activate
export VLLM_WSL2_ENABLE_PIN_MEMORY=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

uv pip install vllm --torch-backend auto
vllm serve Qwen/Qwen3-0.6B \
  --dtype half \
  --max-model-len 1024 \
  --gpu-memory-utilization 0.35 \
  --enforce-eager \
  --host 0.0.0.0 \
  --port 8000
```

서버가 준비되면 `day3/vllm.ipynb`의 연결 주소는 다음과 같습니다.

```python
VLLM_BASE = "http://localhost:8000/v1"
```

`ollama stop`은 모델 이름이 필요한 명령입니다. 실행 중인 모델을 확인하려면 다음을 사용합니다.

```bash
ollama ps
ollama stop <실행_중인_모델_이름>
```

실행 중인 모델이 없으면 `ollama stop`을 실행할 필요가 없습니다.

## 디렉터리

```text
c5-slm/
├─ day1/
├─ day2/
├─ day3/
│  ├─ request.ipynb
│  ├─ request.executed.ipynb
│  ├─ vllm.ipynb
│  └─ vllm.executed.ipynb
├─ docs/
│  ├─ vllm-study.md
│  └─ vllm-study-source.txt
└─ README.md
```
