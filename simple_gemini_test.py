"""
Gemini API 기본 호출 예제
"""
import os
import google.generativeai as genai

def main():
    """
    Gemini API를 직접 호출하는 간단한 예제
    """
    # API 키 설정
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("환경 변수 'GOOGLE_API_KEY'가 설정되지 않았습니다.")
        api_key = input("Google Gemini API 키를 입력하세요: ")
    
    # API 구성
    genai.configure(api_key=api_key)
    
    # 사용 가능한 모델 목록 출력
    models = genai.list_models()
    print("\n사용 가능한 모델 목록:")
    for model in models:
        if "generateContent" in model.supported_generation_methods:
            print(f"- {model.name}")
    
    # 모델 선택
    model_name = "gemini-1.5-pro"
    model = genai.GenerativeModel(model_name=model_name)
    
    # 간단한 프롬프트로 테스트
    prompt = "한국어로 인공지능에 대해 간략하게 설명해줘"
    print(f"\n프롬프트: {prompt}")
    
    # 응답 생성
    response = model.generate_content(prompt)
    
    # 응답 출력
    print("\n응답:")
    print(response.text)
    
    # 채팅 기능 테스트
    print("\n\n채팅 기능 테스트:")
    chat = model.start_chat(history=[])
    
    # 첫 번째 메시지
    response = chat.send_message("안녕하세요! 당신은 누구인가요?")
    print("사용자: 안녕하세요! 당신은 누구인가요?")
    print(f"Gemini: {response.text}\n")
    
    # 두 번째 메시지
    response = chat.send_message("오늘 날씨가 어때요?")
    print("사용자: 오늘 날씨가 어때요?")
    print(f"Gemini: {response.text}")

if __name__ == "__main__":
    main()
