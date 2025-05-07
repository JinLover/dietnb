# `dietnb` (v0.1.2)

[![PyPI version](https://badge.fury.io/py/dietnb.svg)](https://badge.fury.io/py/dietnb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`dietnb`는 `matplotlib` 그림을 자동으로 로컬 PNG 파일로 저장하고, Jupyter 노트북에는 해당 이미지를 가리키는 `<img>` 링크를 삽입합니다. 이를 통해 노트북 파일 내부에 base64 이미지 데이터가 포함되는 것을 방지하여 `.ipynb` 파일 크기를 획기적으로 줄여줍니다.

---

## 주요 특징

*   **노트북 용량 감소:** 이미지를 노트북 외부에 저장하여 `.ipynb` 파일을 작게 유지합니다. 이미지는 `{노트북 파일명_dietnb_imgs}` 경로에 저장됩니다. 해당 경로는 노트북 파일과 같은곳에 위치합니다.
*   **자동 정리:** 셀을 다시 실행하면, 이전에 해당 셀에서 생성된 이미지들을 자동으로 삭제합니다.
*   **수동 정리 기능:** `dietnb.clean_unused()` 함수를 호출하여 현재 커널 세션에서 더 이상 사용되지 않는 이미지 파일들을 정리할 수 있습니다.

## 빠른 사용

1.  **설치:**
    ```bash
    pip install dietnb
    ```
2.  **활성화:**
    주로 두 가지 방법이 있습니다:

    *   **자동 활성화 (권장):** 터미널에서 `dietnb install`을 한 번 실행합니다. Jupyter 커널을 재시작하면, 모든 세션에서 `dietnb`가 자동으로 활성화됩니다. 노트북별 폴더(예: `MyNotebook_dietnb_imgs`)에 이미지를 저장하려고 시도하거나, 기본 `dietnb_imgs` 폴더를 사용합니다.

    *   **수동 활성화 (노트북마다):** `dietnb`를 수동으로 활성화하려면 노트북 상단에 다음 코드를 추가하세요:
        ```python
        import dietnb
        dietnb.activate()
        ```

이제 준비되었습니다! `matplotlib` 그림은 이제 외부 파일로 저장됩니다.

## 작동 방식

(단순화됨: `activate()` 옵션 상세 설명 제거, 결과에 집중)
`dietnb`는 활성화될 때 `matplotlib.figure.Figure`를 패치합니다. 그림이 표시될 때:
1. 기본 인라인 PNG 임베딩을 비활성화합니다.
2. 그림을 디렉토리에 저장합니다:
    - 현재 노트북 경로를 확인하여 (예: VS Code에서 `__vsc_ipynb_file__` 사용) 해당 경로 옆에 `[노트북명]_dietnb_imgs`와 같은 폴더를 생성하려고 시도합니다.
    - 노트북 경로를 찾을 수 없으면 현재 작업 디렉토리의 `dietnb_imgs`를 기본값으로 사용합니다.
3. 저장된 파일을 가리키는 `<img>` HTML 태그를 생성합니다 (캐시 무효화 쿼리 매개변수 포함).
4. 셀이 다시 실행되면, `dietnb`는 결정된 폴더 내에서 해당 셀의 이전 출력에서 오래된 이미지를 정리합니다.

## 불필요한 이미지 정리

관련 이미지 디렉토리(`dietnb_imgs` 또는 `[노트북명]_dietnb_imgs`)에서 현재 IPython 세션의 활성 셀 출력과 더 이상 일치하지 않는 이미지 파일을 제거하려면 다음을 호출하십시오:

```python
import dietnb
dietnb.clean_unused()
```

## 라이선스

MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

---
[English README (영어 README)](README.md) 