# EdenCare — ERD (초안)

> SQL track W1 · Chris · **TODO: 스키마와 대조하며 채우기**

## Core entities (draft)

| Entity | 설명 |
|--------|------|
| `tenant` | 멀티테넌트 기관 |
| `user` | 로그인 · RBAC |
| `beneficiary` | 이용자 |
| `staff` | 직원 |
| `billing` | 청구 |
| `accounting_entry` | 회계 |
| `schedule` | 일정 |
| `audit_log` | 감사 |

## Relationships (TODO)

- tenant 1 — N user
- tenant 1 — N beneficiary
- …

## Notes

- NHIS 검산 rule → 어디에? (rule table vs code)
- soft delete cascade → FK diagram
