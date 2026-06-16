# weatherkocli

터미널에서 바로 확인하는 날씨 대시보드입니다. 스타일은 neofetch를 참고하였습니다.

## 설치 조건

Python 3.9 이상

```bash
pip install .
```

```bash
pipx install .
```
**또는**
```bash
pip install weatherkocli
```

## 명령어

```
wt                   현재 날씨 보기
wt set               설정 변경 (= weather set = wt setting)
wt --logo list       사용 가능한 로고 목록
wt --logo <이름>     해당 로고로 한 번만 날씨 보기
wt --logopin <이름>  해당 로고를 기본 아트로 고정 후 날씨 표시
weather              wt 와 동일
```

## 설정 메뉴 (wt set)

**데이터 · 단위**
- 지역 설정 — 한국 17개 시, 도 빠른 선택 또는 이름 검색
- 온도 단위 — 섭씨 / 화씨 / 둘 다
- 표시 항목 — 날씨 상태, 체감, 습도, 바람, 강수량, 일출몰, 자외선
- 언어 — 한국어 / English

**화면 꾸미기**
- 표시 이름 — 상단 헤더 텍스트 변경 (예: weather@cli → mypc@home)
- 아트 설정
  - 기본 아트 사용
  - 직접 아스키 아트 입력
  - 이미지 파일 사용
  - 로고 목록에서 선택
  - 리스트에 추가 — 아스키 아트를 이름 붙여 등록
  - 사용자 로고 삭제

**데이터 보정**
- 온도 보정 — API 온도와 실제 체감 간 차이를 입력
