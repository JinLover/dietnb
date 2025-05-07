# **`dietnb` (v0.1.2) — "Notebook 비만" 즉시 해소 패키지**

> **문제 의식**  
> * `matplotlib` Figure가 Base-64로 .ipynb 안에 저장 → 노트북 용량 MB ↗︎↗︎  
> * 캐시·누적된 Figure가 메모리까지 잠식  
> * 매 실행마다 `plt.close`, `nbstripout` … 귀찮다  

**`dietnb`** 는 **"그림은 디스크, 노트북은 링크"** 설계를 적용해, `.ipynb` 를 가볍게 유지합니다.
`dietnb install` 명령으로 자동 활성화를 설정하거나, 노트북에서 수동으로 `dietnb.activate()`를 호출하여 사용할 수 있습니다.

---

## 0. 핵심 규칙 (설계 원칙) - 최종 구현됨 (v0.1.2 기준)

| # | 규칙 | 구현 포인트 |
|---|---|----|
| 1 | **ipynb 내부에 이미지 바이트 0** | `Figure._repr_png_ = None` (PNG 임베드 차단) |
| 2 | **셀마다 고유 prefix** | `cellId`(+ SHA-1 fallback) |
| 3 | **셀 재실행 → 기존 PNG 전부 삭제** | `_state[key] != exec_id` 체크 |
| 4 | **한 셀 안 여러 그림 → `_1,_2,…`** | `glob(f"{key}_*.png")` 갯수로 인덱스 |
| 5 | **브라우저 캐시 무효** | `<img …?v=exec_id>` |
| 6 | **첫 Figure부터 적용** | `_repr_html_` 직접 오버라이드 |
| 7 | **백엔드 재등록 방어** | `post_run_cell` 마다 패치 재주입 |
| 8 | **노트북별 이미지 폴더 (자동 감지)** | VSCode (`__vsc_ipynb_file__` 전역 변수), Jupyter (`JPY_SESSION_NAME` 환경 변수), IPython (`ip.kernel.session.path`) 순으로 경로 탐색. 성공 시 `[노트북명]_dietnb_imgs` 폴더 사용. |
| 9 | **사용자 지정 폴더 접두사** | `dietnb.activate(folder_prefix="MyProject")` 호출 시 `MyProject_dietnb_imgs` 폴더 사용. 자동 감지보다 우선. |
| 10 | **기본 폴더 (Fallback)** | 위 방법 모두 실패/미지정 시, 실행 디렉토리 내 `dietnb_imgs` 폴더 사용. |
| 11 | **간편한 자동 활성화** | `dietnb install` 명령으로 IPython 시작 시 자동 로드 스크립트 (`00-dietnb.py`) 설치. 이 스크립트는 `dietnb.activate()`를 기본 옵션으로 실행.|

---

## 1. 빠른 사용

```bash
pip install dietnb                 # ➊ 설치
dietnb install                     # ➋ 자동 스타트업 스크립트 등록 (권장)
```

*`dietnb install` 실행 및 커널 재시작 후에는 대부분의 환경에서 `dietnb`가 자동으로 활성화됩니다.*
*자동 활성화는 노트북 경로를 감지하여 `[노트북파일명]_dietnb_imgs` 폴더를 사용하려고 시도하며, 실패 시 `dietnb_imgs`를 사용합니다.*

> **수동 활성화 및 폴더 지정** — 자동 활성화를 원치 않거나, 특정 폴더 접두사를 사용하고 싶을 때:
> 노트북 시작 부분에 다음 코드를 추가하세요.
> ```python
> import dietnb
>
> # 기본 자동 감지 모드로 활성화
> # dietnb.activate()
>
> # 또는, 특정 프로젝트/노트북용 폴더 지정 (예: MyProject_dietnb_imgs)
> dietnb.activate(folder_prefix="MyProject")
> ```

---

## 2. 추가 기능 — "Clean Images" 버튼 / 함수

| UI | 기능 |
|----|---|
| 🗑 Toolbar 버튼 | **현재 커널에 로드되지 않은 PNG** 일괄 삭제 (`dietnb_js` 필요, **미구현**) |
| Command Palette `DietNB: Clean Images` | 동일 기능 (`dietnb_js` 필요, **미구현**) |
| **Python 함수** | `dietnb.clean_unused()` 또는 `dietnb.clean_unused(folder_prefix="MyProject")` 호출 (**구현됨**) |

*현재는 노트북 셀에서 `dietnb.clean_unused()` 또는 `dietnb.clean_unused(folder_prefix="...")`를 직접 호출하여 사용 가능.*

