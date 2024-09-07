# finance-batch
1. git clone 을 받습니다. (필요시 구글 검색해서)
2. poetry 를 설치합니다. (개발가이드 참고)
3. pyenv 를 설치합니다. (구글 검색해서 설치)
4. pyenv 로 원하는 파이썬 버전 설치및 액티브 버전으로 지정  
   ```(명령어1-설치) pyenv install 3.11.9  ```
   ```(명령어2-지정) pyenv local 3.11.9```
6. (명령어-중요:프로젝트홈에서) poetry env use 3.11.9 로 poetry 가 이용할 버전을 지정합니다.
7. (명령어-중요:프로젝트홈에서) poetry shell 을 실행하여 가상환경을 실행합니다.
8. (명령어) poetry install 을 실행합니다.
9. (명령어) uvicorn app.main:start 를 실행합니다. (그리고 http://localhost:8000 접속)

VMware 로 테스트를 해보긴 했는데  
혹시 오류가 발견되면 알려주세요.

포인트:  
poetry shell 을 먼저 실행하여  
가상환경으로 진입한 후에 poetry install 을 실행합니다.
