# **`dietnb` (v0.1.3) — "Notebook 비만" 즉시 해소 패키지**

> **문제 의식**  
> * `matplotlib` Figure가 Base-64로 .ipynb 안에 저장 → 노트북 용량 MB ↗︎↗︎  
> * 캐시·누적된 Figure가 메모리까지 잠식  
> * 매 실행마다 `plt.close`, `nbstripout` … 귀찮다  

**`dietnb`** 는 **"그림은 디스크, 노트북은 링크"** 설계를 적용해, `.ipynb` 를 가볍게 유지합니다.
`dietnb install` 명령으로 자동 활성화를 설정하거나, 노트북에서 수동으로 `dietnb.activate()`를 호출하여 사용할 수 있습니다.

---

## 0. 핵심 규칙 (설계 원칙) - 최종 구현됨 (v0.1.3 기준)

| # | 규칙 | 구현 포인트 |
|---|---|----|
| 1 | **ipynb 내부에 이미지 바이트 0** | `Figure._repr_png_ = None` (PNG 임베드 차단) |
| 2 | **셀마다 고유 prefix** | `cellId`(+ SHA-1 fallback) |
| 3 | **셀 재실행 → 기존 PNG 전부 삭제** | `_state[key] != exec_id` 체크 |
| 4 | **한 셀 안 여러 그림 → `_1,_2,…`** | `glob(f"{key}_*.png")` 갯수로 인덱스 |
| 5 | **브라우저 캐시 무효** | `<img …?v=exec_id>` |
| 6 | **첫 Figure부터 적용** | `_repr_html_` 직접 오버라이드 |
| 7 | **백엔드 재등록 방어** | `post_run_cell` 마다 패치 재주입 |
| 8 | **노트북별 이미지 폴더 (자동 감지)** | VSCode (`__vsc_ipynb_file__`), Jupyter (`JPY_SESSION_NAME`), IPython (`ip.kernel.session.path`) 순으로 경로 탐색. 성공 시 `[노트북명]_dietnb_imgs` 사용. |
| 9 | **기본 폴더 (Fallback)** | 자동 감지 실패 시, 실행 디렉토리 내 `dietnb_imgs` 폴더 사용. |
| 10 | **간편한 자동 활성화** | `dietnb install` 명령으로 IPython 시작 시 자동 로드 스크립트 설치. 이 스크립트는 `dietnb.activate()`를 실행.|

---

## 1. 빠른 사용

```bash
pip install dietnb                 # ➊ 설치
dietnb install                     # ➋ 자동 스타트업 스크립트 등록 (권장)
# dietnb uninstall                   # (선택) 자동 스타트업 스크립트 제거
```

*`dietnb install` 실행 및 커널 재시작 후에는 대부분의 환경에서 `dietnb`가 자동으로 활성화됩니다.*
*자동 활성화는 노트북 경로를 감지하여 `[노트북파일명]_dietnb_imgs` 폴더를 사용하려고 시도하며, 실패 시 `dietnb_imgs`를 사용합니다.*

> **수동 활성화** — 자동 활성화를 원치 않거나, 특정 상황에서 명시적으로 호출하고 싶을 때:
> 노트북 시작 부분에 다음 코드를 추가하세요.
> ```python
> import dietnb
> dietnb.activate()
> ```

---

## 2. 추가 기능 — "Clean Images" 함수

| UI | 기능 |
|----|---|
| **Python 함수** | `dietnb.clean_unused()` 호출 (**구현됨**) |

*현재는 노트북 셀에서 `dietnb.clean_unused()`를 직접 호출하여 해당 컨텍스트(자동 감지된 폴더 또는 기본 폴더)의 불필요한 이미지를 정리합니다.*

---

## 3. 패키지 구조 (v0.1.3 기준)