---

## 3. 패키지 구조 (v0.1.2 기준)

```
dietnb/
├─ dietnb
│  ├─ __init__.py         # public API: activate(), deactivate(), clean_unused()
│  ├─ _core.py            # Figure 저장/링크 핵심 로직, 상태 관리, 경로 감지
│  ├─ _startup.py         # `dietnb install` 시 복사될 IPython 스타트업 스크립트 내용
│  └─ _cli.py             # `dietnb install` 명령어 처리 로직 (main 함수)
├─ dietnb_js/             # Lab/VSC UI (선택, **미구현**)
├─ tests/                 # 자동화 테스트 (pytest, **기본 설정만 완료**)
├─ README.md
├─ README_ko.md
└─ pyproject.toml
```

### `_core.activate()` 주요 흐름 (요약)

`activate(ipython_instance=None, folder_prefix: Optional[str] = None)`
1.  IPython 인스턴스 가져오기.
2.  로깅 설정 (DEBUG 레벨, StreamHandler).
3.  `folder_prefix` 또는 자동 감지된 노트북 경로에 따라 이미지 저장 폴더 결정 (`_get_notebook_image_dir`).
4.  Matplotlib Figure의 `_repr_png_` 비활성화, `_repr_html_`에 `_save_figure_and_get_html` 연결 (이때 `folder_prefix` 전달).
5.  셀 실행 후 정리 및 재패치 핸들러(`_post_cell_cleanup_and_repatch`) 등록 (이때도 `folder_prefix` 전달).

### `_get_notebook_image_dir` 경로 결정 우선순위
1.  `folder_prefix`가 제공되면: `CWD/[folder_prefix]_dietnb_imgs`
2.  자동 감지 시도 (VSCode의 `__vsc_ipynb_file__`, Jupyter의 `JPY_SESSION_NAME` 등) 성공 시: `[노트북경로]/[노트북명]_dietnb_imgs`
3.  위 모두 실패 시: `CWD/dietnb_imgs`

---

## 4. `pyproject.toml` 핵심 (변경 없음)

```toml
[project]
name            = "dietnb"
version         = "0.1.2" # 버전 업데이트 필요
# ... (이하 동일)
```

---

## 7. 현재 상태 및 로드맵 (v0.1.2 기준)

### 현재 상태 (v0.1.2)
*   **핵심 기능 구현 완료:** Matplotlib 그림 외부 저장 및 링크 기능 정상 작동.
*   **노트북별 폴더 자동 감지 (VS Code):** VS Code 환경에서 노트북 파일명 기반 폴더(`[노트북명]_dietnb_imgs`) 생성 및 이미지 저장 확인.
*   **사용자 지정 폴더 접두사 기능:** `activate(folder_prefix="...")` 및 `clean_unused(folder_prefix="...")` 작동.
*   **CLI `dietnb install` 부활:** IPython 시작 시 자동 활성화 스크립트(`00-dietnb.py`) 설치 기능 복원.
*   **`%load_ext` 방식 제거:** 활성화 방식을 `dietnb.activate()`로 단일화.
*   **이미지 정리 기능 개선:** `folder_prefix` 컨텍스트에 맞게 정리.
*   **문서 업데이트:** 변경된 설치 및 활성화 방법, 폴더 로직 반영.
*   **라이선스 파일 추가 완료.**
*   **소스 코드 GitHub 푸시 완료.**
*   **PyPI 배포 완료 (v0.1.1까지).**

### 다음 단계 (v0.1.2 릴리즈 준비)
*   **`pyproject.toml` 버전 업데이트** (`0.1.2`로 변경).
*   **Jupyter Lab/Server 환경 테스트:** `JPY_SESSION_NAME`을 통한 경로 감지 기능 확인.
*   **IPython 기본 환경 테스트:** `ip.kernel.session.path`를 통한 경로 감지 기능 확인 (가능한 경우).
*   **v0.1.2 Git 태그 생성 및 푸시.**
*   **v0.1.2 PyPI 배포.**
*   **자동화 테스트:** `tests/` 디렉토리 및 `pytest` 설정은 되어 있으나, 상세 테스트 케이스 작성 필요.
*   **JupyterLab/VS Code UI:** `dietnb_js` 구현 필요 (Toolbar 버튼, Command Palette 연동).
*   **로드맵 v0.2 이상:** nbconvert 플러그인, Classic Notebook 지원, JupyterLite 호환 등.