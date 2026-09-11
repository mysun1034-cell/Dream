import { marked } from "marked";

// Dream 문서 안의 상대 링크(./other.md 같은)는 이 사이트에 대응하는 페이지가 없어 깨진 링크가 된다.
// http(s) 링크만 실제 링크로 살리고, 나머지는 글자만 남긴다.
const renderer = new marked.Renderer();
renderer.link = ({ href, title, tokens }) => {
  const text = renderer.parser.parseInline(tokens);
  if (!/^https?:\/\//.test(href)) return text;
  const titleAttr = title ? ` title="${title.replace(/"/g, "&quot;")}"` : "";
  const safeHref = href.replace(/"/g, "&quot;");
  return `<a href="${safeHref}" target="_blank" rel="noopener noreferrer"${titleAttr}>${text}</a>`;
};

marked.setOptions({ renderer, gfm: true, breaks: false });

export function renderMarkdown(source: string): string {
  return marked.parse(source, { async: false }) as string;
}
