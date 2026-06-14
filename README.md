# weathercli

터미널에서 바로 확인하는 날씨 대시보드, neofetch 스타일로 왼쪽에 아트,
오른쪽에 날씨 정보를 나란히 보여줍니다.

## 설치

Python 3.9 이상

```bash
pip install .
# 또는 전역 설치
pipx install .
```

## 명령어

```
wt                   현재 날씨 보기
wt set               설정 변경 (= weather set = wt setting)
wt --logo list       사용 가능한 로고 목록
wt --logo <이름>     해당 로고로 한 번만 날씨 보기
wt --logopin <이름>  해당 로고를 기본 아트로 고정 + 날씨 표시
weather              wt 와 동일
```

## 설정 메뉴 (wt set)

방향키 + 엔터로 조작. 섹션별로 구성됩니다.

**데이터 · 단위**
- 지역 설정 — 한국 17개 시·도 빠른 선택 또는 이름 검색 (해외 포함)
- 온도 단위 — 섭씨 / 화씨 / 둘 다
- 표시 항목 — 날씨 상태, 체감, 습도, 바람, 강수량, 일출몰, 자외선
- 언어 — 한국어 / English

**화면 꾸미기**
- 표시 이름 — 상단 헤더 텍스트 변경 (예: weather@cli → mypc@home)
- 아트 설정
  - 기본 아트 사용
  - 직접 아스키 아트 입력 (여러 줄, Esc→Enter 완료)
  - 이미지 파일 사용 (PNG/JPG → 터미널 블록 자동 변환)
  - 로고 목록에서 선택 (wt --logo list 의 이름들)
  - 리스트에 추가 — 아스키 아트를 이름 붙여 등록, wt --logo 이름 사용 가능
  - 사용자 로고 삭제

**데이터 보정**
- 온도 보정 — API 온도와 실제 체감 간 차이를 오프셋으로 입력 (예: -1.5, 2)
  모든 온도 값(현재/체감/최고/최저)에 일괄 적용됨

## 폴더 구조

```
weathercli/
  cli.py           진입점, 명령어 분기
  config.py        설정 저장/로드
  display.py       화면 렌더링
  settings.py      대화형 설정 메뉴
  geocoding.py     지역 검색
  weatherapi.py    날씨 API
  weathercodes.py  날씨 코드 → 텍스트/색상
  compass.py       풍향
  art.py           아트 렌더링 (아스키/이미지/로고)
  logos.py         로고 인덱스 + 파싱
  textwidth.py     한글/영문 너비 계산
  theme.py         색상 토큰
  i18n.py          한국어/영어 문구
  logos/           내장 로고 파일 (arch.txt, kali.txt)
```

설정 파일: ~/.config/weathercli/config.json
