"""Planning calculation; no hardware, firmware, or CAD access."""
from decimal import Decimal as D
from pathlib import Path
import json

sensor_ma = D('12') * 2
can_reserved_ma = D('100') * 2
ntc_reserved_ma = D('1')
misc_reserved_ma = D('10')
budget_ma = sensor_ma + can_reserved_ma + ntc_reserved_ma + misc_reserved_ma
design_ma = D('300')
vin_nominal, vin_high, vout = D('5'), D('5.25'), D('3.3')
iq_allowance_ma = D('1')
can_rl_min = D('120') * D('0.99') / 2
can_estimate_ma = D('17') + D('3.6') / can_rl_min * 1000
candidate_vout_min = vout * D('0.975')
candidate_loss = (vin_high-candidate_vout_min)*design_ma/1000 + vin_high*iq_allowance_ma/1000

def number(value):
    return float(value)

report = {
    'date': '2026-10-23',
    'status': 'PLANNING_ONLY_NOT_MEASURED',
    'source': 'XL4015 #2 AUX5V, proposed parallel expansion branch',
    'facts': {
        'acs71240_max_no_vout_load_ma_each': 12,
        'sn65hvd230_max_no_bus_load_ma_each': 17,
        'can_data_note': '17 mA excludes bus load; do not use it as loaded maximum',
    },
    'assumptions': {
        'input_design_range_v_not_measured': [4.75, 5.25],
        'can_family': 'Both nodes provisionally use SN65HVD230 class; ESP part unselected',
        'can_reserved_ma_each': 100,
        'ntc_reserved_ma_both': 1,
        'misc_reserved_ma': 10,
        'ldo_iq_allowance_ma_not_selected_part': 1,
        'normal_bus_only': True,
        'encoder_current_ma_each': None,
        's0b_reserved_ma': 10,
    },
    'results': {
        'current_sensors_ma_both': number(sensor_ma),
        'can_load_estimate_ma_each': number(can_estimate_ma),
        'can_load_estimate_scope': '17mA + 3.6V/(2x120ohm,1% parallel); sizing estimate, not guaranteed device maximum',
        'expansion_budget_ma': number(budget_ma),
        'design_continuous_ma': number(design_ma),
        'margin_over_budget_percent': number((design_ma / budget_ma - 1) * 100),
        'regulator_nameplate_search_class_ma': 500,
        'ldo_loss_w_at_budget_5v_excluding_iq': number((vin_nominal-vout)*budget_ma/1000),
        'ldo_loss_w_at_design_5v_excluding_iq': number((vin_nominal-vout)*design_ma/1000),
        'ldo_loss_w_at_design_5v25_excluding_iq': number((vin_high-vout)*design_ma/1000),
        'ldo_loss_w_at_design_5v25_with_iq_allowance': number((vin_high-vout)*design_ma/1000 + vin_high*iq_allowance_ma/1000),
        'xl4015_2_required_ma_ldo_case': 'I_encoder_left + I_encoder_right + 311',
        's0b_bound_ma_ignoring_led_drop_at_5v25_670ohm1': number(D('5.25')/D('670.1')*1000),
        'single_resistor_example': {
            'resistance_ohm': 17,
            'voltage_v_by_load_ma': {str(i): number(vin_nominal - D(str(i))/1000*17) for i in [0,10,100,150]},
        },
        'thermal_rise_examples_c_at_0w585': {'theta_100_c_per_w': 58.5, 'theta_200_c_per_w': 117},
    },
    'excluded_from_guarantee': [
        'CAN short circuit, abnormal termination and bus contention fault envelope',
        'Actual module LEDs, I/O loading, leakage, inrush and regulator capacitors',
        'Final 3.3V regulation tolerance and actual PCB thermal resistance',
        'Encoder consumption and total XL4015 module current/thermal capacity',
        'MCU unpowered backfeed, NTC excitation/reference tracking and USB power combinations',
    ],
    'candidate_assembly_case_not_selected_part': {
        'family': 'Microchip MCP1825S fixed 3.3V, TO-220-3 comparison only',
        'voltage_regulation_table_percent': 2.5,
        'does_not_meet_initial_1_percent_search_target': True,
        'vout_min_v_for_loss_case': number(candidate_vout_min),
        'loss_w_with_existing_1ma_ignd_allowance': number(candidate_loss),
        'not_full_guaranteed_worst_case': 'Other line/load conditions and fault/startup excluded; IGND remains an allowance',
        'datasheet_theta_ja_c_per_w': 29.4,
        'theta_scope': '4-layer standard test board, not the proposed 2-layer shield',
        'rise_c_using_datasheet_test_board_only': number(candidate_loss*D('29.4')),
        'rise_c_at_assumed_theta_100': number(candidate_loss*100),
        'proposed_ambient_c_not_confirmed': 50,
        'proposed_design_junction_c_not_confirmed': 100,
        'required_theta_c_per_w_for_proposed_targets': number(D('50')/candidate_loss),
    },
    'sources': [
        {'url': 'https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP1825-Family-Data-Sheet-DS20002056.pdf', 'revision': 'DS20002056C', 'use': 'Unselected package/precision/capacitor/thermal comparison'},
        {'url': 'https://www.allegromicro.com/-/media/files/datasheets/acs71240-datasheet.pdf', 'revision': '16', 'pdf_page': 8},
        {'url': 'https://www.ti.com/lit/ds/symlink/sn65hvd230.pdf', 'revision': 'O', 'pdf_pages': [6,7]},
        {'url': 'https://www.ti.com/lit/ds/symlink/tlv755p.pdf', 'use': 'LDO power and package/PCB thermal method only; not selected component'},
    ],
}
out = Path(__file__).with_name('budget.json')
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'budget_ma': number(budget_ma), 'design_ma': number(design_ma),
                  'worst_example_ldo_w': report['results']['ldo_loss_w_at_design_5v25_with_iq_allowance'],
                  'output': str(out)}, ensure_ascii=False))