```
dietnb/
├─ dietnb
│  ├─ __init__.py         # public API: activate(), deactivate(), clean_unused()
│  ├─ _core.py            # Figure 저장/링크 핵심 로직, 상태 관리, 경로 감지
│  ├─ _startup.py         # `dietnb install` 시 복사될 IPython 스타트업 스크립트 내용
│  └─ _cli.py             # `dietnb install/uninstall` 명령어 처리 로직 (main 함수)
├─ dietnb_js/             # Lab/VSC UI (선택, **미구현**)
├─ tests/                 # 자동화 테스트 (pytest, **기본 설정만 완료**)
├─ README.md
├─ README_ko.md
└─ pyproject.toml
```

### `_core.activate()` 주요 흐름 (요약)

`activate(ipython_instance=None)`
1.  IPython 인스턴스 가져오기.
2.  자동 감지된 노트북 경로에 따라 이미지 저장 폴더 결정 (`_get_notebook_image_dir`).
3.  Matplotlib Figure의 `_repr_png_` 비활성화, `_repr_html_`에 `_save_figure_and_get_html` 연결.
4.  셀 실행 후 정리 및 재패치 핸들러(`_post_cell_cleanup_and_repatch`) 등록.

### `_get_notebook_image_dir` 경로 결정 우선순위
1.  자동 감지 시도 (VSCode의 `__vsc_ipynb_file__`, Jupyter의 `JPY_SESSION_NAME` 등) 성공 시: `[노트북경로]/[노트북명]_dietnb_imgs`
2.  위 모두 실패 시: `CWD/dietnb_imgs`

---

## 4. `pyproject.toml` 핵심 (버전만 `0.1.3` 로 확인)

```toml
[project]
name            = "dietnb"
version         = "0.1.3"
# ... (이하 동일)
```

---

## 7. 현재 상태 및 로드맵 (v0.1.3 기준)

