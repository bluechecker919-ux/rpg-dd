-- 무기 시스템 스크립트
local GameConfig = require(game.ReplicatedStorage.GameConfig)

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local WeaponSystem = {}
WeaponSystem.PlayerWeapons = {}
WeaponSystem.CurrentCooldowns = {}

-- 무기 장착
local function EquipWeapon(player, weaponData)
    local character = player.Character
    if not character then return end
    
    -- 기존 무기 제거
    local existingWeapon = character:FindFirstChild("EquippedWeapon")
    if existingWeapon then
        existingWeapon:Destroy()
    end
    
    -- 새 무기 모델 생성
    local weaponModel = Instance.new("Model")
    weaponModel.Name = "EquippedWeapon"
    
    -- 무기 파트
    local weaponPart = Instance.new("Part")
    weaponPart.Name = "WeaponPart"
    weaponPart.Size = Vector3.new(0.5, 3, 0.5)
    weaponPart.Color = Color3.fromRGB(200, 200, 200)
    weaponPart.Material = Enum.Material.SmoothPlastic
    weaponPart.Parent = weaponModel
    
    -- 무기 손잡이
    local handle = Instance.new("Part")
    handle.Name = "Handle"
    handle.Size = Vector3.new(0.3, 1, 0.3)
    handle.Color = Color3.fromRGB(139, 69, 19)
    handle.Position = Vector3.new(0, -1, 0)
    handle.Parent = weaponModel
    
    -- 무기 손에 장착
    local rightHand = character:FindFirstChild("RightHand")
    if rightHand then
        local weld = Instance.new("WeldConstraint")
        weld.Part0 = rightHand
        weld.Part1 = weaponPart
        weld.Parent = weaponPart
        weaponPart.Position = rightHand.Position + Vector3.new(0, 1, 0)
    end
    
    weaponModel.Parent = character
    
    -- 무기 데이터 저장
    weaponModel:SetAttribute("Damage", weaponData.Damage)
    weaponModel:SetAttribute("Range", weaponData.Range)
    weaponModel:SetAttribute("Cooldown", weaponData.Cooldown)
    weaponModel:SetAttribute("Name", weaponData.Name)
    
    return weaponModel
end

-- 무기 공격
local function AttackWithWeapon(player, targetSans)
    local character = player.Character
    if not character then return end
    
    local weapon = character:FindFirstChild("EquippedWeapon")
    if not weapon then return end
    
    local damage = weapon:GetAttribute("Damage")
    local range = weapon:GetAttribute("Range")
    local cooldown = weapon:GetAttribute("Cooldown")
    
    -- 쿨다운 체크
    local currentTime = tick()
    local lastAttackTime = WeaponSystem.CurrentCooldowns[player.UserId] or 0
    
    if currentTime - lastAttackTime < cooldown then
        return false -- 쿨다운 중
    end
    
    -- 사거리 체크
    local playerPosition = character.HumanoidRootPart.Position
    local sansPosition = targetSans.HumanoidRootPart.Position
    local distance = (playerPosition - sansPosition).Magnitude
    
    if distance > range then
        return false -- 사거리 밖
    end
    
    -- 쿨다운 업데이트
    WeaponSystem.CurrentCooldowns[player.UserId] = currentTime
    
    -- 공격 애니메이션
    local humanoid = character:FindFirstChild("Humanoid")
    if humanoid then
        humanoid:LoadAnimation(Instance.new("Animation")):Play()
    end
    
    -- 공격 효과
    local attackEffect = Instance.new("Part")
    attackEffect.Name = "AttackEffect"
    attackEffect.Size = Vector3.new(range, 0.5, 0.5)
    attackEffect.Color = Color3.fromRGB(255, 255, 0)
    attackEffect.Transparency = 0.5
    attackEffect.Anchored = true
    attackEffect.CanCollide = false
    attackEffect.Position = playerPosition
    attackEffect.CFrame = CFrame.lookAt(playerPosition, sansPosition)
    attackEffect.Parent = workspace
    
    -- 효과 제거
    spawn(function()
        for i = 1, 10 do
            wait(0.05)
            attackEffect.Transparency = attackEffect.Transparency + 0.05
        end
        attackEffect:Destroy()
    end)
    
    return true, damage
