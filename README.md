# titanic_streamlit

Seaborn 타이타닉 승객 표본으로 성별·객실 등급별 생존율을 분석하고, Streamlit에서 집계와 사실표를 확인합니다.

## 실행

```powershell
python -m pip install -r requirements.txt
python analyze.py
python -m streamlit run app.py
```

`analyze.py`는 `titanic.csv`를 읽어 `titanic_summary.pkl`과 `titanic_facts.md`를 만듭니다. 앱은 직접 생성한 PKL을 읽어 대시보드와 사실표를 표시합니다.

API 키 없이도 대시보드와 사실표 검색을 실습할 수 있습니다. 답변을 생성하려면 앱을 실행하기 전에 PowerShell에서 `$env:OPENAI_API_KEY = Read-Host "OpenAI API 키" -MaskInput`을 실행하세요.

[원본 데이터 · seaborn-data](https://github.com/mwaskom/seaborn-data/blob/master/titanic.csv)
