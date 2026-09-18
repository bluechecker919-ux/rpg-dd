-- UI 시스템 스크립트 (클라이언트 사이드)
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local Player = Players.LocalPlayer
local PlayerGui = Player:WaitForChild("PlayerGui")

local UISystem = {}

-- 색상 설정
local RARITY_COLORS = {
    Common = Color3.fromRGB(128, 128, 128),
    Uncommon = Color3.fromRGB(0, 255, 0),
    Rare = Color3.fromRGB(0, 100, 255),
    Epic = Color3.fromRGB(128, 0, 128),
    Legendary = Color3.fromRGB(255, 215, 0),
    Mythic = Color3.fromRGB(255, 0, 100)
}

-- 메인 HUD 생성
local function CreateMainHUD()
    local screenGui = Instance.new("ScreenGui")
    screenGui.Name = "MainHUD"
    screenGui.ResetOnSpawn = false
    screenGui.Parent = PlayerGui
    
    -- 상단 정보바
    local topBar = Instance.new("Frame")
    topBar.Name = "TopBar"
    topBar.Size = UDim2.new(1, 0, 0, 50)
    topBar.Position = UDim2.new(0, 0, 0, 0)
    topBar.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
    topBar.Parent = screenGui
    
    -- 골드 표시
    local goldFrame = Instance.new("Frame")
    goldFrame.Name = "GoldFrame"
    goldFrame.Size = UDim2.new(0, 150, 0, 40)
    goldFrame.Position = UDim2.new(0, 10, 0, 5)
    goldFrame.BackgroundColor3 = Color3.fromRGB(50, 50, 50)
    goldFrame.Parent = topBar
    
    local goldLabel = Instance.new("TextLabel")
    goldLabel.Name = "GoldLabel"
    goldLabel.Size = UDim2.new(1, 0, 1, 0)
    goldLabel.BackgroundTransparency = 1
    goldLabel.TextColor3 = Color3.fromRGB(255, 215, 0)
    goldLabel.Text = "Gold: 0"
    goldLabel.TextSize = 18
    goldLabel.Font = Enum.Font.Bold
    goldLabel.Parent = goldFrame
    
    -- 샌즈 처치 수 표시
    local sansFrame = Instance.new("Frame")
    sansFrame.Name = "SansFrame"
    sansFrame.Size = UDim2.new(0, 150, 0, 40)
    sansFrame.Position = UDim2.new(0, 170, 0, 5)
    sansFrame.BackgroundColor3 = Color3.fromRGB(50, 50, 50)
    sansFrame.Parent = topBar
    
    local sansLabel = Instance.new("TextLabel")
    sansLabel.Name = "SansLabel"
    sansLabel.Size = UDim2.new(1, 0, 1, 0)
    sansLabel.BackgroundTransparency = 1
    sansLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
    sansLabel.Text = "Sans: 0"
    sansLabel.TextSize = 18
    sansLabel.Font = Enum.Font.Bold
    sansLabel.Parent = sansFrame
    
    -- 메뉴 버튼들
    local menuButtons = {
        {Name = "인벤토리", Position = UDim2.new(1, -350, 0, 5), Event = "OpenInventory"},
        {Name = "도감", Position = UDim2.new(1, -180, 0, 5), Event = "OpenCompendium"},
        {Name = "상점", Position = UDim2.new(1, -90, 0, 5), Event = "OpenShop"}
    }
    
    for _, buttonData in ipairs(menuButtons) do
        local menuButton = Instance.new("TextButton")
        menuButton.Name = buttonData.Name .. "Button"
        menuButton.Size = UDim2.new(0, 80, 0, 40)
        menuButton.Position = buttonData.Position
        menuButton.BackgroundColor3 = Color3.fromRGB(70, 70, 70)
        menuButton.TextColor3 = Color3.fromRGB(255, 255, 255)
        menuButton.Text = buttonData.Name
        menuButton.TextSize = 14
        menuButton.Font = Enum.Font.Bold
        menuButton.Parent = topBar
        
        menuButton.MouseButton1Click:Connect(function()
            UISystem[buttonData.Event]()
        end)
    end
    
    return screenGui
