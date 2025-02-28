from bson.errors import InvalidId
from app.models.common.common import ResponseMessage
from app.models.common.logger import Logger
from app.models.common.py_object_id import PyObjectId


class CommonMethodsManager():
    def __init__(self):
        self.logger = Logger()

    def validate_id(self, id: str):
        try:
            id = PyObjectId(id)
            return id
        except InvalidId as e:
            self.logger.error(e)
            return ResponseMessage(success=False, message=f"id '{id}' is invalid.")
        

    def get_nested_changes(self, original, updated):
        changes = {}
        for key, updated_value in updated.items():
            original_value = original.get(key)
            
            if isinstance(updated_value, dict) and isinstance(original_value, dict):
                nested_changes = self.get_nested_changes(original_value, updated_value)
                if nested_changes:
                    changes[key] = nested_changes
            elif key not in original or original_value != updated_value:
                changes[key] = updated_value

        return changes
