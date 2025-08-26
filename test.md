
### 오건영 추천 책
산둥 수용소 : 이성적, 합리적인 사람들이 어떻게 환경에 따라 변화하는지를 보여줌
일본 현대사 : 일본 만화
사장학개론 : 
돈의 속성 : 

국고채 금리, 내일채움공제

---

## 2025.03.07
구글 아이콘
https://fonts.gstatic.com/s/i/materialicons/search/v5/24px.svg

https://lucide.dev/icons/

## 2025.03.02
### KT 라우터 포트 포워딩
https://triple-f-coding.tistory.com/19
1. 트래픽 관리 --> 포트 포워딩 설정
![[Pasted image 20250304211919.png]]
1. DHCP -> 고정 IP
2. 방화벽 고급 설정 : 인바운드 포트 열기

## 2025.02.28
LLaMA CPP 사용
https://avocadaon.tistory.com/**50**

## 2025.03.02

### 삭제 안되는 파일 삭제 방법
1. 안전 모드로 접속
2. 명령 프롬프트에서 아래 명령 실행
```
takeown /f "C:\Windows\System32\<파일 경로>"
icacls "C:\Windows\System32\<파일 경로>" /grant administrators:F
del "C:\Windows\System32\<파일 경로>"
```

### WSL 삭제 후 재 설치
https://velog.io/@telnturtle/%EC%9E%A1%EB%8B%B4-WSL-%EC%9E%AC%EC%84%A4%EC%B9%98%ED%95%98%EA%B8%B0

### WSL2로 업그레이드
https://wikidocs.net/206696
```
D:\dev>wsl --list
Linux용 Windows 하위 시스템 배포:
Ubuntu-22.04(기본값)

D:\dev>wsl --set-default-version 2
WSL 2와의 주요 차이점에 대한 자세한 내용은 https://aka.ms/wsl2를 참조하세요

작업을 완료했습니다.

D:\dev>wsl --set-version Ubuntu-22.04 2
WSL 2와의 주요 차이점에 대한 자세한 내용은 https://aka.ms/wsl2를 참조하세요

변환이 진행 중입니다. 이 작업은 몇 분 정도 걸릴 수 있습니다.

배포는 이미 요청된 버전입니다.
오류 코드: Wsl/Service/WSL_E_VM_MODE_INVALID_STATE

D:\dev>wsl --list --verbose
  NAME            STATE           VERSION
* Ubuntu-22.04    Stopped         2
```



---

## 2025.02.28
Redis 내용을 보는 프로그램
https://github.com/microsoftarchive/redis/releases

## 2025.02.24
### 잘못 보낸돈 되찾기
https://fins.kdic.or.kr/

### 복싱 밴드 묶는 방법
https://www.youtube.com/shorts/A1avKDWZ5JQ

### 회사 3분기 아트 사진
https://photos.google.com/share/AF1QipPkioHf4kwLqrVVsPz6mfoJGxCO1XVVm46_2rumI71IvnjXMIFHrHPS0hROGIqlkw?pli=1&key=NDMzR3JwMUFVVTh2SHFoNXV1TVdzZUpQNHhTdlRB

### kt 라우터
[Web발신]
[KT고객센터] KT 와이파이(공유기) 설정메뉴 접속방법 안내

안녕하세요.  고객님, KT입니다.

■ 홈허브(또는 WiFi Home)계열의 KT공유기와 유선 또는 무선으로 연결된 상태에서 접속하여 확인 가능

☞ 인터넷 바로가기(URL) 접속: http://172.30.1.254

■ 사용자 ID, 비밀번호, 보안문자 입력하여 로그인
- WiFi Home 계열 초기값 사용자 ID: ktuser, 비밀번호: homehub
- 홈허브 계열 초기값 사용자 ID: ktuser, 비밀번호: megaap

☞ 앱 간편문의: https://kt.com/9plf

☎ 전화문의: 고객센터 100

항상 KT와 함께해 주셔서 감사합니다.

[KT, 당신과_미래 사이에] 컨설턴트 윤정희 드림
### 나이 계산기
https://superkts.com/cal/man_age/20070903

### kt 품질 측정
![[Pasted image 20250224160136.png]]
![[Pasted image 20250224160332.png]]


---

