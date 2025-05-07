# **`dietnb` (v0.1.2) — "Notebook 비만" 즉시 해소 패키지**

> **문제 의식**  
> * `matplotlib` Figure가 Base-64로 .ipynb 안에 저장 → 노트북 용량 MB ↗︎↗︎  
> * 캐시·누적된 Figure가 메모리까지 잠식  
> * 매 실행마다 `plt.close`, `nbstripout` … 귀찮다  

**`dietnb`** 는 **"그림은 디스크, 노트북은 링크"** 설계를 *자동* 적용해, 설치만으로 .ipynb 를 거의 **0 바이트**로 유지한다.

---

## 0. 핵심 규칙 (설계 원칙) - 최종 구현됨

| # | 규칙 | 구현 포인트 |
|---|------|-------------|
| 1 | **ipynb 내부에 이미지 바이트 0** | `Figure._repr_png_ = None` (PNG 임베드 차단) |
| 2 | **셀마다 고유 prefix** | `cellId`(+ SHA-1 fallback) |
| 3 | **셀 재실행 → 기존 PNG 전부 삭제** | `_state[key] != exec_id` 체크 |
| 4 | **한 셀 안 여러 그림 → `_1,_2,…`** | `glob(f"{key}_*.png")` 갯수로 인덱스 |
| 5 | **브라우저 캐시 무효** | `<img …?v=exec_id>` |
| 6 | **첫 Figure부터 적용** | `_repr_html_` 직접 오버라이드 |
| 7 | **백엔드 재등록 방어** | `post_run_cell` 마다 패치 재주입 |
| 8 | **노트북별 폴더 저장 (v0.1.2+)** | `_get_notebook_image_dir()` 사용 |

---

## 1. 빠른 사용

```bash
pip install dietnb                 # ➊ 설치
dietnb install                     # ➋ 자동 스타트업 스크립트 등록
```

*`dietnb install` 실행 및 커널 재시작 후에는 어떤 노트북이든 자동 적용.*

> **수동 모드** — 자동 스타트업 설정을 원치 않거나 실패 시:
> 노트북 시작 부분에 `import dietnb; dietnb.activate()` **또는** `%load_ext dietnb` 실행.

---

## 2. 추가 기능 — "Clean Images" 버튼

| UI | 기능 |
|----|------|
| 🗑 Toolbar 버튼 | **현재 커널에 로드되지 않은 PNG** 일괄 삭제 (`dietnb_js` 필요, **미구현**) |
| Command Palette `DietNB: Clean Images` | 동일 기능 (`dietnb_js` 필요, **미구현**) |
| **Python 함수** | `dietnb.clean_unused()` 호출 (**구현됨**) |

*현재는 노트북 셀에서 `dietnb.clean_unused()`를 직접 호출하여 사용 가능.*

---

## 3. 패키지 구조 (구현됨)

```
dietnb/
├─ dietnb
│  ├─ __init__.py         # public API: activate(), deactivate(), clean_unused()
│  ├─ _core.py            # Figure 저장/링크 핵심 로직, 상태 관리, 노트북 경로 기반 폴더 결정
│  ├─ _startup.py         # `dietnb install` 시 복사될 IPython 스타트업 스크립트 내용
│  ├─ _ipython.py         # `%load_ext dietnb` 구현
│  └─ _cli.py             # `dietnb install` 명령어 처리 로직 (main 함수)
├─ dietnb_js/             # Lab/VSC UI (선택, **미구현**)
├─ tests/                 # 자동화 테스트 (pytest, **기본 설정만 완료**)
├─ README.md              # 영어 README (사용자 중심, 간결화)
├─ README_ko.md           # 한국어 README (사용자 중심, 간결화)
└─ pyproject.toml
```

### `_core.activate()` 주요 흐름 (구현됨)

```python
def activate(folder="dietnb_imgs"): # folder 인자는 이제 내부적으로 사용되지 않음
    ip = get_ipython()                            # ①
    ip.display_formatter.formatters['image/png'].enabled = False # PNG 포매터 비활성화
    Figure._repr_png_  = lambda self: None        # ② PNG 임베드 완전 차단
    Figure._repr_html_ = lambda fig: _save_figure_and_get_html(fig, ip) # ③ HTML 생성 로직 연결 (내부에서 폴더 결정)
    # ④ 셀 실행 후 정리 및 재패치 핸들러 등록 (IPython 이벤트 인자 받도록 수정됨)
    ip.events.register('post_run_cell', _post_cell_cleanup_and_repatch)
```