end

-- 마우스 클릭 공격 처리
local function OnMouseClick(player, clickPosition)
    local character = player.Character
    if not character then return end
    
    -- 클릭 위치 근처의 샌즈 찾기
    local nearestSans = nil
    local nearestDistance = 10 -- 기본 사거리
    
    for _, sans in ipairs(workspace:GetChildren()) do
        if sans:GetAttribute("SansType") and sans:FindFirstChild("HumanoidRootPart") then
            local sansPosition = sans.HumanoidRootPart.Position
            local distance = (clickPosition - sansPosition).Magnitude
            
            if distance < nearestDistance then
                nearestDistance = distance
                nearestSans = sans
            end
        end
    end
    
    if nearestSans then
        local success, damage = AttackWithWeapon(player, nearestSans)
        if success then
            -- 데미지 적용
            local currentHealth = nearestSans:GetAttribute("Health")
            currentHealth = currentHealth - damage
            nearestSans:SetAttribute("Health", currentHealth)
            
            -- 피격 효과
            if nearestSans:FindFirstChild("Body") then
                nearestSans.Body.Color = Color3.fromRGB(255, 0, 0)
                wait(0.1)
                nearestSans.Body.Color = nearestSans:GetAttribute("OriginalColor") or Color3.fromRGB(255, 255, 255)
            end
        end
    end
end

