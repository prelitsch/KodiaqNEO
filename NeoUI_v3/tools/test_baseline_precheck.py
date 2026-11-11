#!/usr/bin/env python3
"""Mock all device commands under NeoUI_v3; never run a hardware command."""
from pathlib import Path
import datetime,hashlib,json,os,re,shlex,subprocess,tempfile
from review_baseline import review,parse_receipt
OUT=Path(__file__).resolve().parents[1]
def posix(p):
 s=p.resolve().as_posix()
 return '/'+s[0].lower()+s[2:] if len(s)>2 and s[1]==':' else s
def main():
 shell=Path('C:/Program Files/Git/bin/sh.exe') if os.name=='nt' else Path('/bin/sh')
 if not shell.is_file():raise RuntimeError('Existing POSIX shell not found; no WSL install attempted')
 script=OUT/'tools/baseline_precheck.sh';assert b'\r' not in script.read_bytes(),'QNX collector must retain LF line endings';subprocess.run([str(shell),'-n',str(script)],check=True,capture_output=True)
 text=script.read_text();tokens=re.findall(r'(?m)^\s*(?:if\s+!?\s*)?([a-z][a-z0-9_-]*)\b',text)
 forbidden={'cp','mv','rm','mkdir','touch','chmod','chown','sync','eval','exec','tee','dd','printf','reboot'}
 assert not forbidden&set(tokens)
 lexer=shlex.shlex(text,posix=True,punctuation_chars='<>');lexer.whitespace_split=True;lex=list(lexer)
 for i,t in enumerate(lex):
  if t in ['>','>>','>|','<>']:assert i+1<len(lex) and (lex[i+1]=='/dev/null' or (lex[i+1]=='&1' and i>0 and lex[i-1]=='2')),'unexpected output-file redirection'
 root=Path(tempfile.mkdtemp(prefix='baseline_precheck_tests_',dir=OUT/'neoui_workspace/refs'));assert root.resolve().is_relative_to(OUT.resolve())
 policy=json.loads((OUT/'release-policy.json').read_text());v2=policy['known_reference_states']['neoui_v2_pilot'];meta=OUT.parent/'app50_extract/lba0/eso/hmi/lsd/Resources/skin1'
 envbase=dict(os.environ,MOCK_SHA1=v2['sha1'],MOCK_SHA256=v2['sha256'],MOCK_BYTES=str(v2['bytes']),MOCK_TRAIN=policy['firmware'],MOCK_MU='1440',MOCK_DF='/dev/hd0t177 1404880 1015019 389861 73% /mnt/app/')
 hashes={n:hashlib.sha1((meta/n).read_bytes()).hexdigest() for n in ['images.res','viewhandler.zip','info.txt','ambienceColorMap.res']}
 def run(name,overrides=None,markers=(),missing=None,sha256=True):
  base=root/name;binpath=base/'bin';app=base/'net/mmx/mnt/app';res=app/'eso/hmi/lsd/Resources/skin3';reader=app/'eso/bin/apps/pc';hashpath=base/'net/rcc/usr/bin/sha1sum'
  for p in [binpath,res,reader.parent,hashpath.parent]:p.mkdir(parents=True,exist_ok=True)
  def put(p,s):p.write_text(s,encoding='utf-8',newline='\n');p.chmod(0o755)
  put(reader,'#!/bin/sh\nexit 1\n');(res/'images.mcf').write_bytes(b'OFFLINE MOCK ONLY')
  for n in hashes:(res/n).write_text('OFFLINE MOCK ONLY')
  put(hashpath,'#!/bin/sh\n[ "${MOCK_HASH_FAIL:-0}" = 0 ] || exit 1\ncase "$1" in\n'+''.join('*/'+n+') echo "'+h+'  $1" ;;\n' for n,h in hashes.items())+'*) echo "$MOCK_SHA1  $1" ;;\nesac\n')
  put(binpath/'on','#!/bin/sh\n[ "${MOCK_ON_FAIL:-0}" = 0 ] || exit 1\ncase "$4" in s:30:1966084) echo "$MOCK_TRAIN" ;; s:30:1966083) echo "$MOCK_MU" ;; *) exit 1 ;; esac\n')
  put(binpath/'df','#!/bin/sh\necho "$MOCK_DF"\nexit "${MOCK_DF_FAIL:-0}"\n');put(binpath/'mount','#!/bin/sh\necho "/dev/hd0t177 on /mnt/app type qnx6 (ro)"\nexit "${MOCK_MOUNT_FAIL:-0}"\n');put(binpath/'wc','#!/bin/sh\necho "$MOCK_BYTES"\n')
  for n in ['awk','date','ls']:put(binpath/n,'#!/bin/sh\nexec /usr/bin/'+n+' "$@"\n')
  if sha256:put(binpath/'sha256sum','#!/bin/sh\n[ "${MOCK_SHA256_FAIL:-0}" = 0 ] || exit 1\necho "$MOCK_SHA256  $1"\n')
  for n in markers:p=base/'net/mmx/fs/sda0/mod/neoui/v3'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('mock marker')
  if missing:(reader if missing=='reader' else res/missing).unlink()
  snapshot=lambda:{str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in base.rglob('*') if p.is_file()}
  before=snapshot();env=dict(envbase,**(overrides or {}))
  # Isolated PATH: all device commands mocked; awk/date/ls explicitly use Git tools.
  cmd=[str(shell),'-c','PATH="$1"; export PATH; shift; exec /bin/sh "$@"','offline-test',posix(binpath),posix(script),'--offline-fixture',posix(base)]
  proc=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=20);assert snapshot()==before,'collector changed fixture files'
  return proc
 cases=[]
 for name,override,markers,missing,success in [
  ('known_v2',{},(),None,True),('known_v1',{'MOCK_SHA1':policy['known_reference_states']['neoui_v1']['sha1']},(),None,True),('known_mib',{'MOCK_SHA1':policy['known_reference_states']['mib_pre_neoui']['sha1']},(),None,True),
  ('unknown_hash',{'MOCK_SHA1':'a'*40},(),None,False),('hash_unknown',{'MOCK_SHA1':'UNKNOWN'},(),None,False),('hash_failure',{'MOCK_HASH_FAIL':'1'},(),None,False),('wrong_train',{'MOCK_TRAIN':'MHI2_UNKNOWN'},(),None,False),('wrong_mu',{'MOCK_MU':'1163'},(),None,False),('reader_failure',{'MOCK_ON_FAIL':'1'},(),None,False),('garbage_train',{'MOCK_TRAIN':'junk\nMHI2_ER_SKG13_P4526'},(),None,False),
  ('df_failure',{'MOCK_DF_FAIL':'1'},(),None,False),('df_ambiguous',{'MOCK_DF':envbase['MOCK_DF']+'\n/dev/hd1 1 1 0 100% /other'},(),None,False),('df_nonnumeric',{'MOCK_DF':'/dev/hd0t177 1 1 UNKNOWN 73% /mnt/app'},(),None,False),('df_no_dev',{'MOCK_DF':'invalid output'},(),None,False),('wrong_df_mount',{'MOCK_DF':'/dev/hd0t177 1 1 100 73% /other'},(),None,False),('invalid_percent',{'MOCK_DF':'/dev/hd0t177 1 1 100 173% /mnt/app'},(),None,False),('zero_free_discovery',{'MOCK_DF':'/dev/hd0t177 1 1 0 100% /mnt/app'},(),None,True),('mount_failure',{'MOCK_MOUNT_FAIL':'1'},(),None,False),('sha256_failure',{'MOCK_SHA256_FAIL':'1'},(),None,False),
  ('missing_target',{},(),'images.mcf',False),('missing_metadata',{},(),'images.res',False),('missing_reader',{},(),'reader',False),('install_marker',{},('INSTALL_V3_NOW',),None,False),('restore_marker',{},('RESTORE_V2',),None,False),('conflicting_markers',{},('INSTALL_V3_NOW','RESTORE_V2'),None,False),('diagnostic_marker',{},('DIAGNOSTIC_ONLY',),None,False)]:
  proc=run(name,override,markers,missing);assert (proc.returncode==0)==success,(name,proc.stdout,proc.stderr);cases.append(dict(name=name,expected='collected, not authorized' if success else 'rejected',passed=True))
 p=run('no_sha256',sha256=False);assert p.returncode==0 and 'CURRENT_SHA256=UNKNOWN' in p.stdout;assert not review(p.stdout)['reference_identity_and_receipt_checks_pass'];cases.append(dict(name='no_sha256_is_incomplete',passed=True))
 good=run('receipt_review');assert good.returncode==0
 assert not review(good.stdout)['reference_identity_and_receipt_checks_pass'],'simulation must not count as live evidence'
 fabricated=good.stdout.replace('MODE=OFFLINE_SIMULATION','MODE=DEVICE_READ_ONLY');r=review(fabricated);assert r['reference_identity_and_receipt_checks_pass'] and not r['release_ready'] and not r['installed_baseline_activated']
 for token,replacement in [(v2['sha256'],'UNKNOWN'),('STABLE_DURING_COLLECTION=true','STABLE_DURING_COLLECTION=false'),('CURRENT_BYTES='+str(v2['bytes']),'CURRENT_BYTES=1'),('MU=1440','MU=1163')]:assert not review(fabricated.replace(token,replacement))['reference_identity_and_receipt_checks_pass']
 assert not review(fabricated,now=datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(days=2))['reference_identity_and_receipt_checks_pass']
 try:parse_receipt(good.stdout+'CURRENT_SHA1=UNKNOWN\n')
 except ValueError:pass
 else:raise AssertionError('duplicate keys accepted')
 result=dict(status='PASS OFFLINE MOCKS ONLY',shell=str(shell),shell_syntax=True,shellcheck='not installed; read-only command audit, isolated mocks and fixture byte snapshots used; QNX empiricism still required',collector_cases=cases,receipt_review_tests=8,all_fixture_files_unchanged=True,device_commands_mocked=True,sd_or_vehicle_access=False,device_baseline_confirmed=False,release_ready=False)
 (OUT/'neoui_reports/BASELINE_PRECHECK_TESTS.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('PASS:',len(cases),'collector cases +8 receipt checks; syntax, isolated device mocks and zero fixture-byte changes; no hardware/SD access')
if __name__=='__main__':main()
