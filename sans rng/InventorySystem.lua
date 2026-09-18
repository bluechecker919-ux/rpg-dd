-- 도감/인벤토리 시스템 스크립트
local GameConfig = require(game.ReplicatedStorage.GameConfig)

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local DataStoreService = game:GetService("DataStoreService")

local InventorySystem = {}
InventorySystem.PlayerInventories = {}
InventorySystem.PlayerCompendiums = {}
InventorySystem.InventoryDataStore = DataStoreService:GetDataStore("PlayerInventories")
InventorySystem.CompendiumDataStore = DataStoreService:GetDataStore("PlayerCompendiums")

-- 인벤토리 슬롯 설정
InventorySystem.MAX_INVENTORY_SLOTS = 50
InventorySystem.MAX_COMPENDIUM_SLOTS = 100

-- 플레이어 인벤토리 초기화
local function InitializePlayerInventory(player)
    if not InventorySystem.PlayerInventories[player.UserId] then
        InventorySystem.PlayerInventories[player.UserId] = {
            Items = {},
            MaxSlots = InventorySystem.MAX_INVENTORY_SLOTS
        }
        
        -- 데이터 저장소에서 로드 시도
        local success, data = pcall(function()
            return InventorySystem.InventoryDataStore:GetAsync("Player_" .. player.UserId)
        end)
        
        if success and data then
            InventorySystem.PlayerInventories[player.UserId] = data
        end
    end
end

-- 플레이어 도감 초기화
local function InitializePlayerCompendium(player)
    if not InventorySystem.PlayerCompendiums[player.UserId] then
        InventorySystem.PlayerCompendiums[player.UserId] = {
            DiscoveredSans = {},
            CompletionPercentage = 0
        }
        
        -- 데이터 저장소에서 로드 시도
        local success, data = pcall(function()
            return InventorySystem.CompendiumDataStore:GetAsync("Player_" .. player.UserId)
        end)
        
        if success and data then
            InventorySystem.PlayerCompendiums[player.UserId] = data
        end
    end
end

-- 아이템 인벤토리에 추가
function InventorySystem.AddItem(player, itemData)
    local inventory = InventorySystem.PlayerInventories[player.UserId]
    if not inventory then
        return false, "인벤토리가 초기화되지 않았습니다"
    end
    
    if #inventory.Items >= inventory.MaxSlots then
        return false, "인벤토리가 가득 찼습니다"
    end
    
    -- 아이템 생성
    local newItem = {
        Name = itemData.Name,
        Rarity = itemData.Rarity,
        SellPrice = itemData.SellPrice,
        AcquiredTime = os.time(),
        UniqueID = game:GetService("HttpService"):GenerateGUID()
    }
    
    table.insert(inventory.Items, newItem)
    
    -- 이벤트 발생
    local inventoryEvent = ReplicatedStorage:FindFirstChild("InventoryChangedEvent")
    if inventoryEvent then
        inventoryEvent:FireClient(player, {
            Action = "Add",
            Item = newItem
        })
    end
    
    return true, newItem
end

-- 아이템 인벤토리에서 제거
function InventorySystem.RemoveItem(player, itemUniqueID)
    local inventory = InventorySystem.PlayerInventories[player.UserId]
    if not inventory then
        return false, "인벤토리가 초기화되지 않았습니다"
    end
    
    for i, item in ipairs(inventory.Items) do
        if item.UniqueID == itemUniqueID then
            local removedItem = table.remove(inventory.Items, i)
            
            -- 이벤트 발생
            local inventoryEvent = ReplicatedStorage:FindFirstChild("InventoryChangedEvent")
            if inventoryEvent then
                inventoryEvent:FireClient(player, {
                    Action = "Remove",
                    Item = removedItem
                })
            end
            
            return true, removedItem
        end
    end
    
    return false, "아이템을 찾을 수 없습니다"
end

-- 인벤토리 아이템 판매
function InventorySystem.SellItem(player, itemUniqueID)
    local inventory = InventorySystem.PlayerInventories[player.UserId]
    if not inventory then
        return false, "인벤토리가 초기화되지 않았습니다"
    end
    
    for i, item in ipairs(inventory.Items) do
        if item.UniqueID == itemUniqueID then
            local sellPrice = item.SellPrice
            
            -- 재화 추가 (CurrencySystem 사용 필요)
            local CurrencySystem = require(game.ServerScriptService.CurrencySystem)
            CurrencySystem.AddCurrency(player, "Gold", sellPrice)
            
            -- 아이템 제거
            local removedItem = table.remove(inventory.Items, i)
            
            -- 이벤트 발생
            local inventoryEvent = ReplicatedStorage:FindFirstChild("InventoryChangedEvent")
            if inventoryEvent then
                inventoryEvent:FireClient(player, {
                    Action = "Sell",
                    Item = removedItem,
                    GoldEarned = sellPrice
                })
            end
            
            return true, sellPrice
        end
    end
    
    return false, "아이템을 찾을 수 없습니다"
end

