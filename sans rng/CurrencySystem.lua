-- 재화 시스템 스크립트
local GameConfig = require(game.ReplicatedStorage.GameConfig)

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local DataStoreService = game:GetService("DataStoreService")

local CurrencySystem = {}
CurrencySystem.PlayerCurrencies = {}
CurrencySystem.CurrencyDataStore = DataStoreService:GetDataStore("PlayerCurrencies")

-- 재화 타입 정의
CurrencySystem.CURRENCY_TYPES = {
    {
        Name = "Gold",
        DisplayName = "골드",
        Icon = "rbxassetid://1234567890",
        StartingAmount = 100,
        MaxAmount = 999999999
    },
    {
        Name = "Gems",
        DisplayName = "보석",
        Icon = "rbxassetid://1234567891",
        StartingAmount = 0,
        MaxAmount = 999999
    },
    {
        Name = "Souls",
        DisplayName = "영혼",
        Icon = "rbxassetid://1234567892",
        StartingAmount = 0,
        MaxAmount = 99999
    }
}

-- 플레이어 재화 초기화
local function InitializePlayerCurrencies(player)
    if not CurrencySystem.PlayerCurrencies[player.UserId] then
        CurrencySystem.PlayerCurrencies[player.UserId] = {}
        
        -- 데이터 저장소에서 로드 시도
        local success, data = pcall(function()
            return CurrencySystem.CurrencyDataStore:GetAsync("Player_" .. player.UserId)
        end)
        
        if success and data then
            CurrencySystem.PlayerCurrencies[player.UserId] = data
        else
            -- 기본값 설정
            for _, currencyType in ipairs(CurrencySystem.CURRENCY_TYPES) do
                CurrencySystem.PlayerCurrencies[player.UserId][currencyType.Name] = currencyType.StartingAmount
            end
        end
        
        -- Leaderstats 업데이트
        UpdateLeaderstats(player)
    end
end

-- Leaderstats 업데이트
local function UpdateLeaderstats(player)
    local leaderstats = player:FindFirstChild("leaderstats")
    if not leaderstats then
        leaderstats = Instance.new("Folder")
        leaderstats.Name = "leaderstats"
        leaderstats.Parent = player
    end
    
    for _, currencyType in ipairs(CurrencySystem.CURRENCY_TYPES) do
        local currencyValue = leaderstats:FindFirstChild(currencyType.Name)
        if not currencyValue then
            currencyValue = Instance.new("IntValue")
            currencyValue.Name = currencyType.Name
            currencyValue.Parent = leaderstats
        end
        
        local currentAmount = CurrencySystem.PlayerCurrencies[player.UserId][currencyType.Name] or 0
        currencyValue.Value = currentAmount
    end
end

-- 재화 추가
function CurrencySystem.AddCurrency(player, currencyName, amount)
    if not CurrencySystem.PlayerCurrencies[player.UserId] then
        return false
    end
    
    local currentAmount = CurrencySystem.PlayerCurrencies[player.UserId][currencyName] or 0
    local currencyType = nil
    
    for _, type in ipairs(CurrencySystem.CURRENCY_TYPES) do
        if type.Name == currencyName then
            currencyType = type
            break
        end
    end
    
    if not currencyType then
        return false
    end
    
    local newAmount = math.min(currentAmount + amount, currencyType.MaxAmount)
    CurrencySystem.PlayerCurrencies[player.UserId][currencyName] = newAmount
    
    -- Leaderstats 업데이트
    UpdateLeaderstats(player)
    
    -- 이벤트 발생
    local currencyChangedEvent = ReplicatedStorage:FindFirstChild("CurrencyChangedEvent")
    if currencyChangedEvent then
        currencyChangedEvent:FireClient(player, {
            CurrencyName = currencyName,
            OldAmount = currentAmount,
            NewAmount = newAmount,
            Change = amount
        })
    end
    
    return true
end

-- 재화 차감
function CurrencySystem.RemoveCurrency(player, currencyName, amount)
    if not CurrencySystem.PlayerCurrencies[player.UserId] then
        return false
    end
    
    local currentAmount = CurrencySystem.PlayerCurrencies[player.UserId][currencyName] or 0
    
    if currentAmount < amount then
        return false -- 재화 부족
    end
    
    local newAmount = currentAmount - amount
    CurrencySystem.PlayerCurrencies[player.UserId][currencyName] = newAmount
    
    -- Leaderstats 업데이트
    UpdateLeaderstats(player)
    
    -- 이벤트 발생
    local currencyChangedEvent = ReplicatedStorage:FindFirstChild("CurrencyChangedEvent")
    if currencyChangedEvent then
        currencyChangedEvent:FireClient(player, {
            CurrencyName = currencyName,
            OldAmount = currentAmount,
            NewAmount = newAmount,
            Change = -amount
        })
    end
    
    return true
end

-- 재화 확인
function CurrencySystem.GetCurrency(player, currencyName)
    if not CurrencySystem.PlayerCurrencies[player.UserId] then
        return 0
    end
    
    return CurrencySystem.PlayerCurrencies[player.UserId][currencyName] or 0
end

-- 재화 교환
function CurrencySystem.ExchangeCurrency(player, fromCurrency, toCurrency, exchangeRate, amount)
    if not CurrencySystem.RemoveCurrency(player, fromCurrency, amount) then
        return false
    end
    
    local receivedAmount = math.floor(amount * exchangeRate)
    CurrencySystem.AddCurrency(player, toCurrency, receivedAmount)
    
    return true
end

-- 재화 저장
local function SavePlayerCurrencies(player)
    if not CurrencySystem.PlayerCurrencies[player.UserId] then
        return
    end
    
    local success, err = pcall(function()
        CurrencySystem.CurrencyDataStore:SetAsync("Player_" .. player.UserId, CurrencySystem.PlayerCurrencies[player.UserId])
    end)
    
    if not success then
        warn("재화 저장 실패: " .. err)
    end
end

-- 재화 시스템 초기화
local function InitializeCurrencySystem()
    -- RemoteEvent 생성
    local currencyChangedEvent = Instance.new("RemoteEvent")
    currencyChangedEvent.Name = "CurrencyChangedEvent"
    currencyChangedEvent.Parent = ReplicatedStorage
    
    -- 재화 요청 RemoteFunction
    local getCurrencyFunction = Instance.new("RemoteFunction")
    getCurrencyFunction.Name = "GetCurrency"
    getCurrencyFunction.Parent = ReplicatedStorage
    
    getCurrencyFunction.OnServerInvoke = function(player, currencyName)
        return CurrencySystem.GetCurrency(player, currencyName)
    end
    
    -- 플레이어 조인/리브 이벤트
    Players.PlayerAdded:Connect(function(player)
        InitializePlayerCurrencies(player)
    end)
    
    Players.PlayerRemoving:Connect(function(player)
        SavePlayerCurrencies(player)
        CurrencySystem.PlayerCurrencies[player.UserId] = nil
    end)
    
    -- 기존 플레이어 처리
    for _, player in ipairs(Players:GetPlayers()) do
        InitializePlayerCurrencies(player)
    end
    
    -- 자동 저장 (5분마다)
    spawn(function()
        while true do
            wait(300) -- 5분
            for _, player in ipairs(Players:GetPlayers()) do
                SavePlayerCurrencies(player)
            end
        end
    end)
end

InitializeCurrencySystem()

return CurrencySystem