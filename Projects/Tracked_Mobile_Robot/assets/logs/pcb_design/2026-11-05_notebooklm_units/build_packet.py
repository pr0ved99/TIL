"""Copy PCB learning sources into separate desktop episode folders; no uploads."""
from pathlib import Path
import csv
import hashlib
import json
import re
import shutil
import fitz

PROJECT = Path(__file__).resolve().parents[4]
DESKTOP = Path('C:/Users/eyh12/Desktop')
DEST = DESKTOP / 'TMR_PCB_단원별_영상자료_2026-11-05'
OLD = DESKTOP / 'TMR_온도·전류·전압_부품선정_참고자료_2026-11-04' / '02_데이터시트와_설명서'
LOG = Path(__file__).resolve().parent


def one(pattern):
    matches = list(PROJECT.glob(pattern))
    if len(matches) != 1:
        raise ValueError((pattern, matches))
    return matches[0]


def design(number):
    return one(f'09_Electrical_Design/{number:02d}_*.md')


def learning(number):
    return one(f'07_Embedded_Learning_Notes/01_Concept_Notes/{number:02d}_*.md')


def ds(name):
    return PROJECT / 'assets/datasheets' / name


def sim(folder, name):
    return PROJECT / '09_Electrical_Design/KiCAD/Simulation' / folder / name


def extract(path, chapters=None, subchapters=None):
    lines = path.read_text(encoding='utf-8-sig').splitlines(keepends=True)
    if chapters is None and subchapters is None:
        return ''.join(lines), '전체', [(1, len(lines))]
    pattern = r'^### (\d+-\d+)\.' if subchapters else r'^## (\d+)\.'
    starts = [(i, m.group(1)) for i, line in enumerate(lines)
              if (m := re.match(pattern, line))]
    requested = set(map(str, subchapters or chapters))
    found, chunks, ranges = set(), [], []
    for j, (start, key) in enumerate(starts):
        if key in requested:
            end = starts[j + 1][0] if j + 1 < len(starts) else len(lines)
            # Do not let a subsection selection consume a later top-level chapter.
            if subchapters:
                end = next((i for i in range(start + 1, end)
                            if lines[i].startswith('## ')), end)
            found.add(key)
            chunks.append(''.join(lines[start:end]))
            ranges.append((start + 1, end))
    if found != requested:
        raise ValueError(f'Missing sections {path}: {requested - found}')
    return '\n\n'.join(chunks), ', '.join(map(str, subchapters or chapters)), ranges


def entry(path, chapters=None, subchapters=None):
    return (path, chapters, subchapters)


stm = PROJECT / 'assets/stm32f446mc.pdf'
an = ds('cd00211314-how-to-optimize-the-adc-accuracy-in-the-stm32-mcus-stmicroelectronics.pdf')
gpio = ds('an4899-guidelines-for-gpio-hardware-settings-and-lowpower-consumption-on-stm32-mcus-stmicroelectronics.pdf')
nucleo = ds('um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf')
board = ds('mb1136-default-c04_schematic.pdf')
acs = ds('Allegro_ACS71240_Datasheet.pdf')
carrier = ds('Pololu_5241_Product_Page.pdf')
ntc = ds('SEMITEC_103JT_Thermistor_Datasheet.pdf')
meter = ds('UNI-T_UT210E_User_Manual.pdf')
tps = OLD / 'TI_TPS3840_SNVSB03E_RevE.pdf'
tmux = OLD / 'TI_TMUX1511_SCDS390B_RevB.pdf'

