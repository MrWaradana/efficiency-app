
import requests
from app.repositories.causes import CausesRepository
from app.repositories.variables import VariablesRepository
from app.schemas.variable_cause import VariableCauseSchema
from core.controller.base import BaseController
from digital_twin_migration.models.efficiency_app import Variable, VariableCause, VariableCauseAction
from core.factory import variable_factory
from app.controllers.data.data_root_cause import data_detail_root_cause_controller
from core.utils import response
from app.controllers.excels import excel_repository
from werkzeug import exceptions
from worker import fetch_variable_data
from typing import Dict, List, Optional
import copy
from core.cache import Cache, cache_flask

variable_cause_schema = VariableCauseSchema()
variable_cause_repository = CausesRepository(VariableCause)

class VariableCauseController(BaseController[VariableCause]):
    def __init__(self, variable_cause_repository: VariablesRepository = variable_cause_repository):
        super().__init__(model=Variable, repository=variable_cause_repository)
        self.variable_cause_repository = variable_cause_repository
        

    def get_cause_actions(self, detail_id: str, variable_id:str) -> List[Dict]:
        
        def has_checked_root_cause_members(node: Dict, root_ids: List[str]) -> bool:
            """
            Check if a node has any checked root cause members with matching root_ids.
            
            Args:
                node (Dict): The node to check
                root_ids (List[str]): List of valid root cause IDs
            
            Returns:
                bool: True if any member is checked and has a matching root_cause_id
            """
            # Get root_cause_members safely using dict.get()
            members = node.get('root_cause_members', [])
            
            if not members:
                return False
            
            # Check both conditions for each member
            return any(
                member.get('is_repair', False) and 
                member.get('root_cause_id') in root_ids 
                for member in members
            )
        
        def is_leaf_node_with_actions(node: Dict) -> bool:
            """Check if a node is a leaf node with actions."""
            has_actions = bool(node.get('actions'))
            has_no_children = not node.get('children')
            return has_actions and has_no_children
        

        def filter_tree(node: Dict, root_ids: List[str]) -> Optional[Dict]:
            """
            Recursively filter the tree structure.
            Returns None if the node should be filtered out.
            """
            # Make a deep copy to avoid modifying the original data
            node = copy.deepcopy(node)
            
            # Base case: if node is None
            if not node:
                return None
            
            # If it's a leaf node with actions
            if is_leaf_node_with_actions(node):
                # Only return the node if it has checked root cause members
                return node if has_checked_root_cause_members(node, root_ids) else None
            
            # Process children if they exist
            if node.get('children'):
                # Filter children recursively
                filtered_children = []
                for child in node['children']:
                    filtered_child = filter_tree(child, root_ids)
                    if filtered_child is not None:
                        filtered_children.append(filtered_child)
                
                # If any children remain after filtering, update node's children
                if filtered_children:
                    node['children'] = filtered_children
                    return node
            
            # If no valid children and not a valid leaf node, return None
            return None
        
        @cache_flask.cached(key_prefix=f"variable_actions_{detail_id}")
        def get_data():
            # Fetch the data
            data = variable_cause_repository.get_by_variable_id(variable_id, {"children", "actions"})
            root_ids = [str(root.id) for root in data_detail_root_cause_controller.data_detail_root_cause_repository.get_by_detail_id(detail_id)]
            
            filtered_data = variable_cause_schema.dump(data, many=True)
            
            # Filter each node in the data array
            filtered_nodes = []
            for node in filtered_data:
                filtered_node = filter_tree(node, root_ids)
                if filtered_node is not None:
                    filtered_nodes.append(filtered_node)
            
            return filtered_nodes

        return get_data()
        
variable_cause_controller = VariableCauseController()