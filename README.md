# DooM for AntigravitY

[![Platform](https://img.shields.io/badge/platform-Linux%20%2F%20WSL-orange.svg)](https://wsl.dev)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

# ⚡ Core Principle: Simplicity

> **Simple != Easy**
>
> We prioritize **Simplicity** above all else. This implies the **Single Responsibility Principle**: *One module, one job.* This is the bedrock of our ECS architecture.
>
> **단순함 ≠ 쉬움**
>
> 우리는 **단순함(Simple)**을 최우선으로 둡니다. 이는 **단일 책임 원칙(One module, one job)**을 의미하며, 하나의 모듈은 오직 하나의 역할만 수행해야 합니다. 이것이 우리 ECS 아키텍처의 기반입니다.

---

**DooM for AntigravitY** is a high-performance ASCII 3D game engine that blends classic Doom resources with Quake-inspired physics and zero-gravity mechanics. Built entirely with the Python standard library, it brings a retro-futuristic combat experience to the terminal.

**DooM for AntigravitY**는 클래식 둠 리소스, 퀘이크 스타일의 물리 엔진, 그리고 무중력 메커니즘을 결합한 고성능 ASCII 3D 게임 엔진입니다. 파이썬 표준 라이브러리만을 사용하여 터미널 환경에서 레트로 퓨처리즘 전투 경험을 선사합니다.

---

## 🚀 Overview | 개요

- **Procedural Texture Generation**: WAD 파일의 텍스처 이름을 분석하여 아스키 패턴을 실시간 생성 (Matrix Style).
- **Scanline Rendering**: 바닥에 가로줄 스캔라인을 적용하여 속도감과 투시도 구현.
- **Raycasting with Physics**: 그리드 기반 충돌 및 물리 엔진과 연동된 3D 뷰.
- **Core Concept**: Classic Doom Resources + Quake Physics + Zero-G Mechanics.
- **Rendering**: 100x40 ASCII Text Grid with DDA Raycasting.
- **Constraints**: Zero-dependency (Python Standard Library only), Keyboard only.
- **Physics**: Real-time inertia, gravity inversion, and wall-kicking in zero-G.

- **핵심 컨셉**: 클래식 둠 리소스 + 퀘이크 물리 + 무중력 메커니즘.
- **렌더링**: DDA 레이캐스팅 기반 100x40 ASCII 텍스트 그리드.
- **제약 사항**: 의존성 제로 (파이썬 표준 라이브러리만 사용), 키보드 전용 조작.
- **물리**: 실시간 관성, 중력 반전, 무중력 상태에서의 벽 차기(Wall Kick).

---

## 🎯 Goals | 목표

1.  **Pure Python Architecture**: Demonstrate high-performance 3D rendering without external libraries like Pygame or NumPy.
    - **순수 파이썬 아키텍처**: Pygame이나 NumPy 없이 순수 파이썬만으로 고성능 3D 렌더링 구현.
2.  **Immersive ASCII Experience**: Implement advanced shading, Z-Shearing (pitch), and perspective-correct projection in a text-based viewport.
    - **몰입감 넘치는 ASCII 경험**: 텍스트 뷰포트에서의 고급 쉐이딩, Z-Shearing(상하 시야), 원근 교정 투영법 구현.
3.  **WAD Integration**: Directly parse and rasterize original Doom WAD files into the ECS grid map.
    - **WAD 통합**: 오리지널 둠 WAD 파일을 직접 파싱하고 ECS 그리드 맵으로 래스터화.
4.  **Advanced Physics**: Create a unique gameplay feel through gravity manipulation and momentum-based movement.
    - **고급 물리**: 중력 조작과 가속도 기반 이동을 통해 독특한 게임플레이 타격감 조성.

---

## 🗺️ Roadmap | 작업 계획

### ✅ Sprint 1: Infrastructure (Completed)
- [x] 100x40 Terminal double buffering system.
- [x] ECS Core (World, Entity, Components).
- [x] Basic Raycasting & Keyboard input handling.

### ✅ Sprint 2: WAD & Rendering (Completed)
- [x] Binary WAD parser (VERTEXES, LINEDEFS, THINGS).
- [x] Map Rasterization using Bresenham's algorithm.
- [x] Perspective-correct DDA rendering & Scale optimization (0.2x).
- [x] Git repository initialization and project structuring.

### 🛠️ Sprint 3: Combat & Polish (InProgress)
- [ ] Combat System: Projectiles & collision detection.
- [ ] Sound System: Linux `aplay` integration for non-blocking sfx.
- [ ] UI/HUD: Health, ammo, and gravity mode display.
- [ ] Strategic Destruction: Destructible walls and debris.

---

## 🕹️ Controls | 조작법

| Key | Action | 설명 |
| :--- | :--- | :--- |
| **W / S** | Move Forward / Backward | 전진 / 후진 |
| **A / D** | Strafe Left / Right | 좌측 / 우측 평행 이동 |
| **Q / E** | Rotate Left / Right | 시야 좌우 회전 |
| **R / F** | Look Up / Down | 시야 상하 조절 (Z-Shearing) |
| **Space** | Boost / Jump | 부스트 상승 (점프) |
| **1 / 2 / 3** | Normal / Zero-G / Inverted | 물리 모드 변경 |
| **X / Ctrl+C** | Quit Game | 게임 종료 |

---

## 🛠️ How to Run | 실행 방법

```bash
# 1. Generate the test level WAD
python3 generate_test_wad.py

# 2. Start the game
python3 main.py
```

---

## 🛠️ Development Environment | 개발 환경

- **Style**: **100% Vibe Coding**
- **AI Models**: **GEMINI 3 / GEMINI 2.5**
- **Tools**: **GEMINI Cli / Antigravity**

- **작업 방식**: **100% 바이브 코딩 (Vibe Coding)**
- **사용 AI**: **GEMINI 3 / GEMINI 2.5**
- **작업 도구**: **GEMINI Cli / Antigravity**

---

## 📄 License | 라이선스

This project is licensed under the **MIT License**.
이 프로젝트는 **MIT 라이선스**에 따라 배포됩니다.

Copyright (c) 2026 Antigravity AI Team.
