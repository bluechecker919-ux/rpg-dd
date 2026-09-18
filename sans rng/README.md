# 로블록스 샌즈 RNG 게임 설치 가이드

## 게임 개요
샌즈들이 돌아다니는 것을 무기나 클릭으로 잡아서 재화와 도감을 채우는 RNG 게임입니다.

## 파일 구조
```
roblox_sans_rng/
├── GameConfig.lua           # 게임 설정 (샌즈 타입, 무기, 게임 설정)
├── MainGameScript.lua       # 메인 게임 스크립트 (샌즈 스폰 시스템)
├── WeaponSystem.lua         # 무기 시스템
├── CurrencySystem.lua       # 재화 시스템
├── InventorySystem.lua      # 인벤토리/도감 시스템
├── RaritySystem.lua        # 희귀도 시스템
├── UISystem.lua             # UI 시스템 (클라이언트)
└── README.md                # 설치 가이드
```

## 설치 단계

### 1. 로블록스 스튜디오에서 새 프로젝트 생성
1. 로블록스 스튜디오를 열고 새 게임을 생성합니다.
2. 게임 이름을 "Sans RNG Game"으로 설정합니다.

### 2. 스크립트 파일 배치

#### ReplicatedStorage 설정
1. Explorer에서 `ReplicatedStorage`를 찾습니다.
2. 다음 스크립트를 `ReplicatedStorage`에 배치합니다:
   - `GameConfig.lua` (ModuleScript)
   - `UISystem.lua` (LocalScript)

#### ServerScriptService 설정
1. Explorer에서 `ServerScriptService`를 찾습니다.
2. 다음 스크립트를 `ServerScriptService`에 배치합니다:
   - `MainGameScript.lua` (Script)
   - `WeaponSystem.lua` (Script)
   - `CurrencySystem.lua` (Script)
   - `InventorySystem.lua` (Script)
   - `RaritySystem.lua` (ModuleScript)

### 3. 스크립트 유형 설정
각 파일의 유형을 올바르게 설정해야 합니다:

- **ModuleScript**: `GameConfig.lua`, `RaritySystem.lua`
- **Script**: `MainGameScript.lua`, `WeaponSystem.lua`, `CurrencySystem.lua`, `InventorySystem.lua`
- **LocalScript**: `UISystem.lua`

### 4. 맵 설정
1. `Workspace`에 기본 맵을 생성합니다.
2. 바닥을 만들어 샌즈들이 이동할 수 있게 합니다.
3. 스폰 영역을 설정합니다 (기본 설정: 100x100 크기).

### 5. API 서비스 활성화
1. Game Settings에서 API Services를 활성화합니다.
2. DataStoreService가 작동하도록 설정합니다.

### 6. 게임 테스트
1. Play 버튼을 눌러 게임을 테스트합니다.
2. 샌즈들이 올바르게 스폰되는지 확인합니다.
3. 클릭/공격 시스템이 작동하는지 확인합니다.
4. UI가 올바르게 표시되는지 확인합니다.

## 게임 기능

### 샌즈 타입
- **기본 샌즈** (Common): 40% 드롭률, 10 Gold
- **파란 샌즈** (Uncommon): 30% 드롭률, 25 Gold
- **오렌지 샌즈** (Rare): 15% 드롭률, 50 Gold
- **보라 샌즈** (Epic): 10% 드롭률, 100 Gold
- **레전드 샌즈** (Legendary): 4% 드롭률, 250 Gold
- **미스틱 샌즈** (Mythic): 1% 드롭률, 500 Gold

### 무기 시스템
- **기본 뼈다귀**: 1 데미지, 무료
- **강화 뼈다귀**: 2 데미지, 100 Gold
- **Gaster Blaster**: 5 데미지, 500 Gold
- **DETERMINATION Sword**: 10 데미지, 1000 Gold

### 재화 시스템
- **Gold**: 기본 재화
- **Gems**: 프리미엄 재화
- **Souls**: 특수 재화

### UI 기능
- **메인 HUD**: 재화 및 통계 표시
- **인벤토리**: 획득한 아이템 관리
- **도감**: 발견한 샌즈 종류 확인
- **상점**: 무기 구매

## 커스터마이징

### 샌즈 설정 수정
`GameConfig.lua`에서 `SANS_TYPES`를 수정하여 샌즈 속성을 변경할 수 있습니다.

### 무기 추가
`GameConfig.lua`에서 `WEAPONS` 배열에 새 무기를 추가할 수 있습니다.

### 게임 설정 변경
`GameConfig.lua`에서 `GAME_SETTINGS`를 수정하여:
- 스폰 간격
- 최대 샌즈 수
- 맵 크기
- 시작 재화

를 변경할 수 있습니다.

## 문제 해결

### 스크립트가 작동하지 않을 때
1. 스크립트 유형이 올바른지 확인합니다.
2. `require` 경로가 올바른지 확인합니다.
3. Output 창에서 에러 메시지를 확인합니다.

### 데이터가 저장되지 않을 때
1. API Services가 활성화되어 있는지 확인합니다.
2. DataStoreService 권한이 있는지 확인합니다.
3. 인터넷 연결이 안정적인지 확인합니다.

### UI가 표시되지 않을 때
1. `UISystem.lua`가 LocalScript인지 확인합니다.
2. StarterGui에 올바르게 배치되었는지 확인합니다.
3. ReplicatedStorage에 있는지 확인합니다.

## 추가 기능 구현 아이디어

1. **멀티플레이어 기능**: 다른 플레이어와 협동 또는 경쟁
2. **보스 시스템**: 정기적으로 강력한 보스 샌즈 등장
3. **퀘스트 시스템**: 일일 퀘스트 및 업적
4. **펫 시스템**: 샌즈를 펫으로 키우기
5. **랭킹 시스템**: 플레이어 랭킹 및 리더보드

## 주의사항
- 게임을 퍼블리시하기 전에 모든 기능을 테스트하세요.
- 데이터 저장소는 로블록스 서버에서만 작동합니다.
- Studio 모드에서는 일부 기능이 제한될 수 있습니다.

## 지원
문제가 발생하면 로블록스 스튜디오의 Output 창을 확인하여 에러 메시지를 확인하세요.