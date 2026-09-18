-- 아이템 등급 및 희귀도 시스템 스크립트
local GameConfig = require(game.ReplicatedStorage.GameConfig)

local RaritySystem = {}

-- 희귀도 설정
RaritySystem.RARITY_SETTINGS = {
    Common = {
        Name = "Common",
        DisplayName = "일반",
        Color = Color3.fromRGB(128, 128, 128),
        DropRate = 0.4,
        Multiplier = 1.0,
        EffectColor = Color3.fromRGB(200, 200, 200),
        ParticleColor = Color3.fromRGB(150, 150, 150)
    },
    Uncommon = {
        Name = "Uncommon",
        DisplayName = "희귀",
        Color = Color3.fromRGB(0, 255, 0),
        DropRate = 0.3,
        Multiplier = 1.5,
        EffectColor = Color3.fromRGB(100, 255, 100),
        ParticleColor = Color3.fromRGB(50, 200, 50)
    },
    Rare = {
        Name = "Rare",
        DisplayName = "레어",
        Color = Color3.fromRGB(0, 100, 255),
        DropRate = 0.15,
        Multiplier = 2.0,
        EffectColor = Color3.fromRGB(100, 150, 255),
        ParticleColor = Color3.fromRGB(50, 100, 200)
    },
    Epic = {
        Name = "Epic",
        DisplayName = "에픽",
        Color = Color3.fromRGB(128, 0, 128),
        DropRate = 0.1,
        Multiplier = 3.0,
        EffectColor = Color3.fromRGB(200, 100, 200),
        ParticleColor = Color3.fromRGB(150, 50, 150)
    },
    Legendary = {
        Name = "Legendary",
        DisplayName = "레전드",
        Color = Color3.fromRGB(255, 215, 0),
        DropRate = 0.04,
        Multiplier = 5.0,
        EffectColor = Color3.fromRGB(255, 235, 100),
        ParticleColor = Color3.fromRGB(255, 200, 50)
    },
    Mythic = {
        Name = "Mythic",
        DisplayName = "미스틱",
        Color = Color3.fromRGB(255, 0, 100),
        DropRate = 0.01,
        Multiplier = 10.0,
        EffectColor = Color3.fromRGB(255, 100, 150),
        ParticleColor = Color3.fromRGB(255, 50, 100)
    }
}

-- 희귀도별 효과 생성
function RaritySystem.CreateRarityEffect(model, rarityName)
    local raritySettings = RaritySystem.RARITY_SETTINGS[rarityName]
    if not raritySettings then
        return
    end
    
    -- 빛나는 효과
    local light = Instance.new("PointLight")
    light.Name = "RarityLight"
    light.Color = raritySettings.EffectColor
    light.Brightness = 2
    light.Range = 10
    light.Parent = model
    
    -- 파티클 효과
    local attachment = Instance.new("Attachment")
    attachment.Name = "RarityAttachment"
    attachment.Parent = model.PrimaryPart or model:FindFirstChild("Body")
    
    local particles = Instance.new("ParticleEmitter")
    particles.Name = "RarityParticles"
    particles.Color = ColorSequence.new(raritySettings.ParticleColor)
    particles.Size = NumberSequence.new(0.5, 0)
    particles.Lifetime = NumberRange.new(0.5, 1.5)
    particles.Rate = 50
    particles.Speed = NumberRange.new(2, 5)
    particles.SpreadAngle = Vector2.new(360, 360)
    particles.Parent = attachment
    
    -- 희귀도에 따른 추가 효과
    if rarityName == "Legendary" or rarityName == "Mythic" then
        -- 레인보우 효과
        local rainbowLight = Instance.new("PointLight")
        rainbowLight.Name = "RainbowLight"
        rainbowLight.Brightness = 3
        rainbowLight.Range = 15
        rainbowLight.Parent = model
        
        spawn(function()
            local hue = 0
            while model and model.Parent do
                hue = (hue + 0.01) % 1
                local color = Color3.fromHSV(hue, 1, 1)
                rainbowLight.Color = color
                wait(0.1)
            end
        end)
    end
end

-- 희귀도 확률 계산
function RaritySystem.CalculateRarityDrop()
    local random = math.random()
    local cumulativeRate = 0
    
    -- 희귀도별로 정렬 (희귀한 것부터)
    local sortedRarities = {}
    for rarityName, settings in pairs(RaritySystem.RARITY_SETTINGS) do
        table.insert(sortedRarities, {Name = rarityName, Settings = settings})
    end
    
    table.sort(sortedRarities, function(a, b)
        return a.Settings.DropRate < b.Settings.DropRate
    end)
    
    for _, rarityData in ipairs(sortedRarities) do
        cumulativeRate = cumulativeRate + rarityData.Settings.DropRate
        if random <= cumulativeRate then
            return rarityData.Name
        end
    end
    
    return "Common" -- 기본값
end

-- 희귀도별 보너스 계산
function RaritySystem.CalculateBonus(baseValue, rarityName)
    local raritySettings = RaritySystem.RARITY_SETTINGS[rarityName]
    if not raritySettings then
        return baseValue
    end
    
    return math.floor(baseValue * raritySettings.Multiplier)
