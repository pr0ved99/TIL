"""Make a non-destructive 39-source upload packet from the verified unit snapshot."""
from pathlib import Path
import hashlib
import json
import shutil

SOURCE = Path(r'C:\Users\eyh12\Desktop\TMR_PCB_단원별_영상자료_2026-11-05')
TARGET = Path(r'C:\Users\eyh12\Desktop\TMR_PCB_NotebookLM_전체영상_2026-11-05')
HERE = Path(__file__).resolve().parent

ALIASES = {
    'stm32f446mc.pdf': 'D01_STM32F446_데이터시트.pdf',
    'um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf': 'D02_NUCLEO64_보드설명서.pdf',
    'mb1136-default-c04_schematic.pdf': 'D03_NUCLEO64_C04_회로도.pdf',
    'Allegro_ACS71240_Datasheet.pdf': 'D04_ACS71240_데이터시트.pdf',
    'Pololu_5241_Product_Page.pdf': 'D05_Pololu5241_캐리어.pdf',
    'SEMITEC_103JT_Thermistor_Datasheet.pdf': 'D06_SEMITEC103JT_데이터시트.pdf',
    'TI_TMUX1511_SCDS390B_RevB.pdf': 'D07_TMUX1511_데이터시트.pdf',
    'TI_TPS3840_SNVSB03E_RevE.pdf': 'D08_TPS3840_데이터시트.pdf',
    'cd00211314-how-to-optimize-the-adc-accuracy-in-the-stm32-mcus-stmicroelectronics.pdf': 'D09_ST_AN2834_ADC정확도.pdf',
    'an4899-guidelines-for-gpio-hardware-settings-and-lowpower-consumption-on-stm32-mcus-stmicroelectronics.pdf': 'D10_ST_AN4899_GPIO.pdf',
    'UNI-T_UT210E_User_Manual.pdf': 'D11_UT210E_사용설명서.pdf',
    'BENETECH_GM1312_User_Manual.pdf': 'D12_GM1312_사용설명서.pdf',
    'Current_RC_AC.png': 'E01_전류_RC_AC.png',
    'Current_RC_Step.png': 'E02_전류_RC_계단응답.png',
    'NTC_25C_AC.png': 'E03_NTC_25C_AC.png',
    'NTC_50C_AC.png': 'E04_NTC_50C_AC.png',
    'Voltage_Divider_AC.png': 'E05_전압분압_AC.png',
    'Current_RC_AC.csv': 'E06_전류_RC_AC.csv',
    'Current_RC_Step.csv': 'E07_전류_RC_계단응답.csv',
    'NTC_25C_AC.csv': 'E08_NTC_25C_AC.csv',
    'NTC_50C_AC.csv': 'E09_NTC_50C_AC.csv',
    'Voltage_Divider_AC.csv': 'E10_전압분압_AC.csv',
    'detector_delay_30us.cir': 'E11_detector_delay_30us.txt',
    'TMR_Monitor_Shield_RevA_schematic.pdf': 'E12_쉴드_회로도초안.pdf',
    'TMR_Monitor_Shield_RevA_placement.pdf': 'E13_쉴드_가배치초안.pdf',
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if TARGET.exists():
        raise SystemExit(f'Existing target preserved: {TARGET}')
    units = sorted(p for p in SOURCE.iterdir() if p.is_dir()
                   and p.name[:2].isdigit() and 1 <= int(p.name[:2]) <= 14)
    assert len(units) == 14
    all_inputs = [p for u in units for p in u.rglob('*') if p.is_file()]
    before = {str(p): digest(p) for p in all_inputs}
    sources_by_name = {}
    for u in units:
        for p in u.rglob('*'):
            if p.is_file() and p.parent != u:
                if p.name in sources_by_name:
                    assert digest(p) == digest(sources_by_name[p.name]), p.name
                sources_by_name[p.name] = p
    assert set(sources_by_name) == set(ALIASES)
    upload = TARGET / '업로드_39개'
    upload.mkdir(parents=True)
    manifest = []
    mapping = []
    for u in units:
        destination = upload / ('U' + u.name + '.txt')
        pieces = [f'TMR 영상 단원 {u.name}\n'
                  '이 자료는 2026-11-05 기존 단원 자료의 본문을 축약 없이 합친 업로드용 묶음이다.\n'
                  '아래 출처별 텍스트와 판본·가정·미결을 보존한다. 복제 당시 생성 안내 보류 문구는 당시 이력이다.\n'
                  '현재는 영상 제작 안내 단계이며 실제 업로드·생성 완료를 뜻하지 않는다.\n\n']
        offsets = []
        position = len(pieces[0])
        for p in sorted(u.glob('*.txt')):
            separator = f'\n===== 출처: {p.relative_to(SOURCE).as_posix()} =====\n'
            body = p.read_text(encoding='utf-8-sig')
            pieces.extend([separator, body, '\n'])
            start = position + len(separator)
            offsets.append({'source': p.relative_to(SOURCE).as_posix(),
                            'source_sha256': before[str(p)], 'start': start, 'length': len(body)})
            position = start + len(body) + 1
        destination.write_text(''.join(pieces), encoding='utf-8', newline='\n')
        saved = destination.read_text(encoding='utf-8')
        for entry in offsets:
            assert saved[entry['start']:entry['start']+entry['length']] == (SOURCE / entry['source']).read_text(encoding='utf-8-sig')
        support = sorted({ALIASES[p.name] for p in u.rglob('*') if p.is_file() and p.parent != u})
        mapping.append({'unit': u.name, 'select': [destination.name] + support})
        manifest.append({'file': destination.name, 'sha256': digest(destination), 'mode': 'verbatim_text_concatenation', 'sources': offsets})
    for original, alias in ALIASES.items():
        source = sources_by_name[original]
        destination = upload / alias
        shutil.copy2(source, destination)
        assert digest(destination) == before[str(source)]
        manifest.append({'file': alias, 'sha256': digest(destination),
                         'mode': 'byte_identical_copy' if source.suffix == destination.suffix else 'byte_identical_copy_with_txt_extension',
                         'source': source.relative_to(SOURCE).as_posix()})
    assert len(list(upload.iterdir())) == len(manifest) == 39
    assert all(digest(Path(p)) == sha for p, sha in before.items())
    guide = (HERE / 'README.md').read_text(encoding='utf-8')
    marker = '## 14단원 전체 영상 제작 가이드'
    assert marker in guide
    (TARGET / '00_전체_제작가이드.txt').write_text(guide[guide.index(marker):], encoding='utf-8', newline='\n')
    receipt = {'date':'2026-11-05', 'source_snapshot':str(SOURCE), 'target':str(TARGET),
               'upload_sources':39, 'unit_txt':14, 'merged_original_txt':61,
               'byte_identical_support':25, 'input_files_unchanged':len(before),
               'unit_source_mapping':mapping, 'manifest':manifest,
               'notebooklm_uploaded':False, 'video_generated':False}
    data = json.dumps(receipt, ensure_ascii=False, indent=2) + '\n'
    (TARGET / '01_출처와_검증.json').write_text(data, encoding='utf-8')
    (HERE / 'single_notebook_receipt.json').write_text(data, encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ['target','upload_sources','unit_txt','merged_original_txt','byte_identical_support','input_files_unchanged']},ensure_ascii=False))

if __name__ == '__main__':
    main()