end

-- 인벤토리 GUI 생성
function UISystem.OpenInventory()
    -- 기존 인벤토리 GUI 제거
    local existingInventory = PlayerGui:FindFirstChild("InventoryGUI")
    if existingInventory then
        existingInventory:Destroy()
        return
    end
    
    local inventoryGUI = Instance.new("ScreenGui")
    inventoryGUI.Name = "InventoryGUI"
    inventoryGUI.Parent = PlayerGui
    
    local mainFrame = Instance.new("Frame")
    mainFrame.Name = "MainFrame"
    mainFrame.Size = UDim2.new(0, 600, 0, 400)
    mainFrame.Position = UDim2.new(0.5, -300, 0.5, -200)
    mainFrame.BackgroundColor3 = Color3.fromRGB(40, 40, 40)
    mainFrame.Parent = inventoryGUI
    
    local titleLabel = Instance.new("TextLabel")
    titleLabel.Name = "TitleLabel"
    titleLabel.Size = UDim2.new(1, 0, 0, 40)
    titleLabel.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
    titleLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
    titleLabel.Text = "인벤토리"
    titleLabel.TextSize = 20
    titleLabel.Font = Enum.Font.Bold
    titleLabel.Parent = mainFrame
    
    local closeButton = Instance.new("TextButton")
    closeButton.Name = "CloseButton"
    closeButton.Size = UDim2.new(0, 40, 0, 40)
    closeButton.Position = UDim2.new(1, -40, 0, 0)
    closeButton.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
    closeButton.TextColor3 = Color3.fromRGB(255, 255, 255)
    closeButton.Text = "X"
    closeButton.TextSize = 18
    closeButton.Parent = mainFrame
    
    closeButton.MouseButton1Click:Connect(function()
        inventoryGUI:Destroy()
    end)
    
    -- 아이템 슬롯 컨테이너
    local itemContainer = Instance.new("ScrollingFrame")
    itemContainer.Name = "ItemContainer"
    itemContainer.Size = UDim2.new(1, -20, 1, -50)
    itemContainer.Position = UDim2.new(0, 10, 0, 45)
    itemContainer.BackgroundColor3 = Color3.fromRGB(35, 35, 35)
    itemContainer.ScrollBarThickness = 10
    itemContainer.Parent = mainFrame
    
    local layout = Instance.new("UIGridLayout")
    layout.CellSize = UDim2.new(0, 100, 0, 100)
    layout.CellPadding = UDim2.new(0, 5, 0, 5)
    layout.Parent = itemContainer
    
    -- 서버에서 인벤토리 데이터 요청
    local getInventoryFunction = ReplicatedStorage:FindFirstChild("GetInventory")
    if getInventoryFunction then
        local inventoryData = getInventoryFunction:InvokeServer()
        
        if inventoryData then
            for i, item in ipairs(inventoryData.Items) do
                local itemSlot = Instance.new("Frame")
                itemSlot.Name = "ItemSlot_" .. i
                itemSlot.BackgroundColor3 = RARITY_COLORS[item.Rarity] or Color3.fromRGB(100, 100, 100)
                itemSlot.Parent = itemContainer
                
                local itemLabel = Instance.new("TextLabel")
                itemLabel.Size = UDim2.new(1, 0, 0.7, 0)
                itemLabel.Position = UDim2.new(0, 0, 0, 0)
                itemLabel.BackgroundTransparency = 1
                itemLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
                itemLabel.Text = item.Name
                itemLabel.TextSize = 12
                itemLabel.TextWrapped = true
                itemLabel.Parent = itemSlot
                
                local rarityLabel = Instance.new("TextLabel")
                rarityLabel.Size = UDim2.new(1, 0, 0.3, 0)
                rarityLabel.Position = UDim2.new(0, 0, 0.7, 0)
                rarityLabel.BackgroundTransparency = 1
                rarityLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
                rarityLabel.Text = item.Rarity
                rarityLabel.TextSize = 10
                rarityLabel.Parent = itemSlot
                
                -- 판매 버튼
                local sellButton = Instance.new("TextButton")
                sellButton.Size = UDim2.new(0, 60, 0, 20)
                sellButton.Position = UDim2.new(0.5, -30, 0.8, 0)
                sellButton.BackgroundColor3 = Color3.fromRGB(50, 200, 50)
                sellButton.TextColor3 = Color3.fromRGB(255, 255, 255)
                sellButton.Text = "판매"
                sellButton.TextSize = 12
                sellButton.Parent = itemSlot
                
                sellButton.MouseButton1Click:Connect(function()
                    local sellItemEvent = ReplicatedStorage:FindFirstChild("SellItem")
                    if sellItemEvent then
                        sellItemEvent:FireServer(item.UniqueID)
                    end
                end)
            end
        end
    end
    
    itemContainer.CanvasSize = UDim2.new(0, 0, 0, math.ceil(#(inventoryData and inventoryData.Items or {}) / 5) * 105)
end

-- 도감 GUI 생성
function UISystem.OpenCompendium()
    -- 기존 도감 GUI 제거
    local existingCompendium = PlayerGui:FindFirstChild("CompendiumGUI")
    if existingCompendium then
        existingCompendium:Destroy()
        return
    end
    
    local compendiumGUI = Instance.new("ScreenGui")
    compendiumGUI.Name = "CompendiumGUI"
    compendiumGUI.Parent = PlayerGui
    
    local mainFrame = Instance.new("Frame")
    mainFrame.Name = "MainFrame"
    mainFrame.Size = UDim2.new(0, 700, 0, 500)
    mainFrame.Position = UDim2.new(0.5, -350, 0.5, -250)
    mainFrame.BackgroundColor3 = Color3.fromRGB(40, 40, 40)
    mainFrame.Parent = compendiumGUI
    
    local titleLabel = Instance.new("TextLabel")
    titleLabel.Name = "TitleLabel"
    titleLabel.Size = UDim2.new(1, 0, 0, 40)
    titleLabel.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
    titleLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
    titleLabel.Text = "샌즈 도감"
    titleLabel.TextSize = 20
    titleLabel.Font = Enum.Font.Bold
    titleLabel.Parent = mainFrame
    
    local closeButton = Instance.new("TextButton")
    closeButton.Name = "CloseButton"
    closeButton.Size = UDim2.new(0, 40, 0, 40)
    closeButton.Position = UDim2.new(1, -40, 0, 0)
    closeButton.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
    closeButton.TextColor3 = Color3.fromRGB(255, 255, 255)
    closeButton.Text = "X"
    closeButton.TextSize = 18
    closeButton.Parent = mainFrame
    
    closeButton.MouseButton1Click:Connect(function()
        compendiumGUI:Destroy()
    end)
    
    -- 완성도 표시
    local completionLabel = Instance.new("TextLabel")
    completionLabel.Name = "CompletionLabel"
    completionLabel.Size = UDim2.new(0, 200, 0, 30)
    completionLabel.Position = UDim2.new(0.5, -100, 0, 45)
    completionLabel.BackgroundColor3 = Color3.fromRGB(50, 50, 50)
    completionLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
    completionLabel.Text = "완성도: 0%"
    completionLabel.TextSize = 16
    completionLabel.Parent = mainFrame
    
    -- 도감 슬롯 컨테이너
    local compendiumContainer = Instance.new("ScrollingFrame")
    compendiumContainer.Name = "CompendiumContainer"
    compendiumContainer.Size = UDim2.new(1, -20, 1, -85)
    compendiumContainer.Position = UDim2.new(0, 10, 0, 80)
    compendiumContainer.BackgroundColor3 = Color3.fromRGB(35, 35, 35)
    compendiumContainer.ScrollBarThickness = 10
    compendiumContainer.Parent = mainFrame
    
    local layout = Instance.new("UIGridLayout")
    layout.CellSize = UDim2.new(0, 120, 0, 120)
    layout.CellPadding = UDim2.new(0, 10, 0, 10)
    layout.Parent = compendiumContainer
    
    -- 서버에서 도감 데이터 요청
    local getCompendiumFunction = ReplicatedStorage:FindFirstChild("GetCompendium")
    if getCompendiumFunction then
        local compendiumData = getCompendiumFunction:InvokeServer()
        
        if compendiumData then
            completionLabel.Text = "완성도: " .. compendiumData.CompletionPercentage .. "%"
            
            -- 모든 샌즈 타입 표시
            local GameConfig = require(ReplicatedStorage.GameConfig)
            for i, sansType in ipairs(GameConfig.SANS_TYPES) do
                local discovered = compendiumData.DiscoveredSans[sansType.Name]
                
                local sansSlot = Instance.new("Frame")
                sansSlot.Name = "SansSlot_" .. i
                sansSlot.BackgroundColor3 = discovered and RARITY_COLORS[sansType.Rarity] or Color3.fromRGB(20, 20, 20)
                sansSlot.Parent = compendiumContainer
                
                local sansLabel = Instance.new("TextLabel")
                sansLabel.Size = UDim2.new(1, 0, 0.5, 0)
                sansLabel.Position = UDim2.new(0, 0, 0, 0)
                sansLabel.BackgroundTransparency = 1
                sansLabel.TextColor3 = discovered and Color3.fromRGB(255, 255, 255) or Color3.fromRGB(100, 100, 100)
                sansLabel.Text = discovered and sansType.DisplayName or "???"
                sansLabel.TextSize = 12
                sansLabel.Parent = sansSlot
                
                local rarityLabel = Instance.new("TextLabel")
                rarityLabel.Size = UDim2.new(1, 0, 0.3, 0)
                rarityLabel.Position = UDim2.new(0, 0, 0.5, 0)
                rarityLabel.BackgroundTransparency = 1
                rarityLabel.TextColor3 = discovered and Color3.fromRGB(255, 255, 255) or Color3.fromRGB(100, 100, 100)
                rarityLabel.Text = discovered and sansType.Rarity or "???"
                rarityLabel.TextSize = 10
                rarityLabel.Parent = sansSlot
                
                if discovered then
                    local countLabel = Instance.new("TextLabel")
                    countLabel.Size = UDim2.new(1, 0, 0.2, 0)
                    countLabel.Position = UDim2.new(0, 0, 0.8, 0)
                    countLabel.BackgroundTransparency = 1
                    countLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
                    countLabel.Text = "획득: " .. discovered.DiscoveryCount .. "회"
                    countLabel.TextSize = 8
                    countLabel.Parent = sansSlot
                end
            end
        end
    end
    
    compendiumContainer.CanvasSize = UDim2.new(0, 0, 0, math.ceil(#GameConfig.SANS_TYPES / 5) * 130)
end

-- 상점 GUI 생성
function UISystem.OpenShop()
    -- 기존 상점 GUI 제거
    local existingShop = PlayerGui:FindFirstChild("ShopGUI")
    if existingShop then
        existingShop:Destroy()
        return
    end
    
    local shopGUI = Instance.new("ScreenGui")
    shopGUI.Name = "ShopGUI"
    shopGUI.Parent = PlayerGui
    
    local mainFrame = Instance.new("Frame")
    mainFrame.Name = "MainFrame"
    mainFrame.Size = UDim2.new(0, 500, 0, 400)
    mainFrame.Position = UDim2.new(0.5, -250, 0.5, -200)
    mainFrame.BackgroundColor3 = Color3.fromRGB(40, 40, 40)
    mainFrame.Parent = shopGUI
    
    local titleLabel = Instance.new("TextLabel")
    titleLabel.Name = "TitleLabel"
    titleLabel.Size = UDim2.new(1, 0, 0, 40)
    titleLabel.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
    titleLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
    titleLabel.Text = "무기 상점"
    titleLabel.TextSize = 20
    titleLabel.Font = Enum.Font.Bold
    titleLabel.Parent = mainFrame
    
    local closeButton = Instance.new("TextButton")
    closeButton.Name = "CloseButton"
    closeButton.Size = UDim2.new(0, 40, 0, 40)
    closeButton.Position = UDim2.new(1, -40, 0, 0)
    closeButton.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
    closeButton.TextColor3 = Color3.fromRGB(255, 255, 255)
    closeButton.Text = "X"
    closeButton.TextSize = 18
    closeButton.Parent = mainFrame
    
    closeButton.MouseButton1Click:Connect(function()
        shopGUI:Destroy()
    end)
    
    -- 무기 상점 열기 이벤트
    local openWeaponShopEvent = ReplicatedStorage:FindFirstChild("OpenWeaponShop")
    if openWeaponShopEvent then
        openWeaponShopEvent:FireServer()
    end
    
    shopGUI:Destroy() -- 서버에서 GUI를 생성하므로 클라이언트 GUI는 제거
end

-- 알림 시스템
function UISystem.ShowNotification(message, duration)
    duration = duration or 3
    
    local notificationGUI = Instance.new("ScreenGui")
    notificationGUI.Name = "NotificationGUI"
    notificationGUI.Parent = PlayerGui
    
    local notificationFrame = Instance.new("Frame")
    notificationFrame.Name = "NotificationFrame"
    notificationFrame.Size = UDim2.new(0, 300, 0, 50)
    notificationFrame.Position = UDim2.new(0.5, -150, 0, -60)
    notificationFrame.BackgroundColor3 = Color3.fromRGB(50, 50, 50)
    notificationFrame.Parent = notificationGUI
    
    local notificationLabel = Instance.new("TextLabel")
    notificationLabel.Size = UDim2.new(1, 0, 1, 0)
    notificationLabel.BackgroundTransparency = 1
    notificationLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
    notificationLabel.Text = message
    notificationLabel.TextSize = 16
    notificationLabel.Font = Enum.Font.Bold
    notificationLabel.Parent = notificationFrame
    
    -- 애니메이션
    local tweenIn = TweenService:Create(notificationFrame, TweenInfo.new(0.3), {
        Position = UDim2.new(0.5, -150, 0, 10)
    })
    
    local tweenOut = TweenService:Create(notificationFrame, TweenInfo.new(0.3), {
        Position = UDim2.new(0.5, -150, 0, -60)
    })
    
    tweenIn:Play()
    
    spawn(function()
        wait(duration)
        tweenOut:Play()
        wait(0.3)
        notificationGUI:Destroy()
    end)
end

-- 이벤트 리스너 설정
local function SetupEventListeners()
    -- 샌즈 처치 이벤트
    local sansCaughtEvent = ReplicatedStorage:FindFirstChild("SansCaughtEvent")
    if sansCaughtEvent then
        sansCaughtEvent.OnClientEvent:Connect(function(data)
            local message = data.SansType .. " (" .. data.Rarity .. ") 획득! +" .. data.GoldEarned .. " Gold"
            UISystem.ShowNotification(message, 2)
        end)
    end
    
    -- 재화 변경 이벤트
    local currencyChangedEvent = ReplicatedStorage:FindFirstChild("CurrencyChangedEvent")
    if currencyChangedEvent then
        currencyChangedEvent.OnClientEvent:Connect(function(data)
            local hud = PlayerGui:FindFirstChild("MainHUD")
            if hud then
                local goldLabel = hud.TopBar.GoldFrame.GoldLabel
                if goldLabel then
                    goldLabel.Text = "Gold: " .. data.NewAmount
                end
            end
        end)
    end
    
    -- 인벤토리 변경 이벤트
    local inventoryChangedEvent = ReplicatedStorage:FindFirstChild("InventoryChangedEvent")
    if inventoryChangedEvent then
        inventoryChangedEvent.OnClientEvent:Connect(function(data)
            if data.Action == "Add" then
                UISystem.ShowNotification(data.Item.Name .. " 획득!", 2)
            elseif data.Action == "Sell" then
                UISystem.ShowNotification(data.Item.Name .. " 판매 완료! +" .. data.GoldEarned .. " Gold", 2)
            end
        end)
    end
end

-- 시스템 초기화
local function InitializeUISystem()
    CreateMainHUD()
    SetupEventListeners()
end

InitializeUISystem()

return UISystem