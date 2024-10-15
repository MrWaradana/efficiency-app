

from collections import defaultdict
from core.controller.base import BaseController
from digital_twin_migration.models.efficiency_app import EfficiencyDataDetailRootCause, EfficiencyDataDetailRootCauseMember, EfficiencyDataDetailRootCauseAction
from core.factory import data_detail_root_cause_factory
from core.cache import Cache, cache_flask
from werkzeug import exceptions as exc
from digital_twin_migration.database import Propagation, Transactional
from app.controllers.data.data_details import data_detail_controller
from app.controllers.variable.variable_cause import variable_cause_repository


class DataDetailRootCauseController(BaseController[EfficiencyDataDetailRootCause]):
    def __init__(self, data_detail_root_cause_repository=data_detail_root_cause_factory.data_detail_root_cause_repository):
        super().__init__(model=EfficiencyDataDetailRootCause, repository=data_detail_root_cause_repository)
        self.data_detail_root_cause_repository = data_detail_root_cause_repository

    def get_by_detail_id(self, detail_id, is_repair=False):
        root_causes = self.data_detail_root_cause_repository.get_by_detail_id(detail_id)

        return root_causes

    @Transactional(propagation=Propagation.REQUIRED)
    def create_data_detail_root_cause(self, user_id, transaction_id, detail_id, is_bulk, data_root_causes, **inputs):
        if is_bulk:
            if not data_root_causes:
                return exc.BadRequest("Data root causes must be provided if is_bulk is True")

            # parent_ids = [root_cause["parent_id"] for root_cause in data_root_causes]

            data_roots = {str(root.parent_cause_id): root for root in self.data_detail_root_cause_repository.get_by_detail_id(detail_id)}

            for root_cause in data_root_causes:
                # CHeck if root cause is already exist

                data_root_cause = data_roots.get(root_cause["parent_id"], None)

                if not data_root_cause:
                    data_root_cause = self.data_detail_root_cause_repository.create({
                        "data_detail_id": detail_id,
                        "is_repair": False,
                        "biaya": 0,
                        "parent_cause_id": root_cause["parent_id"],
                        "created_by": user_id
                    })
                else:
                    data_root_cause.is_repair = False
                    data_root_cause.biaya = 0
                    for member in data_root_cause.members:
                        self.data_detail_root_cause_repository.session.delete(member)

                root_cause_members = [
                    EfficiencyDataDetailRootCauseMember(
                        root_cause_id=data_root_cause.id,
                        cause_id=cause_id,
                        is_parent=True if cause_id == root_cause["parent_id"] else False,
                        is_checked=data['isChecked'],
                        is_repair=data['is_repair'],
                        biaya=0,
                        created_by=user_id
                    )for cause_id, data in root_cause["root_causes"].items()
                ]

                cache_flask.delete(f"variable_actions_{detail_id}")
                cache_flask.delete(f"data_pareto_{transaction_id}")

                self.data_detail_root_cause_repository.session.add_all(root_cause_members)

            # data_root_causes_records = [
            #     EfficiencyDataDetailRootCause(
            #         data_detail_id=detail_id,
            #         cause_id=root_cause["cause_id"],
            #         is_repair=(
            #             root_cause["is_repair"] if "is_repair" in root_cause else False
            #         ),
            #         biaya=root_cause["biaya"] if "biaya" in root_cause else 0,
            #         variable_header_value=(
            #             root_cause["variable_header_value"]
            #             if "variable_header_value" in root_cause
            #             else None
            #         ),
            #         created_by=user_id,
            #     )
            #     for root_cause in data_root_causes
            # ]

            # self.data_detail_root_cause_repository.create_bulk(data_root_causes_records)

        else:
            missing_input = next(
                (name for name, input in inputs.items() if not input), None
            )
            if missing_input:
                return exc.BadRequest(f"'{missing_input}' is required when 'is_bulk' is not set")

            self.data_detail_root_cause_repository.create(
                {**inputs, "data_detail_id": detail_id, "created_by": user_id}
            )

        Cache.remove_by_prefix(f"data_detail_root_cause_{detail_id}")

        return None

    @Transactional(propagation=Propagation.REQUIRED)
    def create_data_detail_root_cause_actions(self, user_id, data_actions, detail_id):

        if not data_actions:
            return exc.BadRequest("Data actions must be provided")

        data_roots = {str(root.parent_cause_id): root for root in self.data_detail_root_cause_repository.get_by_detail_id(detail_id)}

        root_cause_actions = []

        for data_action in data_actions:
            parent_id = data_action["parent_id"]
            data_root = data_roots.get(parent_id)

            if not data_root:
                return exc.BadRequest(f"Root cause not found for parent_id: {parent_id}")

            total_biaya = sum(action.biaya for action in data_root.actions)
            data_root.biaya -= total_biaya

            for action in data_root.actions:
                self.data_detail_root_cause_repository.session.delete(action)

            # Process new actions
            new_actions = [
                EfficiencyDataDetailRootCauseAction(
                    root_cause_id=data_root.id,
                    action_id=action_id,
                    is_checked=action_data.get('isChecked', False),
                    biaya=action_data.get('biaya', 0) if action_data.get('isChecked', False) else 0,
                    created_by=user_id
                )
                for action_id, action_data in data_action['actions'].items()
            ]

            # Update total biaya with new actions
            new_total_biaya = sum(action.biaya for action in new_actions)
            data_root.biaya += new_total_biaya

            root_cause_actions.extend(new_actions)

        cache_flask.delete(f"variable_actions_{data_root.data_detail_id}")

        self.data_detail_root_cause_repository.session.add_all(root_cause_actions)

    def check_root_cause(self, data_id):
        # Get data
        data_details = {data_detail.variable_id: data_detail.id for data_detail in data_detail_controller.get_data_details(data_id, "out", True)}

        root_cause_count = self.data_detail_root_cause_repository.get_total_root_cause_by_detail_ids(list(data_details.values()))
        # variable_causes_count = dict(variable_cause_repository.get_count_by_variable_ids(list(data_details.keys())))

        results = defaultdict(lambda: {
            "root_causes": [],
            "actions": [],
            "variable_id": ""
        })

        for data_detail_id, var_id, is_repair, is_checked, variable_cause_name , variable_cause_id in root_cause_count:
            if not is_checked:
                continue
            
            data_detail_id = str(data_detail_id)
            actions = []
            if is_repair:
                variable_cause = variable_cause_repository.get_by_uuid(variable_cause_id, {"actions"})[0]
                actions = [action.name for action in variable_cause.actions]

            results[data_detail_id]["root_causes"].append(variable_cause_name)
            results[data_detail_id]["actions"].extend(actions)
            results[data_detail_id]["variable_id"] = var_id

        return results


data_detail_root_cause_controller = DataDetailRootCauseController()
