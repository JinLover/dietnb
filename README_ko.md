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
    # 방법 1: 파이썬 호출 (기본 폴더: 'dietnb_imgs' 또는 자동 감지된 노트북 이름 기반)
    import dietnb
    dietnb.activate()

    # 방법 1a: 파이썬 호출 (사용자 지정 폴더: 'MyProject_dietnb_imgs')
    # import dietnb
    # dietnb.activate(folder_prefix="MyProject")
    ```
    ```python
    # 방법 2: IPython 매직 명령어
    %load_ext dietnb
    ```

이제 준비되었습니다! 활성화 후에는 `plt.show()`를 사용하거나 셀 마지막에서 자동으로 표시되는 `matplotlib` 그림이 폴더에 저장되고, 출력에는 링크만 표시됩니다.
- 기본적으로 이 폴더는 노트북 실행 디렉토리 기준으로 `dietnb_imgs` 이거나, 자동 감지에 성공하면 노트북 파일명을 기반으로 생성됩니다.
- 만약 `dietnb.activate(folder_prefix="PREFIX")`를 사용하면, 이미지는 `PREFIX_dietnb_imgs` 폴더에 저장됩니다.

*(참고: 자동 활성화를 위한 `dietnb install` 명령어는 현재 버전에서 비활성화되었습니다.)*

## 작동 방식

**1. 자동 활성화 (`dietnb install` 사용)**

IPython/Jupyter 세션을 시작할 때마다 `dietnb`가 자동으로 활성화되기를 원한다면,
터미널에서 다음 명령어를 한 번 실행하세요:

```bash
dietnb install
```
그 다음, **Jupyter 커널을 재시작**하세요. `dietnb`는 모든 새 세션에서 활성화되어,
노트북별 폴더(예: `MyNotebook_dietnb_imgs`)에 이미지를 저장하려고 시도하거나,
노트북 경로를 결정할 수 없는 경우 `dietnb_imgs`로 대체됩니다.

**2. 수동 활성화 (노트북마다)**

특정 노트북에 대해서만 `dietnb`를 수동으로 활성화하거나 `folder_prefix` 옵션을 사용하고 싶다면,
노트북 상단에 다음 코드를 추가하세요:

```python
# 방법 A: 파이썬 코드
import dietnb

# 기본 동작으로 활성화 (폴더 이름 자동 감지 시도)
dietnb.activate()

# 또는, 특정 폴더 접두사로 활성화 (예: 'MyProject_dietnb_imgs' 용)
# dietnb.activate(folder_prefix="MyProject")
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

## 불필요한 이미지 정리

이전 셀 실행에서 생성되었거나 더 이상 현재 커널 상태에 연결되지 않은 이미지 파일을 삭제하려면 다음 함수를 호출할 수 있습니다:

```python
import dietnb

# 기본/자동 감지된 폴더 컨텍스트의 이미지 정리
dietnb.clean_unused()

# 특정 folder_prefix 컨텍스트의 이미지 정리
# dietnb.clean_unused(folder_prefix="MyProject")
```

이 함수는 관련된 이미지 디렉토리(`dietnb_imgs`, `[노트북명]_dietnb_imgs`, 또는 `[prefix]_dietnb_imgs`)를 스캔하여 현재 IPython 세션의 해당 컨텍스트에서 활성 셀 출력과 연결되지 않은 `.png` 파일을 삭제합니다.

## 라이선스

MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

---
[English README (영어 README)](README.md) 