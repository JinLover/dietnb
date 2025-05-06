# **`dietnb` (v0.1.0) — "Notebook 비만" 즉시 해소 패키지**

> **문제 의식**  
> * `matplotlib` Figure가 Base-64로 .ipynb 안에 저장 → 노트북 용량 MB ↗︎↗︎  
> * 캐시·누적된 Figure가 메모리까지 잠식  
> * 매 실행마다 `plt.close`, `nbstripout` … 귀찮다  

**`dietnb`** 는 **"그림은 디스크, 노트북은 링크"** 설계를 *자동* 적용해, 설치만으로 .ipynb 를 거의 **0 바이트**로 유지한다.

---

## 0. 핵심 규칙 (설계 원칙)

| # | 규칙 | 구현 포인트 |
|---|---|----|
| 1 | **ipynb 내부에 이미지 바이트 0** | `Figure._repr_png_ = None` (PNG 임베드 차단) |
| 2 | **셀마다 고유 prefix** | `cellId`(+ SHA-1 fallback) |
| 3 | **셀 재실행 → 기존 PNG 전부 삭제** | `_state[key] != exec_id` 체크 |
| 4 | **한 셀 안 여러 그림 → `_1,_2,…`** | `glob(f"{key}_*.png")` 갯수로 인덱스 |
| 5 | **브라우저 캐시 무효** | `<img …?v=exec_id>` |
| 6 | **첫 Figure부터 적용** | `_repr_html_` 직접 오버라이드 |
| 7 | **백엔드 재등록 방어** | `post_run_cell` 마다 패치 재주입 |

---

## 1. 빠른 사용

```bash
pip install dietnb                 # ➊ 설치
python -m dietnb install           # ➋ 자동 스타트업·UI 버튼 등록
```

*설치만으로 어떤 노트북이든 즉시 적용.*

> **수동 모드** — 스타트업을 건드리고 싶지 않다면  
> `import dietnb; dietnb.activate()` **또는** `%load_ext dietnb` 한 줄로 충분.

---

## 2. 추가 기능 — "Clean Images" 버튼

| UI | 기능 |
|----|---|
| 🗑 Toolbar 버튼 | **현재 커널에 로드되지 않은 PNG** 일괄 삭제 |
| Command Palette `DietNB: Clean Images` | 동일 기능 (단축키 배정 가능) |

Jupyter Lab / VS Code 확장(`dietnb_js`)이 버튼 → 커널 RPC 로 `dietnb.clean_unused()`를 호출.

---

## 3. 패키지 구조

```
dietnb/
├─ dietnb
│  ├─ __init__.py         # activate(), clean_unused()
│  ├─ _core.py            # Figure ↔ HTML 로직
│  ├─ _startup.py         # sitecustomize용 스타트업 코드
│  └─ _ipython.py         # load_ipython_extension
├─ dietnb_js/             # Lab/VSC UI (선택)
├─ tests/
├─ README.md
└─ pyproject.toml
```

### `_core.activate()` 주요 흐름

```python
def activate(folder="dietnb_imgs"):
    ip = get_ipython()                            # ①
    ip.display_formatter.formatters['image/png'].enabled = False
    Figure._repr_png_  = lambda self: None        # ② PNG 임베드 완전 차단
    Figure._repr_html_ = lambda f: _save_link(f, ip, folder)
    ip.events.register('post_run_cell', _close_and_repatch)
```

`_save_link()` : 앞서 합의된 최종 코드(폴더 `mkdir(parents=True)` 포함).

---

## 4. `pyproject.toml` 핵심

```toml
[project]
name            = "dietnb"
version         = "0.1.0"
description     = "Save matplotlib figures as external files and link them, keeping notebooks tiny."
readme          = "README.md"
license         = {text = "MIT"}
authors         = [{name = "Taeyong Park"}]
requires-python = ">=3.8"
dependencies    = ["ipython>=8", "matplotlib>=3.5"]

[project.scripts]
dietnb = "dietnb._cli:main"         # python -m dietnb install
```

---

## 5. 배포

```bash
python -m pip install --upgrade build twine
python -m build              # dist/ 디렉터리 생성
twine upload dist/*
```

---

## 6. 사용 예

```python
import numpy as np, matplotlib.pyplot as plt
# dietnb 설치 후엔 별다른 설정 없이 자동 적용

for i in range(3):
    plt.plot(np.linspace(0, 100), np.sin(np.linspace(0, 10) + i))
    plt.show()
```

* ipynb 증가량 ≈ 120 bytes  
* `dietnb_imgs/<hash>_{1,2,3}.png` 생성  
* "Clean Images" → 다른 셀의 PNG 즉시 정리

---

## 7. 로드맵

| 버전 | 기능 |
|---|---|
| 0.2  | nbconvert 플러그인 – HTML/PDF 내보낼 때 이미지 자동 복사 |
| 0.3  | Classic Notebook 6.x(셀 ID 없음) JS shim |
| 1.0  | JupyterLite / Pyodide 호환, VS Code WebView API 안정화 |

---

## 8. 라이선스 / 크레딧

*MIT.*  
아이디어·초기 코드 : **Taeyong Park × ChatGPT**  
Issue / PR 환영. 