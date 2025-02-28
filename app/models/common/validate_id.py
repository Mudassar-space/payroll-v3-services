


from app.models.common.common import ResponseMessage
from app.models.common.py_object_id import PyObjectId


# def validate_id(self, id: str):
#         try:
#             id = PyObjectId(id)
#             return id
#         except InvalidId as e:
#             self.logger.error(e)
#             return ResponseMessage(success=False, message=f"Category id '{id}' is invalid.")