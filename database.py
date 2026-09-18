import json
import os
from typing import Dict, Any, Optional

class Database:
    def __init__(self, file_path: str = "data.json"):
        self.file_path = file_path
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._create_default_data()
        return self._create_default_data()
    
    def _create_default_data(self) -> Dict[str, Any]:
        return {
            "players": {},
            "inventories": {},
            "parties": {},
            "battles": {}
        }
    
    def save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_player(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.data["players"].get(user_id)
    
    def create_player(self, user_id: str, player_data: Dict[str, Any]):
        self.data["players"][user_id] = player_data
        self.save()
    
    def update_player(self, user_id: str, player_data: Dict[str, Any]):
        if user_id in self.data["players"]:
            self.data["players"][user_id].update(player_data)
            self.save()
    
    def get_inventory(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.data["inventories"].get(user_id)
    
    def create_inventory(self, user_id: str, inventory_data: Dict[str, Any]):
        self.data["inventories"][user_id] = inventory_data
        self.save()
    
    def update_inventory(self, user_id: str, inventory_data: Dict[str, Any]):
        if user_id in self.data["inventories"]:
            self.data["inventories"][user_id].update(inventory_data)
            self.save()
