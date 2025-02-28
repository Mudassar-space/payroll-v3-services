from typing import Optional, Union
from fastapi_camelcase import CamelModel


class DataGridHeaderColumn(CamelModel):
    # The column identifier. It's used to map with data row values.
    field: str
    # The title of the column rendered in the column header cell.
    headerName: str
    # The description of the column rendered as tooltip if the column header name is not fully displayed.
    description: Optional[str]
    # Set the width of the column. default 100
    # width: Optional[int]
    # If set, it indicates that a column has fluid width. Range [0, ∞).
    flex: int = 1
    # Sets the minimum width of a column. default 50
    # minWidth: Optional[int]
    # Sets the maximum width of a column. default Infinity
    # maxWidth: Optional[int]
    # If `true`, hide the column. default false
    hide: bool = False
    # If `false`, removes the buttons for hiding this column.. default false
    hideable: bool = False
    # If `true`, the column is sortable. default true
    sortable: bool = True
    # The order of the sorting sequence.
    sortingOrder: str = 'asc' #| 'desc'
    # If `true`, the column is resizable. default true
    resizable: bool = False
    # If `true`, the cells of the column are editable. default false
    # editable: bool
    # Type allows to merge this object with a default definition. default 'string'
    type: str = "string"
    # Allows to align the column values in cells. default left
    align: str = 'left' #| 'right' | 'center'
    # Header cell element alignment.
    headerAlign: str = 'left' #| 'right' | 'center'
    # Toggle the visibility of the sort icons. default false
    hideSortIcons: bool = False
    # If `true`, the column menu is disabled for this column. default true
    disableColumnMenu: bool = True
    #  If `true`, the column is filterable. default true
    # filterable: Optional[bool] = False
    # If `true`, this column cannot be reordered. default true
    disableReorder: bool = True
    # If `true`, this column will not be included in exports. default true
    disableExport: bool = True
    # If `true`, this column will be displayed as ****. default false
    maskable: bool = False
    # If `true`, this column will be read from DB directly and not from the flex fields. default true
    isFixed: bool = True
    sequence: int
    frozenColumn: bool = False
    footer: Optional[Union[int, str]]