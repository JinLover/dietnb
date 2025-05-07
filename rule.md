## 1. 빠른 사용

```bash
pip install dietnb                 # ➊ 설치
# dietnb install 은 비활성화됨
```

*각 노트북 시작 시 **수동으로 활성화**해야 합니다.*

> **수동 활성화 방법** — 노트북 시작 부분에 다음 중 하나 실행:
> ```python
> import dietnb
>
> # 기본 작동 (dietnb_imgs 또는 자동 감지된 폴더)
> dietnb.activate()
>
> # 또는, 특정 프로젝트/노트북용 폴더 지정 (예: MyProject_dietnb_imgs)
> # dietnb.activate(folder_prefix="MyProject")
> ```
> **또는**
> ```python
> %load_ext dietnb
> ``` 