end

-- 희귀도 정보 가져오기
function RaritySystem.GetRarityInfo(rarityName)
    return RaritySystem.RARITY_SETTINGS[rarityName]
end

-- 희귀도별 사운드 효과
function RaritySystem.PlayRaritySound(rarityName)
    local soundSettings = {
        Common = {SoundId = "rbxassetid://1234567890", Volume = 0.5},
        Uncommon = {SoundId = "rbxassetid://1234567891", Volume = 0.6},
        Rare = {SoundId = "rbxassetid://1234567892", Volume = 0.7},
        Epic = {SoundId = "rbxassetid://1234567893", Volume = 0.8},
        Legendary = {SoundId = "rbxassetid://1234567894", Volume = 0.9},
        Mythic = {SoundId = "rbxassetid://1234567895", Volume = 1.0}
    }
    
    local settings = soundSettings[rarityName]
    if settings then
        local sound = Instance.new("Sound")
        sound.SoundId = settings.SoundId
        sound.Volume = settings.Volume
        sound.Parent = workspace
        sound:Play()
        sound.Ended:Connect(function()
            sound:Destroy()
        end)
    end
end

-- 희귀도별 애니메이션 효과
function RaritySystem.PlayRarityAnimation(model, rarityName)
    local raritySettings = RaritySystem.RARITY_SETTINGS[rarityName]
    if not raritySettings then
        return
    end
    
    -- 크기 변화 애니메이션
    local primaryPart = model.PrimaryPart or model:FindFirstChild("Body")
    if primaryPart then
        local originalSize = primaryPart.Size
        local originalColor = primaryPart.Color
        
        -- 희귀도에 따른 애니메이션 강도
        local animationIntensity = {
            Common = 1.0,
            Uncommon = 1.2,
            Rare = 1.4,
            Epic = 1.6,
            Legendary = 2.0,
            Mythic = 2.5
        }
        
        local intensity = animationIntensity[rarityName] or 1.0
        
        -- 확대 애니메이션
        local tweenInfo = TweenInfo.new(0.3, Enum.EasingStyle.Elastic, Enum.EasingDirection.Out)
        local tweenIn = game:GetService("TweenService"):Create(primaryPart, tweenInfo, {
            Size = originalSize * intensity,
            Color = raritySettings.EffectColor
        })
        
        local tweenOut = game:GetService("TweenService"):Create(primaryPart, tweenInfo, {
            Size = originalSize,
            Color = originalColor
        })
        
        tweenIn:Play()
        tweenIn.Completed:Wait()
        tweenOut:Play()
    end
end

-- 샌즈 모델에 희귀도 적용
function RaritySystem.ApplyRarityToSans(sansModel, sansType)
    local rarityName = sansType.Rarity
    
    -- 희귀도 속성 설정
    sansModel:SetAttribute("Rarity", rarityName)
    
    -- 희귀도 효과 적용
    RaritySystem.CreateRarityEffect(sansModel, rarityName)
    
    -- 희귀도별 색상 적용
    local raritySettings = RaritySystem.RARITY_SETTINGS[rarityName]
    if raritySettings and sansModel:FindFirstChild("Body") then
        sansModel.Body.Color = raritySettings.Color
    end
    
    return rarityName
end

-- 강화 시스템 (샌즈 강화)
function RaritySystem.EnhanceSans(baseSansType, enhancementLevel)
    local enhancedSans = {
        Name = baseSansType.Name .. " +" .. enhancementLevel,
        BaseName = baseSansType.Name,
        Color = baseSansType.Color,
        Rarity = baseSansType.Rarity,
        DropRate = baseSansType.DropRate,
        Health = baseSansType.Health * (1 + enhancementLevel * 0.2),
        Speed = baseSansType.Speed * (1 + enhancementLevel * 0.1),
        SellPrice = baseSansType.SellPrice * (1 + enhancementLevel * 0.5),
        DisplayName = baseSansType.DisplayName .. " +" .. enhancementLevel,
        EnhancementLevel = enhancementLevel
    }
    
    -- 강화 레벨에 따른 희귀도 상승
    if enhancementLevel >= 5 then
        local rarityLevels = {"Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"}
        local currentRarityIndex = 1
        for i, rarity in ipairs(rarityLevels) do
            if rarity == baseSansType.Rarity then
                currentRarityIndex = i
                break
            end
        end
        
        local newRarityIndex = math.min(currentRarityIndex + math.floor(enhancementLevel / 5), #rarityLevels)
        enhancedSans.Rarity = rarityLevels[newRarityIndex]
    end
    
    return enhancedSans
end

-- 희귀도별 통계 정보
function RaritySystem.GetRarityStatistics()
    local stats = {}
    
    for rarityName, settings in pairs(RaritySystem.RARITY_SETTINGS) do
        stats[rarityName] = {
            Name = settings.DisplayName,
            DropRate = settings.DropRate,
            Multiplier = settings.Multiplier,
            Color = settings.Color
        }
    end
    
    return stats
end

return RaritySystem