-Windows에서 Diskpart 유틸리티를 사용하여 USB 드라이브의 숨겨진 파티션을 삭제할 수 있습니다. 먼저 'Windows + R'을 눌러 실행 창을 열고 'cmd'를 입력하여 명령 프롬프트를 관리자 권한으로 실행합니다. 'diskpart'를 입력하고 'list disk' 명령어로 디스크 목록을 확인한 후, USB 드라이브를 선택합니다. 'select disk X' (X는 USB 드라이브 번호) 명령어를 사용한 후 'list partition'으로 파티션 목록을 확인하고, 'select partition Y' (Y는 삭제할 파티션 번호) 명령어를 입력한 후 'delete partition'을 입력하여 파티션을 삭제합니다. [[EaseUS](https://www.easeus.co.kr/partition-manager-software/delete-a-partition-on-a-usb-drive-in-windows-10.html)]

🛠️ **EaseUS 파티션 마스터 사용**

-EaseUS 파티션 마스터와 같은 파티션 관리 도구를 사용하여 USB 드라이브의 파티션을 쉽게 삭제할 수 있습니다. 프로그램을 실행한 후, USB 드라이브의 파티션을 마우스 오른쪽 버튼으로 클릭하고 '삭제'를 선택합니다. '확인'을 클릭하여 선택한 파티션을 삭제하고, '작업 실행' 버튼을 클릭하여 변경 사항을 적용합니다. 이 도구는 사용하기 쉬우며, 다양한 디스크 관리 기능을 제공합니다. [[EaseUS](https://www.easeus.co.kr/partition-manager-software/delete-a-partition-on-a-usb-drive-in-windows-10.html)]

🔄 **Diskpart로 파티션 합치기**

-Diskpart를 사용하여 파티션을 합치려면, 먼저 삭제할 파티션을 선택하고 삭제한 후, 확장할 파티션을 선택하여 확장합니다. [[네이버 블로그](https://m.blog.naver.com/kangyh5/221965263828)]

1️⃣ **Step 1**: 명령 프롬프트 실행

-명령 프롬프트(cmd)를 관리자 권한으로 실행합니다. 'diskpart'를 입력하여 Diskpart 유틸리티를 시작합니다.

2️⃣ **Step 2**: 볼륨 선택 및 삭제

-'list volume' 명령어로 볼륨 목록을 확인하고, 'select volume X' (X는 삭제할 볼륨 번호) 명령어로 삭제할 볼륨을 선택합니다. 'delete volume' 명령어로 선택한 볼륨을 삭제하여 할당되지 않은 공간으로 만듭니다.

3️⃣ **Step 3**: 파티션 확장

-'list partition' 명령어로 파티션 목록을 확인하고, 'select partition Y' (Y는 확장할 파티션 번호) 명령어로 확장할 파티션을 선택합니다. 'extend' 명령어를 사용하여 선택한 파티션을 확장합니다. [[네이버 블로그](https://m.blog.naver.com/kangyh5/221965263828)]

📘 **참고**

-Diskpart를 사용하여 파티션을 합칠 때는 데이터 손실을 방지하기 위해 중요한 데이터를 백업하는 것이 좋습니다.






### 무료 포스터, 캠페인, 챌린지 저작 도구
https://www.canva.com/ko_kr/
https://www.miricanvas.com/


### 다이어리
업무용  https://sailors.co.kr/product/%EC%9B%8C%ED%81%AC%EB%A1%9C%EA%B7%B8-%ED%95%98%ED%94%84-%EB%8B%A4%EC%9D%B4%EC%96%B4%EB%A6%AC-ver4-%EB%8D%B0%EC%9D%BC%EB%A6%AC/78/?srsltid=AfmBOoofOutCdsUDcX_fTp88gjO38GQz21vKbBV_j89qkwq4KPsCkpzo

타임트래커 : https://www.timetracker.kr/shop_view/?idx=19


### 마크다운 에디터 (웹)
stackedit.io


---

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling

from datasets import DatasetDict

device_map = "cpu"
max_new_tokens = 64

def generate_response(prompt, model, tokenizer):
    tokenized_prompt = tokenizer([prompt], return_tensors='pt')
   , shape = [1, 261]

    generated_ids = model.generate(
        tokenized_prompt.input_ids,
        tokenizer=tokenizer,
        max_new_tokens=max_new_tokens)
    # shape = [1, 325] <= 261 + 64(max_new_token)
    # mddel.generate()로 생성된 'generated_ids'에는 prompt id도 포함되어 있으므로
    # 아래 로직을 통해서 prompt_ids(tokenized_prompt.input_ids)를 제거함
    # zip()을 통해서 [1,261]과 [1,325]를 [261], [325]로 바꿔서 리턴함
    # Stripping the input text from generated_ids
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(tokenized_prompt.input_ids, generated_ids)
    ]
    # shape = [64]

    # 인덱스 형태를 텍스트 형태로 변환함
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response

model = AutoModelForCausalLM.from_pretrained(
    path_pretrained_model,
    device_map=device_map
)

#Loading the tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    path_pretrained_model,
    device_map=device_map
)

dataset = DatasetDict.from_json({'train': path_json_dataset})

dataset = dataset.map(
    lambda x: tokenizer(x["text"], truncation=True, padding=True, max_length=512),
    batched=True,
    remove_columns=dataset["train"].column_names
    )
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False, return_tensors='pt')

training_args = TrainingArguments(
    output_dir = 'out',
    learning_rate=7e-4,
    do_train=True,
    do_eval=False,
    num_train_epochs=100,
    per_device_train_batch_size=4,
    use_cpu=True,
    save_strategy="no"
)

trainer = Trainer(model, train_dataset=dataset['train'], args=training_args, data_collator=data_collator)

trainer.train()
```



## 20241027


### 미국 주식 할 때 봐야할 사이트
https://youtube.com/shorts/DR77quEoA0w?si=TckoGGPNM_u_Vj0d

정현호 : https://youtube.com/shorts/qFXW3sbh_yw?si=LFEdN8-9mu75oOX9

## 20241026

### 한국어 LLM 리더 보드
https://huggingface.co/spaces/upstage/open-ko-llm-leaderboard
https://github.com/NomaDamas/awesome-korean-llm
https://huggingface.co/EleutherAI/polyglot-ko-3.8b

#### 일반적 파인튜닝 방법
https://blog.sionic.ai/finetuning_llama

##### DPO
https://devocean.sk.com/experts/techBoardDetail.do?ID=165903&boardType=experts


#### 한국어 LLM
##### KoVicuna
https://github.com/melodysdreamj/KoVicuna


각종 암호나 기록을 안드로이드 폰에서만 암호화해서 기록하는 안드로이드 앱을 cursor AI IDE에서 flutter를 가지고 만들려고 해.
 
[기능 목록]
- 암호화된 저장 내용 : 
	- 각종 웹사이트: 아이디, 암호, 설명 
	- 이메일 계정: 이메일 주소, 암호, 설명
	- 자주 까먹는 기록 : 주소, 여권번호 등
- 검색 : 
	- 각 암호는 웹사이트 이름이나 URL 등을 1글자 입력할 때마다 검색되어서 화면에 보여줘야 해. 
	- 검색된 목록 중에 하나를 선택하면 전체 정보가 보이면 돼.
- 암호화  : 
	- 모든 정보는 안드로이드 앱 내에 파일 또는 DB에 암호화 되어서 저장되어야 해.
	- 저장된 내용을 열었을 때, 사람이 이해할 수 없는 암호화된 내용이어야 해
- 백업  : 
	- 자신에 이메일 계정에 모든 저장된 암호를 바이너리 형태로 보낼 수 있어야 해.
	- 바이너리 파일을 암호화를 해제해서 볼 수 없어야 해
- 백업 복원 : 
	- 자신에 이메일에 저장된 파일을 다시 폰에 다운로드 받으면 그 파일로 데이터를 복원해야 해.
- 데이터 그룹화 :
	- 각 기록 내용은 태깅으로 그룹화가 가능해야 해.
	- 그룹명을 선택하면 해당 그룹에 속한 기록들이 보여야 해.
- 전체 작성 목록 조회 :
	- 로그인 후 보이는 메인 화면에서는 전체 내용이 보여야 해
	- 메인 화면에는 검색과 데이터 그룹을 필터링할 수 있는 기능이 있어야 해.
- 최초 앱 실행 시 "로그인" :
	- 로그인은 "지문 인식"으로 가능해야 해.
		- 최초 지문 등록 과정이 필요 해
	- 최초 앱 실행 시 로그인에 성공하면, 앱을 종료하기 전까지는 다시 로그인을 할 필요가 없엄.

[코드 생성 기준]
2. 코드 생성을 단계별로 자세히 설명해야 해. 
3. 코드가 실제로 실행되는지 검증을 한번씩 하면서 코드를 작성해야해.
4. 안드로이드 스튜디오를 사용해서 작성하는 방법은 단계별로 상세하게 설명하면서 최신 버전 기준으로 진행해야해.
5. 각 코드의 파일명과 위치도 알려주고  기존 코드 파일에서 어디에 추가해야 하는지 상세히 설명해야해.
6. 코드 생략없이 필요한 모든 코드를 전부 작성해야해.
7. 사용자 UI는 fancy하고 모던해야 해.


Visual Studio - develop Windows apps (Visual Studio Community 2022 17.11.5)
    X Visual Studio is missing necessary components. Please re-run the Visual Studio installer for the "Desktop
      development with C++" workload, and include these components:
        MSVC v142 - VS 2019 C++ x64/x86 build tools
         - If there are multiple build tool versions available, install the latest
        C++ CMake tools for Windows
        Windows 10 SDK



## 20241020

### RSS AI 기사들
https://news.google.com/rss/search?q=ai&hl=ko&gl=KR&ceid=KR:ko
https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml
https://www.techrepublic.com/rssfeeds/topic/artificial-intelligence/
https://techcrunch.com/tag/artificial-intelligence/feed/
https://www.reddit.com/r/artificial/.rss


## 20241019

키보드 : # archon AK47 59,000원    저소음 리니어, 저소음 넌클릭
https://www.youtube.com/watch?v=qkxGLr-tfA0


---

https:/![[Pasted image 20241019002241.png]]/www.youtube.com/watch?v=0D2NSR1rkkI
![[Pasted image 20241019000916.png]]
![[Pasted image 20241019000945.png]]
![[Pasted image 20241019001239.png]]
![[Pasted image 20241019001441.png]]
![[Pasted image 20241019001928.png]]
![[Pasted image 20241019002051.png]]
![[Pasted image 20241019002118.png]]
![[Pasted image 20241019002200.png]]
![[Pasted image 20241019002244.png]]
![[Pasted image 20241019002422.png]]
![[Pasted image 20241019002546.png]]


노트북 전원 완전히 끄기
https://m.post.naver.com/viewer/postView.naver?volumeNo=33978689&memberNo=50815841

바탕화면에 '바로가기' 를 만들고, '항목 위치 입력'에 아래 내용 입력
```
shutdown -s -t 0
```
1주일에 한번은 Shift 누르고 전원 > "다시 시작"을 눌러서 재부팅 후 아래 화면처럼 뜨면 "PC 끄기"를 실행한다.
![[Pasted image 20241019004114.png]]




---
> 꿀을 먹고 싶다면 꿀통을 발로 차지 마라
    => 비난은 사람을 기운 빠지게 한다


### 항공기 좌석 고르는 법
https://youtube.com/shorts/YpgxCDWJDdM?si=-2KqL1zYbkg4Eofx

seat guru 사이트에 항공편 입력

### 임차권 등기로 전세금 받기
https://youtube.com/shorts/5Xl-0rYEcFo?si=-GnWv8OJHgqB0Ob-

### 마인드맵
https://youtube.com/shorts/5Xl-0rYEcFo?si=-GnWv8OJHgqB0Ob-

### 실용적인 한국어 모델 3종
https://www.youtube.com/watch?v=eNxAgYBdJ2A

beomi/Llama-3-Open-Ko-8B-Instruct-preview

MLP-KTLim/llama3-Bllossom

Llama-3-Open-Ko-8B-Instruct



vscode에서 주피터노트북의 노트에 수식에 포함되어 있을 때 PDF 내보내기 시 에러가 나서 설치가 필요함 MiKTex 
https://miktex.org/download
https://github.com/jgm/pandoc/releases/tag/3.4
=> 결국 포기함
=> 그냥 html 파일로 저장 후에 다시 웹브라우저로 읽고, PDF로 저장하는 방식으로 해결



공부나 모의 시험 문제를 풀때 항상 스탑워치를 사용한다 (😀😀😀) 
해설집을 절대 보지 안는다.
꼭 봐야하면 첫줄만 봄.
집중력이 안되면, 최애 과목을 공부하면서 다시 집중력을 높임
인강듣고 나서 다시 정리하는 시간을 반드시 가진다
오답이 나오는 것을 좋아한다. 바로 오답노트에 정리한다.
휴식 시간을 반드시 지킨다.
https://www.youtube.com/watch?v=MRTQ-mCi2Mk


알고e즘: 밤샘 게임 꼴찌에서 1년만에 전교 5등(😀😀😀) #공부왕도
https://www.youtube.com/watch?v=80VxRM4caaI
* 국어/문학 공부법
* 모방하기

알고e즘: 대치동 사교육없이 1년만에 성적 수직 향상(😀) #공부왕도 
- http://youtube.com/watch?v=phEGlU2sUe0
* 중학교까지만 대치동 3-4개 학원 다님 -> 흥미없음
* 중학교 게임랭킹 1위
* 공부법 향상법과 수기를 봄 -> 학원 다니지 않고 혼자 공부하겠다고 선언
* 열심히만 했지만 성적 안좋음 -> 나를 아는 것 필요 -> 공부 느낀점 일기
	* 자신에 대한 격려의 글
	* 문제점 파악 -> 해결을 위한 방법/체크리스트 작성 -> 공부습관 변화
	* 아침 시간 100% 활용 + 공부 습관 형성

알고e즘: 아버지의 교육으로 전교 1등 달성(😀😀) #공부왕도 
- https://www.youtube.com/watch?v=rnksg3BMAPU
- 전국 모의학력고사 수석
- 수업시간
	- 선생님 내용 모두 필기: 포스트잇, 형광펜, 색깔 다른 볼펜 → 이미지화
	- 핵심 과목이 아닌 경우(윤리), 수업 시간 내 암기/이해하려고 함
- 아빠의 영향 - 연상 암기법 활용
	* 매일 숙제내고 아빠와 시험 → 토플, 한자
	* 영어 일기 매일 숙제 검사  → 못 쓴날은 이유를 설명해야 함 (충격 요법)
	* 첨부터 잘 따라오지는 않았음(공부 습관이 없어서) - 게임, 운동 마니아
* 수학 경시대회 준비 - 동아리
* 야간 자율학습 시간
	* 전에 집에서 잠깐 자기
	* 책에 있는 내용을 공책에 옮겨 적고 주말에 한번더 보기 (에빙하우스의 망각곡선)
* 수학
	* 새로운 공식이 나올때마다 그 공식이 나오는 과정을 증명해봄
	* 어려운 문제를 많이 풀었음 (쉬운 문제를 많이 푸는 것은 노동임)
		* 하루가 걸리더라도 어려운 문제를 더 푼다 (심화/고난이도 문제 위주)
		* 문제 하나 푸는데 1주일이 걸리기도 함 (답지를 최대한 안봄)
		* 어렵게 풀면, 오랫동안 기억에 남음

알고e즘 : 기적의 공부법 서울대 (수능, 😀) #공부왕도 
* 1학년 말 성적이 최저
* 그 이후 목표를 서울대로 잡음 → 주위에 알림
* 1등하는 친구를 따라해보기로 함.
	* 같은 문제집, 같은 문제를 풀면 그때로 따라함 → 친구 공부습관을 자기것으로
	* 공부 습관을 위해서 쉬운 수학 문제집을 선택해서 풀기 시작함
* 남보다 늦게 시작해서 더 많은 노력 필요했음
	* 재수/삼수까지 함
* 공부양을 2배로 늘림 


성공한 사람들의 시간 관리 비법(이지영 강사, 😀) #자기계발
https://www.youtube.com/watch?v=3GRt5XUKCPQ

아라미드 자켓 #쇼핑


플렉스 모니터암 : 14만원 #쇼핑

![[Pasted image 20240919181225.png]]![[Pasted image 20240919181552.png]]
![[Pasted image 20240919181817.png]]


GPT로 논문 쓰기
https://www.youtube.com/watch?v=M0epTSZwI8A


온누리 상품권 10% 할인 #쇼핑 
https://youtube.com/shorts/JSXKwdjmOfg?si=wgaLS-3VERR6rOPs

물신청 : 물풍선 앱 #쇼핑
=> 그렇게 싸지 않음

넷플릭스 싸게 : https://youtube.com/shorts/ZxLk4ddyylk?si=J_1vVcjqyQQLoRJo

napkin ai #GenAI서비스


---
![[Pasted image 20240920231554.png]]
![[Pasted image 20240920231642.png]]
![[Pasted image 20240920231744.png]]
![[Pasted image 20240920232127.png]]
![[Pasted image 20240920232214.png]]
379000원

![[Pasted image 20240920232852.png]]
간단한 설정으로 무선 출력
잉크 1개 출력 DCP-T426ㅉ : 블랙 5292wkd, 컬러 5000장 / 9900원
잉크 노즐 막힘, 셀프 노즐 청소함 (30일마다)
용지 150장 가능
https://www.youtube.com/watch?v=RRDMhD-BVQs
양면인쇄 지원안됨
199000원


![[Pasted image 20240920234004.png]]
자동 양면인쇄. 팩스 기능 없음
227,620원

![[Pasted image 20240920234532.png]]
팩스, 자동양면인쇄 기능 없음
239000원


![[Pasted image 20240921123703.png]]
또는 아래에서 확인 가능
https://www.myhome.go.kr/hws/portal/main/getMgtMainHubPage.do
=> 자가진단 해본 결과, 지원 가능 서비스 없음으로 나옴 (2024/09/21)



---

