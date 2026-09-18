-- 로블록스 스튜디오 자동 설치 스크립트
-- 이 스크립트를 Command Bar에서 실행하여 자동으로 게임을 설정하세요

print("=== 샌즈 RNG 게임 자동 설치 시작 ===")

-- 서비스 가져오기
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")
local InsertService = game:GetService("InsertService")

-- 폴더 생성 함수
local function CreateFolder(parent, name)
    local folder = parent:FindFirstChild(name)
    if not folder then
        folder = Instance.new("Folder")
        folder.Name = name
        folder.Parent = parent
        print("폴더 생성: " .. name)
    else
        print("폴더 이미 존재: " .. name)
    end
    return folder
end

-- ModuleScript 생성 함수
local function CreateModuleScript(parent, name, source)
    local script = parent:FindFirstChild(name)
    if not script then
        script = Instance.new("ModuleScript")
        script.Name = name
        script.Parent = parent
        print("ModuleScript 생성: " .. name)
    else
        print("ModuleScript 이미 존재: " .. name)
    end
    
    -- 소스 코드 설정 (실제 파일 내용을 여기에 붙여넣어야 함)
    -- script.Source = [[-- 파일 내용 여기에]]
    
    return script
end

-- Script 생성 함수
local function CreateScript(parent, name, source)
    local script = parent:FindFirstChild(name)
    if not script then
        script = Instance.new("Script")
        script.Name = name
        script.Parent = parent
        print("Script 생성: " .. name)
    else
        print("Script 이미 존재: " .. name)
    end
    
    -- 소스 코드 설정
    -- script.Source = [[-- 파일 내용 여기에]]
    
    return script
end

-- LocalScript 생성 함수
local function CreateLocalScript(parent, name, source)
    local script = parent:FindFirstChild(name)
    if not script then
        script = Instance.new("LocalScript")
        script.Name = name
        script.Parent = parent
        print("LocalScript 생성: " .. name)
    else
        print("LocalScript 이미 존재: " .. name)
    end
    
    -- 소스 코드 설정
    -- script.Source = [[-- 파일 내용 여기에]]
    
    return script
end

-- 설치 과정
print("1. ReplicatedStorage 설정 시작")
local replicatedFolder = CreateFolder(ReplicatedStorage, "SansRNGGame")

print("2. ServerScriptService 설정 시작")
local serverFolder = CreateFolder(ServerScriptService, "SansRNGGame")

print("3. 스크립트 파일 생성 시작")

-- ReplicatedStorage에 배치할 파일
print("   - GameConfig.lua 생성")
CreateModuleScript(replicatedFolder, "GameConfig")

print("   - UISystem.lua 생성")
CreateLocalScript(replicatedFolder, "UISystem")

-- ServerScriptService에 배치할 파일
print("   - MainGameScript.lua 생성")
CreateScript(serverFolder, "MainGameScript")

print("   - WeaponSystem.lua 생성")
CreateScript(serverFolder, "WeaponSystem")

print("   - CurrencySystem.lua 생성")
CreateScript(serverFolder, "CurrencySystem")

print("   - InventorySystem.lua 생성")
CreateScript(serverFolder, "InventorySystem")

print("   - RaritySystem.lua 생성")
CreateModuleScript(serverFolder, "RaritySystem")

print("4. RemoteEvents/Functions 생성")

-- RemoteEvents
local sansCaughtEvent = Instance.new("RemoteEvent")
sansCaughtEvent.Name = "SansCaughtEvent"
sansCaughtEvent.Parent = ReplicatedStorage
print("   - SansCaughtEvent 생성")

local currencyChangedEvent = Instance.new("RemoteEvent")
currencyChangedEvent.Name = "CurrencyChangedEvent"
currencyChangedEvent.Parent = ReplicatedStorage
print("   - CurrencyChangedEvent 생성")

local inventoryChangedEvent = Instance.new("RemoteEvent")
inventoryChangedEvent.Name = "InventoryChangedEvent"
inventoryChangedEvent.Parent = ReplicatedStorage
print("   - InventoryChangedEvent 생성")

local compendiumChangedEvent = Instance.new("RemoteEvent")
compendiumChangedEvent.Name = "CompendiumChangedEvent"
compendiumChangedEvent.Parent = ReplicatedStorage
print("   - CompendiumChangedEvent 생성")

local openWeaponShopEvent = Instance.new("RemoteEvent")
openWeaponShopEvent.Name = "OpenWeaponShop"
openWeaponShopEvent.Parent = ReplicatedStorage
print("   - OpenWeaponShop 생성")

-- RemoteFunctions
local getCurrencyFunction = Instance.new("RemoteFunction")
getCurrencyFunction.Name = "GetCurrency"
getCurrencyFunction.Parent = ReplicatedStorage
print("   - GetCurrency 생성")

local getInventoryFunction = Instance.new("RemoteFunction")
getInventoryFunction.Name = "GetInventory"
getInventoryFunction.Parent = ReplicatedStorage
print("   - GetInventory 생성")

local getCompendiumFunction = Instance.new("RemoteFunction")
getCompendiumFunction.Name = "GetCompendium"
getCompendiumFunction.Parent = ReplicatedStorage
print("   - GetCompendium 생성")

local sellItemEvent = Instance.new("RemoteEvent")
sellItemEvent.Name = "SellItem"
sellItemEvent.Parent = ReplicatedStorage
print("   - SellItem 생성")

print("5. 맵 기본 설정")
local workspace = game:GetService("Workspace")

-- 바닥 생성
local floor = Instance.new("Part")
floor.Name = "GameFloor"
floor.Size = Vector3.new(200, 1, 200)
floor.Position = Vector3.new(0, 0, 0)
floor.Anchored = true
floor.Color = Color3.fromRGB(50, 50, 50)
floor.Material = Enum.Material.Slate
floor.Parent = workspace
print("   - 게임 바닥 생성")

-- 스폰 지역 표시
local spawnZone = Instance.new("Part")
spawnZone.Name = "SpawnZone"
spawnZone.Size = Vector3.new(200, 1, 200)
spawnZone.Position = Vector3.new(0, 0.5, 0)
spawnZone.Anchored = true
spawnZone.Transparency = 0.8
spawnZone.Color = Color3.fromRGB(100, 100, 100)
spawnZone.Parent = workspace
print("   - 스폰 지역 생성")

print("=== 자동 설치 완료 ===")
print("=== 다음 단계 ===")
print("1. 생성된 스크립트 파일들에 소스 코드를 붙여넣으세요.")
print("2. 각 스크립트의 속성을 확인하세요:")
print("   - GameConfig.lua: ModuleScript")
print("   - RaritySystem.lua: ModuleScript") 
print("   - 나머지: Script 또는 LocalScript")
print("3. 게임을 테스트하세요.")

print("설치 완료! 수고하셨습니다.")