UNITS = [
    dict(name='01_목표와_시스템_아키텍처',
         purpose='모니터링 PCB의 목적, STM·ESP 역할, 전류2·온도2·전압2와 CAN 확장, 기존 로봇과 새 PCB의 경계를 설명한다.',
         limit='확장 CAN은 목표 구성이다. 현재 실물 UART 통신과 혼동하지 않는다. 요구 수치의 제안/채택 상태를 구분한다.',
         notes=[entry(design(n)) for n in [14,15,16,19,20,21]], pdfs=[], artifacts=[]),
    dict(name='02_전원_기준전압과_ADC_기초',
         purpose='확장 전원 예산, 센서 공급과 MCU 기준전압의 차이, Nucleo VDD/AVDD 경로를 설명한다.',
         limit='초기 전체 LDO안과 이후 NTC/TPS/TMUX 공급 후보는 검토 이력이 다르다. 실제 CAD 반영/실물 공급 확인과 구분한다.',
         notes=[entry(design(17)),entry(design(18)),entry(learning(11),[1,3,11]),entry(learning(21),[30,31])],
         pdfs=[stm,nucleo,board], artifacts=[]),
    dict(name='03_전류센서_선정과_환산',
         purpose='ACS71240KEXBLT-030B3/Pololu #5241 선정, ±30A/3.3V, 감도·영점·nonratiometric 특성과 전체 전류/입력계 오차를 설명한다.',
         limit='센서 IC와 캐리어의 조건을 구분한다. 부품 도착은 정확도 검증이 아니며 내장 고속 보호가 구현된 것으로 표현하지 않는다.',
         notes=[entry(learning(11),[7,10]),entry(learning(13)),entry(learning(14)),entry(design(22))],
         pdfs=[acs,carrier,meter], artifacts=[]),
    dict(name='04_전류_RC필터와_응답_시뮬레이션',
         purpose='12kΩ/100nF 선택 근거, 차단주파수·dB·19kHz 감쇠, 시정수와 계단 응답의 관계를 설명한다.',
         limit='약0.7%는 이상 RC의19kHz 진폭 전달비다. 전체 잡음/센서 오차가0.7%라는 뜻이 아니다. 사용자 GUI 결과와 이전 자동 계산을 구분한다.',
         notes=[entry(learning(11),[8,9]),entry(learning(20),[1,2,3,4,5,6,7,8]),entry(sim('01_Current_RC','README.md'))],
         pdfs=[acs,an], artifacts=[sim('01_Current_RC',n) for n in ['Current_RC_AC.png','Current_RC_AC.csv','Current_RC_Step.png','Current_RC_Step.csv']]),
    dict(name='05_NTC_온도센서와_분압_회로',
         purpose='103JT-025 선정, 온도-저항-전압 변환,25/50°C 모사, 공급 추종·RC·단선·잔류 전하와 검증 범위를 설명한다.',
         limit='고정 저항 대입은 NTC 열응답 시험이 아니다. B식은 비교용이며 명세23은 제조사 R-T표/log(R) 보간을 기준으로 한다. 모터 케이스와 권선 온도를 구분한다.',
         notes=[entry(learning(11),[2,3,4,5,6]),entry(learning(20),[9,10,11,12]),entry(design(23)),entry(design(24)),entry(sim('02_NTC','README.md'))],
         pdfs=[ntc,stm,board], artifacts=[sim('02_NTC',n) for n in ['NTC_25C_AC.png','NTC_25C_AC.csv','NTC_50C_AC.png','NTC_50C_AC.csv']]),
    dict(name='06_전압_측정위치와_분압_필터',
         purpose='K1의30/87을 각각 GND 기준으로 측정하는 목적,12k+12k/4.7k 분압,12.6/16V OP, 전력과 AC 응답을 설명한다.',
         limit='부하 없는 초기 모델의 K=6.10638과 보호 부하를 포함한 후속 K=6.74720을 혼용하지 않는다.16V는 검토 상한이며 실제 배터리 운용 전압 지시가 아니다.',
         notes=[entry(learning(20),[13,14,15,16]),entry(learning(21),[1,2]),entry(sim('03_Voltage_Divider','README.md'))],
         pdfs=[stm],artifacts=[sim('03_Voltage_Divider',n) for n in ['Voltage_Divider_AC.png','Voltage_Divider_AC.csv']]),
    dict(name='07_저항공차_누설과_보정',
         purpose='1%/0.1% 공차 비교, 실측 저항 환산비, ADC 누설과 VREFINT/두 점 보정의 서로 다른 역할을 설명한다.',
         limit='0.1%는 구매 지시가 아닌 비교 조건이다. 키트 저항의 TCR과 계기 불확도는 미확정이다. 보정이 비선형성/온도/잡음을 모두 제거하지 않는다.',
         notes=[entry(learning(21),[3,4,5,6,10,21,22,25]),entry(learning(16)),entry(learning(19))],
         pdfs=[stm,meter,tmux,an],artifacts=[]),
    dict(name='08_MCU_OFF_입력차단과_잔류전하',
         purpose='배터리는 살아 있고 MCU는 꺼진 조건, S1/V2/VCTRL·47kΩ 풀다운, 누설과 C2 방전 모델을 설명한다.',
         limit='100pF와1GΩ OFF 모델은 학습용 가정이다. 작은 잔류 전압/에너지만으로 실제 핀 보호 PASS를 선언하지 않는다.',
         notes=[entry(learning(21),list(range(7,19))),entry(design(25))],
         pdfs=[stm,gpio,tmux],artifacts=[]),
    dict(name='09_실제_감시기_스위치_조건과_지연',
         purpose='TPS3840PL30/TMUX1511의 검출 지연, RON·누설·무전원 누설, VIT−/VIT+와 빠른 전원 하강의 검토 의미를 설명한다.',
         limit='30µs 고정 지연과 전원 기울기는 모델 조건이다.10nA@25°C와 전 온도2µA 조건을 구분한다. 특정 하강 시뮬레이션은 실제 파형 입증이 아니다.',
         notes=[entry(learning(21),[19,20,22,23,24,27,28,29]),entry(design(26))],
         pdfs=[tps,tmux,stm,gpio],artifacts=[sim('03_Voltage_Divider','detector_delay_30us.cir')]),
    dict(name='10_TPS_TMUX_연결과_전원_상태',
         purpose='AVDD 공급, MR/CT/RESET, SEL/S/D/미사용 채널, 시작·정상·하강·완전OFF·복귀와 후보 유지 판단을 설명한다.',
         limit='TPS CT-open tD는MAX50µs이며 typical이 아니다. NRST/ARM과 측정 경로 복귀를 혼동하지 않는다. 연결 초안은 제작 승인이나 전원OFF 보호 완료가 아니다.',
         notes=[entry(learning(21),list(range(30,36)))],
         pdfs=[tps,tmux,nucleo,board,stm],artifacts=[]),
    dict(name='11_전압_오차예산_ADC와_VREFINT',
         purpose='모든 오차를 VRAIL mV로 환산하고 회로/TUE/VREFINT 비율·연동 오차를 모으는 과정을 설명한다.',
         limit='TUE와 그 구성 오차를 중복 합산하지 않는다. 미정 항목을0으로 두지 않는다. 전체±0.10V 목표 충족은 아직 미판정이다.',
         notes=[entry(learning(21),subchapters=[f'36-{i}' for i in range(1,14)]),entry(learning(19))],
         pdfs=[stm,tmux,an],artifacts=[]),
    dict(name='12_온도변화_기준계기와_보정의_한계',
         purpose='보정 당시 온도, 저항 공차와TCR, VREFINT 온도 변화, 기준계기 불확도와 센서/회로 정확도 구분을 설명한다.',
         limit='키트 저항 TCR은 미상이고 가정값 계산은 실물 규격이 아니다. UT210E 보유가±0.10V 검증 적합성을 의미하지 않는다. 향후38절의 완성본은 아직 없다.',
         notes=[entry(learning(21),[26]),entry(learning(21),subchapters=[f'36-{i}' for i in range(14,20)]),entry(learning(16)),entry(learning(19))],
         pdfs=[stm,meter,ntc,acs],artifacts=[]),
    dict(name='13_외부정착_ADC취득과_채널전환',
         purpose='37-1~37-3의 네 시간 구분, 허용 잔차에서 정착 시간 계산, RADC/CADC·VREFINT·샘플링 후보와 채널 전환을 설명한다.',
         limit='10mV 배분/약2.68ms는 설명용 명목 계산이다.14MHz/480cycles는 미구현 후보이며100pF와 내부4/7pF를 구분한다.37-4 잡음/처리는 다음 학습으로 남는다.',
         notes=[entry(learning(21),[37])],pdfs=[stm,an],artifacts=[]),
    dict(name='14_검증명세와_제작_전_남은일',
         purpose='센서 제외/포함 시험, 보정점/독립 검증점, DC/PWM/고장 검증, ERC/DRC·실물 단계와 현재 미결을 설명한다.',
         limit='제작 CAD는 전류2·온도2 초안이며 전압 보호2채널은 미반영이다. ERC·모델 계산·실측·전체 인수는 서로 다르다. 잡음 처리 과거 전류 학습을 전압37-4 완료로 표현하지 않는다.',
         notes=[entry(learning(n)) for n in [12,15,17,18]]+[entry(design(22)),entry(design(23)),entry(PROJECT/'09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/README.md')],
         pdfs=[meter,ds('BENETECH_GM1312_User_Manual.pdf')],
         artifacts=[PROJECT/'09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/exports/TMR_Monitor_Shield_RevA_schematic.pdf',PROJECT/'09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/exports/TMR_Monitor_Shield_RevA_placement.pdf']),
]

