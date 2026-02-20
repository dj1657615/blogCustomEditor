import json
import os

class CampaignManager:
    def __init__(self, filepath='campaign.json'):
        self.filepath = filepath
        self.campaigns = []
        self.load_campaigns()

    def load_campaigns(self):
        if not os.path.exists(self.filepath):
            self.campaigns = []
            return self.campaigns
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.campaigns = json.load(f)
        except json.JSONDecodeError:
            self.campaigns = []
            
        return self.campaigns

    def save_campaigns(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.campaigns, f, ensure_ascii=False, indent=4)

    def get_campaign_by_name(self, name):
        for camp in self.campaigns:
            if camp.get("name") == name:
                return camp
        return None

    def update_campaign(self, campaign_data):
        for i, camp in enumerate(self.campaigns):
            if camp.get("name") == campaign_data.get("name"):
                self.campaigns[i] = campaign_data
                self.save_campaigns()
                return
        # 기존에 없으면 새로 추가
        self.campaigns.append(campaign_data)
        self.save_campaigns()

    def delete_campaign(self, name):
        self.campaigns = [c for c in self.campaigns if c.get("name") != name]
        self.save_campaigns()