-- 무기 상점 GUI
local function CreateWeaponShopGUI(player)
    local playerGui = player:FindFirstChild("PlayerGui")
    if not playerGui then return end
    
    local screenGui = Instance.new("ScreenGui")
    screenGui.Name = "WeaponShop"
    screenGui.Parent = playerGui
    
    local mainFrame = Instance.new("Frame")
    mainFrame.Name = "MainFrame"
    mainFrame.Size = UDim2.new(0, 400, 0, 300)
    mainFrame.Position = UDim2.new(0.5, -200, 0.5, -150)
    mainFrame.BackgroundColor3 = Color3.fromRGB(50, 50, 50)
    mainFrame.Parent = screenGui
    
    local titleLabel = Instance.new("TextLabel")
    titleLabel.Name = "TitleLabel"
    titleLabel.Size = UDim2.new(1, 0, 0, 30)
    titleLabel.Position = UDim2.new(0, 0, 0, 0)
    titleLabel.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
    titleLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
    titleLabel.Text = "무기 상점"
    titleLabel.TextSize = 20
    titleLabel.Font = Enum.Font.Bold
    titleLabel.Parent = mainFrame
    
    local closeButton = Instance.new("TextButton")
    closeButton.Name = "CloseButton"
    closeButton.Size = UDim2.new(0, 30, 0, 30)
    closeButton.Position = UDim2.new(1, -30, 0, 0)
    closeButton.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
    closeButton.TextColor3 = Color3.fromRGB(255, 255, 255)
    closeButton.Text = "X"
    closeButton.TextSize = 16
    closeButton.Parent = mainFrame
    
    closeButton.MouseButton1Click:Connect(function()
        screenGui:Destroy()
    end)
    
    -- 무기 목록 스크롤링 프레임
    local scrollFrame = Instance.new("ScrollingFrame")
    scrollFrame.Name = "WeaponList"
    scrollFrame.Size = UDim2.new(1, -10, 1, -40)
    scrollFrame.Position = UDim2.new(0, 5, 0, 35)
    scrollFrame.BackgroundColor3 = Color3.fromRGB(40, 40, 40)
    scrollFrame.ScrollBarThickness = 10
    scrollFrame.Parent = mainFrame
    
    local layout = Instance.new("UIListLayout")
    layout.Parent = scrollFrame
    
    -- 무기 아이템 추가
    for i, weapon in ipairs(GameConfig.WEAPONS) do
        local weaponButton = Instance.new("TextButton")
        weaponButton.Name = "Weapon_" .. i
        weaponButton.Size = UDim2.new(1, -10, 0, 50)
        weaponButton.Position = UDim2.new(0, 5, 0, (i-1) * 55)
        weaponButton.BackgroundColor3 = Color3.fromRGB(60, 60, 60)
        weaponButton.TextColor3 = Color3.fromRGB(255, 255, 255)
        weaponButton.Text = weapon.DisplayName .. " (데미지: " .. weapon.Damage .. ", 가격: " .. weapon.Price .. " Gold)"
        weaponButton.TextSize = 14
        weaponButton.Parent = scrollFrame
        
        weaponButton.MouseButton1Click:Connect(function()
            -- 구매 로직
            local playerData = _G.GameService.PlayerData[player.UserId]
            if playerData and playerData.Gold >= weapon.Price then
                playerData.Gold = playerData.Gold - weapon.Price
                player.leaderstats.Gold.Value = playerData.Gold
                playerData.CurrentWeapon = weapon
                EquipWeapon(player, weapon)
                
                -- 구매 성공 메시지
                local successMessage = Instance.new("TextLabel")
                successMessage.Size = UDim2.new(0, 200, 0, 30)
                successMessage.Position = UDim2.new(0.5, -100, 0.8, 0)
                successMessage.BackgroundColor3 = Color3.fromRGB(0, 200, 0)
                successMessage.TextColor3 = Color3.fromRGB(255, 255, 255)
                successMessage.Text = weapon.DisplayName .. " 구매 완료!"
                successMessage.Parent = screenGui
                
                spawn(function()
                    wait(2)
                    successMessage:Destroy()
                end)
            else
                -- 구매 실패 메시지
                local failMessage = Instance.new("TextLabel")
                failMessage.Size = UDim2.new(0, 200, 0, 30)
                failMessage.Position = UDim2.new(0.5, -100, 0.8, 0)
                failMessage.BackgroundColor3 = Color3.fromRGB(200, 0, 0)
                failMessage.TextColor3 = Color3.fromRGB(255, 255, 255)
                failMessage.Text = "Gold가 부족합니다!"
                failMessage.Parent = screenGui
                
                spawn(function()
                    wait(2)
                    failMessage:Destroy()
                end)
            end
        end)
    end
    
    scrollFrame.CanvasSize = UDim2.new(0, 0, 0, #GameConfig.WEAPONS * 55)
end

-- 무기 상점 열기 명령
local function OpenWeaponShop(player)
    CreateWeaponShopGUI(player)
end

-- 시스템 초기화
local function InitializeWeaponSystem()
    -- 플레이어 조인 시 기본 무기 장착
    Players.PlayerAdded:Connect(function(player)
        WeaponSystem.PlayerWeapons[player.UserId] = GameConfig.WEAPONS[1]
        
        player.CharacterAdded:Connect(function(character)
            wait(0.5) -- 캐릭터 로딩 대기
            EquipWeapon(player, GameConfig.WEAPONS[1])
        end)
    end)
    
    -- 기존 플레이어 처리
    for _, player in ipairs(Players:GetPlayers()) do
        WeaponSystem.PlayerWeapons[player.UserId] = GameConfig.WEAPONS[1]
        if player.Character then
            EquipWeapon(player, GameConfig.WEAPONS[1])
        end
    end
    
    -- 마우스 클릭 이벤트
    UserInputService.InputBegan:Connect(function(input, gameProcessed)
        if gameProcessed then return end
        
        if input.UserInputType == Enum.UserInputType.MouseButton1 then
            local player = Players.LocalPlayer
            local mouse = player:GetMouse()
            OnMouseClick(player, mouse.Hit.p)
        end
    end)
    
    -- 무기 상점 RemoteEvent
    local weaponShopEvent = Instance.new("RemoteEvent")
    weaponShopEvent.Name = "OpenWeaponShop"
    weaponShopEvent.Parent = ReplicatedStorage
    
    weaponShopEvent.OnServerEvent:Connect(function(player)
        OpenWeaponShop(player)
    end)
end

InitializeWeaponSystem()

return WeaponSystem