




from core.controller.base import BaseController


class DataEngineFlowController(BaseController):
    
    def get_all_engine_flow_data(self):
        """Data to get
        EG = EG = out__Plant gross power
        HPT = out__ST Assembly [1] - HPT: ST Group [1] - HPT-1: Group overall efficiency|*|out__ST Assembly [1] - HPT: ST Group [2] - HPT-2: Group overall efficiency|*|out__ST Assembly [1] - HPT: ST Group [58] - HPT-3: Group overall efficiency
        IPT = out__ST Assembly [2] - IPT: ST Group [3] - IPT-1: Group overall efficiency|*|out__ST Assembly [2] - IPT: ST Group [4] - IPT-2: Group overall efficiency
        LPT = out__ST Assembly [3] - LPT: ST Group [5] - LPT-1: Group overall efficiency|*|out__ST Assembly [3] - LPT: ST Group [6] - LPT-2: Group overall efficiency|*|out__ST Assembly [3] - LPT: ST Group [7] - LPT-3: Group overall efficiency|*|out__ST Group [60] - LPT-4: Group overall efficiency
        RH7 = out_ttd_hph_7
        RH6 = out_ttd_hph_6
        RH5 = out_ttd_hph_5
        RH1 = out_ttd_lph_1
        RH2 = out_ttd_lph_2
        RH3 = out_ttd_lph_3
        """