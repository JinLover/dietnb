# `dietnb` (v0.1.2)

[![PyPI version](https://badge.fury.io/py/dietnb.svg)](https://badge.fury.io/py/dietnb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`dietnb`는 `matplotlib` 그림을 자동으로 로컬 PNG 파일로 저장하고, Jupyter 노트북에는 해당 이미지를 가리키는 `<img>` 링크를 삽입합니다. 이를 통해 노트북 파일 내부에 base64 이미지 데이터가 포함되는 것을 방지하여 `.ipynb` 파일 크기를 획기적으로 줄여줍니다.

---

## 주요 특징

*   **노트북 용량 감소:** 이미지를 노트북 외부에 저장하여 `.ipynb` 파일을 작게 유지합니다. 이미지는 `{노트북 파일명_dietnb_imgs}` 경로에 저장됩니다. 해당 경로는 노트북 파일과 같은곳에 위치합니다.
*   **자동 정리:** 셀을 다시 실행하면, 이전에 해당 셀에서 생성된 이미지들을 자동으로 삭제합니다.
*   **수동 정리 기능:** `dietnb.clean_unused()` 함수를 호출하여 현재 커널 세션에서 더 이상 사용되지 않는 이미지 파일들을 정리할 수 있습니다.

## 설치

```bash
pip install dietnb
```

## 사용법

**1. 자동 활성화 (권장)**

설치 후, 터미널에서 다음 명령을 실행하세요 (가상 환경 사용 시 활성화된 상태여야 합니다):

```bash
dietnb install
```
그 다음, **Jupyter 커널을 재시작**해야 합니다. 재시작 후에는 모든 새 Jupyter 세션에서 `dietnb`가 자동으로 활성화됩니다.

**2. 수동 활성화 (노트북마다)**

노트북 상단에서 다음 코드 중 하나를 실행하세요:

```python
# 방법 A: 파이썬 코드
import dietnb
dietnb.activate()
```

```python
# 방법 B: IPython 매직 명령어
%load_ext dietnb
```

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