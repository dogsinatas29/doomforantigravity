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

