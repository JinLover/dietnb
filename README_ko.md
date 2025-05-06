# `dietnb` (v0.1.1)

[![PyPI version](https://badge.fury.io/py/dietnb.svg)](https://badge.fury.io/py/dietnb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`dietnb`는 `matplotlib` 그림을 외부 PNG 파일로 자동 저장하고, Jupyter 노트북에는 `<img>` 링크로 삽입합니다. 이를 통해 base64 이미지 임베딩을 방지하여 `.ipynb` 파일 크기를 크게 줄입니다.

---

## 주요 기능

*   **노트북 용량 감소:** 이미지를 외부에 저장하여 `.ipynb` 파일을 작게 유지합니다.
*   **자동 작동:** 설치 및 최초 설정 후 백그라운드에서 자동으로 작동합니다.
*   **셀 기반 이름 규칙:** 이미지는 셀 ID 및 셀당 여러 그림에 대한 인덱스를 기반으로 이름이 지정됩니다.
*   **자동 정리:** 셀 재실행 시 해당 셀의 이전 이미지를 자동으로 삭제합니다.
*   **캐시 무효화:** 이미지 링크에 버전 쿼리를 사용하여 안정적인 업데이트를 보장합니다.
*   **수동 정리:** `dietnb.clean_unused()` 함수로 더 이상 참조되지 않는 이미지 파일을 제거합니다.

## 설치

```bash
pip install dietnb
```

## 사용법

**1. 자동 활성화 (권장)**

설치 후, 터미널에서 다음 명령을 실행하세요 (가상 환경을 사용 중이라면 활성화된 상태에서):

```bash
dietnb install
```
그 다음, **Jupyter 커널을 재시작**하세요. `dietnb`는 모든 새 세션에서 활성화됩니다.

**2. 수동 활성화 (노트북마다)**

노트북 시작 부분에 다음 중 하나를 추가하세요:

```python
# 방법 A: 파이썬 코드
import dietnb
dietnb.activate()
```

```python
# 방법 B: IPython 매직 명령어
%load_ext dietnb
```

**사용 예:**

활성화 후, 평소처럼 `matplotlib`을 사용하세요:

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x, y)
plt.title("사인파")
plt.show() # dietnb_imgs/ 폴더에 저장되고 링크로 표시됩니다.
```

그림은 노트북 옆의 `dietnb_imgs` 하위 디렉토리(기본값)에 저장됩니다.

## 미사용 이미지 정리

커널에서 더 이상 참조하지 않는 이미지 파일을 제거하려면:

```python
import dietnb
dietnb.clean_unused()
```

## 라이선스

MIT 라이선스. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

---
[English README (영어 README)](README.md) 