-- 도감에 샌즈 등록
function InventorySystem.RegisterToCompendium(player, sansType, rarity)
    local compendium = InventorySystem.PlayerCompendiums[player.UserId]
    if not compendium then
        return false, "도감이 초기화되지 않았습니다"
    end
    
    if not compendium.DiscoveredSans[sansType] then
        compendium.DiscoveredSans[sansType] = {
            Name = sansType,
            Rarity = rarity,
            FirstDiscoveredTime = os.time(),
            DiscoveryCount = 0
        }
    end
    
    compendium.DiscoveredSans[sansType].DiscoveryCount = compendium.DiscoveredSans[sansType].DiscoveryCount + 1
    
    -- 완성도 계산
    local totalSansTypes = #GameConfig.SANS_TYPES
    local discoveredCount = 0
    for _ in pairs(compendium.DiscoveredSans) do
        discoveredCount = discoveredCount + 1
    end
    compendium.CompletionPercentage = math.floor((discoveredCount / totalSansTypes) * 100)
    
    -- 이벤트 발생
    local compendiumEvent = ReplicatedStorage:FindFirstChild("CompendiumChangedEvent")
    if compendiumEvent then
        compendiumEvent:FireClient(player, {
            Action = "Register",
            SansType = sansType,
            Rarity = rarity,
            CompletionPercentage = compendium.CompletionPercentage
        })
    end
    
    return true, compendium.CompletionPercentage
end

-- 도감 정보 가져오기
function InventorySystem.GetCompendiumInfo(player)
    local compendium = InventorySystem.PlayerCompendiums[player.UserId]
    if not compendium then
        return nil
    end
    
    return {
        DiscoveredSans = compendium.DiscoveredSans,
        CompletionPercentage = compendium.CompletionPercentage,
        TotalSansTypes = #GameConfig.SANS_TYPES
    }
end

-- 인벤토리 정보 가져오기
function InventorySystem.GetInventoryInfo(player)
    local inventory = InventorySystem.PlayerInventories[player.UserId]
    if not inventory then
        return nil
    end
    
    return {
        Items = inventory.Items,
        MaxSlots = inventory.MaxSlots,
        UsedSlots = #inventory.Items
    }
end

-- 인벤토리 저장
local function SavePlayerInventory(player)
    if not InventorySystem.PlayerInventories[player.UserId] then
        return
    end
    
    local success, err = pcall(function()
        InventorySystem.InventoryDataStore:SetAsync("Player_" .. player.UserId, InventorySystem.PlayerInventories[player.UserId])
    end)
    
    if not success then
        warn("인벤토리 저장 실패: " .. err)
    end
end

-- 도감 저장
local function SavePlayerCompendium(player)
    if not InventorySystem.PlayerCompendiums[player.UserId] then
        return
    end
    
    local success, err = pcall(function()
        InventorySystem.CompendiumDataStore:SetAsync("Player_" .. player.UserId, InventorySystem.PlayerCompendiums[player.UserId])
    end)
    
    if not success then
        warn("도감 저장 실패: " .. err)
    end
end

-- 인벤토리 시스템 초기화
local function InitializeInventorySystem()
    -- RemoteEvent 생성
    local inventoryChangedEvent = Instance.new("RemoteEvent")
    inventoryChangedEvent.Name = "InventoryChangedEvent"
    inventoryChangedEvent.Parent = ReplicatedStorage
    
    local compendiumChangedEvent = Instance.new("RemoteEvent")
    compendiumChangedEvent.Name = "CompendiumChangedEvent"
    compendiumChangedEvent.Parent = ReplicatedStorage
    
    -- 인벤토리 요청 RemoteFunction
    local getInventoryFunction = Instance.new("RemoteFunction")
    getInventoryFunction.Name = "GetInventory"
    getInventoryFunction.Parent = ReplicatedStorage
    
    getInventoryFunction.OnServerInvoke = function(player)
        return InventorySystem.GetInventoryInfo(player)
    end
    
    -- 도감 요청 RemoteFunction
    local getCompendiumFunction = Instance.new("RemoteFunction")
    getCompendiumFunction.Name = "GetCompendium"
    getCompendiumFunction.Parent = ReplicatedStorage
    
    getCompendiumFunction.OnServerInvoke = function(player)
        return InventorySystem.GetCompendiumInfo(player)
    end
    
    -- 아이템 판매 RemoteEvent
    local sellItemEvent = Instance.new("RemoteEvent")
    sellItemEvent.Name = "SellItem"
    sellItemEvent.Parent = ReplicatedStorage
    
    sellItemEvent.OnServerEvent:Connect(function(player, itemUniqueID)
        local success, result = InventorySystem.SellItem(player, itemUniqueID)
        if not success then
            warn("아이템 판매 실패: " .. tostring(result))
        end
    end)
    
    -- 플레이어 조인/리브 이벤트
    Players.PlayerAdded:Connect(function(player)
        InitializePlayerInventory(player)
        InitializePlayerCompendium(player)
    end)
    
    Players.PlayerRemoving:Connect(function(player)
        SavePlayerInventory(player)
        SavePlayerCompendium(player)
        InventorySystem.PlayerInventories[player.UserId] = nil
        InventorySystem.PlayerCompendiums[player.UserId] = nil
    end)
    
    -- 기존 플레이어 처리
    for _, player in ipairs(Players:GetPlayers()) do
        InitializePlayerInventory(player)
        InitializePlayerCompendium(player)
    end
    
    -- 자동 저장 (5분마다)
    spawn(function()
        while true do
            wait(300) -- 5분
            for _, player in ipairs(Players:GetPlayers()) do
                SavePlayerInventory(player)
                SavePlayerCompendium(player)
            end
        end
    end)
end

InitializeInventorySystem()

return InventorySystem