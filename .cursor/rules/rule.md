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
| 8 | **노트북별 이미지 폴더 (자동 감지)** | VSCode (`__vsc_ipynb_file__`), Jupyter (`JPY_SESSION_NAME`), IPython (`ip.kernel.session.path`) 순으로 경로 탐색. 성공 시 `[노트북명]_dietnb_imgs` 사용. |
| 9 | **기본 폴더 (Fallback)** | 자동 감지 실패 시, 실행 디렉토리 내 `dietnb_imgs` 폴더 사용. |
| 10 | **간편한 자동 활성화** | `dietnb install` 명령으로 IPython 시작 시 자동 로드 스크립트 설치. 이 스크립트는 `dietnb.activate()`를 실행.|

---

## 1. 빠른 사용

```bash
pip install dietnb                 # ➊ 설치
dietnb install                     # ➋ 자동 스타트업 스크립트 등록 (권장)
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

`activate(ipython_instance=None)`
1.  IPython 인스턴스 가져오기.
2.  자동 감지된 노트북 경로에 따라 이미지 저장 폴더 결정 (`_get_notebook_image_dir`).
3.  Matplotlib Figure의 `_repr_png_` 비활성화, `_repr_html_`에 `_save_figure_and_get_html` 연결.
4.  셀 실행 후 정리 및 재패치 핸들러(`_post_cell_cleanup_and_repatch`) 등록.

### `_get_notebook_image_dir` 경로 결정 우선순위
1.  자동 감지 시도 (VSCode의 `__vsc_ipynb_file__`, Jupyter의 `JPY_SESSION_NAME` 등) 성공 시: `[노트북경로]/[노트북명]_dietnb_imgs`
2.  위 모두 실패 시: `CWD/dietnb_imgs`

---

## 4. `pyproject.toml` 핵심 (버전만 `0.1.2` 로 확인)

```toml
[project]
name            = \"dietnb\"
version         = \"0.1.2\"
# ... (이하 동일)
```

---

## 7. 현재 상태 및 로드맵 (v0.1.2 기준)

### 현재 상태 (v0.1.2) - PyPI 배포 완료
*   **핵심 기능 단순화:** `folder_prefix` 옵션 제거. 자동 경로 감지 또는 기본 폴더 사용으로 통일.
*   **노트북별 폴더 자동 감지 (VS Code):** VS Code 환경에서 노트북 파일명 기반 폴더 생성 및 이미지 저장 확인.
*   **CLI `dietnb install` 동작:** IPython 시작 시 `dietnb.activate()` 자동 실행.
*   **로깅 제거:** 코드 내 모든 로깅 호출 제거.
*   **문서 업데이트:** 단순화된 사용법 및 폴더 로직 반영. README 사용자 친화적으로 개선.
*   **라이선스 파일 추가 완료.**
*   **소스 코드 GitHub 푸시 완료.**
*   **PyPI v0.1.2 배포 완료:** [https://pypi.org/project/dietnb/0.1.2/](https://pypi.org/project/dietnb/0.1.2/)

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