### 현재 상태 (v0.1.3)
*   **버전 업데이트:** 0.1.3으로 업데이트.
*   **브랜치 전략 도입:** `dev` 및 `release` 브랜치 생성.
*   **변경 로그 추가:** `CHANGELOG.md` 파일 추가.
*   **핵심 기능 단순화:** `folder_prefix` 옵션 제거. 자동 경로 감지 또는 기본 폴더 사용으로 통일.
*   **노트북별 폴더 자동 감지 (VS Code):** VS Code 환경에서 노트북 파일명 기반 폴더 생성 및 이미지 저장 확인.
*   **CLI `dietnb install`/`uninstall` 동작:** IPython 시작 스크립트 설치/제거 기능 구현.
*   **로깅 제거:** 코드 내 모든 로깅 호출 제거.
*   **문서 업데이트:** 단순화된 사용법 및 폴더 로직 반영. README 사용자 친화적으로 개선.
*   **라이선스 파일 추가 완료.**
*   **소스 코드 GitHub 푸시 완료.**
*   **PyPI v0.1.2 배포 완료:** [https://pypi.org/project/dietnb/0.1.2/](https://pypi.org/project/dietnb/0.1.2/) (v0.1.3는 아직 배포 전)

### 다음 단계
*   **Jupyter Lab/Server 환경 테스트:** `JPY_SESSION_NAME`을 통한 경로 감지 기능 확인.
*   **IPython 기본 환경 테스트:** `ip.kernel.session.path`를 통한 경로 감지 기능 확인.
*   **`pyproject.toml` 라이선스 형식 업데이트:** `project.license` 테이블 형식 사용에 대한 `setuptools` 경고 해결.
*   **자동화 테스트 강화:** `tests/` 디렉토리 및 `pytest` 설정은 되어 있으나, 상세 테스트 케이스 작성 필요.
*   **JupyterLab/VS Code UI (Toolbar 버튼 등) 고려.**
*   **로드맵 v0.2 이상:** nbconvert 플러그인, Classic Notebook 지원, JupyterLite 호환 등.

---

## 8. 라이선스 / 크레딧

*MIT.*  
아이디어·초기 코드 : **JinLover × ChatGPT**
현재 개발: **Cursor AI (Gemini)**
Issue / PR 환영.

---

## 9. 개발 여정 및 기술 상세 (v0.1.0 ~ v0.1.3)

이 섹션은 `dietnb` 패키지가 v0.1.0 초기 아이디어에서 v0.1.3 릴리스에 이르기까지의 개발 과정, 주요 기술적 결정, 문제 해결 과정을 상세히 기록합니다.

### 가. 초기 목표 및 설계 (v0.1.0 이전)

*   **문제 인식:** Jupyter 노트북 (`.ipynb`)에 `matplotlib` 그림이 Base64로 인코딩되어 저장될 경우 파일 크기가 급격히 증가하는 문제. 이는 노트북 로딩, 공유, 버전 관리에 부담을 줌. 또한, 사용자가 수동으로 `plt.close('all')`을 호출하거나 `nbstripout` 같은 도구를 사용해야 하는 번거로움 존재.
*   **핵심 아이디어:** "그림은 디스크 파일로, 노트북은 링크만" - 그림을 외부 파일(예: PNG)로 저장하고, 노트북에는 해당 파일을 가리키는 HTML `<img>` 태그만 삽입하여 노트북 용량 최소화.
*   **초기 설계 원칙 (rule.md 초기 내용 기반):**
    1.  ipynb 내 이미지 바이트 0: `Figure._repr_png_ = None`
    2.  셀마다 고유 prefix: `cellId` (+ SHA-1 fallback)
    3.  셀 재실행 시 기존 PNG 삭제: `_state[key] != exec_id` 체크 (실제 구현에서는 약간 다름, `clean_unused` 및 실행 카운트 기반 캐시 무효화)
    4.  한 셀 안 여러 그림: `_1,_2,...` 인덱싱
    5.  브라우저 캐시 무효: `<img ...?v=exec_id>`
    6.  첫 Figure부터 적용: `_repr_html_` 직접 오버라이드
    7.  백엔드 재등록 방어: `post_run_cell` 마다 패치 재주입

### 나. 핵심 기능 구현 (v0.1.0)

*   **패키지 기본 구조:**
    *   `pyproject.toml`: PEP 517/518 표준 빌드 시스템 및 패키지 메타데이터 정의 (의존성: `ipython>=8`, `matplotlib>=3.5`; 스크립트 진입점: `dietnb = "dietnb._cli:main"`).
    *   `dietnb/` (소스 루트):
        *   `dietnb/` (패키지 디렉토리):
            *   `__init__.py`: 공개 API (`activate`, `deactivate`, `clean_unused`) 노출. `activate()` 호출 시 `_core.activate()` 실행.
            *   `_core.py`: 핵심 로직.
                *   `activate(folder="dietnb_imgs")`:
                    1.  `ip = get_ipython()`: 현재 IPython 인스턴스 가져오기.
                    2.  `ip.display_formatter.formatters['image/png'].enabled = False`: IPython의 기본 PNG 포매터 비활성화 (이중 방어).
                    3.  `Figure._repr_png_ = lambda self: None`: `matplotlib.figure.Figure` 객체가 PNG 바이트를 반환하지 않도록 몽키 패칭.
                    4.  `Figure._repr_html_ = lambda fig: _save_figure_and_get_html(fig, ip)`: HTML 표현을 커스텀 함수로 교체.
                    5.  `ip.events.register('post_run_cell', _post_cell_cleanup_and_repatch_handler)`: 셀 실행 후 정리 및 재패치 핸들러 등록.
                *   `_save_figure_and_get_html(fig, ip, base_folder_name)`:
                    1.  노트북별 이미지 저장 폴더 결정 (`_get_notebook_image_dir`).
                    2.  고유 셀 키 생성 (`_get_cell_key`).
                    3.  폴더 내 기존 이미지 정리 (셀 재실행 시 이전 이미지 삭제 로직 - 초기 아이디어 반영).
                    4.  이미지 파일명 생성 (셀 키 + 인덱스: `f"{cell_key}_{fig_index + 1}.png"`).
                    5.  `fig.savefig(filepath)`: 그림을 파일로 저장.
                    6.  HTML `<img>` 태그 생성 (경로, 캐시 무효화 `?v={ip.execution_count}`).
                *   `_get_cell_key(ip, raw_cell=None)`: 셀 ID (`metadata.cellId`) 또는 셀 내용 SHA1 해시로 고유 키 생성.
                *   `_get_notebook_image_dir(ip_instance, base_folder_name)`: 이미지 저장 폴더 경로 결정 로직 (상세 내용은 '마. 기능 개선' 참조).
                *   `_post_cell_cleanup_and_repatch_handler(result)`: 셀 실행 후 호출.
                    1.  `plt.close('all')`: 메모리 누수 방지를 위해 모든 `matplotlib` 그림 닫기.
                    2.  `_patch_matplotlib(get_ipython())`: `matplotlib` 패치 재적용 (다른 확장에 의한 오버라이드 방지).
                *   `clean_unused(notebook_name_for_imgs=None)`: 현재 IPython 세션에서 활성화되지 않은 (참조되지 않는) 이미지 파일 정리.
            *   `_startup.py`: `import dietnb; dietnb.activate()` 내용. `dietnb install` 시 IPython 시작 스크립트로 복사됨.
            *   `_cli.py`: CLI 명령어 처리.
                *   `main()`: `argparse` 사용하여 `install`, `uninstall` 명령어 분기.
                *   `_install_startup_script()`: `_startup.py`를 `IPython.paths.get_ipython_dir() + "/profile_default/startup/00-dietnb.py"`로 복사.
                *   `_uninstall_startup_script()`: 설치된 시작 스크립트 삭제.
    *   `tests/`: 테스트 코드 (초기에는 기본 설정만).
    *   `dietnb_js/`: UI 확장용 (미구현).

*   **IPython 통합:**
    *   `get_ipython()`: 전역 IPython 인스턴스 접근.
    *   `ip.events.register('post_run_cell', ...)`: 셀 실행 후 콜백 함수 등록.
    *   `ip.execution_count`: 셀 실행 카운터 (캐시 무효화에 사용).

### 다. 초기 문제 해결 및 개선 (v0.1.0 과정)

*   **패키징 문제:**
    *   `pyproject.toml`의 `[tool.setuptools.packages.find].where` 설정: 초기 `pip install -e .` 시 `ModuleNotFoundError` 발생. `where = ["dietnb"]` (프로젝트 루트 아래 `dietnb` 디렉토리 내 `dietnb` 패키지)로 수정하여 해결.
*   **타입 힌트 호환성:** Python 3.8에서 `Optional[X]` 대신 `Union[X, None]` 사용하도록 수정.
*   **`post_run_cell` 핸들러 `TypeError`:** 핸들러 함수가 IPython 이벤트 시스템에서 전달하는 `result` 인자를 받도록 시그니처 수정.

### 라. Git 버전 관리 및 PyPI 배포 (v0.1.0, v0.1.1)

*   **Git:** `git init`, `.gitignore` (Python 기본), 단계별 커밋, `JinLover/dietnb` 원격 저장소로 푸시.
*   **라이선스:** `LICENSE` 파일 (MIT) 추가.
*   **빌드 및 배포:**
    *   `python -m pip install --upgrade build twine`
    *   `python -m build`: `dist/` 디렉토리에 `sdist` (`.tar.gz`) 및 `wheel` (`.whl`) 파일 생성.
    *   `twine upload dist/*`: PyPI에 패키지 업로드.
*   **README 개선 (v0.1.1):**
    *   `README_ko.md` (초기) -> `README.md` (영문 번역).
    *   사용자 피드백 반영: 과도한 홍보성 문구 제거, 명확성 및 사용자 중심 내용으로 수정. 이 변경으로 v0.1.1로 버전 업데이트 후 재배포.

### 마. 주요 기능 개선: 노트북별 이미지 폴더 (v0.1.2)

*   **요구사항:** 이미지를 `[노트북_파일명]_dietnb_imgs`와 같이 노트북 파일명 기반 폴더에 저장.
*   **`_core.py`의 `_get_notebook_image_dir` 함수 로직 변경 과정:**
    1.  **시도 1 (`ip.kernel.session.path`):**
        *   `session_path = getattr(getattr(ip_instance, 'kernel', None), 'session', None)`
        *   `notebook_path = getattr(session_path, 'path', None)`
        *   VS Code 환경에서 `notebook_path`를 가져오지 못하는 문제 발생. 디버깅 위해 로깅 추가.
    2.  **시도 2 (JavaScript 연동 - 사용자 요청으로 중단):** 프론트엔드에서 JS를 통해 경로를 전달하는 방식은 복잡성 증가로 중단. `git reset --hard`로 이전 상태 복구.
    3.  **시도 3 (환경 변수 및 전역 네임스페이스 - 성공):**
        *   다음 순서로 노트북 경로 탐색:
            1.  `ip_instance.kernel.session.path` (일부 Jupyter 환경)
            2.  `ip_instance.user_global_ns.get("__vsc_ipynb_file__")` (VS Code에서 주입하는 전역 변수 - **성공 지점**)
            3.  `os.environ.get("JPY_SESSION_NAME")` (JupyterLab/Server에서 사용하는 환경 변수)
            4.  위 방법 모두 실패 시, 작업 디렉토리(CWD)에 기본 폴더명(`dietnb_imgs` 또는 사용자가 `activate`시 전달한 이름) 사용.
        *   `pathlib.Path(notebook_path).stem`을 사용하여 확장자를 제외한 파일명 추출.
        *   최종 폴더명: `f"{notebook_stem}_{base_folder_name}"`.

### 바. 코드 단순화 및 최종 다듬기 (v0.1.2)

*   **`%load_ext dietnb` 매직 명령어 제거:**
    *   사용 편의성 및 API 단순화를 위해 IPython 확장 로딩 방식 제거.
    *   `_ipython.py` 파일 (내용: `load_ipython_extension`, `unload_ipython_extension`) 삭제.
    *   관련 문서 및 `pyproject.toml` 내 관련 설정 삭제.
*   **`activate(folder_prefix=...)` 인자 제거:** API 단순화를 위해 사용자가 폴더 접두사를 직접 지정하는 기능 제거. 노트북 파일명 기반으로 고정.
*   **내부 로깅 제거:** 사용자 경험을 깔끔하게 하기 위해 `_core.py` 및 기타 모듈에서 `logging` 호출 모두 제거. `_cli.py`의 오류 처리는 `print(..., file=sys.stderr)` 및 `sys.exit(1)` 사용으로 변경.
*   **`dietnb install` 재활성화 및 `uninstall` 명령어 추가:**
    *   경로 탐지 디버깅 중 비활성화했던 `dietnb install` 기능 복구.
    *   `_cli.py`에 `dietnb uninstall` 명령어 추가하여 `00-dietnb.py` 시작 스크립트 삭제 기능 제공.
*   **README 최종 검토:** `README.md` (영문) 및 `README_ko.md` (국문) 내용 최종 수정. 사용자 중심, 기능/혜택 강조, 내부 구현 상세는 최소화. 코드 예제 주석 및 레이블 영문화.

### 사. 최종 릴리스 (v0.1.2)

*   `pyproject.toml` 버전 `0.1.2`로 업데이트.
*   `git tag v0.1.2` 생성 및 `git push --tags`.
*   `python -m build`로 재빌드.
*   `twine upload dist/*`로 v0.1.2 PyPI에 배포 완료.

---