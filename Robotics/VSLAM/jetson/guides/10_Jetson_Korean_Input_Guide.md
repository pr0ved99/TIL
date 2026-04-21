# 10 Jetson Korean Input Guide

## 결론

- 현재 `Jetson`에는 `ibus`와 `im-config`는 이미 설치돼 있다.
- 지금 빠진 것은 `ibus-hangul`과 한국어 language pack이다.
- 즉, `ibus`를 다시 설치하기보다 `ibus-hangul` 중심으로 마무리하는 편이 맞다.

## 현재 확인 상태

- 설치됨: `ibus`, `im-config`, `fonts-noto-cjk`
- 미설치: `ibus-hangul`, `language-pack-ko`, `language-pack-gnome-ko`
- 현재 locale: `en_US.UTF-8`

## 1. 한글 입력 패키지 설치

```bash
sudo apt update
sudo apt install -y ibus-hangul language-pack-ko language-pack-gnome-ko
```

## 2. 입력기를 ibus로 고정

```bash
im-config -n ibus
```

## 3. 세션 다시 시작

아래 둘 중 하나:

```bash
ibus restart
```

또는

- 로그아웃 후 다시 로그인
- 그래도 안 보이면 재부팅

## 4. GUI에서 한국어 입력 소스 추가

`Settings -> Keyboard -> Input Sources -> + -> Korean -> Korean (Hangul)`

추가 후:

- 입력 전환: 보통 `Super + Space`
- 환경에 따라 `Hangul` 키나 `Alt_R`도 동작할 수 있다

## 5. 빠른 확인

브라우저나 VS Code에서 아래를 쳐본다.

```text
dkssudgktpdy
```

한글 입력기로 전환된 상태면 `안녕하세요`가 나와야 한다.

## 6. 메뉴까지 한국어로 바꾸고 싶을 때

지금은 입력만 필요하면 이 단계는 굳이 안 해도 된다.

전체 locale까지 바꾸고 싶으면:

```bash
sudo update-locale LANG=ko_KR.UTF-8 LANGUAGE=ko:en
```

주의:

- 이 명령은 시스템 메시지와 일부 UI 언어에도 영향을 준다.
- 개발 환경을 영어로 유지하고 싶으면 locale은 그대로 두고 입력기만 추가하는 편이 낫다.