GLOBAL = '''기준일: 2026-11-05, 학습37-3 자료 작성 시점.
현재 단계는 계산·부품 후보·검증 조건 검토다. 제작 PCB/전체 보호/전체 정확도는 완료되지 않았다.
자료의 수치를 제조사 규격, 프로젝트 목표/후보, 가정 계산, 사용자 시뮬레이션 관측, 실물 측정으로 구분한다.
설명과 자료 작성 완료는 사용자 필기/이해/실측 완료가 아니다.
본문 날짜별 '다음'은 당시 이력이다. 현재 PCB 재개점은37-4이며 오늘 학습은37-3에서 멈췄다.
원문 수식의 단위·MIN/TYP/MAX·판본·시험 조건과 미결 항목을 유지한다. 상충하면 이 안내만으로 원문을 덮지 말고 후속 문서와 원본 근거를 대조한다.
영상 생성·업로드·NotebookLM 조작은 수행하지 않았다. 제작 방법/맞춤 프롬프트는 사용자가 별도 요청한 뒤 다룬다.
'''


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    if DEST.exists():
        raise FileExistsError(f'Existing packet preserved: {DEST}')
    sources = sorted({p for u in UNITS for p in
                      [*(x[0] for x in u['notes']), *u['pdfs'], *u['artifacts']]}, key=str)
    for p in sources:
        if not p.is_file():
            raise FileNotFoundError(p)
    # Validate chapter selectors before creating the destination.
    for u in UNITS:
        for args in u['notes']:
            extract(*args)
    DEST.mkdir()
    archive = DEST / '90_원문보관'
    archive.mkdir()
    manifest, originals, pages = [], {}, {}
    for i, source in enumerate(sources, 1):
        target = archive / f'{i:03d}_{source.name}'
        shutil.copy2(source, target)
        digest = sha(source)
        if digest != sha(target):
            raise ValueError(f'Hash mismatch: {source}')
        originals[source] = (target, digest)
        if source.suffix.lower() == '.pdf':
            with fitz.open(target) as doc:
                if doc.page_count < 1: raise ValueError(target)
                pages[str(source)] = doc.page_count
        manifest.append(dict(kind='exact_original_copy', unit='archive', source=str(source),
                             source_sha256=digest, destination=str(target.relative_to(DEST)),
                             sha256=digest, bytes=target.stat().st_size))
    index = ['TMR PCB 단원별 영상 참고자료', '', GLOBAL, '단원 목록', '']
    for u in UNITS:
        folder = DEST / u['name']; folder.mkdir()
        index += [f"{u['name']}: {u['purpose']}", f"  경계: {u['limit']}", '']
        scope = f"{u['name']}\n\n{GLOBAL}\n다룰 내용\n{u['purpose']}\n\n이 단원의 해석 경계\n{u['limit']}\n\n출처별 자료\n"
        for j, args in enumerate(u['notes'], 1):
            source = args[0]
            content, selected, ranges = extract(*args)
            original, digest = originals[source]
            title = f'{j:02d}_{source.stem}.txt'
            target = folder / title
            header = f"단원: {u['name']}\n원본: {source}\n발췌 범위: {selected}\n원문 줄 범위(1부터): {ranges}\n원본 SHA256: {digest}\n보존 사본: ../{original.relative_to(DEST).as_posix()}\n이하 원문 발췌(요약/새 실험 결과 아님)\n\n"
            target.write_text(header + content, encoding='utf-8')
            manifest.append(dict(kind='verbatim_text_extract',unit=u['name'],source=str(source),
                                 source_sha256=digest,sections=selected,lines=ranges,
                                 destination=str(target.relative_to(DEST)),sha256=sha(target),bytes=target.stat().st_size))
            scope += f'- {title}: 원문 {selected}\n'
        for category, paths in [('데이터시트',u['pdfs']),('관측과_모델근거',u['artifacts'])]:
            if not paths: continue
            child = folder / category; child.mkdir()
            for source in paths:
                target = child / source.name
                shutil.copy2(source,target)
                digest = originals[source][1]
                if sha(target) != digest: raise ValueError(target)
                manifest.append(dict(kind='exact_topic_copy',unit=u['name'],source=str(source),source_sha256=digest,
                                     destination=str(target.relative_to(DEST)),sha256=digest,bytes=target.stat().st_size))
                scope += f'- {category}/{source.name}\n'
        target=folder/'00_단원범위와_현재상태.txt';target.write_text(scope,encoding='utf-8')
        manifest.append(dict(kind='generated_scope',unit=u['name'],source='',source_sha256='',
                             destination=str(target.relative_to(DEST)),sha256=sha(target),bytes=target.stat().st_size))
    index += ['보관 구조', '각 단원: 해당 주제의 원문 발췌 TXT + 관련 PDF + 저장 관측/모델 근거.',
              '90_원문보관: 사용한 파일 전체의 바이트 동일 사본. 번호는 파일명 충돌 방지용이며 원본 경로는 목록에 보존.',
              'TI TPS/TMUX PDF는 이전 바탕화면 자료 묶음에서 복제했고 나머지는 현재 프로젝트 원본을 사용.',
              '기존11/4 폴더와 프로젝트 원본은 이동/삭제/덮어쓰기하지 않았다.',
              '원본 CAD/원시 수치 파일은 읽기 근거다. 영상의 검증 완료 주장으로 확대하지 않는다.',
              '학습37-4 및38/39 새 본문은 미작성이다. 관련 과거 자료를 완료된 후속 학습으로 표현하지 않는다.']
    (DEST/'00_자료목록과_현재상태.txt').write_text('\n'.join(index)+'\n',encoding='utf-8')
    (DEST/'01_복제_출처_목록.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    with (DEST/'02_복제_출처_목록.csv').open('w',encoding='utf-8-sig',newline='') as handle:
        fields=['kind','unit','source','source_sha256','destination','sha256','bytes']
        writer=csv.DictWriter(handle,fields,extrasaction='ignore');writer.writeheader();writer.writerows(manifest)
    mismatches=[]
    for row in manifest:
        if sha(DEST/row['destination']) != row['sha256']: mismatches.append(row['destination'])
        if row['source'] and sha(Path(row['source'])) != row['source_sha256']:
            mismatches.append('SOURCE_CHANGED:'+row['source'])
    if mismatches: raise ValueError(mismatches)
    receipt=dict(date='2026-11-05',destination=str(DEST),units=len(UNITS),unique_source_files=len(sources),
                 exact_copies=sum(x['kind'].startswith('exact_') for x in manifest),
                 text_extracts=sum(x['kind']=='verbatim_text_extract' for x in manifest),
                 original_pdfs_opened=len(pages),pdf_page_counts=pages,hash_mismatches=mismatches,
                 source_files_unchanged=True,notebooklm_uploaded=False,video_generated=False,
                 instructions_deferred=True,manifest_sha256=sha(DEST/'01_복제_출처_목록.json'))
    receipt['total_files_including_receipt']=sum(1 for p in DEST.rglob('*') if p.is_file())+1
    receipt['bytes_excluding_receipt']=sum(p.stat().st_size for p in DEST.rglob('*') if p.is_file())
    payload=json.dumps(receipt,ensure_ascii=False,indent=2)
    (DEST/'03_복제_검증결과.json').write_text(payload,encoding='utf-8')
    (LOG/'receipt.json').write_text(payload,encoding='utf-8')
    (LOG/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='pdf_page_counts'},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
