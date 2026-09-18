-- 메인 게임 스크립트
local GameConfig = require(game.ReplicatedStorage.GameConfig)

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

-- 게임 상태 관리
local GameService = {}
GameService.ActiveSans = {}
GameService.PlayerData = {}

-- 플레이어 데이터 초기화
local function InitializePlayerData(player)
    if not GameService.PlayerData[player.UserId] then
        GameService.PlayerData[player.UserId] = {
            Gold = GameConfig.GAME_SETTINGS.StartingCurrency,
            Inventory = {},
            Compendium = {},
            CurrentWeapon = GameConfig.WEAPONS[1],
            TotalClicks = 0,
            TotalSansCaught = 0
        }
        
        -- Leaderstats 설정
        local leaderstats = Instance.new("Folder")
        leaderstats.Name = "leaderstats"
        leaderstats.Parent = player
        
        local gold = Instance.new("IntValue")
        gold.Name = "Gold"
        gold.Value = GameConfig.GAME_SETTINGS.StartingCurrency
        gold.Parent = leaderstats
        
        local sansCaught = Instance.new("IntValue")
        sansCaught.Name = "SansCaught"
        sansCaught.Value = 0
        sansCaught.Parent = leaderstats
    end
end

-- 랜덤 샌즈 타입 선택
local function GetRandomSansType()
    local random = math.random()
    local cumulativeRate = 0
    
    for _, sansType in ipairs(GameConfig.SANS_TYPES) do
        cumulativeRate = cumulativeRate + sansType.DropRate
        if random <= cumulativeRate then
            return sansType
        end
    end
    
    return GameConfig.SANS_TYPES[1] -- 기본값
end

-- 샌즈 모델 생성
local function CreateSansModel(sansType, spawnPosition)
    local sansModel = Instance.new("Model")
    sansModel.Name = sansType.Name
    
    -- 샌즈 바디
    local body = Instance.new("Part")
    body.Name = "Body"
    body.Size = Vector3.new(2, 3, 1)
    body.Color = sansType.Color
    body.Position = spawnPosition
    body.Anchored = false
    body.CanCollide = true
    body.Parent = sansModel
    
    -- 샌즈 머리
    local head = Instance.new("Part")
    head.Name = "Head"
    head.Size = Vector3.new(1.5, 1.5, 1)
    head.Color = Color3.fromRGB(255, 255, 255)
    head.Position = spawnPosition + Vector3.new(0, 2, 0)
    head.Anchored = false
    head.CanCollide = true
    head.Parent = sansModel
    
    -- 클릭 디텍터
    local clickDetector = Instance.new("ClickDetector")
    clickDetector.MaxActivationDistance = 10
    clickDetector.Parent = body
    
    -- 휴머노이드 설정
    local humanoid = Instance.new("Humanoid")
    humanoid.Health = sansType.Health
    humanoid.MaxHealth = sansType.Health
    humanoid.WalkSpeed = sansType.Speed
    humanoid.Parent = sansModel
    
    -- 데이터 저장
    sansModel:SetAttribute("SansType", sansType.Name)
    sansModel:SetAttribute("Rarity", sansType.Rarity)
    sansModel:SetAttribute("Health", sansType.Health)
    sansModel:SetAttribute("SellPrice", sansType.SellPrice)
    
    return sansModel
end

-- 샌즈 스폰
local function SpawnSans()
    if #GameService.ActiveSans >= GameConfig.GAME_SETTINGS.MaxSans then
        return
    end
    
    local sansType = GetRandomSansType()
    local mapSize = GameConfig.GAME_SETTINGS.MapSize
    
    -- 랜덤 위치 생성
    local spawnX = math.random(-mapSize, mapSize)
    local spawnZ = math.random(-mapSize, mapSize)
    local spawnPosition = Vector3.new(spawnX, 5, spawnZ)
    
    local sansModel = CreateSansModel(sansType, spawnPosition)
    sansModel.Parent = workspace
    
    table.insert(GameService.ActiveSans, sansModel)
    
    -- 이동 AI
    spawn(function()
        while sansModel and sansModel.Parent do
            wait(0.1)
            if sansModel:FindFirstChild("Humanoid") then
                local humanoid = sansModel.Humanoid
                local randomX = math.random(-mapSize, mapSize)
                local randomZ = math.random(-mapSize, mapSize)
                local targetPosition = Vector3.new(randomX, 5, randomZ)
                
                humanoid:MoveTo(targetPosition)
            end
        end
    end)
