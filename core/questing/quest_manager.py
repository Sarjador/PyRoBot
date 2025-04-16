import torch
from transformers import BertTokenizer, BertModel
from core.vision.ocr import extract_text_from_region


class QuestManager:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
        self.quest_bert = BertModel.from_pretrained('bert-base-multilingual-cased').to(self.device)
        self.current_quests = []

    def process_quest_window(self, frame):
        """Procesa la ventana de misiones"""
        quest_text = extract_text_from_region(frame, (50, 100, 500, 400))

        # Codificar texto con BERT
        inputs = self.tokenizer(quest_text, return_tensors="pt", truncation=True, padding=True).to(self.device)
        with torch.no_grad():
            outputs = self.quest_bert(**inputs)

        quest_embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()

        # Clasificar tipo de misión
        quest_type = self._classify_quest(quest_embedding)

        # Actualizar registro de misiones
        self._update_quest_log(quest_text, quest_type)

        return quest_type

    def _classify_quest(self, embedding):
        """Clasifica el tipo de misión"""
        # Implementar clasificador
        return "hunt"

    def _update_quest_log(self, quest_text, quest_type):
        """Actualiza el registro de misiones"""
        self.current_quests.append({
            'text': quest_text,
            'type': quest_type,
            'completed': False
        })

    def get_next_quest_action(self):
        """Determina la siguiente acción para completar misiones"""
        if not self.current_quests:
            return "find_new_quest"

        current = self.current_quests[0]

        if current['type'] == 'hunt':
            return "hunt_monsters"
        elif current['type'] == 'collect':
            return "gather_items"

        return "explore"