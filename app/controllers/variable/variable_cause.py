
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


variable_cause_schema = VariableCauseSchema()
variable_cause_repository = CausesRepository(VariableCause)

class VariableCauseController(BaseController[VariableCause]):
    def __init__(self, variable_cause_repository: VariablesRepository = variable_cause_repository):
        super().__init__(model=Variable, repository=variable_cause_repository)
        self.variable_cause_repository = variable_cause_repository
        
        
    def get_cause_actions(self, detail_id: str) -> List[Dict]:
        
        def has_checked_root_cause_members(nodeId: str) -> bool:
            """Check if a node has any checked root cause members."""
            members = data_detail_root_cause_controller.data_detail_root_cause_repository.get_by_member_id_and_detail_id(nodeId, detail_id).members
            
            raise Exception(members)
            
            if not members:
                return False
            return any(member.is_checked for member in members.members)
        
        has_checked_root_cause_members()
        
        def is_leaf_node_with_actions(node: VariableCause) -> bool:
            """Check if a node is a leaf node with actions."""
            has_actions = bool(node.actions)
            has_no_children = not node.children
            return has_actions and has_no_children
        

        def filter_tree(node: VariableCause) -> Optional[Dict]:
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
                return node if has_checked_root_cause_members(node.id) else None
            
            # Process children if they exist
            if node.children:
                # Filter children recursively
                filtered_children = []
                for child in node.children:
                    filtered_child = filter_tree(child)
                    if filtered_child is not None:
                        filtered_children.append(filtered_child)
                
                # If any children remain after filtering, update node's children
                if filtered_children:
                    node.children = filtered_children
                    return node
            
            # If no valid children and not a valid leaf node, return None
            return None
        
        # Fetch the data
        data = self.variable_cause_repository.
        
        filtered_data = copy.deepcopy(data)
        
        # Filter each node in the data array
        filtered_nodes = []
        for node in filtered_data['data']:
            filtered_node = filter_tree(node)
            if filtered_node is not None:
                filtered_nodes.append(filtered_node)
        
        return {
            'data': filtered_nodes,
            'message': 'Filtered data',
            'status': True
        }