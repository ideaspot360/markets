# 📈 Market Context 360 (`markets.ideaspot360.com`) 전담 에이전트 마스터 가이드

> **블로그 정체성**: 글로벌 거시경제(Macro), 미국 증시(US Equities), 유동성 레짐(Central Bank Liquidity), 퀀트/팩터 투자 프레임워크를 심층 분석하는 글로벌 기관급 리서치 블로그입니다.  
> **도메인**: `https://markets.ideaspot360.com`  
> **호스팅**: GitHub Pages (`ideaspot360/markets` 리포지토리)  
> **인프라 관제**: `01_you_idea_blog` 워크스페이스에서 중앙 모니터링 (Porkbun DNS, GA4, 라이브 실측)

---

## 🏛️ 운영 원칙 및 역할 경계
1. **독립적 콘텐츠 생산**:
   - 본 블로그의 콘텐츠 기획, 데이터 분석, 마크다운 원고 작성 및 일상 발행은 **글로벌 증시 전담 에이전트**가 100% 자율적이고 독립적으로 수행합니다.
   - 중앙 인프라 워크스페이스(`01_you_idea_blog`)는 글 작성에 일체 관여하지 않으며, 오직 DNS, GA4 통계 수집, 라이브 상태 실측만 지원합니다.
2. **원클릭 배포 파이프라인**:
   - `_posts/YYYY-MM-DD-slug.md` 파일을 생성하여 `origin main`에 푸시하면, GitHub Actions / Pages가 수 초 내에 전 세계로 자동 빌드 및 배포합니다.
3. **금융 면책 조항 (Compliance)**:
   - 모든 글 최하단 또는 템플릿에 공인 금융 면책 조항(Financial Disclaimer: 투자 권유 아님, 정보 제공 목적)이 자동 삽입되도록 설계되어 있습니다.

---

## 🔍🖼️ 초정밀 인터랙티브 줌 & 팬 기능 내장 (Ultra-Precision Lightbox)
- 본 사이트에는 **초정밀 인터랙티브 줌 & 팬 모달 엔진**이 기본 탑재되어 있습니다.
- 거시경제 시계열 차트, 연준 점도표, 기업 밸류에이션 매트릭스 도안 등을 본문에 마크다운 이미지(`![설명](url)`)로 삽입하기만 하면:
  - 독자가 클릭 시 즉시 딥 다크 모달 뷰어로 전환
  - 마우스 휠로 **0.5배 ~ 6.0배까지 초정밀 줌인/줌아웃** (마우스 커서 위치 기준 확대)
  - 마우스 드래그로 **360도 자유 이동(Pan)**
  - 더블클릭 시 2.5배 스마트 줌
  - 모바일 터치 핀치 줌 완벽 지원

---

## 📚 4대 추천 카테고리 체계
1. **`Macro Intelligence`**: 연준 순유동성(Net Liquidity), 재무부 TGA, 역레포(RRP), 금리/인플레이션 및 통화정책.
2. **`US Equity Deep-Dive`**: 빅테크 및 주요 섹터 펀더멘털, FCF 수익률, AI 인프라 CapEx 효율성, 밸류에이션.
3. **`Earnings Post-Mortem`**: 실적 발표 분기 리뷰, 컨센서스 괴리율 분석, 가이던스 품질 평가.
4. **`Systematic & Factor Frameworks`**: 주식 리스크 프리미엄(ERP), 변동성(VIX/MOVE) 구조, 팩터 로테이션.

---

## 🚀 글 작성 및 배포 절차 (SOP)

### 1단계: 원고 마크다운 파일 작성
`_posts/YYYY-MM-DD-제목슬러그.md` 형식으로 작성합니다:

```markdown
---
title: "리포트 영문 제목"
date: 2026-11-16 09:30:00 +0900
category: "Macro Intelligence"
tags: [태그1, 태그2, 태그3]
author: "Market Context Research"
summary: "리포트 핵심 요약 (1~2문장)"
layout: post
---

# 리포트 본문 제목
...
```

### 2단계: Git 커밋 & 푸시
```bash
git add _posts/YYYY-MM-DD-제목슬러그.md
git commit -m "feat(markets): publish publication title"
git push origin main
```
푸시 즉시 `https://markets.ideaspot360.com`에 자동 반영됩니다.
