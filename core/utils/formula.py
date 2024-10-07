def calculate_gap(target, current) -> float:
    if target is not None and current is not None:
        return current - target
    return 0


def calculate_persen_losses(gap, deviasi, persen_hr):
    if deviasi == 0 or None:
        raise Exception("deviasi cannot be 0")

    if gap is None and persen_hr is None:
        return 0

    result = (gap / deviasi) * persen_hr

    return abs(result)


def calculate_pareto(target_data, current_data):
    gap = calculate_gap(target_data.nilai, current_data.nilai)
    persen_losses = calculate_persen_losses(
        gap, target_data.deviasi, current_data.persen_hr
    )
    nilai_losses = (persen_losses / 100) * 1000

    return gap, persen_losses, nilai_losses


def calculate_cost_benefit(netto, heatRate, nilai_losses):
    cost_benefit = nilai_losses * (netto * heatRate)
    return cost_benefit


class VariableFormula():
    def __init__(self, current_data):
        self.current_data = current_data
        self.current_data_details = {
            details.variable.excel_variable_name: details
            for details in current_data.efficiency_transaction_details
        }

    def calculate_sfc(self):
        "__Stream [95] - Outlet of Fuel Mixer [32] -> Fuel inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Mass flow|*1000/|__Plant gross power"
        stream_95 = self.current_data_details.get("Stream [95] - Outlet of Fuel Mixer [32] -> Fuel inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Mass flow", None)
        plant_gross_power = self.current_data_details.get("Plant gross power", None)

        if not stream_95 or not plant_gross_power:
            return None

        return stream_95.nilai * 1000 / plant_gross_power.nilai if plant_gross_power.nilai != 0 else 0
    
    def calculate_total_coal_flow(self):
        "__Stream [95] - Outlet of Fuel Mixer [32] -> Fuel inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Mass flow|*|1000"
        stream_95 = self.current_data_details.get("Stream [95] - Outlet of Fuel Mixer [32] -> Fuel inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Mass flow", None)
        
        if not stream_95:
            return None
        
        return stream_95.nilai * 1000
    
    
    def calculate_HHV_batubara(self):
        "__Fuel Source [33] - FUEL SOURCE-1: HHV|*0,239"
        fuel_source_33 = self.current_data_details.get("Fuel Source [33] - FUEL SOURCE-1: HHV", None)
        
        if not fuel_source_33:
            return None
        
        return fuel_source_33.nilai * 0.239
    
    def calculate_plant_gross_heat_rate(self):
        "__Plant gross heat rate (HHV)|*0,239"
        plant_gross_heat_rate = self.current_data_details.get("Plant gross heat rate (HHV)", None)
        
        if not plant_gross_heat_rate:
            return None
        
        return plant_gross_heat_rate.nilai * 0.239
    
    def calculate_plant_net_heat_rate(self):
        "__Plant net heat rate (HHV)|*0,239"
        plant_net_heat_rate = self.current_data_details.get("Plant net heat rate (HHV)", None)
        
        if not plant_net_heat_rate:
            return None
        
        return plant_net_heat_rate.nilai * 0.239
    
    def calculate_water_spray(self):
        "__Desuperheater [83] - DESUP SH-1: Spray mass flow|+|__Desuperheater [84] - DESUP SH-2: Spray mass flow"
        desuperheater_83 = self.current_data_details.get("Desuperheater [83] - DESUP SH-1: Spray mass flow", None)
        desuperheater_84 = self.current_data_details.get("Desuperheater [84] - DESUP SH-2: Spray mass flow", None)
        
        if not desuperheater_83 or not desuperheater_84:
            return None
        
        return desuperheater_83.nilai + desuperheater_84.nilai
    
    def calculate_auxiliary_power(self):
        "__Plant auxiliary|/|__Plant gross power"
        plant_auxiliary = self.current_data_details.get("Plant auxiliary", None)
        plant_gross_power = self.current_data_details.get("Plant gross power", None)
        
        if not plant_auxiliary or not plant_gross_power:
            return None
        
        return plant_auxiliary.nilai / plant_gross_power.nilai if plant_gross_power.nilai != 0 else 0
    
    def calculate_hp_turbine_efficiency(self):
        "(|__ST Assembly [1] - HPT: ST Group [1] - HPT-1: Outlet temperature|+|__ST Assembly [1] - HPT: ST Group [2] - HPT-2: Group overall efficiency|+|__ST Assembly [1] - HPT: ST Group [58] - HPT-3: Group overall efficiency|)/3"
        st_assembly_1_hpt_1 = self.current_data_details.get("ST Assembly [1] - HPT: ST Group [1] - HPT-1: Outlet temperature", None)
        st_assembly_1_hpt_2 = self.current_data_details.get("ST Assembly [1] - HPT: ST Group [2] - HPT-2: Group overall efficiency", None)
        st_assembly_1_hpt_3 = self.current_data_details.get("ST Assembly [1] - HPT: ST Group [58] - HPT-3: Group overall efficiency", None)
        
        if not st_assembly_1_hpt_1 or not st_assembly_1_hpt_2 or not st_assembly_1_hpt_3:
            return None
        
        return (st_assembly_1_hpt_1.nilai + st_assembly_1_hpt_2.nilai + st_assembly_1_hpt_3.nilai) / 3
    
   
    
        

    def calculate_cost_benefit(self, netto, heatRate, nilai_losses):
        cost_benefit = nilai_losses * (netto * heatRate)
        return cost_benefit
