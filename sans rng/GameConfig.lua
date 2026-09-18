-- 샌즈 RNG 게임 설정
local GameConfig = {}

GameConfig.SANS_TYPES = {
    {
        Name = "기본 샌즈",
        Color = Color3.fromRGB(255, 255, 255),
        Rarity = "Common",
        DropRate = 0.4,
        Health = 10,
        Speed = 5,
        SellPrice = 10,
        DisplayName = "기본 샌즈"
    },
    {
        Name = "파란 샌즈",
        Color = Color3.fromRGB(0, 100, 255),
        Rarity = "Uncommon",
        DropRate = 0.3,
        Health = 15,
        Speed = 6,
        SellPrice = 25,
        DisplayName = "파란 샌즈"
    },
    {
        Name = "오렌지 샌즈",
        Color = Color3.fromRGB(255, 165, 0),
        Rarity = "Rare",
        DropRate = 0.15,
        Health = 20,
        Speed = 7,
        SellPrice = 50,
        DisplayName = "오렌지 샌즈"
    },
    {
        Name = "보라 샌즈",
        Color = Color3.fromRGB(128, 0, 128),
        Rarity = "Epic",
        DropRate = 0.1,
        Health = 30,
        Speed = 8,
        SellPrice = 100,
        DisplayName = "보라 샌즈"
    },
    {
        Name = "레전드 샌즈",
        Color = Color3.fromRGB(255, 215, 0),
        Rarity = "Legendary",
        DropRate = 0.04,
        Health = 50,
        Speed = 10,
        SellPrice = 250,
        DisplayName = "레전드 샌즈"
    },
    {
        Name = "미스틱 샌즈",
        Color = Color3.fromRGB(255, 0, 100),
        Rarity = "Mythic",
        DropRate = 0.01,
        Health = 100,
        Speed = 12,
        SellPrice = 500,
        DisplayName = "미스틱 샌즈"
    }
}

GameConfig.WEAPONS = {
    {
        Name = "기본 뼈다귀",
        Damage = 1,
        Range = 5,
        Cooldown = 0.5,
        DisplayName = "기본 뼈다귀",
        Price = 0
    },
    {
        Name = "강화 뼈다귀",
        Damage = 2,
        Range = 6,
        Cooldown = 0.4,
        DisplayName = "강화 뼈다귀",
        Price = 100
    },
    {
        Name = "Gaster Blaster",
        Damage = 5,
        Range = 10,
        Cooldown = 0.3,
        DisplayName = "Gaster Blaster",
        Price = 500
    },
    {
        Name = "DETERMINATION Sword",
        Damage = 10,
        Range = 8,
        Cooldown = 0.2,
        DisplayName = "DETERMINATION Sword",
        Price = 1000
    }
}

GameConfig.GAME_SETTINGS = {
    SpawnInterval = 2, -- 샌즈 스폰 간격 (초)
    MaxSans = 50, -- 최대 동시 스폰 수
    MapSize = 100, -- 맵 크기
    BaseCurrency = "Gold",
    StartingCurrency = 100
}

return GameConfig