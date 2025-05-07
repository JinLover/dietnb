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
2.  **활성화 (각 노트북마다 필수):**
    노트북 시작 부분에 다음 중 **하나**를 추가하세요:

    ```python
    # 방법 1: 파이썬 호출
    import dietnb
    dietnb.activate()
    ```
    ```python
    # 방법 2: IPython 매직 명령어
    %load_ext dietnb
    ```

이제 준비되었습니다! 활성화 후에는 `plt.show()`를 사용하거나 셀 마지막에서 자동으로 표시되는 `matplotlib` 그림이 노트북 실행 디렉토리 기준으로 `dietnb_imgs` 폴더에 저장되고, 출력에는 링크만 표시되어 `.ipynb` 파일 크기를 작게 유지합니다.

*(참고: 자동 활성화를 위한 `dietnb install` 명령어는 현재 버전에서 비활성화되었습니다.)*

## 작동 방식

**사용 예시:**

`dietnb` 활성화 후, 평소처럼 `matplotlib` 코드를 실행하면 됩니다:

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x, y)
plt.title("사인파")
plt.show() # 그림이 로컬 파일로 저장되고 노트북에는 링크가 표시됩니다.
```

## 미사용 이미지 정리

현재 커널에서 더 이상 참조되지 않는 이미지 파일들을 제거하려면 다음 코드를 실행하세요:

```python
import dietnb
dietnb.clean_unused()
```

## 라이선스

MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

---
[English README (영어 README)](README.md) 