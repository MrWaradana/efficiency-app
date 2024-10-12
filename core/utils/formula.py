import requests


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


class PIFormula():
    def __init__(self, current_data):
        self.current_data_details = current_data

    def calculate_design_point_condenser(self, value_pi):
        return value_pi / 1000

    def calculate_divide_by_100(self, value_pi):
        return value_pi / 100

    def calculate_mass_flow_from_pi(self, value_pi = None):
        pi_id = "F1DPw1kUu10ziUaXEx2rIyo4pA5wsAAAS1RKQi1LSTAwLVBJMVxUSkIzLkNPQUwgRkVFREVSIFRPVEFMIENPQUwgRkxPVw"
        username = 'tjb.piwebapi'
        password = 'PLNJepara@2024'

        try:
            res = requests.get(f"https://10.47.0.54/piwebapi/streams/{pi_id}/value", auth=(username, password) , timeout=2, verify=False)

            if res.ok:
                data = res.json().get("Value", None)

                if not data:
                    return None

                return data / 2
        except requests.exceptions.RequestException:
            return None


class VariableFormula():
    def __init__(self, current_data):
        self.current_data_details = current_data

    def calculate_sfc(self):
        "__Stream [95] - Outlet of Fuel Mixer [32] -> Fuel inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Mass flow|*1000/|__Plant gross power"
        stream_95 = self.current_data_details.get("Stream [95] - Outlet of Fuel Mixer [32] -> Fuel inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Mass flow", None)
        plant_gross_power = self.plant_gross_power()

        if not stream_95 or not plant_gross_power:
            return None

        return stream_95 * 1000 / plant_gross_power if plant_gross_power != 0 else 0

    def calculate_total_coal_flow(self):
        "__Stream [95] - Outlet of Fuel Mixer [32] -> Fuel inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Mass flow|*|1000"
        stream_95 = self.current_data_details.get("Stream [95] - Outlet of Fuel Mixer [32] -> Fuel inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Mass flow", None)

        if not stream_95:
            return None

        return stream_95 * 1000

    def calculate_HHV_batubara(self):
        "__Fuel Source [33] - FUEL SOURCE-1: HHV|*0,239"
        fuel_source_33 = self.current_data_details.get("Fuel Source [33] - FUEL SOURCE-1: HHV", None)

        if not fuel_source_33:
            return None

        return fuel_source_33 * 0.239

    def calculate_plant_gross_heat_rate(self):
        "__Plant gross heat rate (HHV)|*0,239"
        plant_gross_heat_rate = self.current_data_details.get("Plant gross heat rate (HHV)", None)

        if not plant_gross_heat_rate:
            return None

        return plant_gross_heat_rate * 0.239

    def calculate_plant_net_heat_rate(self):
        "__Plant net heat rate (HHV)|*0,239"
        plant_net_heat_rate = self.current_data_details.get("Plant net heat rate (HHV)", None)

        if not plant_net_heat_rate:
            return None

        return plant_net_heat_rate * 0.239

    def calculate_water_spray(self):
        "__Desuperheater [83] - DESUP SH-1: Spray mass flow|+|__Desuperheater [84] - DESUP SH-2: Spray mass flow"
        desuperheater_83 = self.current_data_details.get("Desuperheater [83] - DESUP SH-1: Spray mass flow", None)
        desuperheater_84 = self.current_data_details.get("Desuperheater [84] - DESUP SH-2: Spray mass flow", None)

        if not desuperheater_83 or not desuperheater_84:
            return None

        return desuperheater_83 + desuperheater_84

    def calculate_auxiliary_power(self):
        "__Plant auxiliary|/|__Plant gross power"
        plant_auxiliary = self.plant_auxiliary()
        plant_gross_power = self.plant_gross_power()

        if not plant_auxiliary or not plant_gross_power:
            return None

        return plant_auxiliary / plant_gross_power if plant_gross_power != 0 else 0

    def calculate_hp_turbine_efficiency(self):
        "(|__ST Assembly [1] - HPT: ST Group [1] - HPT-1: Outlet temperature|+|__ST Assembly [1] - HPT: ST Group [2] - HPT-2: Group overall efficiency|+|__ST Assembly [1] - HPT: ST Group [58] - HPT-3: Group overall efficiency|)/3"
        st_assembly_1_hpt_1 = self.current_data_details.get("ST Assembly [1] - HPT: ST Group [1] - HPT-1: Outlet temperature", None)
        st_assembly_1_hpt_2 = self.current_data_details.get("ST Assembly [1] - HPT: ST Group [2] - HPT-2: Group overall efficiency", None)
        st_assembly_1_hpt_3 = self.current_data_details.get("ST Assembly [1] - HPT: ST Group [58] - HPT-3: Group overall efficiency", None)

        if not st_assembly_1_hpt_1 or not st_assembly_1_hpt_2 or not st_assembly_1_hpt_3:
            return None

        return ((st_assembly_1_hpt_1 / 100) * (st_assembly_1_hpt_2 / 100) * (st_assembly_1_hpt_3 / 100))

    def calculate_lp_turbine_efficiency(self):
        "(|__ST Assembly [3] - LPT: ST Group [5] - LPT-1: Group overall efficiency|+|__ST Assembly [3] - LPT: ST Group [6] - LPT-2: Group overall efficiency|+|__ST Assembly [3] - LPT: ST Group [7] - LPT-3: Group overall efficiency|+|__ST Group [60] - LPT-4: Group overall efficiency|)/4,"
        st_assembly_3_lpt_1 = self.current_data_details.get("ST Assembly [3] - LPT: ST Group [5] - LPT-1: Group overall efficiency", None)
        st_assembly_3_lpt_2 = self.current_data_details.get("ST Assembly [3] - LPT: ST Group [6] - LPT-2: Group overall efficiency", None)
        st_assembly_3_lpt_3 = self.current_data_details.get("ST Assembly [3] - LPT: ST Group [7] - LPT-3: Group overall efficiency", None)
        st_group_60_lpt_4 = self.current_data_details.get("ST Group [60] - LPT-4: Group overall efficiency", None)

        if not st_assembly_3_lpt_1 or not st_assembly_3_lpt_2 or not st_assembly_3_lpt_3 or not st_group_60_lpt_4:
            return None

        return ((st_assembly_3_lpt_1 / 100) * (st_assembly_3_lpt_2 / 100) * (st_assembly_3_lpt_3 / 100) * (st_group_60_lpt_4 / 100))

    def calculate_ip_turbine_efficiency(self):
        "(|__ST Assembly [2] - IPT: ST Group [3] - IPT-1: Group overall efficiency|+|__ST Assembly [2] - IPT: ST Group [4] - IPT-2: Group overall efficiency|)/2"
        st_assembly_2_ipt_1 = self.current_data_details.get("ST Assembly [2] - IPT: ST Group [3] - IPT-1: Group overall efficiency", None)
        st_assembly_2_ipt_2 = self.current_data_details.get("ST Assembly [2] - IPT: ST Group [4] - IPT-2: Group overall efficiency", None)

        if not st_assembly_2_ipt_1 or not st_assembly_2_ipt_2:
            return None

        return ((st_assembly_2_ipt_1 / 100) * (st_assembly_2_ipt_2 / 100))

    def plant_gross_power(self):
        "Plant gross power"
        plant_gross_power = self.current_data_details.get("Plant gross power", None)

        if not plant_gross_power:
            return None

        return plant_gross_power

    def plant_net_power(self):
        "Plant net power"
        plant_net_power = self.current_data_details.get("Plant net power", None)

        if not plant_net_power:
            return None

        return plant_net_power

    def plant_auxiliary(self):
        "Plant auxiliary"
        plant_auxiliary = self.current_data_details.get("Plant auxiliary", None)

        if not plant_auxiliary:
            return None

        return plant_auxiliary

    def calculate_ttd_hph_7(self):
        "(T feedwater out - T saturated)"
        t_feedwater_out_pi = "F1DPw1kUu10ziUaXEx2rIyo4pAZA0AAAS1RKQi1LSTAwLVBJMVxUSkIzLkhQIEZXIEhUUiA3IE9VVEwgRlcgVEVNUA"
        t_saturated = self.current_data_details.get("Feedwater Heater [16] - HPH-6: Saturation temperature", None)
        username = 'tjb.piwebapi'
        password = 'PLNJepara@2024'

        try:
            res = requests.get(f"https://10.47.0.54/piwebapi/streams/{t_feedwater_out_pi}/value", auth=(username, password) , timeout=2, verify=False)

            if res.ok:
                data = res.json().get("Value", None)

                if not data or not t_saturated:
                    return None

                return data - t_saturated
        except requests.exceptions.RequestException:
            return None

    def calculate_ttd_hph_6(self):
        "(T feedwater out - T saturated)"
        t_feedwater_out_pi = "F1DPw1kUu10ziUaXEx2rIyo4pAWg0AAAS1RKQi1LSTAwLVBJMVxUSkIzLkhQIEZXIEhUUiA2IE9VVEwgRlcgVEVNUA"
        t_saturated = self.current_data_details.get("Feedwater Heater [15] - HPH-5: Saturation temperature", None)

        username = 'tjb.piwebapi'
        password = 'PLNJepara@2024'

        try:
            res = requests.get(f"https://10.47.0.54/piwebapi/streams/{t_feedwater_out_pi}/value", auth=(username, password) , timeout=2, verify=False)

            if res.ok:
                data = res.json().get("Value", None)

                if not data or not t_saturated:
                    return None

                return data - t_saturated
        except requests.exceptions.RequestException:
            return None

    def calculate_ttd_hph_5(self):
        "(T feedwater out - T saturated)"
        t_feedwater_out_pi = "F1DPw1kUu10ziUaXEx2rIyo4pAUQ0AAAS1RKQi1LSTAwLVBJMVxUSkIzLkhQIEZXIEhUUiA1IE9VVEwgRlcgVEVNUA"
        t_saturated = self.current_data_details.get("Feedwater Heater [14] - HPH-4: Saturation temperature", None)

        username = 'tjb.piwebapi'
        password = 'PLNJepara@2024'

        try:
            res = requests.get(f"https://10.47.0.54/piwebapi/streams/{t_feedwater_out_pi}/value", auth=(username, password) , timeout=2, verify=False)

            if res.ok:
                data = res.json().get("Value", None)

                if not data or not t_saturated:
                    return None

                return data - t_saturated

        except requests.exceptions.RequestException:
            return None

    def calculate_ttd_lph_1(self):
        "(T saturated - T feedwater out)"

        t_feedwater_out_pi = "F1DPw1kUu10ziUaXEx2rIyo4pA6w0AAAS1RKQi1LSTAwLVBJMVxUSkIzLkxQIEZXIEhUUiAxIE9VVEwgQ09ORCBXVFIgVEVNUA"
        t_saturated = self.current_data_details.get("Feedwater Heater [10] - LPH-1: Saturation temperature", None)

        username = 'tjb.piwebapi'
        password = 'PLNJepara@2024'

        try:
            res = requests.get(f"https://10.47.0.54/piwebapi/streams/{t_feedwater_out_pi}/value", auth=(username, password) , timeout=2, verify=False)

            if res.ok:
                data = res.json().get("Value", None)

                if not data or not t_saturated:
                    return None

                return t_saturated - data

        except requests.exceptions.RequestException:
            return None

    def calculate_ttd_lph_2(self):
        "(T saturated - T feedwater out)"

        t_feedwater_out_pi = "F1DPw1kUu10ziUaXEx2rIyo4pA8w0AAAS1RKQi1LSTAwLVBJMVxUSkIzLkxQIEZXIEhUUiAyIE9VVEwgQ09ORCBXVFIgVEVNUA"
        t_saturated = self.current_data_details.get("Feedwater Heater [11] - LPH-2: Saturation temperature", None)

        username = 'tjb.piwebapi'
        password = 'PLNJepara@2024'

        try:
            res = requests.get(f"https://10.47.0.54/piwebapi/streams/{t_feedwater_out_pi}/value", auth=(username, password) , timeout=2, verify=False)

            if res.ok:
                data = res.json().get("Value", None)

                if not data or not t_saturated:
                    return None

                return t_saturated - data

        except requests.exceptions.RequestException:
            return None

    def calculate_ttd_lph_3(self):
        "(T saturated - T feedwater out)"

        t_feedwater_out_pi = "F1DPw1kUu10ziUaXEx2rIyo4pAUgwAAAS1RKQi1LSTAwLVBJMVxUSkIzLkRFQSZGVyBUSyBJTkwgQ09ORCBXVFIgVEVNUA"
        t_saturated = self.current_data_details.get("Feedwater Heater [12] - LPH-3: Saturation temperature", None)

        username = 'tjb.piwebapi'
        password = 'PLNJepara@2024'

        try:
            res = requests.get(f"https://10.47.0.54/piwebapi/streams/{t_feedwater_out_pi}/value", auth=(username, password) , timeout=2, verify=False)

            if res.ok:
                data = res.json().get("Value", None)

                if not data or not t_saturated:
                    return None

                return t_saturated - data

        except requests.exceptions.RequestException:
            return None

    def calculate_air_heater_effectiveness(self):
        # PA1 = ( [Stream [98] - Outlet 1 of Splitter [82] -> Primary air inlet of Rotary Air Heater [67] - ROTARY AH: Mass flow] + [Stream [96] - Primary air outlet of Rotary Air Heater [67] - ROTARY AH -> Primary air inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Mass flow] ) / 2

        PA1 = (self.current_data_details.get("Stream [98] - Outlet 1 of Splitter [82] -> Primary air inlet of Rotary Air Heater [67] - ROTARY AH: Mass flow", None) + self.current_data_details.get("Stream [96] - Primary air outlet of Rotary Air Heater [67] - ROTARY AH -> Primary air inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Mass flow", None)) / 2
        PA2 = (self.current_data_details.get("Stream [98] - Outlet 1 of Splitter [82] -> Primary air inlet of Rotary Air Heater [67] - ROTARY AH: Specific heat", None) + self.current_data_details.get("Stream [96] - Primary air outlet of Rotary Air Heater [67] - ROTARY AH -> Primary air inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Specific heat", None)) / 2

        PA3 = (1000 / 3600) * PA1 * PA2

        # SA1 = ( [Stream [89] - Outlet of Duct - Classic [79] -> Main air inlet of Rotary Air Heater [67] - ROTARY AH: Mass flow] + [Stream [90] - Main air outlet of Rotary Air Heater [67] - ROTARY AH -> Combustion air inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Mass flow] ) / 2
        # SA2 = ( [Stream [89] - Outlet of Duct - Classic [79] -> Main air inlet of Rotary Air Heater [67] - ROTARY AH: Specific heat] + [Stream [90] - Main air outlet of Rotary Air Heater [67] - ROTARY AH -> Combustion air inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Specific heat] ) / 2

        SA1 = (self.current_data_details.get("Stream [89] - Outlet of Duct - Classic [79] -> Main air inlet of Rotary Air Heater [67] - ROTARY AH: Mass flow", None) + self.current_data_details.get("Stream [90] - Main air outlet of Rotary Air Heater [67] - ROTARY AH -> Combustion air inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Mass flow", None)) / 2
        SA2 = (self.current_data_details.get("Stream [89] - Outlet of Duct - Classic [79] -> Main air inlet of Rotary Air Heater [67] - ROTARY AH: Specific heat", None) + self.current_data_details.get("Stream [90] - Main air outlet of Rotary Air Heater [67] - ROTARY AH -> Combustion air inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Specific heat", None)) / 2

        SA3 = (1000 / 3600) * SA1 * SA2

        # FG1 = ( [Stream [100] - Gas outlet of Economiser [71] - ECO -> Flue gas inlet of Rotary Air Heater [67] - ROTARY AH: Mass flow] + [Stream [91] - Flue gas outlet of Rotary Air Heater [67] - ROTARY AH -> Inlet of Electrostatic Precipitator [68] - ESP: Mass flow] ) / 2
        # FG2 = ( [Stream [100] - Gas outlet of Economiser [71] - ECO -> Flue gas inlet of Rotary Air Heater [67] - ROTARY AH: Specific heat] + [Stream [91] - Flue gas outlet of Rotary Air Heater [67] - ROTARY AH -> Inlet of Electrostatic Precipitator [68] - ESP: Specific heat] ) / 2

        FG1 = (self.current_data_details.get("Stream [100] - Gas outlet of Economiser [71] - ECO -> Flue gas inlet of Rotary Air Heater [67] - ROTARY AH: Mass flow", None) + self.current_data_details.get("Stream [91] - Flue gas outlet of Rotary Air Heater [67] - ROTARY AH -> Inlet of Electrostatic Precipitator [68] - ESP: Mass flow", None)) / 2
        FG2 = (self.current_data_details.get("Stream [100] - Gas outlet of Economiser [71] - ECO -> Flue gas inlet of Rotary Air Heater [67] - ROTARY AH: Specific heat", None) + self.current_data_details.get("Stream [91] - Flue gas outlet of Rotary Air Heater [67] - ROTARY AH -> Inlet of Electrostatic Precipitator [68] - ESP: Specific heat", None)) / 2

        FG3 = (1000 / 3600) * FG1 * FG2

        # AVGin = ( [Stream [98] - Outlet 1 of Splitter [82] -> Primary air inlet of Rotary Air Heater [67] - ROTARY AH: Temperature]+[Stream [89] - Outlet of Duct - Classic [79] -> Main air inlet of Rotary Air Heater [67] - ROTARY AH: Temperature] ) / 2
        # AVGout = ( [Stream [96] - Primary air outlet of Rotary Air Heater [67] - ROTARY AH -> Primary air inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Temperature]+[Stream [90] - Main air outlet of Rotary Air Heater [67] - ROTARY AH -> Combustion air inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Temperature] ) / 2

        AVGin = (self.current_data_details.get("Stream [98] - Outlet 1 of Splitter [82] -> Primary air inlet of Rotary Air Heater [67] - ROTARY AH: Temperature", None) + self.current_data_details.get("Stream [89] - Outlet of Duct - Classic [79] -> Main air inlet of Rotary Air Heater [67] - ROTARY AH: Temperature", None)) / 2
        AVGout = (self.current_data_details.get("Stream [96] - Primary air outlet of Rotary Air Heater [67] - ROTARY AH -> Primary air inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Temperature", None) + self.current_data_details.get("Stream [90] - Main air outlet of Rotary Air Heater [67] - ROTARY AH -> Combustion air inlet of Furnace w/ Pulverizer [48] - BOILER-PULVERIZER: Temperature", None)) / 2

        # Stream [100] - Gas outlet of Economiser [71] - ECO -> Flue gas inlet of Rotary Air Heater [67] - ROTARY AH: Temperature
        stream_100 = self.current_data_details.get("Stream [100] - Gas outlet of Economiser [71] - ECO -> Flue gas inlet of Rotary Air Heater [67] - ROTARY AH: Temperature", None)

        if ((PA3 + SA3) < FG3):
            AHE = ((AVGout - AVGin) / (stream_100 - AVGin))
        else:
            AHE = ((PA3 + SA3)(AVGout - AVGin) / (FG3)(stream_100 - AVGin))

        return AHE

    def calculate_air_heater_leakage(self):
        # 90*( ( [Stream [100] - Gas outlet of Economiser [71] - ECO -> Flue gas inlet of Rotary Air Heater [67] - ROTARY AH: Mole percent of CO2] - [Stream [91] - Flue gas outlet of Rotary Air Heater [67] - ROTARY AH -> Inlet of Electrostatic Precipitator [68] - ESP: Mole percent of CO2] ) / [Stream [91] - Flue gas outlet of Rotary Air Heater [67] - ROTARY AH -> Inlet of Electrostatic Precipitator [68] - ESP: Mole percent of CO2] )
        air_heater_leakage = 90 * ((self.current_data_details.get("Stream [100] - Gas outlet of Economiser [71] - ECO -> Flue gas inlet of Rotary Air Heater [67] - ROTARY AH: Mole percent of CO2", None) - self.current_data_details.get("Stream [91] - Flue gas outlet of Rotary Air Heater [67] - ROTARY AH -> Inlet of Electrostatic Precipitator [68] - ESP: Mole percent of CO2", None)) / self.current_data_details.get("Stream [91] - Flue gas outlet of Rotary Air Heater [67] - ROTARY AH -> Inlet of Electrostatic Precipitator [68] - ESP: Mole percent of CO2", None))

        return air_heater_leakage
