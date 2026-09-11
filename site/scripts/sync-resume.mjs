// 이력서 원본은 레포의 career/resume 에 있다. 개발·빌드 전에 사이트 공개 폴더로 복사한다.
// 원본 폴더가 없으면(사이트 폴더만 받은 경우) 커밋된 사본을 그대로 쓴다.
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const siteRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const source = join(siteRoot, "..", "career", "resume");
const target = join(siteRoot, "public", "resume");
const files = [
  ["resume_ko.html", "ko.html"],
  ["resume_en.html", "en.html"],
];

if (!existsSync(source)) {
  console.log("sync-resume: career/resume 폴더가 없어 커밋된 사본을 사용합니다.");
  process.exit(0);
}

mkdirSync(target, { recursive: true });
for (const [from, to] of files) {
  copyFileSync(join(source, from), join(target, to));
}
console.log("sync-resume: career/resume → public/resume 복사 완료");
