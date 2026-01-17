​:rocket: DooM for AntigravitY: Final Blueprint
​:milky_way: 1. Project Identity
​Title: DooM for AntigravitY

​Concept: Classic Doom Resources + Quake Physics + Zero-G Mechanics.

​Platform: Linux / WSL (Windows Subsystem for Linux).

​Environment: GNOME Terminal / Windows Terminal (Recommended).

​Constraint:

​Zero-Dependency: Python 3.8+ Standard Library Only (No pygame, numpy, etc).

​Keyboard Only: No Mouse Support.

​ASCII Rendering: 100x40 Text Grid Resolution.

​Communication: 모든 대화는 한글로 진행한다.

​:open_file_folder: 2. Project File Structure
​의존성 제로 원칙을 지키며 모듈화를 극대화한 구조입니다.

DooM-AntigravitY/
├── assets/ # 외부 리소스
│ ├── DOOM.WAD # 오리지널 둠 WAD 파일 (Shareware or Full)
│ └── config.json # 사용자 설정 (키매핑, 감도, 사운드볼륨)
├── saves/ # 세이브 데이터
│ └── save_slot_1.json # 직렬화된 ECS 상태 덤프
├── src/ # 소스 코드
│ ├── init.py
│ ├── engine.py # 메인 루프 및 터미널 제어 (Entry Point)
│ ├── ecs/ # Entity Component System 코어
│ │ ├── world.py # 엔티티 매니저
│ │ └── components.py # 데이터 클래스 모음 (Pos, Vel, Stats…)
│ ├── systems/ # 게임 로직
│ │ ├── input_sys.py # termios 비차단 입력
│ │ ├── physics_sys.py # 중력, 관성, 충돌 처리
│ │ ├── render_sys.py # 레이캐스팅 및 아스키 버퍼링
│ │ ├── combat_sys.py # 투사체, 대미지, 파괴
│ │ └── sound_sys.py # aplay 프로세스 호출
│ └── utils/ # 유틸리티
│ ├── wad_loader.py # WAD 바이너리 파서 & Scaler
│ └── math_core.py # 삼각함수 및 벡터 연산
├── docs/ # 문서
│ └── GEMINI.md # 본 설계 문서
└── main.py # 실행 스크립트 (src.engine 호출)

​:building_construction: 3. ECS Architecture
​데이터(Component)와 로직(System)의 완벽한 분리.

​:puzzle_piece: Components (Data)
​Transform: x, y, z, angle (위치)

​Motion: vx, vy, vz (속도), ax, ay, az (가속도), friction (마찰계수)

​Body: radius, height (충돌 박스)

​Stats: hp, armor, ammo, fuel (생존 수치)

​PhysicsMode: NORMAL | ZERO_G | INVERTED (현재 적용된 물리 법칙)

​Render: sprite_char (스프라이트), texture_id (벽 텍스처)

​:gear: Systems (Logic)
​InputSystem: 키보드 입력을 가속도 벡터로 변환합니다.

​GravitySystem: PhysicsMode에 따라 중력 가속도(g)의 방향을 결정합니다.

​PhysicsSystem:

​위치를 업데이트합니다 (P = P + V).

​벽/천장/바닥 충돌을 처리합니다 (반사 벡터 계산).

​CombatSystem: 투사체 이동, 피격 판정 및 벽 파괴를 처리합니다.

​RenderSystem: 3D 뷰포트를 생성하고 HUD를 합성합니다.

​:video_game: 4. Gameplay Mechanics
​:joystick: Physics Modes (The Core)
​Normal Mode:

​g = -9.8. 바닥 마찰력 높음.

​Space 누를 시 부스트 상승.

​Zero-G Mode:

​g = 0. 마찰력 거의 없음(0.99).

​벽 충돌 시 튕겨 나감(Bounce). 360도 전방향 이동.

​Inverted Mode:

​g = +9.8. 천장이 바닥이 됨.

​렌더링 화면 상하 반전 (Upside Down).

​:person_running: Movement Tech
​Inertia: 즉시 멈추지 않고 미끄러지며, Shift 키로 달리기 시 관성이 증가합니다.

​Hovering: 부스트(Space) 키를 짧게 끊어 눌러 고도를 유지합니다.

​Wall Kick: 무중력 상태에서 벽을 차고 반대 방향으로 급가속합니다.

​:crossed_swords: Combat & Destruction
​Ballistics: 투사체 궤적이 중력 모드에 따라 휘어집니다 (직선/포물선/역포물선).

​Targeting: 우하단에서 발사하여 중앙 조준점으로 수렴합니다 (Parallax).

​Strategic Destruction: ‘약한 벽’ 파괴 시 통로 개척 및 파편(Debris) 생성.

