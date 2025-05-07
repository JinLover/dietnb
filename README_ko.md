# `dietnb` (v0.1.2)

[![PyPI version](https://badge.fury.io/py/dietnb.svg)](https://badge.fury.io/py/dietnb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`dietnb`는 Jupyter 노트북 사용 시 `matplotlib` 그래프가 파일 내부에 Base64로 저장되어 `.ipynb` 파일 크기가 커지는 문제를 해결합니다. `dietnb`는 그래프를 로컬 PNG 파일로 저장하고 노트북에는 이미지 링크만 삽입하여, 노트북 파일을 가볍게 유지하고 관리 효율성을 높입니다.

---

## 주요 기능

*   **노트북 파일 크기 최소화:** `matplotlib` 그래프를 노트북 외부의 PNG 파일로 저장하여 `.ipynb` 파일의 용량 부담을 크게 줄여줍니다.
*   **자동 이미지 폴더 관리:** 노트북 파일 위치를 기준으로 이미지 저장 폴더(`[NotebookFileName]_dietnb_imgs`)를 자동으로 생성하고 관리합니다. (VS Code 등의 환경에서 경로 감지 성공 시 적용되며, 실패 시 현재 작업 디렉토리에 `dietnb_imgs` 폴더를 사용합니다.)
*   **자동 이미지 업데이트:** 노트북 셀을 다시 실행할 경우, 해당 셀에서 이전에 생성된 이미지 파일은 자동으로 삭제되어 항상 최신 결과물만 유지됩니다.
*   **이미지 정리 기능:** `dietnb.clean_unused()` 함수를 통해 현재 세션에서 사용하지 않는 불필요한 이미지 파일을 쉽게 정리할 수 있습니다.
*   **간편한 자동 활성화:** `dietnb install` 명령어를 통해 IPython 및 Jupyter 환경 시작 시 `dietnb`가 자동으로 활성화되도록 설정할 수 있습니다.

---

## 설치 및 활성화

**1. `dietnb` 패키지 설치**

터미널에서 다음 명령어를 실행합니다:
```bash
pip install dietnb
```

**2. 활성화 방법 선택**

   **A. 자동 활성화 (권장)**
   터미널에서 다음 명령어를 최초 1회 실행합니다:
   ```bash
   dietnb install
   ```
   이후 Jupyter 커널을 재시작하면, `dietnb`가 자동으로 활성화됩니다. 이미지는 노트북 파일 경로를 기준으로 생성된 폴더 또는 기본 `dietnb_imgs` 폴더에 저장됩니다.

   **B. 수동 활성화 (노트북마다 적용)**
   특정 노트북에서만 `dietnb`를 사용하거나 자동 활성화를 원치 않을 경우, 노트북 상단에 다음 코드를 추가하여 수동으로 활성화할 수 있습니다:
   ```python
   import dietnb
   dietnb.activate()
   ```

---

## 사용 예시

`dietnb`가 활성화된 상태에서는 기존과 동일하게 `matplotlib` 코드를 사용합니다.

```python
import matplotlib.pyplot as plt
import numpy as np

# Create a plot
x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x), label='sin(x)')
plt.plot(x, np.cos(x), label='cos(x)')
plt.title("Trigonometric Functions") # English Title
plt.xlabel("X-axis")              # English Label
plt.ylabel("Y-axis")              # English Label
plt.legend()

plt.show() # On show(), the image is saved to a file, and a link is displayed in the notebook.
```
생성된 이미지는 노트북 파일과 동일한 경로의 `[NotebookFileName]_dietnb_imgs` 폴더 또는 `dietnb_imgs` 폴더에서 확인할 수 있습니다.

---

## 불필요한 이미지 파일 정리

더 이상 사용되지 않는 이미지 파일을 정리하려면, 노트북 셀에서 다음 함수를 실행합니다:

```python
import dietnb
dietnb.clean_unused()
```

---

## 라이선스

MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

---
[English README (영어 README)](README.md) 