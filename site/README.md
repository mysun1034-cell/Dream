# 한정욱 사이트

이력서(공개)와 학습 보드(본인만 로그인)를 담은 Next.js 사이트입니다.
화면은 Vercel, 로그인과 데이터는 Supabase가 맡습니다.

| 주소 | 내용 | 공개 범위 |
|------|------|-----------|
| `/` | 소개와 이력서 바로가기 | 누구나 |
| `/resume/ko` · `/resume/en` | 한국어 · 영문 이력서 (전화번호 없음) | 누구나 |
| `/board` | 학습 보드 | 로그인한 본인만 |

## 로컬에서 실행

```bash
npm install
npm run dev
```

http://localhost:3100 에서 열립니다. Supabase를 연결하기 전에도 홈과 이력서는 보이고, 보드는 "아직 연결 전입니다"로 나옵니다.

## 이력서 고치기

이력서 원본은 레포의 `career/resume/`에 있습니다. `npm run dev`와 `npm run build`가 시작할 때 원본을 `public/resume/`로 복사하므로, 원본만 고치면 됩니다. `public/resume/`를 직접 고치면 다음 실행 때 덮어써집니다.

## 연결 순서

### 1. Supabase — 로그인과 데이터

1. supabase.com에서 새 프로젝트를 만든다.
2. SQL Editor에서 `supabase/schema.sql` 전체를 실행한다.
3. Authentication 설정에서 새 사용자 가입 허용(Allow new users to sign up)을 끈다. 지금은 본인만 쓰기 때문이다.
4. Authentication → Users → Add user에서 본인 이메일과 비밀번호로 계정을 만든다(Auto Confirm 체크).
5. SQL Editor에서 `supabase/seed.local.sql`을 실행해 claude.ai 학습 보드의 계획과 체크 상태를 옮긴다. 이 파일은 개인 데이터라 레포에 없다. 옮기기 직전에 보드를 JSON 폴더로 내보내고 `node scripts/board-to-seed.mjs <내보내기 폴더> <로그인 이메일>`로 새로 만든다.
6. Project Settings의 API 메뉴에서 프로젝트 URL과 publishable 키를 확인한다.

### 2. 로컬에서 로그인 확인

`.env.example`을 `.env.local`로 복사해 두 값을 넣고 `npm run dev`를 다시 시작한 뒤 http://localhost:3100/board 에서 로그인한다.

### 3. Vercel — 배포

1. vercel.com에 GitHub 계정으로 로그인하고 Add New → Project에서 `Dream` 레포를 가져온다.
2. Root Directory를 `site`로 지정한다.
3. Environment Variables에 `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`를 넣고 Deploy한다. 이 값은 빌드할 때 코드에 들어가므로, 나중에 바꾸면 다시 배포해야 한다.
4. (선택) 비밀번호 재설정 메일을 쓰려면 배포 주소를 Supabase Authentication → URL Configuration의 Site URL에 넣는다.

## 지켜야 할 것

- secret 키(`sb_secret_…`)와 `service_role` 키는 어디에도 넣지 않는다. 이 키는 행 단위 보안을 건너뛰어 모든 데이터를 연다.
- `.env.local`과 `supabase/seed.local.sql`은 커밋하지 않는다(`.gitignore`에 있다).
- Supabase 무료 요금제는 1주일 동안 요청이 없으면 프로젝트가 일시 정지되고, 자동 백업이 없다.
- Vercel 무료(Hobby) 요금제는 개인·비상업 용도만 허용한다.
- 다른 사람에게 열기 전에 가입 방식, 개인정보 처리방침, 백업을 먼저 준비한다.