​:desktop_computer: 5. Engine Specs
​:brick: WAD Integration (No Editor Needed)
​Binary Parsing: struct 모듈로 오리지널 WAD 직접 해석.

​Auto-Scaling: 맵 로딩 시 모든 섹터의 Ceiling Height에 x2.5 배율 적용.

​이유: 오리지널 둠 맵은 낮아서 부스트팩 사용 시 머리를 박기 때문.
​Texture Mapping: WAD의 텍스처 이름을 아스키 패턴(@%#…)으로 변환.

​:artist_palette: Rendering Pipeline
​Raycasting: DDA 알고리즘. 수직 시야각(Pitch) 대신 Z-Shearing(Y축 밀기) 기법 사용.

​Post-Processing:

​Shading: 거리별 10단계 명암 (ASCII_RAMP).

​View Flip: Inverted 모드 시 버퍼 배열 역순 출력.

​Double Buffering: 화면 깜빡임 제거를 위한 프레임 버퍼 스와핑.

​:speaker_high_volume: Sound
​Tech: Linux aplay (ALSA) 활용.

​Implementation: subprocess.Popen을 이용한 Non-blocking(비차단) 사운드 재생.

​:white_check_mark: 6. Development Roadmap (Sprint 1)
​1단계: 인프라 구축
​[ ] 100x40 터미널 강제 설정 및 더블 버퍼링 출력.

​[ ] ECS 기본 클래스(World, Entity) 구현.

​2단계: 렌더링 (The Eye)
​[ ] 더미 맵(Python List)을 이용한 레이캐스팅 구현.

​[ ] 2.5배 수직 스케일링 수식 적용 테스트.

​3단계: 물리 (The Body)
​[ ] termios 키보드 입력 처리.

​[ ] 관성 이동 및 부스트 물리 구현.

​[ ] 중력 반전 시 화면 뒤집기 테스트.

​:shield: 7. Design Principles & Safety
​1. 성능 최적화 (The Bottleneck)
​- math_core.py에서 sin, cos 값을 미리 계산된 Lookup Table(LUT)로 캐싱하여 레이캐스팅 연산 비용 절감.
​- 각 픽셀별 print 호출 대신, 프레임 전체를 하나의 문자열로 결합(join)하여 sys.stdout.write로 일괄 출력해 깜빡임 방지.

​2. 터미널 제어 (Input & Safety)
​- termios Raw 모드 사용 시, 에러 발생에 대비해 try...finally 블록으로 감싸 종료 시 반드시 Cooked 모드(원상복구) 보장.

​3. ECS와 3D 물리
​- Z-Shearing: 실제 3D Pitch 대신 렌더링 된 좌표를 위아래로 밀어 고개를 드는 효과 구현 (연산 효율 극대화).
​- PhysicsMode: 컴포넌트로 분리하여 ZERO_G 등 다양한 환경 전환 용이성 확보.


# 📅 Weekend Sprint: The Engine Awakening
> **Project:** DooM for AntigravitY  
> **Goal:** Create a "Playable Prototype" with Core Rendering, Physics, and Visual Feedback.  
> **Timeframe:** Weekend (Saturday - Sunday)

---

## 🛑 Phase 1: Foundation (기초 공사)
**목표:** 터미널을 게임 엔진처럼 제어하고, ECS 루프를 가동한다.

- [ ] **Terminal Setup (`engine.py`)**
    - [ ] `100x40` 크기로 터미널 리사이즈 강제 명령 전송.
    - [ ] 커서 숨김(`\033[?25l`) 및 Echo 끄기 설정.
    - [ ] `atexit` 모듈을 이용한 프로그램 종료 시 터미널 복구 로직.

- [ ] **Input Handling (`systems/input_sys.py`)**
    - [ ] `termios` & `tty` 모듈을 이용한 Raw Mode 진입.
    - [ ] 비차단(Non-blocking) `sys.stdin.read(1)` 구현.
    - [ ] `WASD` + `Space` + `Shift` 동시 입력 처리용 `KeyBuffer` 딕셔너리 구현.

- [ ] **ECS Core (`ecs/`)**
    - [ ] `World` 클래스: 엔티티 생성/삭제 및 ID 발급.
    - [ ] `Component` 데이터 클래스 정의 (`Transform`, `Motion`, `Stats`).

---

## 👁️ Phase 2: The Eye (렌더링 엔진)
**목표:** 3D 벽을 화면에 그리고, '하이브리드 쉐이딩'의 질감을 확인한다.

- [ ] **Double Buffering (`systems/render_sys.py`)**
    - [ ] 100x40 크기의 `ScreenBuffer` (2차원 리스트) 생성.
    - [ ] 이전 프레임과 비교 없이 통째로 덮어쓰는 `sys.stdout.write` 최적화.

- [ ] **Raycasting Core**
    - [ ] `DUMMY_MAP` (10x10 리스트) 기반의 DDA 알고리즘 구현.
    - [ ] **Vertical Scaling (x2.5)**: 벽 높이 계산 시 `wall_height * 2.5` 적용.

- [ ] **Hybrid Shading Implementation**
    - [ ] `assets/visual_assets.py`에 쉐이딩 테이블 정의.
        - `TEXTURE_CHARS` (질감용: `#`, `+`, `H`)
        - `BLOCK_CHARS` (양감용: `█`, `▓`, `▒`)
    - [ ] 거리(`dist`)와 벽 종류(`texture_id`)에 따른 문자 매핑 로직.
    - [ ] **Noise Dithering**: 경계값에서 난수 섞기 적용.

---

## 🏃 Phase 3: The Body (물리 엔진)
**목표:** 관성 이동을 느끼고, 중력 반전 시 화면이 뒤집히는지 확인한다.

- [ ] **Basic Movement (`systems/physics_sys.py`)**
    - [ ] 가속도(`acc`) → 속도(`vel`) → 위치(`pos`) 적분 로직.
    - [ ] **Friction (마찰력)**: 입력이 없을 때 속도가 서서히 `0`으로 수렴하는 관성 구현.

- [ ] **Gravity Modes**
    - [ ] `Normal Mode`: `vel_z`에 `-9.8 * dt` 적용. 바닥 충돌 처리.
    - [ ] `Zero-G Mode`: `vel_z` 중력 제거. 벽 충돌 시 속도 반전(Bounce).
    - [ ] `Inverted Mode`: `vel_z`에 `+9.8 * dt` 적용. 천장 충돌 처리.

- [ ] **Inverted Rendering**
    - [ ] 중력 반전 상태일 때 `ScreenBuffer`를 `reverse()` 하여 출력하는 로직 연결.

---

## 💀 Phase 4: The Feel (비주얼 피드백)
**목표:** 하드코어 얼굴과 샷건 애니메이션으로 타격감을 완성한다.

- [ ] **Big-Face HUD (`systems/ui_sys.py`)**
    - [ ] 높이 4줄짜리 아스키 얼굴 에셋(`assets/face_data.py`) 준비.
    - [ ] HUD 템플릿에 현재 `hp`에 맞는 얼굴 배열 합성(Blit).

- [ ] **Weapon Overlay (`systems/render_sys.py`)**
    - [ ] **Shotgun Asset**: Idle, Fire, Pump-Action(Down/Up) 아스키 아트 준비.
    - [ ] **Weapon State Machine**: `Input(Ctrl)` → `Fire` → `Reload` 상태 전이 로직.
    - [ ] 3D 렌더링 후 버퍼 우측 하단에 무기 레이어 합성 (공백 투명 처리).

---

## ✅ Checkpoints (성공 기준)
1.  **Friday Night**: 터미널에 `WASD` 입력 로그가 딜레이 없이 찍히는가?
2.  **Saturday Noon**: 아스키 벽이 보이고, 거리에 따라 질감(블록+문자)이 변하는가?
3.  **Saturday Night**: `Space`를 눌러 날아오르고, 중력을 반전시켰을 때 천장이 바닥이 되는가?
4.  **Sunday Final**: 샷건을 발사(`Ctrl`)하면 "쾅" 하는 모션과 함께 얼굴이 반응하는가?

# 🎨 Visual Polish & Advanced Rendering Specs

## 1. 흑백 vs 컬러 모드 렌더링 전략
### A. 블록 문자(Lighting) vs 특수 문자(Texture)
블록 문자(`█`, `▓`, `▒`)는 명암 표현에 유리하지만 텍스처 질감이 부족하여 '울펜슈타인 3D'처럼 매끈해 보일 수 있습니다. 둠 특유의 거친(Gritty) 느낌을 위해 거리에 따라 문자를 혼합합니다.

*   **Close (근거리)**: 텍스처 특징이 드러나는 문자 위주.
    *   벽돌: `I`, `[`, `]`, `#`
    *   기계: `+`, `=`, `-`, `%`
*   **Mid (중거리)**: 블록 문자(`▓`, `▒`)를 섞어 덩어리감 표현.
*   **Far (원거리)**: 흐린 블록(`░`)이나 점(`.`)으로 거리감 표현.

**[렌더링 예시 비교]**
```text
(1) Plain Block (Too Clean)
████████████
▓▓▓▓▓▓▓▓▓▓▓▓
▒▒▒▒▒▒▒▒▒▒▒▒

(2) Doom Style Mix (Gritty)
##|##|##|##|  <-- Close: Texture details
▓▓#▓▓|▓▓#▓▓|  <-- Mid: Noise + Block
▒▒▒▒▒▒▒▒▒▒▒▒  <-- Far: Darker
```

### B. 노이즈 디더링 (Noise Dithering)
거리 단계 사이의 급격한 변화를 막고 모자이크 질감을 주기 위해 확률적으로 문자를 섞습니다.

```python
if distance < 2.0:
    char = random.choice(["#", "|", "H"])
elif distance < 4.0:
    char = "█"
elif distance < 6.0:
    # 30% 확률로 더 어두운 문자 섞기
    char = "▓" if random.random() > 0.3 else "▒"
else:
    char = "░"
```

## 2. ANSI Color System (The Atmosphere)
형태보다 중요한 것은 **색감**입니다. xterm-256color를 적극 활용합니다.

### Palette Strategy
*   **Brown Strings (ANSI 94)**: 흙탕물, 녹슨 금속 (STARAN3).
*   **Slime Green (ANSI 46/118)**: 독극물, 방사능 바닥.
*   **Concrete Grey (ANSI 248)**: 차가운 기계벽 (TEKWALL).
*   **Blood Red (ANSI 196)**: 피, 용암, 사망 시 화면 점멸.

**[Color Map CSV Structure]**
소스 코드 수정 없이 색감을 튜닝하기 위해 `color_map.csv`를 도입합니다.
| tile_char | ansi_code | description |
| :--- | :--- | :--- |
| # | 94 | Brown Wall Base |
| * | 160 | Explosion Red |

## 3. Hardcore Big-Face HUD
높이 4줄의 대형 아스키 아트를 사용하여 플레이어의 상태를 직관적으로 전달합니다.

### Face States
1.  **Healthy (100-80%)**: 단호함. `[===]`
2.  **Pissed (79-60%)**: 찌푸림. `[---]`
3.  **Bleeding (59-40%)**: 코피 흘림. `,,###,,`
4.  **Messy (39-20%)**: 눈탱이 밤탱이. 한쪽 눈 부음 `o`.
5.  **Critical (19-0%)**: 피칠갑. 식별 불가. (ANSI Red 필수).
6.  **Evil Grin**: 무기 획득/학살 시. `[wWw]`

### Layout Strategy
```text
+------------------------------------------------------------------+
|  AMMO   |  HEALTH  |    .-------.     |  ARMOR   |   KEYS    |
|   042   |   086%   |   /  _   _  \    |   100%   |   [R]     |
|  SHELLS |  NORMAL  |   |  ■ | ■  |    |  SHIELD  |    B      |
|         |          |   \  [===]  /    |          |    Y      |
+------------------------------------------------------------------+
```

## 4. Weapon Overlay & Animation
3D 뷰포트 위에 합성되는 2D 레이어로, '움직임'이 핵심입니다.

*   **Chainsaw**: 아이들 상태에서 톱날 문자(`~`, `-`, `=`)가 진동. 발사 시 Zoom-In.
*   **Shotgun**: 우측 하단에서 중앙으로 뻗는 사선 디자인. 발사 시 **Muzzle Flash**(`*` 섬광) + **Recoil**(총 들림).
*   **Rocket Launcher**: 발사 시 포구 연기(`@`) + 화면 전체 반동(Kickback).

## 5. Visual Effects (VFX) & Fog
### VFX
*   **Muzzle Flash**: 발사 순간 화면 전체 명도 높임.
*   **Damage Flash**: 피격 시 ANSI Red 배경으로 1프레임 점멸.
*   **Gravity Flip**: 중력 반전 시 렌더링 버퍼 `reverse()`로 즉시 상하 반전.

### Fog System: Red Mist (The Hell Atmosphere)
지옥의 붉은 안개를 표현하기 위해 바닥(Floor) 렌더링을 완전히 교체합니다.

1.  **안개 타일링 (Fog Tiling)**
    *   바닥을 면으로 채우지 않고, 흐릿한 아스키 문자(`.` `,` `~`)를 무작위로 섞어서 배치합니다.
2.  **Living Fog (Animation)**
    *   **Noise Effect**: 매 프레임마다 안개 타일의 위치를 조금씩 흔들거나(Jitter) 문자를 교체하여, 바닥에서 독기가 피어오르는 듯한 애니메이션을 구현합니다.
3.  **Color Gradient (Depth)**
    *   **Near**: Bright Red. 농도가 짙음.
    *   **Far**: Dark Red / Black. 어둠 속으로 페이드 아웃.
4.  **Implementation Logic**
    *   `RenderSystem`에서 벽을 그리고 남은 하단 영역을 `Floor Segment`로 인식.
    *   해당 영역에 Loop를 돌며 `Red Mist` 렌더링 함수를 호출.