---

## 4. `pyproject.toml` 핵심 (구현됨)

```toml
[project]
name            = "dietnb"
version         = "0.1.2" # 버전 업데이트
description     = "Save matplotlib figures as external files and link them, keeping notebooks tiny."
readme          = "README.md" # 영어 README 참조
license         = {text = "MIT"}
authors         = [{name = "JinLover"}]
requires-python = ">=3.8"
dependencies    = ["ipython>=8", "matplotlib>=3.5"]

[project.scripts]
dietnb = "dietnb._cli:main"         # `dietnb` 명령어 생성 -> _cli.main 연결

[tool.setuptools.packages.find]
# 패키지 코드를 찾을 위치 지정 (프로젝트 루트 아래 'dietnb' 디렉토리 내부)
where = ["dietnb"]

[project.optional-dependencies]
# 개발 및 테스트용 의존성 (`pip install -e '.[dev]'`)
dev = [
    "pytest>=7.0",
    "pytest-mock>=3.10"
]
```

---

## 5. 배포 (v0.1.2 준비 중)

```bash
python -m pip install --upgrade build twine  # ➊ 빌드 도구 설치 (완료)
python -m build                            # ➋ dist/ 디렉터리 생성 (진행 예정)
twine upload dist/*                        # ➌ PyPI 업로드 (진행 예정)
```

---

## 6. 사용 예 (현재 작동 확인됨)

```python
# `dietnb install` 실행 및 커널 재시작 후, 또는 수동 활성화 후:
import numpy as np
import matplotlib.pyplot as plt

for i in range(3):
    plt.plot(np.linspace(0, 100), np.sin(np.linspace(0, 10) + i))
    plt.show() # 자동으로 [노트북이름]_dietnb_imgs/ 폴더에 저장되고 링크 출력
```

* ipynb 증가량 ≈ 120 bytes
* `[노트북이름]_dietnb_imgs/<hash>_{1,2,3}.png` 생성
* 다른 셀 실행 후 `dietnb.clean_unused()` 호출 시 이전 셀 이미지 정리 가능

---

## 7. 현재 상태 및 로드맵

### 현재 상태 (v0.1.2 기준) - 배포 준비
*   **핵심 기능 구현 완료:** Matplotlib 그림 외부 저장 및 링크 기능 정상 작동.
*   **노트북별 폴더 저장 기능 추가:** 이미지가 노트북 파일명 기반의 폴더에 저장됨.
*   **설치 및 자동 활성화 구현:** `pip install dietnb` 및 `dietnb install` 통한 설치 및 자동 시작 스크립트 등록 완료.
*   **수동 활성화 구현:** `%load_ext dietnb` 및 `dietnb.activate()` 작동.
*   **이미지 정리 기능 구현:** `dietnb.clean_unused()` 함수 구현 완료 (노트북 컨텍스트 기반).
*   **기본 패키지 구조 완료:** `pyproject.toml` 기반 패키징 및 CLI 설정 완료.
*   **라이선스 파일 추가 완료:** `LICENSE` (MIT) 파일 추가.
*   **소스 코드 GitHub 푸시 완료:** `https://github.com/JinLover/dietnb` 에 소스 코드 게시.
*   **README 개편 완료:** 사용자 중심의 간결한 README (영문/한글) 제공.
*   **v0.1.1 PyPI 배포 완료:** [https://pypi.org/project/dietnb/0.1.1/](https://pypi.org/project/dietnb/0.1.1/)

### 다음 단계
*   **v0.1.2 배포:** `python -m build` 및 `twine upload dist/*` 실행.
*   **`pyproject.toml` 라이선스 형식 업데이트:** `project.license` 테이블 형식 사용에 대한 `setuptools` 경고 해결.
*   **자동화 테스트:** `tests/` 디렉토리 및 `pytest` 설정은 되어 있으나, 상세 테스트 케이스 작성 필요.
*   **JupyterLab/VS Code UI:** `dietnb_js` 구현 필요 (Toolbar 버튼, Command Palette 연동).
*   **로드맵 v0.2 이상:** nbconvert 플러그인, Classic Notebook 지원, JupyterLite 호환 등.

---

## 8. 라이선스 / 크레딧

*MIT.*
아이디어·초기 코드 : **JinLover × ChatGPT**
현재 개발: **Cursor AI (Gemini)**
Issue / PR 환영.