end

-- 샌즈 클릭 처리
local function OnSansClicked(sansModel, player)
    local sansType = sansModel:GetAttribute("SansType")
    local currentHealth = sansModel:GetAttribute("Health")
    local playerData = GameService.PlayerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local weapon = playerData.CurrentWeapon
    local damage = weapon.Damage
    
    -- 데미지 적용
    currentHealth = currentHealth - damage
    sansModel:SetAttribute("Health", currentHealth)
    
    -- 시각적 피드백
    if sansModel:FindFirstChild("Body") then
        sansModel.Body.Transparency = 0.5
        wait(0.1)
        sansModel.Body.Transparency = 0
    end
    
    -- 샌즈 처치
    if currentHealth <= 0 then
        local sellPrice = sansModel:GetAttribute("SellPrice")
        local rarity = sansModel:GetAttribute("Rarity")
        
        -- 재화 지급
        playerData.Gold = playerData.Gold + sellPrice
        player.leaderstats.Gold.Value = playerData.Gold
        
        -- 도감 등록
        if not playerData.Compendium[sansType] then
            playerData.Compendium[sansType] = {
                Name = sansType,
                Rarity = rarity,
                CaughtCount = 0
            }
        end
        playerData.Compendium[sansType].CaughtCount = playerData.Compendium[sansType].CaughtCount + 1
        
        -- 인벤토리에 추가
        table.insert(playerData.Inventory, {
            Name = sansType,
            Rarity = rarity,
            SellPrice = sellPrice
        })
        
        -- 통계 업데이트
        playerData.TotalSansCaught = playerData.TotalSansCaught + 1
        player.leaderstats.SansCaught.Value = playerData.TotalSansCaught
        
        -- 샌즈 제거
        sansModel:Destroy()
        
        -- 활성 샌즈 목록에서 제거
        for i, activeSans in ipairs(GameService.ActiveSans) do
            if activeSans == sansModel then
                table.remove(GameService.ActiveSans, i)
                break
            end
        end
        
        -- 처치 이벤트 발생
        local remoteEvent = ReplicatedStorage:FindFirstChild("SansCaughtEvent")
        if remoteEvent then
            remoteEvent:FireClient(player, {
                SansType = sansType,
                Rarity = rarity,
                GoldEarned = sellPrice
            })
        end
    end
end

-- 게임 초기화
local function InitializeGame()
    -- 플레이어 조인 이벤트
    Players.PlayerAdded:Connect(function(player)
        InitializePlayerData(player)
        
        player.CharacterAdded:Connect(function(character)
            -- 무기 장착
            local weapon = GameService.PlayerData[player.UserId].CurrentWeapon
            -- 무기 장착 로직 추가 필요
        end)
    end)
    
    -- 기존 플레이어 처리
    for _, player in ipairs(Players:GetPlayers()) do
        InitializePlayerData(player)
    end
    
    -- 샌즈 스폰 타이머
    spawn(function()
        while true do
            wait(GameConfig.GAME_SETTINGS.SpawnInterval)
            SpawnSans()
        end
    end)
    
    -- 클릭 이벤트 연결
    workspace.ChildAdded:Connect(function(child)
        if child:GetAttribute("SansType") then
            local clickDetector = child:FindFirstChild("Body", true):FindFirstChild("ClickDetector")
            if clickDetector then
                clickDetector.MouseClick:Connect(function(player)
                    OnSansClicked(child, player)
                end)
            end
        end
    end)
end

-- 게임 시작
InitializeGame()

return GameService